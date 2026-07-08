#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
bisque_require_venv

# shellcheck disable=SC1091
source "$VENV/bin/activate"
cd "$ROOT/source"

bq-admin server --site "$BISQUE_SITE_CONFIG" stop "$@"
