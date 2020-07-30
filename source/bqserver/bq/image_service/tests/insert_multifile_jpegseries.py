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

##################################################################
# Upload
##################################################################


config = ConfigParser.ConfigParser()
config.read('config.cfg')

root = config.get('Host', 'root') or 'localhost:8080'
user = config.get('Host', 'user') or 'test'
pswd = config.get('Host', 'password') or 'test'

session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)

request = '<image name="%s">'%'series_t_jpeg'
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/series_t_jpeg/t_000241.jpg'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/series_t_jpeg'))
request = '%s<tag name="%s" type="%s">'%(request, 'image_meta', 'image_meta')
request = '%s<tag name="%s" value="%s" type="number" />'%(request, 'image_num_z', '1')
request = '%s<tag name="%s" value="%s" type="number" />'%(request, 'image_num_t', '80')
request = '%s<tag name="%s" value="%s" />'%(request, 'dimensions', 'XYCZT')
request = '%s<tag name="%s" value="%s" type="number" />'%(request, 'pixel_resolution_x', '0.4')
request = '%s<tag name="%s" value="%s" type="number" />'%(request, 'pixel_resolution_y', '0.4')
request = '%s<tag name="%s" value="%s" type="number" />'%(request, 'pixel_resolution_t', '2.0')
request = '%s<tag name="%s" value="%s" />'%(request, 'pixel_resolution_unit_x', 'micron')
request = '%s<tag name="%s" value="%s" />'%(request, 'pixel_resolution_unit_y', 'micron')
request = '%s<tag name="%s" value="%s" />'%(request, 'pixel_resolution_unit_t', 'seconds')
request = '%s</tag>'%(request)
request = '%s</image>'%request

#url = session.service_url('data_service', 'image')
#r = session.postxml(url, etree.fromstring(request), method='POST')
r = save_blob(session, resource=request)
if r is None or r.get('uri') is None:
    print 'Upload failed'
else:
    print 'id: %s'%r.get('resource_uniq')
    print 'url: %s'%r.get('uri')

