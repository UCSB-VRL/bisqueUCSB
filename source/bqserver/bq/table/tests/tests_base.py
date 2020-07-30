#!/usr/bin/python

""" Image service testing framework
update config to your system: config.cfg
call by: python run_tests.py
"""

__module__    = "tests_base"
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

import urllib
import os
import posixpath
import ConfigParser
from lxml import etree
from subprocess import Popen, call, PIPE
from datetime import datetime
import urllib
import shortuuid

from bq.util.mkdir import _mkdir

from bqapi import BQSession, BQCommError # bisque
from bqapi.util import save_blob # bisque

import logging
#logging.basicConfig(level=logging.DEBUG)

IMGCNV='imgcnv'

url_image_store     = 'http://hammer.ece.ucsb.edu/~bisque/test_data/images/'
local_store_images  = 'images'
local_store_tests   = 'tests'

service_data        = 'data_service'
service_image       = 'image_service'
resource_image      = 'image'

#TEST_PATH = 'tests_multifile_%s'%shortuuid.uuid()
#TEST_PATH = 'tests_%s'%urllib.quote(datetime.now().isoformat())
TEST_PATH = 'tests_%s'%urllib.quote(datetime.now().strftime('%Y%m%d%H%M%S%f'))

###############################################################
# info comparisons
###############################################################

def print_failed(s, f='-'):
    print 'FAILED %s'%(s)

class InfoComparator(object):
    '''Compares two info dictionaries'''
    def compare(self, iv, tv):
        return False
    def fail(self, k, iv, tv):
        print_failed('%s failed comparison [%s] [%s]'%(k, iv, tv))
        pass

class InfoEquality(InfoComparator):
    def compare(self, iv, tv):
        return (iv.lower()==tv.lower())
    def fail(self, k, iv, tv):
        print_failed('%s failed comparison %s = %s'%(k, iv, tv))
        pass

class InfoNumericLessEqual(InfoComparator):
    def compare(self, iv, tv):
        return (int(iv)<=int(tv))
    def fail(self, k, iv, tv):
        print_failed('%s failed comparison %s <= %s'%(k, iv, tv))
        pass

def compare_info(meta_req, meta_test, cc=InfoEquality() ):
    if meta_req is None: return False
    if meta_test is None: return False
    for tk in meta_req:
        if tk not in meta_test:
            return False
        if not cc.compare(meta_req[tk], meta_test[tk]):
            cc.fail( tk, meta_req[tk], meta_test[tk] )
            return False
    return True

###############################################################
# xml comparisons
###############################################################

def compare_xml(meta_req, meta_test, cc=InfoEquality() ):
    for t in meta_req:
        req_xpath = t['xpath']
        req_attr  = t['attr']
        req_val   = t['val']
        l = meta_test.xpath(req_xpath)
        if len(l)<1:
            print_failed( 'xpath did not return any results' )
            return False
        e = l[0]
        if req_val is None:
            return e.get(req_attr, None) is not None
        v = e.get(req_attr)
        if not cc.compare(req_val, v):
            cc.fail( '%s attr %s'%(req_xpath, req_attr), req_val, v )
            return False
    return True

##################################################################
# utils
##################################################################

def repeat(times):
    def repeatHelper(f):
        def callHelper(*args):
            for i in range(0, times):
                f(*args)
        return callHelper
    return repeatHelper

def parse_imgcnv_info(s):
    d = {}
    for l in s.splitlines():
        k = l.split(': ', 1)
        if len(k)>1:
            d[k[0]] = k[1]
    return d

def metadata_read( filename ):
    command = [IMGCNV, '-i', filename, '-meta']
    r = Popen (command, stdout=PIPE).communicate()[0]
    if r is None or r.startswith('Input format is not supported'):
        return None
    return parse_imgcnv_info(r)

##################################################################
# ImageServiceTestBase
##################################################################

class ImageServiceTestBase(unittest.TestCase):
    """
        Test image service operations
    """

    @classmethod
    def setUpClass(self):
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')

        self.root = config.get('Host', 'root') or 'localhost:8080'
        self.user = config.get('Host', 'user') or 'test'
        self.pswd = config.get('Host', 'password') or 'test'

        self.session = BQSession().init_local(self.user, self.pswd,  bisque_root=self.root, create_mex=False)

        # download and upload test images ang get their IDs
        #self.uniq_2d_uint8  = self.ensure_bisque_file(image_rgb_uint8)
        #self.uniq_3d_uint16 = self.ensure_bisque_file(image_zstack_uint16)

    @classmethod
    def tearDownClass(self):
        #self.delete_resource(self.uniq_2d_uint8)
        #self.delete_resource(self.uniq_3d_uint16)
        self.cleanup_tests_dir()
        pass

    @classmethod
    def fetch_file(self, filename):
        _mkdir(local_store_images)
        _mkdir(local_store_tests)
        url = posixpath.join(url_image_store, filename).encode('utf-8')
        path = os.path.join(local_store_images, filename)
        if not os.path.exists(path):
            urllib.urlretrieve(url, path)
        return path

    @classmethod
    def upload_file(self, path, resource=None):
        #if resource is not None:
        #    print etree.tostring(resource)
        r = save_blob(self.session, path, resource=resource)
        if r is None or r.get('uri') is None:
            print 'Error uploading: %s'%path.encode('ascii', 'replace')
            return None
        print 'Uploaded id: %s url: %s'%(r.get('resource_uniq'), r.get('uri'))
        return r

    @classmethod
    def delete_resource(self, r):
        if r is None:
            return
        url = r.get('uri')
        print 'Deleting id: %s url: %s'%(r.get('resource_uniq'), url)
        self.session.deletexml(url)

    @classmethod
    def delete_package(self, package):
        if 'dataset' in package:
            # delete dataset
            url = package['dataset']
            print 'Deleting dataset: %s'%(url)
            try:
                self.session.fetchxml('/dataset_service/delete?duri=%s'%url)
            except BQCommError:
                print 'Error deleting the dataset'
        elif 'items' in package:
            # delete all items
            for url in package['items']:
                print 'Deleting item: %s'%(url)
                try:
                    self.session.deletexml(url)
                except BQCommError:
                    print 'Error deleting the item'

        # # delete dataset
        # if 'dataset' in package:
        #     url = package['dataset']
        #     print 'Deleting dataset: %s'%(url)
        #     try:
        #         self.session.deletexml(url)
        #     except BQCommError:
        #         print 'Error deleting the dataset'

        # # delete all items
        # if 'items' in package:
        #     for url in package['items']:
        #         print 'Deleting item: %s'%(url)
        #         try:
        #             self.session.deletexml(url)
        #         except BQCommError:
        #             print 'Error deleting the item'

    @classmethod
    def ensure_bisque_file(self, filename, metafile=None):
        path = self.fetch_file(filename)
        if metafile is None:
            filename = u'%s/%s'%(TEST_PATH, filename)
            resource = etree.Element ('resource', name=filename)
            return self.upload_file(path, resource=resource)
        else:
            metafile = self.fetch_file(metafile)
            return self.upload_file(path, resource=etree.parse(metafile).getroot())


    @classmethod
    def ensure_bisque_package(self, package):
        path = self.fetch_file(package['file'])
        r = self.upload_file(path, resource=etree.XML(package['resource']))
        package['resource'] = r
        if r is None:
            return None
        print 'Uploaded id: %s url: %s'%(r.get('resource_uniq'), r.get('uri'))
        #print etree.tostring(r)
        if r.tag != 'dataset':
            package['items'] = [r.get('uri')]
        else:
            package['dataset'] = r.get('uri')
            values = r.xpath('value')
            if len(values) != package['count']:
                print 'Error: uploaded %s has %s elements but needs %s'%(package['file'], len(values), package['count'])
            if r.get('name') != package['name']:
                print 'Error: uploaded %s name is %s but should be %s'%(package['file'], r.get('name'), package['name'])
            package['items'] = [x.text for x in values]

        package['last'] = self.session.fetchxml(package['items'][-1], view='deep')
        #print 'Last item\n'
        #print etree.tostring(package['last'])


    @classmethod
    def cleanup_tests_dir(self):
        print 'Cleaning-up %s'%local_store_tests
        for root, dirs, files in os.walk(local_store_tests, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

    def validate_image_variant(self, resource, filename, commands, meta_required=None):
        path = os.path.join(local_store_tests, filename)
        try:
            #image = fromXml(resource, session=self.session)
            image = self.session.factory.from_etree(resource)
            px = image.pixels()
            for c,a in commands:
                px = px.command(c, a)
            px.fetch(path)
        except BQCommError:
            logging.exception('Comm error')
            self.fail('Communication error while fetching image')

        if meta_required is not None:
            meta_test = metadata_read(path)
            self.assertTrue(meta_test is not None, msg='Retrieved image can not be read')
            self.assertTrue(compare_info(meta_required, meta_test), msg='Retrieved metadata differs from test template')

    def validate_xml(self, resource, filename, commands, xml_parts_required):
        path = os.path.join(local_store_tests, filename)
        try:
            #image = fromXml(resource, session=self.session)
            image = self.session.factory.from_etree(resource)
            px = image.pixels()
            for c,a in commands:
                px = px.command(c, a)
            px.fetch(path)
        except BQCommError:
            self.fail()

        xml_test = etree.parse(path).getroot()
        #print etree.tostring(xml_test)
        self.assertTrue(compare_xml(xml_parts_required, xml_test), msg='Retrieved XML differs from test template')

