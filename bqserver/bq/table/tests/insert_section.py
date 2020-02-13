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
from datetime import datetime

url_import  = '/import/transfer'
url_data  = '/data_service/'

if len(sys.argv)<1:
    print "usage: PATH_TO_FILES"
    sys.exit()

path_files = sys.argv[1]
files = os.listdir(path_files)
files = [os.path.join(path_files, f) for f in files]

##################################################################
# Upload
##################################################################


config = ConfigParser.ConfigParser()
config.read('config.cfg')

root = config.get('Host', 'root') or 'localhost:8080'
user = config.get('Host', 'user') or 'test'
pswd = config.get('Host', 'password') or 'test'

session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)

start=datetime.now()
url = urlparse.urljoin(root, url_import)
members = []
for f in files:
    resource = etree.Element('resource', name=os.path.basename(f), value=localpath2url(f) )
    print etree.tostring(resource)
    r = save_blob(session, resource=resource)
    #r = session.postblob(xml=resource)
    if r is None or r.get('uri') is None:
        print 'Upload failed for %s'%f
    else:
        members.append(r.get('uri'))
print "Inserted all in: %s"%(datetime.now()-start)

dataset = etree.Element('dataset', name=os.path.basename(os.path.dirname(files[0])))
for m in members:
    n = etree.SubElement(dataset, 'value')
    n.text = m

#print etree.tostring(dataset)
url = urlparse.urljoin(root, url_data)
r = session.postxml(url, xml=etree.tostring(dataset))
print r
