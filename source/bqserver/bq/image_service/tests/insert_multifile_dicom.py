#!/usr/bin/python

"""Image service testing framework
update config to your system: config.cfg
call by: python run_tests.py
"""

__module__ = "run_tests"
__author__ = "Dmitry Fedorov"
__version__ = "1.0"
__revision__ = "$Rev$"
__date__ = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import configparser
import os
import posixpath
import time
import urllib.parse

from bqapi import BQCommError, BQSession
from bqapi.util import localpath2url, save_blob
from lxml import etree

##################################################################
# Upload
##################################################################


config = configparser.ConfigParser()
config.read("config.cfg")

root = config.get("Host", "root") or "localhost:8080"
user = config.get("Host", "user") or "test"
pswd = config.get("Host", "password") or "test"

session = BQSession().init_local(user, pswd, bisque_root=root, create_mex=False)

request = '<image name="%s">' % "IM-0001-0001.dcm"
request = "%s<value>%s</value>" % (
    request,
    localpath2url(
        "f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/dicom/IM-0001-0001.dcm"
    ),
)
request = "%s<value>%s</value>" % (
    request,
    localpath2url("f:/dima/develop/python/bq5irods/data/imagedir/admin/tests/multi_file/dicom"),
)
request = "%s</image>" % request

# url = session.service_url('data_service', 'image')
# r = session.postxml(url, etree.fromstring(request), method='POST')
r = save_blob(session, resource=request)
if r is None or r.get("uri") is None:
    print("Upload failed")
else:
    print("id: %s" % r.get("resource_uniq"))
    print("url: %s" % r.get("uri"))
