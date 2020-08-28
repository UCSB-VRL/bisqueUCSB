#!/bin/bash
set -x
# INDEX="https://biodev.ece.ucsb.edu/py/bisque/d8/+simple"
PIP_INDEX_URL= pip install -U pip
PIP_INDEX_URL= pip install -U setuptools==34.4.1

pip install --extra-index-url https://pypi.org/simple -r requirements.txt

#export  PIP_INDEX_URL=$INDEX

paver setup all
bq-admin setup -y install
rm -rf external tools docs  modules/UNPORTED


pwd
/bin/ls -l
/bin/ls -l ${VENV}/bin/
echo "DONE"
