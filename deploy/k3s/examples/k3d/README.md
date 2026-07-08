# BisQue k3d Example
This is an example that deploys BisQue in a docker-deployed K3s instance and orchestrates modules using ArgoWorkflows. When you installed Flox you also gained access to Nix - an ecosystem for reproducing environments. This gives us access to the `nix-shell` command which creates a temporary shell with the packages outlined in `shell.nix`. This allows us to run the following commands and deploy the cluster:

From this directory:

```bash
nix-shell
source ./env.example

scripts/create-cluster.sh
scripts/install-deps.sh
scripts/build-load-bisque.sh
scripts/deploy-bisque.sh
```

Open BisQue through the local ingress:

```text
http://bisque.localhost:8080
```

To clean up the cluster:

```bash
scripts/reset.sh
```

## Configuration

The scripts default `BISQUE_REPO` to the repository checkout that contains this
example. Source `env.example`, copy it to an untracked `env.sh`, or export
variables in your shell to override defaults:

```bash
export BISQUE_REPO=/path/to/bisque
export CLUSTER_NAME=bisque-test
export K3S_IMAGE=rancher/k3s:v1.30.14-k3s1
export ARGO_WORKFLOWS_VERSION=v4.0.6
export BISQUE_ENV_IMAGE=bisque:env
export BISQUE_DOCKER_TAG=dev
export BISQUE_IMAGE=bisque:local
export BISQUE_HTTP_PORT=8080
export BISQUE_HTTPS_PORT=8443
```

This example installs only the local smoke-test dependencies: ingress-nginx,
Argo Workflows, the local BisQue image, and the BisQue k3s manifests.

## Module images in k3d
The k3s manifests configure BisQue module execution through Argo Workflows. The
workflow templates use `imagePullPolicy: IfNotPresent`, so every local module
image referenced by a module's `runtime-module.cfg` must be available inside the
k3d cluster. For example, EdgeDetection declares `docker.image =
edgedetection:v1.0.0`.

Build and import that module image before running the module:

```bash
k3d image import edgedetection:v1.0.0 -c "$CLUSTER_NAME"
```

Repeat the `k3d image import` step after rebuilding a local module image. If a
module image is pushed to a registry that the cluster can pull from, update the
module configuration to reference that registry tag instead of importing it into
k3d.
