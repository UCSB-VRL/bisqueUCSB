#!/usr/bin/env bash
set -euxo pipefail

phase="${1:?usage: container-build-step.sh <install-converters|sync-deps|install-app> [args...]}"
shift

FLOX_ENV=""
for candidate in /nix/store/*environment-develop; do
  if [ -d "$candidate" ]; then
    FLOX_ENV="$candidate"
    break
  fi
done
export FLOX_ENV

EXTRA_PATH=""
for candidate in /nix/store/*gnutar*/bin /nix/store/*findutils*/bin /nix/store/*gnugrep*/bin; do
  if [ -d "$candidate" ]; then
    EXTRA_PATH="$EXTRA_PATH:$candidate"
  fi
done

export PATH="/app/.local/bin:$VENV/bin:$FLOX_ENV/bin:$FLOX_ENV/sbin$EXTRA_PATH:$PATH"
export PKG_CONFIG_PATH="$FLOX_ENV/lib/pkgconfig:$FLOX_ENV/share/pkgconfig"
export CPATH="$FLOX_ENV/include"
export LIBRARY_PATH="$FLOX_ENV/lib"
export LD_LIBRARY_PATH="/app/.local/lib:$FLOX_ENV/lib:$FLOX_ENV/x86_64-unknown-linux-gnu/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

SSL_CERT_FILE=""
for candidate in /nix/store/*/etc/ssl/certs/ca-bundle.crt /etc/ssl/certs/ca-certificates.crt /etc/ssl/cert.pem; do
  if [ -f "$candidate" ]; then
    SSL_CERT_FILE="$candidate"
    break
  fi
done
export SSL_CERT_FILE
export NIX_SSL_CERT_FILE="$SSL_CERT_FILE"
export CURL_CA_BUNDLE="$SSL_CERT_FILE"

export XDG_CACHE_HOME="/app/.cache/build"
export UV_CACHE_DIR="/app/.cache/build/uv"

if command -v mysql_config >/dev/null 2>&1; then
  export MYSQLCLIENT_CFLAGS="$(mysql_config --cflags)"
  export MYSQLCLIENT_LDFLAGS="$(mysql_config --libs)"
fi

mkdir -p "$HOME" "$XDG_CACHE_HOME" "$UV_CACHE_DIR"

case "$phase" in
  install-converters)
    install_bioformats="${1:-0}"
    if [ "$install_bioformats" = "1" ]; then
      bash /app/scripts/install-converters.sh
    else
      bash /app/scripts/install-converters.sh --skip-bioformats
    fi
    rm -rf /app/.cache/build /app/.cache/converters /app/.cache/maven
    ;;
  sync-deps)
    uv sync --python "${PYTHON_VERSION:-3.11}" --frozen --no-install-local --no-install-project
    rm -rf /app/.cache/build
    ;;
  install-app)
    bash /app/scripts/bootstrap-uv.sh
    BISQUE_PUBLIC_DIR=/app/public bash /app/scripts/link-static-assets.sh
    test -f /app/public/core/js/bq_api.js
    "$VENV/bin/python" /app/scripts/build-static-bundles.py
    test -f /app/public/core/css/all_css.css
    test -f /app/public/core/js/all_js.js
    touch "$VENV/.bisque-uv-sync"
    rm -rf /app/.cache/build
    ;;
  *)
    echo "Unknown container build phase: $phase" >&2
    exit 2
    ;;
esac
