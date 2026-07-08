#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"

bisque_runtime_mkdirs
bisque_toolchain_mkdirs

echo "Prepared BisQue runtime directories under $BISQUE_RUNTIME_DIR"
