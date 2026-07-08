#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT/scripts/runtime-env.sh"
PUBLIC="$BISQUE_PUBLIC_DIR"

mkdir -p "$PUBLIC"

link_static_dir() {
  local name="$1"
  local target="$2"
  local dest="$PUBLIC/$name"

  if [ ! -d "$target" ]; then
    echo "Missing static source: $target" >&2
    exit 1
  fi

  if [ -L "$dest" ] || [ -f "$dest" ]; then
    rm -f "$dest"
  elif [ -d "$dest" ]; then
    rm -rf "$dest"
  fi

  ln -s "$target" "$dest"
}

link_static_dir core "$ROOT/source/bqcore/bq/core/public"
link_static_dir client_service "$ROOT/source/bqserver/bq/client_service/public"
link_static_dir data_service "$ROOT/source/bqserver/bq/data_service/public"
link_static_dir dataset_service "$ROOT/source/bqserver/bq/dataset_service/public"
link_static_dir export "$ROOT/source/bqserver/bq/export_service/public"
link_static_dir graph "$ROOT/source/bqserver/bq/graph/public"
link_static_dir image_service "$ROOT/source/bqserver/bq/image_service/public"
link_static_dir import "$ROOT/source/bqserver/bq/import_service/public"
link_static_dir ingest_service "$ROOT/source/bqserver/bq/ingest/public"
link_static_dir module_service "$ROOT/source/bqserver/bq/module_service/public"
link_static_dir registration "$ROOT/source/bqserver/bq/registration/public"
link_static_dir stats "$ROOT/source/bqserver/bq/stats/public"
link_static_dir usage "$ROOT/source/bqserver/bq/usage/public"

echo "Linked BisQue static assets under $PUBLIC"
