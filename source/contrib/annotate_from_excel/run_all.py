__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

import os
import logging
import sys
from subprocess import Popen, call, PIPE


path = '.'
files = os.listdir(path)
files = [f for f in files if f.lower().endswith('.xlsx')]
files.sort()

for fn in files:
    dataset_name = fn.replace('.xlsx', '')
    command = ['python', 'annotate.py', fn]
    print '\n\nRunning %s'%dataset_name
    call(command)


