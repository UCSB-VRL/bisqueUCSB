#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
bisque_require_venv

# shellcheck disable=SC1091
source "$VENV/bin/activate"
bisque_enable_native_libs

cd "$ROOT/source"

bq-admin setup -c "$BISQUE_CONFIG_DIR" -y binaries
bq-admin setup -c "$BISQUE_CONFIG_DIR" -y plugins
bq-admin setup -c "$BISQUE_CONFIG_DIR" -y database
bq-admin setup -c "$BISQUE_CONFIG_DIR" -y preferences
