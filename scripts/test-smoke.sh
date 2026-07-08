#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"

usage() {
  cat <<'USAGE'
Usage: scripts/test-smoke.sh [--live] [--image] [--no-sync]

Runs the default developer smoke suite:
  - uv environment sync
  - core unit tests
  - converter binary sanity checks
  - config-backed WSGI pytest slice

Options:
  --live     also check a running BisQue server on http://localhost:8080
  --image    also run the focused image-service converter pytest file
  --no-sync  skip uv sync
USAGE
}

LIVE=0
IMAGE=0
SYNC=1

while [ "$#" -gt 0 ]; do
  case "$1" in
    --live)
      LIVE=1
      ;;
    --image)
      IMAGE=1
      ;;
    --no-sync)
      SYNC=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [ "$SYNC" -eq 1 ]; then
  if ! command -v uv >/dev/null 2>&1; then
    echo "Missing uv. Run this inside 'flox activate' or run just bootstrap first." >&2
    exit 1
  fi
  uv sync --frozen --group dev
fi

bisque_require_venv

# shellcheck disable=SC1091
source "$VENV/bin/activate"

step() {
  printf '\n==> %s\n' "$1"
}

step "Core unit tests"
scripts/test-unit.sh

step "Converter binaries"
command -v imgcnv >/dev/null
imgcnv -v >/dev/null
command -v showinf >/dev/null
showinf -version >/dev/null
command -v bfconvert >/dev/null

step "Config-backed WSGI tests"
scripts/test-server.sh

if [ "$LIVE" -eq 1 ]; then
  step "Live local server checks"
  curl -fsS -o /dev/null http://localhost:8080/
  curl -fsS -o /dev/null http://localhost:8080/core/js/bq_api.js
  curl -fsS -o /dev/null http://localhost:8080/core/css/bq.css
  curl -fsS -o /dev/null http://localhost:8080/dataset_service/dataset_service.js
  curl -fsS -o /dev/null 'http://localhost:8080/data_service/mex?offset=0&limit=1'
fi

if [ "$IMAGE" -eq 1 ]; then
  step "Focused image-service converter tests"
  scripts/test-server.sh bqserver/bq/image_service/tests/test_image_service_modern.py
fi

step "Smoke suite passed"
