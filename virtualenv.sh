#!/bin/bash

cd /tmp
wget https://pypi.python.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
tar xvfz virtualenv-15.1.0.tar.gz
cd virtualenv-15.1.0
python setup.py install
cd /tmp
rm -rf virtualenv*
