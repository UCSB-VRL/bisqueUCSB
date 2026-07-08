#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
bisque_require_venv
bisque_enable_native_libs

# shellcheck disable=SC1091
source "$VENV/bin/activate"

if [ "$#" -gt 0 ]; then
  exec python -m pytest -q -m "unit and not server and not converter" "$@"
fi

exec python -m pytest -q -m "unit and not server and not converter" \
  source/bqapi/bqapi/tests/test_bqclass.py \
  source/bqapi/bqapi/tests/test_comm.py \
  source/bqengine/bq/engine/tests/test_module_definition.py \
  source/bqengine/bq/engine/tests/test_module_runner.py \
  source/bqserver/bq/blob_service/tests/test_driver.py \
  source/bqserver/bq/data_service/tests/test_resource_query_parser.py \
  source/bqserver/bq/table/tests/test_runquery.py
