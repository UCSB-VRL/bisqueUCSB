#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

require_command docker
require_command k3d
require_bisque_repo

if ! docker image inspect "$BISQUE_ENV_IMAGE" >/dev/null 2>&1; then
  require_command flox
  (
    cd "$BISQUE_REPO"
    BISQUE_DOCKER_IMAGE="$BISQUE_ENV_IMAGE" \
      BISQUE_DOCKER_TAG="$BISQUE_DOCKER_TAG" \
      ./scripts/docker-build-env.sh
  )
fi

docker build \
  -f "$BISQUE_REPO/deploy/docker/Dockerfile" \
  --build-arg "BISQUE_ENV_IMAGE=$BISQUE_ENV_IMAGE" \
  -t "$BISQUE_IMAGE" \
  "$BISQUE_REPO"

k3d image import "$BISQUE_IMAGE" -c "$CLUSTER_NAME"
