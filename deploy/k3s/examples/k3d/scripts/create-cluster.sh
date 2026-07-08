#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

require_command docker
require_command k3d
require_command kubectl

docker info >/dev/null

k3d cluster delete "$CLUSTER_NAME" >/dev/null 2>&1 || true

k3d cluster create "$CLUSTER_NAME" \
  --image "$K3S_IMAGE" \
  --agents 1 \
  --port "${BISQUE_HTTP_PORT}:80@loadbalancer" \
  --port "${BISQUE_HTTPS_PORT}:443@loadbalancer" \
  --k3s-arg "--disable=traefik@server:*" \
  --k3s-arg "--disable=servicelb@server:*"

kubectl cluster-info
