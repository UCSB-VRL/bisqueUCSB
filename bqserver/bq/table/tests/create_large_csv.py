#!/usr/bin/python

""" Create a large random CSV file for testing
"""

__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys
if sys.version_info  < ( 2, 7 ):
    import unittest2 as unittest
else:
    import unittest

import os
import uuid
import random
import string
import csv

if len(sys.argv)<1:
    print "usage: PATH"
    sys.exit()

filename = sys.argv[1]
nrows = 1000
if len(sys.argv)>2:
    nrows = int(sys.argv[2])

rows = 0
chunksize = min(1000, nrows)
with open(filename, 'wb') as f:
    # write header
    h = ['id']
    for i in range(8):
        h.append(''.join([random.choice(string.ascii_lowercase)] * 6))
    f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % tuple(h))

    # write values
    while rows < nrows:
        data = [None] * chunksize;
        for i in range(chunksize):
            data[i] = (rows+i,
                       str(uuid.uuid4()),
                       random.randint(0, 100000),
                       random.random()*random.randint(0, 100000),
                       random.random()*random.randint(0, 100000),
                       random.random()*random.randint(0, 100000),
                       random.random()*random.randint(0, 100000),
                       random.random()*random.randint(0, 100000),
                       random.random()*random.randint(0, 100000),
                       )
        f.writelines(['%i,%s,%i,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n' % row for row in data])
        rows += chunksize