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
from bqapi.util import save_blob, localpath2url

T = [1,2,3,4,5,6,7] #t007
R = ['C', 'D'] #D
C = [6, 7] #06
CH = [1,2,3] #d2
CH_Z = [2,3]
FIELD = [1,2,3,4] #f02
Z = [0,1,2,3,4] #z4
name = 'uspi2-swtest44_151026120002i3'

dir_p = '\\converted\\'
dir_z = '\\ZStackImages\\converted\\'

ext_p = 'C01.ome.tif'
ext_z = 'DIB.ome.tif'

#uspi2-swtest44_151026120002i3 t001 C 06 f01 d1.C01
#uspi2-swtest44_151026120002i3 t007 D 06 f02 d2.C01
#uspi2-swtest44_151026120002i3 t001 D 06 f02 d2 z3.DIB

def create_resource(path, name, r, c, field):
    files = []
    for t in T:
        for z in Z:
            for ch in CH:
                if ch in CH_Z:
                    filename = '%s%s%st%.3d%s%.2df%.2dd%sz%s.%s'%(path, dir_z, name, t, r, c, field, ch, z, ext_z)
                else:
                    filename = '%s%s%st%.3d%s%.2df%.2dd%s.%s'%(path, dir_p, name, t, r, c, field, ch, ext_p)
                files.append(filename)

    resource = etree.Element ('image', name='%s_%s_%s_%s'%(name, r, c, field))

    meta = etree.SubElement (resource, 'tag', name='image_meta', type='image_meta')
    etree.SubElement (meta, 'tag', name='image_num_c', value=str(len(CH)), type='number')
    etree.SubElement (meta, 'tag', name='image_num_z', value=str(len(Z)), type='number')
    etree.SubElement (meta, 'tag', name='image_num_t', value=str(len(T)), type='number')
    etree.SubElement (meta, 'tag', name='dimensions', value='XYCZT')

    etree.SubElement (meta, 'tag', name='channel_0_name', value='Hoechst')
    etree.SubElement (meta, 'tag', name='channel_1_name', value='cmfda')
    etree.SubElement (meta, 'tag', name='channel_2_name', value='LysoTrackerRed')

    etree.SubElement (meta, 'tag', name='channel_color_0', value='0,0,255')
    etree.SubElement (meta, 'tag', name='channel_color_1', value='0,255,0')
    etree.SubElement (meta, 'tag', name='channel_color_2', value='255,0,0')

    etree.SubElement (resource, 'tag', name='row', value='%s'%r)
    etree.SubElement (resource, 'tag', name='column', value='%s'%c, type='number')
    etree.SubElement (resource, 'tag', name='field', value='%s'%field, type='number')

    for f in files:
        v = etree.SubElement (resource, 'value')
        v.text = localpath2url(f)
    return resource

##################################################################
# Upload
##################################################################


config = ConfigParser.ConfigParser()
config.read('config.cfg')

root = config.get('Host', 'root') or 'localhost:8080'
user = config.get('Host', 'user') or 'test'
pswd = config.get('Host', 'password') or 'test'

session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)
url = session.service_url('data_service', 'image')


path = sys.argv[1]
r = R[1]
c = C[0]
field = FIELD[0]
resource = create_resource(path, name, r, c, field)
print etree.tostring(resource)
r = session.postxml(url, resource, method='POST')
print r.get('uri')

#r = save_blob(session, resource=request)
#if r is None or r.get('uri') is None:
#    print 'Upload failed'
#else:
#    print 'id: %s'%r.get('resource_uniq')
#    print 'url: %s'%r.get('uri')

