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

url_import  = '/data_service/image'

request_xml = '<image name="{NAME}" value="{PATH}#{SERIES}" />'


##################################################################
# Upload
##################################################################


config = ConfigParser.ConfigParser()
config.read('config.cfg')

root = config.get('Host', 'root') or 'localhost:8080'
user = config.get('Host', 'user') or 'test'
pswd = config.get('Host', 'password') or 'test'

session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)


url = urlparse.urljoin(root, url_import)
request = request_xml.replace('{NAME}', 'cx-11.sld#3')
request = request.replace('{PATH}', localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_image/Slidebook/cx-11.sld'))
request = request.replace('{SERIES}', '3')

r = save_blob(session, resource=request)
if r is None or r.get('uri') is None:
    print 'Upload failed'
else:
    print 'id: %s'%r.get('resource_uniq')
    print 'url: %s'%r.get('uri')
