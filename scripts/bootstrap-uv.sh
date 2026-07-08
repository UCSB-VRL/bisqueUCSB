#!/usr/bin/env bash
# gee morty this just looks like uv sync with extra steps
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
PYTHON_VERSION="${PYTHON_VERSION:-3.11}"
DEV=0

usage() {
  cat <<'USAGE'
Usage: scripts/bootstrap-uv.sh [--dev]

Create or update the BisQue uv environment.

Options:
  --dev      Include developer tooling such as pytest, ruff, and pre-commit.
  -h, --help Show this help.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dev)
      DEV=1
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

bisque_toolchain_mkdirs

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Run this from 'flox activate' or allow direnv." >&2
  exit 1
fi

python_bin="$PYTHON_VERSION"
if [ -n "${FLOX_ENV:-}" ]; then
  if [ -x "$FLOX_ENV/bin/python$PYTHON_VERSION" ]; then
    python_bin="$FLOX_ENV/bin/python$PYTHON_VERSION"
  elif [ -x "$FLOX_ENV/bin/python3" ]; then
    python_bin="$FLOX_ENV/bin/python3"
  elif [ -x "$FLOX_ENV/bin/python" ]; then
    python_bin="$FLOX_ENV/bin/python"
  else
    echo "Missing Python in FLOX_ENV=$FLOX_ENV." >&2
    exit 1
  fi
fi

uv_args=(sync --frozen --python "$python_bin")
if [ "$DEV" -eq 1 ]; then
  uv_args+=(--group dev)
fi

uv "${uv_args[@]}"

"$VENV/bin/bq-admin" --help >/dev/null
echo "BisQue uv environment is ready at $VENV"
