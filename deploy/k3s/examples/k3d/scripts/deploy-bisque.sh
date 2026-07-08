#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

require_command kubeconform
require_command kubectl
require_bisque_repo

kubeconform -ignore-missing-schemas -summary "$BISQUE_REPO"/deploy/k3s/*.yaml
kubectl apply -f "$BISQUE_REPO/deploy/k3s/"
kubectl -n bisque rollout status deploy/bisque --timeout=5m
