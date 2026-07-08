# Docker Deployment

Build the BisQue app image:

```bash
BISQUE_DOCKER_TAG=dev just docker-build
```

`just docker-build` builds the reusable Flox environment image first when
`BISQUE_ENV_IMAGE` does not already exist, then builds the runnable BisQue app
image from `deploy/docker/Dockerfile`.

The equivalent manual build is:

```bash
docker build \
  -f deploy/docker/Dockerfile \
  --build-arg BISQUE_ENV_IMAGE=bisque:env \
  -t bisque:local .
```

`bisque:env` is the reusable Flox environment image. `bisque:local` is the
locally built BisQue app image used by Compose and the k3s examples; set
`BISQUE_ENV_IMAGE` or `BISQUE_IMAGE` when you want to use a registry or
production tag instead.

The app image build runs `uv sync`, installs the converter wrappers, and bakes
static asset links into `/app/public`. Container startup only prepares runtime
config/data, renders legacy config files from environment variables, runs the
idempotent BisQue setup steps, and starts BisQue.
Bio-Formats is excluded from the Docker image by default because it is GPL
licensed. For a private/local image that intentionally bundles Bio-Formats, add
`--build-arg BISQUE_INSTALL_BIOFORMATS=1` to the app image build.

Run the compose stack with nginx in front:

```bash
cp .env.example .env
# edit .env for local ports, secrets, site metadata, or SMTP if needed
docker compose -f deploy/docker/compose.yml up --build
```

The compose stack starts nginx, BisQue, and Postgres. BisQue uses Postgres by
default in compose, while direct local Flox runs still default to SQLite unless
`BISQUE_DBURL` is set. Postgres must be healthy before BisQue starts, and nginx
waits for BisQue's HTTP healthcheck before accepting traffic.

Compose uses the same env-first config generator as local development. It reads
the root `.env` in two ways: Compose uses it for `${...}` interpolation, and the
BisQue service also receives it through `env_file`. Explicit values in
`deploy/docker/compose.yml` override `.env` for container-only settings such as
`/app/.bisque` runtime paths, `/app/public` static assets, and the in-container
HTTP port.

The most important production settings are:

```bash
BISQUE_DBURL=postgresql://bisque:bisque@postgres:5432/bisque
BISQUE_SECRET=replace-me
BISQUE_HTTP_PORT=8080
BISQUE_DEBUG=false
BISQUE_JS_ENVIRONMENT=production
```

Compose defaults to deployment-style debug settings; set `BISQUE_DEBUG=true`
and `BISQUE_JS_ENVIRONMENT=development` in `.env` only when debugging the
containerized app.

Leave `BISQUE_PUBLIC_URL` unset for normal compose runs. Compose defaults it to
`http://127.0.0.1:${BISQUE_HTTP_PORT}`, matching the host port published by
nginx. Docker-backed module containers receive rewritten callback URLs through
`BISQUE_DOCKER_CALLBACK_URL`, which defaults to
`http://host.docker.internal:${BISQUE_HTTP_PORT}`. Use
`http://localhost:${BISQUE_HTTP_PORT}` or the machine's IP address in the
browser.

Startup writes generated config under the `bisque-runtime` volume at
`.bisque/config`. Changed generated files are backed up before they are
rewritten, but production secrets should still be supplied from the deployment
environment rather than edited into generated files. Static assets are not
linked during container startup; `/app/public` is immutable image content while
`/app/.bisque` remains mutable runtime state.

Large uploads through compose use nginx's `X-File` handoff path. nginx writes
request bodies into the shared `bisque-upload-tmp` volume and BisQue reads the
same path from its container.

The compose stack stores BisQue runtime config/data/log state in the
`bisque-runtime` volume and database state in the `postgres-data` volume.

Docker-backed module execution uses the host Docker daemon through
`/var/run/docker.sock`, which is mounted into the `bisque` service. The app image
inherits the Docker CLI from the Flox environment for module launchers. For local
module images, compose sets `BISQUE_DOCKER_HUB` to empty by default so module
image names are used exactly as written in each `runtime-module.cfg`.
On Linux, generated module launchers use host networking and add
`host.docker.internal` as a host-gateway alias so module callback URLs resolve
inside the spawned module container.

Build the EdgeDetection module image before running that module:

```bash
docker build \
  -f source/modules/EdgeDetection/Dockerfile \
  -t edgedetection:v1.0.0 \
  source/modules/EdgeDetection
```
