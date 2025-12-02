#!/bin/bash

###################################################################
# BQ-ADMIN-SETUP.SH
# Moved from Build Folder
# Amil Khan 2022
# Updated by Wahid Sadique Koly on 2025-07-29 to align with the new upgraded codebase.
###################################################################

VENV=${VENV:=/usr/lib/bisque}

source ${VENV}/bin/activate

# Ensure we're using Python 3
python --version

# Run paver setup (this handles configuration)
# paver setup all

# Clean up any old .pyc files
find /source -name '*.pyc' -delete

# Run bq-admin setup for database and configuration
bq-admin setup -y install

# Clean up unnecessary directories
rm -rf external tools docs  modules/UNPORTED

# Verify installations
echo "Verifying package installations..."
python -c "import bq.core; print('bqcore installed successfully')"
python -c "import bq.server; print('bqserver installed successfully')"
python -c "import bqapi; print('bqapi installed successfully')"
python -c "import bq.engine; print('bqengine installed successfully')"
python -c "import bq.features; print('bqfeature installed successfully')"

pwd
/bin/ls -l
/bin/ls -l ${VENV}/bin/
echo "DONE"