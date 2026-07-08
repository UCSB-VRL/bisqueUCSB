# k3s Deployment

These manifests run BisQue, nginx, Postgres, and Argo WorkflowTemplates in the
`bisque` namespace.

Build and load or push a BisQue app image before applying these manifests. The
example deployment uses `bisque:local` with `imagePullPolicy: IfNotPresent`.
Change the image in `40-bisque.yaml` when using a registry tag.

For a disposable local k3s cluster, see the k3d example in
`deploy/k3s/examples/k3d`.

## Configure

Edit `10-configmap.yaml` for non-secret runtime settings. The manifest lists
the deployment-relevant `BISQUE_*` settings explicitly so k3s behavior does not
depend on hidden generator defaults for paths, service loading, mail settings,
or module runtime settings.
The container image carries immutable static asset links in `/app/public`; the
`bisque-runtime` volume mounted at `/app/.bisque` is only for mutable runtime
config, data, logs, and setup state.

```yaml
BISQUE_PUBLIC_URL: http://bisque.localhost
BISQUE_DOCKER_BACKEND: argo
BISQUE_DOCKER_CALLBACK_URL: http://bisque:8080
BISQUE_ORGANIZATION: Your Organization
BISQUE_TITLE: BisQue Image Repository
BISQUE_ADMIN_EMAIL: admin@example.com
```

Edit `11-secret.yaml` for secrets and database credentials:

```yaml
BISQUE_SECRET: change-me
BISQUE_DBURL: postgresql://bisque:bisque@postgres:5432/bisque
BISQUE_SMTP_PASSWORD: ""
POSTGRES_DB: bisque
POSTGRES_USER: bisque
POSTGRES_PASSWORD: bisque
```

Keep `BISQUE_DBURL` consistent with `POSTGRES_DB`, `POSTGRES_USER`, and
`POSTGRES_PASSWORD`. If the Postgres credentials change but the URL does not,
BisQue will start with stale database credentials.

## Apply

```bash
kubectl apply -f deploy/k3s
```

Runtime files are stored in the `bisque-runtime` persistent volume, database
files in the `postgres-data` persistent volume, and nginx upload handoff files in
an `emptyDir` shared by the BisQue and nginx containers.
At startup, BisQue still renders legacy config files from ConfigMap and Secret
environment variables, but it no longer links static assets into the runtime
volume.

## Local module images

The Argo WorkflowTemplates use module image names from each module's
`runtime-module.cfg` and set `imagePullPolicy: IfNotPresent`. In a k3d cluster,
local module images must be imported into the cluster before the module runs:

```bash
docker build \
  -f source/modules/EdgeDetection/Dockerfile \
  -t edgedetection:v1.0.0 \
  source/modules/EdgeDetection

k3d image import edgedetection:v1.0.0 -c "$CLUSTER_NAME"
```

Use this for each local module image, or push the image to a registry that the
cluster can pull from and update the module image reference accordingly.
