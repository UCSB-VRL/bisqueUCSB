#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_NAME="${BISQUE_FLOX_ENV_NAME:-bisque}"
IMAGE_TAG="${BISQUE_DOCKER_TAG:-dev}"
IMAGE="${BISQUE_ENV_IMAGE:-${BISQUE_DOCKER_IMAGE:-bisque:env}}"
RUNTIME="${CONTAINER_RUNTIME:-docker}"
PORT="${BISQUE_DOCKER_PORT:-8080}"
HOST_UID="$(id -u)"
HOST_GID="$(id -g)"

if ! command -v "$RUNTIME" >/dev/null 2>&1; then
  echo "$RUNTIME is required. Set CONTAINER_RUNTIME=docker or podman." >&2
  exit 1
fi

if ! "$RUNTIME" image inspect "$IMAGE" >/dev/null 2>&1; then
  scripts/docker-build-env.sh
fi

tty_args=()
if [ -t 0 ] && [ -t 1 ]; then
  tty_args=(-it)
fi

exec "$RUNTIME" run --rm "${tty_args[@]}" --init \
  -p "$PORT:8080" \
  -v "$ROOT:/workspace" \
  -w /workspace \
  -e HOME=/workspace/.cache/container-home \
  -e FLOX_ENV_PROJECT=/workspace \
  -e HOST_UID="$HOST_UID" \
  -e HOST_GID="$HOST_GID" \
  -e BISQUE_RUNTIME_DIR=/workspace/.bisque \
  "$IMAGE" \
  bash -lc '
    set -euo pipefail
    export XDG_CACHE_HOME=/workspace/.cache/container
    export UV_CACHE_DIR=/workspace/.cache/container/uv
    export VENV=/.venv
    source /workspace/scripts/runtime-env.sh

    mkdir -p "$HOME" "$XDG_CACHE_HOME" "$UV_CACHE_DIR" /usr/bin
    ln -sf /bin/env /usr/bin/env

    cleanup() {
      chown -R "$HOST_UID:$HOST_GID" \
        /workspace/.bisque \
        /workspace/.cache/container \
        /workspace/.cache/container-home \
        /workspace/.local 2>/dev/null || true
    }
    trap cleanup EXIT

    bash /workspace/scripts/bootstrap-uv.sh
    bash /workspace/scripts/setup-bisque-local.sh
    bisque_enable_native_libs
    cd /workspace/.bisque/config
    "$VENV/bin/paster" serve h1_paster.cfg
  '
