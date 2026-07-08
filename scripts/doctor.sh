#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"

FAILED=0

check() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    printf 'ok   %s\n' "$label"
  else
    printf 'miss %s\n' "$label"
    FAILED=1
  fi
}

check_path() {
  local label="$1"
  local path="$2"
  if [ -e "$path" ]; then
    printf 'ok   %s\n' "$label"
  else
    printf 'miss %s\n' "$label"
    FAILED=1
  fi
}

check_optional() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    printf 'ok   %s\n' "$label"
  else
    printf 'warn %s\n' "$label"
  fi
}

printf 'BisQue developer environment\n'
printf 'repo %s\n\n' "$ROOT"

check "flox command" command -v flox
check "uv command" command -v uv
check_path "uv virtualenv" "$VENV/bin/python"

if [ -x "$VENV/bin/python" ]; then
  check "bq-admin entrypoint" "$VENV/bin/bq-admin" --help
fi

check_path "runtime directory" "$BISQUE_RUNTIME_DIR"
check_path "site config" "$BISQUE_SITE_CONFIG"
check_path "pytest config" "$BISQUE_TEST_CONFIG"
check_path "static asset links" "$BISQUE_PUBLIC_DIR/core"

check "imgcnv converter" imgcnv -v
check "Bio-Formats showinf" showinf -version
check "Bio-Formats bfconvert" command -v bfconvert

check_optional "Docker CLI for containerized modules" command -v docker
check_optional "Argo CLI for workflow-backed modules" command -v argo
check_optional "kubectl for local/cluster Argo" command -v kubectl

if command -v curl >/dev/null 2>&1 && curl -fsS -o /dev/null http://localhost:8080/core/js/bq_api.js; then
  printf 'ok   live BisQue static asset on port 8080\n'
else
  printf 'warn live BisQue server is not responding on port 8080\n'
fi

if [ "$FAILED" -eq 0 ]; then
  printf '\nEnvironment looks ready. Run: just test\n'
else
  printf '\nEnvironment is incomplete. Run: just setup\n'
fi

exit "$FAILED"
