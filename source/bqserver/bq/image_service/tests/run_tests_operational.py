#!/usr/bin/python

""" Image service operational testing framework
update config to your system: config.cfg
call by: python run_tests.py
"""

__module__    = "run_tests_operational"
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
import ConfigParser
import time
from bqapi import BQSession

from bq.image_service.tests.tests_base import ImageServiceTestBase

image_2k            = 'synthetic_3d_2k.ome.tif'
image_2k_meta       = 'synthetic_3d_2k.ome.tif.xml'
image_2k_gobs       = 'synthetic_3d_2k.ome.tif.gobs.xml'
image_5k            = 'synthetic_3d_5k.ome.tif'
image_5k_meta       = 'synthetic_3d_5k.ome.tif.xml'
image_5k_gobs       = 'synthetic_3d_5k.ome.tif.gobs.xml'

##################################################################
# utils
##################################################################

def repeat(times):
    def repeatHelper(f):
        def callHelper(*args):
            for i in range(0, times):
                t1 = time.time()
                f(*args)
                t2 = time.time()
                print 'Run %s took %s seconds'%(i+1, str(t2-t1))
        return callHelper
    return repeatHelper

##################################################################
# ImageServiceTests
##################################################################

class ImageServiceTestsOperational(ImageServiceTestBase):

    @classmethod
    def setUpClass(self):
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')
        self.root = config.get('Host', 'root') or 'localhost:8080'
        self.user = config.get('Host', 'user') or 'test'
        self.pswd = config.get('Host', 'password') or 'test'
        self.session = BQSession().init_local(self.user, self.pswd,  bisque_root=self.root, create_mex=False)

    @classmethod
    def tearDownClass(self):
        self.cleanup_tests_dir()
        pass

    # this tests will test uploading image, first time tiling operation and deleting an image
    @repeat(10)
    def test_image_2k_upload_tile(self):
        # test upload
        print '\nUploading %s\n'%image_2k
        resource  = self.ensure_bisque_file(image_2k, image_2k_meta)
        self.assertIsNotNone(resource, msg='File could not be uploaded: %s'%image_2k)
        # test standard tile op
        print 'Getting tiles for %s'%image_2k
        filename = 'image.2k.tile.jpg'
        commands = [('slice', ',,1,1'), ('tile', '0,0,0,512'), ('depth', '8,f'), ('fuse', '255,255,255;:m'), ('format', 'jpeg')]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

        # test removing the resource
        self.delete_resource(resource)

    # this tests will test uploading image, first time tiling operation and deleting an image
    @repeat(10)
    def test_image_5k_upload_tile(self):
        # test upload
        print '\nUploading %s\n'%image_5k
        resource  = self.ensure_bisque_file(image_5k, image_5k_meta)
        self.assertIsNotNone(resource, msg='File could not be uploaded: %s'%image_5k)

        # test standard tile op
        print 'Getting tiles for %s'%image_5k
        filename = 'image.5k.tile.jpg'
        commands = [('slice', ',,1,1'), ('tile', '0,0,0,512'), ('depth', '8,f'), ('fuse', '255,255,255;:m'), ('format', 'jpeg')]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

        # test removing the resource
        self.delete_resource(resource)

    # this tests will test uploading image, first time tiling operation and deleting an image
    @repeat(10)
    def test_image_2k_upload_largemeta(self):
        # test upload
        print '\nUploading %s\n'%image_2k
        resource  = self.ensure_bisque_file(image_2k, image_2k_gobs)
        self.assertIsNotNone(resource, msg='File could not be uploaded: %s'%image_2k)
        # test removing the resource
        self.delete_resource(resource)

#def suite():
#    tests = ['test_thumbnail']
#    return unittest.TestSuite(map(ImageServiceTests, tests))

if __name__=='__main__':
    if not os.path.exists('images'):
        os.makedirs('images')
    if not os.path.exists('tests'):
        os.makedirs('tests')
    unittest.main(verbosity=2)















