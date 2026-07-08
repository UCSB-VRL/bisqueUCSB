#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

require_command helm
require_command kubectl

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.kind=DaemonSet \
  --set controller.service.type=ClusterIP \
  --set controller.hostPort.enabled=true \
  --wait \
  --timeout 5m

kubectl create namespace argo --dry-run=client -o yaml | kubectl apply -f -

kubectl apply --server-side --validate=false -n argo \
  -f "https://github.com/argoproj/argo-workflows/releases/download/${ARGO_WORKFLOWS_VERSION}/install.yaml"

kubectl -n argo rollout status deploy/workflow-controller --timeout=5m
kubectl -n argo rollout status deploy/argo-server --timeout=5m
