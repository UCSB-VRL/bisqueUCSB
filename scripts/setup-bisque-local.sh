#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
bisque_require_venv

# shellcheck disable=SC1091
source "$VENV/bin/activate"

if [ "${BISQUE_SKIP_CONVERTER_SETUP:-0}" != "1" ]; then
  scripts/install-converters.sh
fi

scripts/prepare-bisque-runtime.sh
scripts/link-static-assets.sh
scripts/render-config.sh
scripts/setup-bisque-runtime.sh

bisque_enable_native_libs
bq-admin --help >/dev/null
imgcnv -v >/dev/null || echo "warning: imgcnv did not report a version" >&2
showinf -version >/dev/null || echo "warning: Bio-Formats showinf did not report a version" >&2

echo "BisQue local runtime is configured under $BISQUE_RUNTIME_DIR"
