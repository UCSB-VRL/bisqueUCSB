#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"

# make people opt in to removing the runtime dir if it is outside of the project dir
refuse() {
  echo "Refusing to remove unsafe BISQUE_RUNTIME_DIR: ${BISQUE_RUNTIME_DIR:-<empty>}" >&2
  echo "Resolved path: ${runtime_dir:-<unresolved>}" >&2
  exit 1
}

if [ -z "${BISQUE_RUNTIME_DIR:-}" ]; then
  refuse
fi

runtime_dir="$(realpath -m "$BISQUE_RUNTIME_DIR")"
root_dir="$(realpath -m "$ROOT")"
home_dir=""
if [ -n "${HOME:-}" ]; then
  home_dir="$(realpath -m "$HOME")"
fi

case "$runtime_dir" in
  ""|"/"|"/home"|"/tmp"|"/var"|"$root_dir"|"$home_dir")
    refuse
    ;;
esac

case "$runtime_dir" in
  "$root_dir"/*)
    ;;
  *)
    if [ "${BISQUE_CLEAN_ALLOW_EXTERNAL:-0}" != "1" ]; then
      echo "BISQUE_RUNTIME_DIR is outside the repository: $runtime_dir" >&2
      echo "Set BISQUE_CLEAN_ALLOW_EXTERNAL=1 to remove an external runtime directory." >&2
      exit 1
    fi
    ;;
esac

rm -rf "$runtime_dir"

echo "Removed BisQue local runtime state from $runtime_dir"
