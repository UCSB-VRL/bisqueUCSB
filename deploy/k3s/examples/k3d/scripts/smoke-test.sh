#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

require_command curl
require_command kubectl

kubectl get pods -A
kubectl -n bisque get pods
kubectl -n bisque get workflowtemplates

curl -fsS -H "Host: ${BISQUE_HOST}" "http://127.0.0.1:${BISQUE_HTTP_PORT}/robots.txt"

echo
echo "BisQue k3d smoke test passed"
