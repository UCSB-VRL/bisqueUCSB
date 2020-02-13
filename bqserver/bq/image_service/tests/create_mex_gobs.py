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
import random

from bqapi import BQSession, BQCommError

def int2hex(v):
    s = str(hex(v))[2:].upper()
    return s if len(s)>1 else '0%s'%s

##################################################################
# Upload
##################################################################

num_gobs = 5000
gobs_sz = 100
image_uri = sys.argv[1]

config = ConfigParser.ConfigParser()
config.read('config.cfg')

root = config.get('Host', 'root') or 'localhost:8080'
user = config.get('Host', 'user') or 'test'
pswd = config.get('Host', 'password') or 'test'

session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)

# fetch image sizes
meta = session.fetchxml('%s?meta'%image_uri.replace('data_service', 'image_service'))
w = int(meta.xpath('//tag[@name="image_num_x"]')[0].get('value'))
h = int(meta.xpath('//tag[@name="image_num_y"]')[0].get('value'))
z = int(meta.xpath('//tag[@name="image_num_z"]')[0].get('value'))
t = int(meta.xpath('//tag[@name="image_num_t"]')[0].get('value'))

# create mex
mex = etree.Element ('mex', name='ExternalAnnotator %s'%num_gobs, value='FINISHED')

inputs = etree.SubElement (mex, 'tag', name='inputs')
etree.SubElement (inputs, 'tag', name='resource_url', type='image', value=image_uri)

outputs = etree.SubElement (mex, 'tag', name='outputs')
img = etree.SubElement (outputs, 'tag', name='MyImage', type='image', value=image_uri)
gob = etree.SubElement (img, 'gobject', name='Annotations', type='Annotations')


for j in range(num_gobs):

    poly = etree.SubElement (gob, 'polygon', name='%s'%j)
    dx = random.randint(0, w)
    dy = random.randint(0, h)
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    etree.SubElement (poly, 'tag', name='color', value='#%s%s%s'%(int2hex(r), int2hex(g), int2hex(b)))
    zz = random.randint(0, z)
    tt = random.randint(0, t)

    vrtx = []
    for i in range(10):
        x = dx + random.randint(-gobs_sz, gobs_sz)
        y = dy + random.randint(-gobs_sz, gobs_sz)
        vrtx.append((x,y))

    vrtx = sorted(vrtx,key=lambda x: x[0])
    for v in vrtx:
        etree.SubElement (poly, 'vertex', x='%s'%v[0], y='%s'%v[1], z='%s'%zz, t='%s'%tt)


#print etree.tostring(mex)

url = session.service_url('data_service', 'mex')
r = session.postxml(url, mex, method='POST')
if r is None:
    print 'Upload failed'
print 'id: %s'%r.get('resource_uniq')
print 'url: %s'%r.get('uri')
