#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
export PYTHONPATH="$ROOT/source/bqapi:$ROOT/source/bqcore:$ROOT/source/bqserver:$ROOT/source/bqengine${PYTHONPATH:+:$PYTHONPATH}"
bisque_require_venv
bisque_enable_native_libs
"$VENV/bin/python" "$ROOT/scripts/generate-config.py"

# shellcheck disable=SC1091
source "$VENV/bin/activate"
cd "$ROOT/source"

if [ "$#" -gt 0 ]; then
  exec python -m pytest -q "$@"
fi

exec python -m pytest -q \
  bqserver/bq/data_service/tests/test_ds.py \
  bqserver/bq/data_service/tests/test_resource_query_parser.py
