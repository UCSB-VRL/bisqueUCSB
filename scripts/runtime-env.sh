#!/usr/bin/env bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bisque_load_dotenv() {
  local env_file line key value
  env_file="${BISQUE_DOTENV:-$ROOT/.env}"
  [ -f "$env_file" ] || return 0

  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%$'\r'}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"

    case "$line" in
      ""|\#*)
        continue
        ;;
      export\ *)
        line="${line#export }"
        line="${line#"${line%%[![:space:]]*}"}"
        ;;
    esac

    case "$line" in
      *=*)
        key="${line%%=*}"
        value="${line#*=}"
        ;;
      *)
        continue
        ;;
    esac

    key="${key%"${key##*[![:space:]]}"}"
    if [[ ! "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
      continue
    fi

    if [ -z "${!key+x}" ]; then
      value="${value#"${value%%[![:space:]]*}"}"
      value="${value%"${value##*[![:space:]]}"}"
      case "$value" in
        \"*\")
          value="${value#\"}"
          value="${value%\"}"
          ;;
        \'*\')
          value="${value#\'}"
          value="${value%\'}"
          ;;
      esac
      export "$key=$value"
    fi
  done < "$env_file"
}

bisque_load_dotenv

bisque_abs_path() {
  realpath -m "$1"
}

bisque_path_prepend() {
  local entry="$1"
  case ":$PATH:" in
    *":$entry:"*)
      ;;
    *)
      PATH="$entry:$PATH"
      ;;
  esac
}

export BISQUE_RUNTIME_DIR="$(bisque_abs_path "${BISQUE_RUNTIME_DIR:-$ROOT/.bisque}")"
export BISQUE_CONFIG_DIR="$(bisque_abs_path "${BISQUE_CONFIG_DIR:-$BISQUE_RUNTIME_DIR/config}")"
export BISQUE_DATA_DIR="$(bisque_abs_path "${BISQUE_DATA_DIR:-$BISQUE_RUNTIME_DIR/data}")"
export BISQUE_EXTERNAL_DIR="$(bisque_abs_path "${BISQUE_EXTERNAL_DIR:-$BISQUE_RUNTIME_DIR/external}")"
export BISQUE_PUBLIC_DIR="$(bisque_abs_path "${BISQUE_PUBLIC_DIR:-$BISQUE_RUNTIME_DIR/public}")"
export BISQUE_REPORTS_DIR="$(bisque_abs_path "${BISQUE_REPORTS_DIR:-$BISQUE_RUNTIME_DIR/reports}")"
export BISQUE_STAGING_DIR="$(bisque_abs_path "${BISQUE_STAGING_DIR:-$BISQUE_RUNTIME_DIR/staging}")"
export BISQUE_LOG_DIR="$(bisque_abs_path "${BISQUE_LOG_DIR:-$BISQUE_RUNTIME_DIR/logs}")"
export BISQUE_RUN_DIR="$(bisque_abs_path "${BISQUE_RUN_DIR:-$BISQUE_RUNTIME_DIR/run}")"
export BISQUE_CACHE_DIR="$(bisque_abs_path "${BISQUE_CACHE_DIR:-$BISQUE_RUNTIME_DIR/cache}")"
export BISQUE_SITE_CONFIG="$(bisque_abs_path "${BISQUE_SITE_CONFIG:-$BISQUE_CONFIG_DIR/site.cfg}")"
export BISQUE_TEST_CONFIG="$(bisque_abs_path "${BISQUE_TEST_CONFIG:-$BISQUE_CONFIG_DIR/test.ini}")"

export XDG_CACHE_HOME="$(bisque_abs_path "${XDG_CACHE_HOME:-$ROOT/.cache}")"
export UV_CACHE_DIR="$(bisque_abs_path "${UV_CACHE_DIR:-$ROOT/.cache/uv}")"
export VENV="$(bisque_abs_path "${VENV:-$ROOT/.venv}")"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$VENV}"
export PYTHONNOUSERSITE=1

bisque_path_prepend "$VENV/bin"
bisque_path_prepend "$ROOT/.local/bin"
export PATH

bisque_runtime_mkdirs() {
  mkdir -p \
    "$BISQUE_CONFIG_DIR" \
    "$BISQUE_DATA_DIR" \
    "$BISQUE_EXTERNAL_DIR" \
    "$BISQUE_PUBLIC_DIR" \
    "$BISQUE_REPORTS_DIR" \
    "$BISQUE_STAGING_DIR" \
    "$BISQUE_LOG_DIR" \
    "$BISQUE_RUN_DIR" \
    "$BISQUE_CACHE_DIR"

  mkdir -p "$BISQUE_DATA_DIR/test-results" "$BISQUE_DATA_DIR/uploads"
  if [ -n "${BISQUE_UPLOAD_TMP_DIR:-}" ]; then
    mkdir -p "$BISQUE_UPLOAD_TMP_DIR"
  fi
}

bisque_toolchain_mkdirs() {
  mkdir -p "$XDG_CACHE_HOME" "$UV_CACHE_DIR"
}

bisque_require_venv() {
  if [ ! -x "$VENV/bin/python" ]; then
    echo "Missing $VENV. Run just bootstrap first." >&2
    exit 1
  fi
}

bisque_enable_native_libs() {
  local flox_active_env candidate
  flox_active_env="${FLOX_ENV:-}"

  if [ -z "$flox_active_env" ] && [ -d "$ROOT/.flox/run" ]; then
    for candidate in "$ROOT"/.flox/run/*.dev "$ROOT"/.flox/run/*.run; do
      if [ -e "$candidate" ] && [ -d "$candidate" ]; then
        flox_active_env="$candidate"
        break
      fi
    done
  fi

  if [ -n "$flox_active_env" ] && [ -d "$flox_active_env" ]; then
    export LD_LIBRARY_PATH="$ROOT/.local/lib:$flox_active_env/lib:$flox_active_env/x86_64-unknown-linux-gnu/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  else
    export LD_LIBRARY_PATH="$ROOT/.local/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  fi
}
