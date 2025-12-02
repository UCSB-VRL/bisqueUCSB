#!/bin/bash
# Updated by Wahid Sadique Koly on 2025-07-29 to align with the new upgraded codebase.

set -ex
# INDEX="https://biodev.ece.ucsb.edu/py/bisque/d8/+simple"

# Use VENV variable or default
VENV=${VENV:=/usr/lib/bisque}

# Ensure virtual environment exists
if [ ! -d "$VENV" ]; then
    echo "Virtual environment not found at $VENV"
    exit 1
fi

# Activate virtual environment
source ${VENV}/bin/activate

# Verify Python version and environment
echo "Python version: $(python --version)"
echo "Python path: $(which python)"
echo "Pip version: $(pip --version)"

# Upgrade pip and setuptools for Python 3
python -m pip install --upgrade pip setuptools wheel

# Install external dependencies from requirements.txt
pip install -r requirements.txt

# Install legacy upgraded packages FIRST (they are dependencies for local BisQue packages)
echo "Installing legacy upgraded packages..."

# Install WebHelpers first (Pylons depends on it)
cd /source/legacy_upgraded/WebHelpers-2.0 
pip install . || { echo "Failed to install WebHelpers-2.0"; exit 1; }
cd /source

# Install WebError (may be needed by other packages)
cd /source/legacy_upgraded/WebError-2.0 
pip install . || { echo "Failed to install WebError-2.0"; exit 1; }
cd /source

# Install paste first (Pylons might depend on it)
cd /source/legacy_upgraded/paste-103.10.1 
pip install . || { echo "Failed to install paste-103.10.1"; exit 1; }
cd /source

# Install Pylons (depends on WebHelpers and potentially others)
cd /source/legacy_upgraded/Pylons-2.0 
pip install . || { echo "Failed to install Pylons-2.0"; exit 1; }
cd /source

# Install Minimatic
cd /source/legacy_upgraded/Minimatic-2.0 
pip install . || { echo "Failed to install Minimatic-2.0"; exit 1; }
cd /source

# Now install local BisQue packages (they depend on the legacy packages above)
echo "Installing local Bisque packages..."

# Install bqcore first (it's a dependency for others and provides bq-admin)
echo "Installing bqcore..."
cd /source/bqcore 
pip install . || { echo "Failed to install bqcore"; exit 1; }
# Force refresh of entry points
hash -r
cd /source

# Verify bq-admin is available
echo "Checking if bq-admin is available..."
echo "Contents of ${VENV}/bin:"
ls -la ${VENV}/bin/ | grep -E "(bq|python)"

if [ -f "${VENV}/bin/bq-admin" ]; then
    echo "bq-admin found at ${VENV}/bin/bq-admin"
    ${VENV}/bin/bq-admin --help > /dev/null 2>&1 || { 
        echo "bq-admin exists but not working properly"
        pip show bqcore
        exit 1
    }
else
    echo "bq-admin not found, checking pip installation..."
    pip show bqcore
    echo "Trying to reinstall bqcore with --force-reinstall"
    pip install --force-reinstall .
    hash -r
    if [ ! -f "${VENV}/bin/bq-admin" ]; then
        echo "Still no bq-admin after reinstall, exiting"
        exit 1
    fi
fi

# Install bqapi
echo "Installing bqapi..."
cd /source/bqapi 
pip install . || { echo "Failed to install bqapi"; exit 1; }
cd /source

# Install bqengine
echo "Installing bqengine..."
cd /source/bqengine 
pip install . || { echo "Failed to install bqengine"; exit 1; }
cd /source

# Install bqfeature
echo "Installing bqfeature..."
cd /source/bqfeature 
pip install . || { echo "Failed to install bqfeature"; exit 1; }
cd /source

# Install bqserver (main application)
echo "Installing bqserver..."
cd /source/bqserver 
pip install . || { echo "Failed to install bqserver"; exit 1; }
cd /source

#export  PIP_INDEX_URL=$INDEX

# Use full path to bq-admin to ensure it's found
echo "Running bq-admin setup..."
${VENV}/bin/bq-admin setup -y install

# Clean up unnecessary directories
rm -rf external tools docs  modules/UNPORTED


pwd
/bin/ls -l
/bin/ls -l ${VENV}/bin/
echo "DONE"
