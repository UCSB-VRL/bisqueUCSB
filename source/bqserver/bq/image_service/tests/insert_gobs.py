#!/usr/bin/python

""" Image service testing framework
update config to your system: config.cfg
call by: python run_tests.py
"""

__module__    = "run_tests"
__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys
if sys.version_info  < ( 2, 7 ):
    import unittest2 as unittest
else:
    import unittest
import os
import posixpath
import urlparse
import time
from lxml import etree
import ConfigParser
from bqapi import BQSession, BQCommError
import random

def int2hex(v):
    s = str(hex(v))[2:].upper()
    return s if len(s)>1 else '0%s'%s

##################################################################
# Upload
##################################################################

config = ConfigParser.ConfigParser()
config.read('config.cfg')

root = config.get('Host', 'root') or 'localhost:8080'
user = config.get('Host', 'user') or 'test'
pswd = config.get('Host', 'password') or 'test'

session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)


polygon = '<polygon name="%s"><vertex x="%s" y="%s" /><tag name="color" value="%s" /></polygon>'

polygons = []
for i in range(10):
    x = random.randint(0, 900)
    y = random.randint(0, 900)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    d1 = random.randint(10, 150)
    d2 = random.randint(10, 150)
    d3 = random.randint(10, 150)
    color = '#%s%s%s'%(int2hex(r), int2hex(g), int2hex(b))
    polygon = '<polygon name="%s"><vertex x="%s" y="%s" /><vertex x="%s" y="%s" /><vertex x="%s" y="%s" /><tag name="color" value="%s" type="color" /></polygon>'%(i, x, y, x+d1, y, x+d2, y+d3, color)
    polygons.append(polygon)

request = '<request>%s</request>'%''.join(polygons)

print request

url = session.service_url('data_service', 'image')
url = '%s/175501/gobject'%url

print url

r = session.postxml(url, etree.fromstring(request), method='POST')
if r is None:
    print 'Upload failed'
print 'id: %s'%r.get('resource_uniq')
print 'url: %s'%r.get('uri')
