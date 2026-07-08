#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAB_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_BISQUE_REPO="$(cd "$LAB_DIR/../../../.." && pwd)"

if [[ -f "$LAB_DIR/env.sh" ]]; then
  # shellcheck source=/dev/null
  source "$LAB_DIR/env.sh"
fi

: "${BISQUE_REPO:=$DEFAULT_BISQUE_REPO}"
: "${CLUSTER_NAME:=bisque-test}"
: "${K3S_IMAGE:=rancher/k3s:v1.30.14-k3s1}"
: "${ARGO_WORKFLOWS_VERSION:=v4.0.6}"
: "${BISQUE_ENV_IMAGE:=bisque:env}"
: "${BISQUE_DOCKER_TAG:=dev}"
: "${BISQUE_IMAGE:=bisque:local}"
: "${BISQUE_HOST:=bisque.localhost}"
: "${BISQUE_HTTP_PORT:=8080}"
: "${BISQUE_HTTPS_PORT:=8443}"

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
}

require_bisque_repo() {
  if [[ ! -f "$BISQUE_REPO/deploy/docker/Dockerfile" ]]; then
    echo "BISQUE_REPO does not look like a BisQue checkout: $BISQUE_REPO" >&2
    exit 1
  fi
  if [[ ! -d "$BISQUE_REPO/deploy/k3s" ]]; then
    echo "Missing k3s manifests: $BISQUE_REPO/deploy/k3s" >&2
    exit 1
  fi
}
