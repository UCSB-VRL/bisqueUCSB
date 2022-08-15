#!/bin/bash

###################################################################
# BQ-ADMIN-SETUP.SH
# Moved from Build Folder
# Amil Khan 2022
###################################################################

VENV=${VENV:=/usr/lib/bisque}

source ${VENV}/bin/activate
paver setup all
find /source -name '*.pyc' -delete
bq-admin setup -y install
rm -rf external tools docs  modules/UNPORTED
cd /source/bqserver && python setup.py install && cd /source

pwd
/bin/ls -l
/bin/ls -l ${VENV}/bin/
echo "DONE"