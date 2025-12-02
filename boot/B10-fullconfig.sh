#!/bin/sh
# Updated by Wahid Sadique Koly on 2025-07-29 to align with the new upgraded codebase.

set -x

source /usr/lib/bisque/bin/activate
echo "bq-admin location: $(which bq-admin)"

bq-admin setup -y fullconfig
