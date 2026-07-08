#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
bisque_require_venv

"$VENV/bin/python" "$ROOT/scripts/generate-config.py"
