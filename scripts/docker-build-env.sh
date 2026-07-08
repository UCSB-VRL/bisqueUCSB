#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_NAME="${BISQUE_FLOX_ENV_NAME:-bisque}"
IMAGE_TAG="${BISQUE_DOCKER_TAG:-dev}"
IMAGE="${BISQUE_ENV_IMAGE:-${BISQUE_DOCKER_IMAGE:-bisque:env}}"
RUNTIME="${CONTAINER_RUNTIME:-docker}"

if ! command -v flox >/dev/null 2>&1; then
  echo "flox is required to build the BisQue environment image." >&2
  exit 1
fi

if ! command -v "$RUNTIME" >/dev/null 2>&1; then
  echo "$RUNTIME is required. Set CONTAINER_RUNTIME=docker or podman." >&2
  exit 1
fi

flox containerize --runtime "$RUNTIME" --tag "$IMAGE_TAG"

FLOX_IMAGE="$ENV_NAME:$IMAGE_TAG"
if [ "$IMAGE" != "$FLOX_IMAGE" ]; then
  "$RUNTIME" tag "$FLOX_IMAGE" "$IMAGE"
fi

echo "Built $IMAGE from .flox/env/manifest.toml"
