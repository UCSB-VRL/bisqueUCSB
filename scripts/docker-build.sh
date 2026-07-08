#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_IMAGE="${BISQUE_ENV_IMAGE:-bisque:env}"
IMAGE="${BISQUE_IMAGE:-bisque:local}"
RUNTIME="${CONTAINER_RUNTIME:-docker}"

if ! command -v "$RUNTIME" >/dev/null 2>&1; then
  echo "$RUNTIME is required. Set CONTAINER_RUNTIME=docker or podman." >&2
  exit 1
fi

if ! "$RUNTIME" image inspect "$ENV_IMAGE" >/dev/null 2>&1; then
  BISQUE_ENV_IMAGE="$ENV_IMAGE" scripts/docker-build-env.sh
fi

"$RUNTIME" build \
  -f deploy/docker/Dockerfile \
  --build-arg "BISQUE_ENV_IMAGE=$ENV_IMAGE" \
  -t "$IMAGE" \
  "$@" \
  .

echo "Built $IMAGE from $ENV_IMAGE"
