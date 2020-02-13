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

url = session.service_url('data_service', 'image')

request = '<image name="%s">'%'kif5b 8102010.mvd2#0'
request = '%s<value>%s</value>'%(request, '%s#0'%localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/kif5b 8102010.mvd2'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/116.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/147.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/153.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/31.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/69.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/152.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/158.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/33.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/71.dat'))
request = '%s</image>'%request

#url = session.service_url('data_service', 'image')
#r = session.postxml(url, etree.fromstring(request), method='POST')
r = save_blob(session, resource=request)
if r is None or r.get('uri') is None:
    print 'Upload failed'
else:
    print 'id: %s'%r.get('resource_uniq')
    print 'url: %s'%r.get('uri')



request = '<image name="%s">'%'kif5b 8102010.mvd2#1'
request = '%s<value>%s</value>'%(request, '%s#1'%localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/kif5b 8102010.mvd2'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/116.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/147.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/153.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/31.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/69.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/152.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/158.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/33.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/71.dat'))
request = '%s</image>'%request

r = save_blob(session, resource=request)
if r is None or r.get('uri') is None:
    print 'Upload failed'
else:
    print 'id: %s'%r.get('resource_uniq')
    print 'url: %s'%r.get('uri')


request = '<image name="%s">'%'kif5b 8102010.mvd2#2'
request = '%s<value>%s</value>'%(request, '%s#2'%localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/kif5b 8102010.mvd2'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/116.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/147.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/153.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/31.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/69.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/152.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/158.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/33.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/71.dat'))
request = '%s</image>'%request

r = save_blob(session, resource=request)
if r is None or r.get('uri') is None:
    print 'Upload failed'
else:
    print 'id: %s'%r.get('resource_uniq')
    print 'url: %s'%r.get('uri')


request = '<image name="%s">'%'kif5b 8102010.mvd2#3'
request = '%s<value>%s</value>'%(request, '%s#3'%localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/kif5b 8102010.mvd2'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/116.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/147.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/153.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/31.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/69.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/152.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/158.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/33.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/71.dat'))
request = '%s</image>'%request

r = save_blob(session, resource=request)
if r is None or r.get('uri') is None:
    print 'Upload failed'
else:
    print 'id: %s'%r.get('resource_uniq')
    print 'url: %s'%r.get('uri')

request = '<image name="%s">'%'kif5b 8102010.mvd2#4'
request = '%s<value>%s</value>'%(request, '%s#4'%localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/kif5b 8102010.mvd2'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aiix'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/119.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/151.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/157.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/32.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/70.aisf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/116.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/147.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/153.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/31.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/69.atsf'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/152.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/158.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/33.dat'))
request = '%s<value>%s</value>'%(request, localpath2url('f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/8102010-kif5b_control/Data/71.dat'))
request = '%s</image>'%request

r = save_blob(session, resource=request)
if r is None or r.get('uri') is None:
    print 'Upload failed'
else:
    print 'id: %s'%r.get('resource_uniq')
    print 'url: %s'%r.get('uri')
