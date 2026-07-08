#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
bisque_require_venv
bisque_enable_native_libs

if [ ! -f "$BISQUE_SITE_CONFIG" ]; then
  echo "Missing $BISQUE_SITE_CONFIG. Run just setup first." >&2
  exit 1
fi

for arg in "$@"; do
  if [ "$arg" = "--force" ]; then
    while read -r pid; do
      [ -n "$pid" ] || continue
      args="$(ps -p "$pid" -o args= 2>/dev/null || true)"
      case "$args" in
        *"$ROOT/.venv/bin/paster"*|*"$VENV/bin/paster"*)
          kill "$pid" 2>/dev/null || true
          ;;
      esac
    done < <(ss -ltnp "sport = :${BISQUE_HTTP_PORT:-8080}" 2>/dev/null | sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p')
    sleep 1
    break
  fi
done

mkdir -p "$BISQUE_LOG_DIR"
logfile="$BISQUE_LOG_DIR/bisque_${BISQUE_HTTP_PORT:-8080}.log"
oldlog="$logfile.save"

if [ -f "$logfile" ]; then
  rm -f "$oldlog"
  mv "$logfile" "$oldlog"
fi

echo "Logging to $logfile"
cd "$BISQUE_CONFIG_DIR"
set +e
"$VENV/bin/paster" serve h1_paster.cfg 2>&1 | tee "$logfile"
status=${PIPESTATUS[0]}
set -e
exit "$status"
