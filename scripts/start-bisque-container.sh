#!/usr/bin/env bash
set -euo pipefail

ROOT="${BISQUE_APP_DIR:-/app}"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
bisque_enable_native_libs

if [ ! -x "$VENV/bin/bq-admin" ] || [ ! -x "$VENV/bin/paster" ]; then
  echo "Missing prebuilt BisQue virtualenv at $VENV. Rebuild the image." >&2
  exit 1
fi

bash "$ROOT/scripts/prepare-bisque-runtime.sh"
bash "$ROOT/scripts/render-config.sh"
bash "$ROOT/scripts/setup-bisque-runtime.sh"

cd "$BISQUE_RUNTIME_DIR/config"
exec "$VENV/bin/paster" serve h1_paster.cfg
