#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"

usage() {
  cat <<'USAGE'
Usage: scripts/test-services.sh [--no-sync] [--list] [service ...]

Runs service-focused BisQue test slices.

Default services:
  data blob table

Available services:
  data    Config-backed data-service smoke tests
  blob    Blob-service driver tests
  table   Stable table/query tests
  bqapi   BQ API functional tests, including blob upload paths
  ingest  Ingest-service tests
  image   Image upload and image-service integration tests

Options:
  --no-sync  skip uv sync
  --list     show service names
USAGE
}

list_services() {
  printf '%s\n' data blob table bqapi ingest image
}

step() {
  printf '\n==> %s\n' "$1"
}

SYNC=1
SERVICES=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --no-sync)
      SYNC=0
      ;;
    --list)
      list_services
      exit 0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      SERVICES+=("$1")
      ;;
  esac
  shift
done

if [ "${#SERVICES[@]}" -eq 0 ]; then
  SERVICES=(data blob table)
fi

if [ "$SYNC" -eq 1 ]; then
  if ! command -v uv >/dev/null 2>&1; then
    echo "Missing uv. Run this inside 'flox activate' or run just bootstrap first." >&2
    exit 1
  fi
  uv sync --frozen --group dev
fi

bisque_require_venv

for service in "${SERVICES[@]}"; do
  case "$service" in
    data)
      step "Data service tests"
      scripts/test-server.sh \
        bqserver/bq/data_service/tests/test_ds.py \
        bqserver/bq/data_service/tests/test_resource_query_parser.py
      ;;
    blob)
      step "Blob service tests"
      scripts/test-unit.sh source/bqserver/bq/blob_service/tests/test_driver.py
      ;;
    table)
      step "Table service tests"
      scripts/test-unit.sh source/bqserver/bq/table/tests/test_runquery.py
      ;;
    bqapi)
      step "BQ API service tests"
      scripts/test-server.sh bqapi/bqapi/tests/test_comm.py
      ;;
    ingest)
      step "Ingest service tests"
      scripts/test-server.sh bqserver/bq/ingest/tests/test_new_resource.py
      ;;
    image)
      step "Image upload and image-service tests"
      scripts/test-server.sh bqserver/bq/image_service/tests/test_image_service_modern.py
      ;;
    *)
      echo "Unknown service: $service" >&2
      echo "Valid services:" >&2
      list_services >&2
      exit 2
      ;;
  esac
done

step "Service tests passed"
