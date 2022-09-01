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
from bqapi.comm import BQSession, BQCommError

from bq.image_service.tests.tests_base import ImageServiceTestBase

url_module  = '/module_service/NuclearDetector3D'

request_xml = '<mex><tag name="inputs" >\
  <tag type="system-input" name="mex_url" />\
  <tag type="system-input" name="bisque_token" />\
  <tag type="image" name="resource_url" value="{IMAGE_URL}" ><gobject name="roi" /></tag>\
  <tag type="image_channel" name="nuclear_channel" value="{NUCLEAR_CHANNEL}" />\
  <tag type="image_channel" name="membrane_channel" value="0" />\
  <tag type="number" name="nuclear_size" value="{NUCLEAR_SIZE}" />\
  <tag type="pixel_resolution" name="pixel_resolution" >\
      <value type="number" index="0" >0.4395</value><value type="number" index="1" >0.4395</value><value type="number" index="2" >1</value><value type="number" index="3" >1</value>\
  </tag>\
  </tag><tag name="execute_options" ><tag name="iterable" value="resource_url" /></tag></mex>'


image_2k = 'synthetic_3d_2k.ome.tif'


##################################################################
# ImageServiceTests
##################################################################

class NuclearDetector3DTests(ImageServiceTestBase):

    # setups

    @classmethod
    def setUpClass(self):
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')

        self.root = config.get('Host', 'root') or 'localhost:8080'
        self.user = config.get('Host', 'user') or 'test'
        self.pswd = config.get('Host', 'password') or 'test'

        self.session = BQSession().init_local(self.user, self.pswd,  bisque_root=self.root, create_mex=False)

        # download and upload test images ang get their IDs
        self.resource_2k  = self.ensure_bisque_file(image_2k)

    @classmethod
    def tearDownClass(self):
        self.delete_resource(self.resource_2k)
        self.cleanup_tests_dir()
        pass

    # tests

    def test_nd3d_run(self):
        resource = self.resource_2k
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        
        url = urlparse.urljoin(self.root, posixpath.join(url_module, 'execute'))
        request = request_xml.replace('{IMAGE_URL}', resource.get('uri', ''))
        request = request.replace('{NUCLEAR_CHANNEL}', '1')
        request = request.replace('{NUCLEAR_SIZE}', '5')
        
        r = self.session.postxml(url, etree.fromstring(request), method='POST')
        self.assertIsNotNone(r, 'Module execution failed')

        url = r.get('uri', None)
        status = r.get('value', None)
        self.assertIsNotNone(url, 'Module MEX is incorrect')
        self.assertIsNotNone(status, 'Module MEX is incorrect')
        self.assertTrue(status != 'FAILED', msg='Module failed to run correctly')
        
        while status != 'FINISHED':
            time.sleep(2)
            mex = self.session.fetchxml(url)
            self.assertIsNotNone(mex, 'Fetching MEX update failed')
            status = mex.get('value', None)
            self.assertTrue(status != 'FAILED', msg='Module failed to run correctly')
        
        # module finished, compare results
        mex = self.session.fetchxml(url, view='deep')
        l = mex.xpath('//gobject[@type="nucleus"]/point')
        self.assertTrue(len(l) == 444, msg='Module returned incorrect number of points, expected 444 got %s'%len(l))

#def suite():
#    tests = ['test_thumbnail']
#    return unittest.TestSuite(map(ImageServiceTests, tests))

if __name__=='__main__':
    if not os.path.exists('images'):
        os.makedirs('images')
    if not os.path.exists('tests'):
        os.makedirs('tests')
    unittest.main(verbosity=2)
