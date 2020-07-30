__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

import os
import logging
import sys
import inspect
from datetime import datetime
import ConfigParser

from lxml import etree
import pandas as pd


path = '.'
files = os.listdir(path)
files = [f for f in files if f.lower().endswith('.xlsx')]
files.sort()

data = pd.read_excel('d20111009_6.xlsx')
keys = data.keys()
types = data.dtypes
converters={'names':str,'ages':str}

# ensure same key names
print '\nChecking keys'
for fn in files:
    data = pd.read_excel(fn)
    K = data.keys()
    for k in keys:
        if k not in K:
            print 'missing %s in %s'%(k, dataset_name)

# ensure same types
print '\nChecking types'
for fn in files:
    data = pd.read_excel(fn)
    T = data.dtypes
    for k in keys:
        if T[k] != types[k]:
            print '%s different types in %s, expecting %s and has %s'%(fn, k, types[k], T[k])

# for d in datasets.xpath('dataset'):
#    dataset_name = fn.replace('.xlsx', '')
#     url = d.get('uri')
#     command = ['python', script, url]
#     command.extend(sys.argv[2:])
#     call(command)


