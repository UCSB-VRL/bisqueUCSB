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
import ConfigParser
from bqapi import BQSession, BQCommError

from bq.image_service.tests.tests_base import ImageServiceTestBase

image_unicode_jpeg  = 'пустыня.jpg' #utf-8 encoded filename
image_unicode_mov   = 'видео.mov' #utf-8 encoded filename
image_unicode_ims   = 'никлаус.ims' #utf-8 encoded filename
image_unicode_oib   = 'ретина.oib' #utf-8 encoded filename
image_unicode_tiff  = 'рыбы.tif' #utf-8 encoded filename
image_unicode_dicom = 'сердце.dcm' #utf-8 encoded filename
image_unicode_svs   = 'сму_регион.svs' #utf-8 encoded filename
image_latin1_tiff   = 'test_latin1_chars_°µÀÁÂÃÄÅ¿ÇÆÈÉÊËÌÍÎÏÑÐÒÓÔÕÖØÙÚÛÜÝßßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ.tif' #utf-8 encoded filename

##################################################################
# ImageServiceTests
##################################################################

class ImageServiceTestsUnicode(ImageServiceTestBase):

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
        self.resource_unicode_jpeg  = self.ensure_bisque_file(image_unicode_jpeg.decode('utf-8'))
        self.resource_unicode_mov   = self.ensure_bisque_file(image_unicode_mov.decode('utf-8'))
        self.resource_unicode_oib   = self.ensure_bisque_file(image_unicode_oib.decode('utf-8'))
        self.resource_unicode_tiff  = self.ensure_bisque_file(image_unicode_tiff.decode('utf-8'))
        self.resource_unicode_ims   = self.ensure_bisque_file(image_unicode_ims.decode('utf-8'))
        self.resource_unicode_dicom = self.ensure_bisque_file(image_unicode_dicom.decode('utf-8'))
        self.resource_unicode_svs   = self.ensure_bisque_file(image_unicode_svs.decode('utf-8'))
        self.resource_latin1_tiff   = self.ensure_bisque_file(image_latin1_tiff.decode('utf-8'))

    @classmethod
    def tearDownClass(self):
        self.delete_resource(self.resource_unicode_jpeg)
        self.delete_resource(self.resource_unicode_mov)
        self.delete_resource(self.resource_unicode_oib)
        self.delete_resource(self.resource_unicode_tiff)
        self.delete_resource(self.resource_unicode_ims)
        self.delete_resource(self.resource_unicode_dicom)
        self.delete_resource(self.resource_unicode_svs)
        self.delete_resource(self.resource_latin1_tiff)
        self.cleanup_tests_dir()

    # tests

    def test_thumbnail_unicode_jpeg(self):
        resource = self.resource_unicode_jpeg
        filename = 'unicode.jpeg.thumbnail.jpg'
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        self.assertEqual(resource.get('name').encode('utf8'), image_unicode_jpeg)
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '73',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_unicode_mov(self):
        resource = self.resource_unicode_mov
        filename = 'unicode.mov.thumbnail.jpg'
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        self.assertEqual(resource.get('name').encode('utf8'), image_unicode_mov)
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '109',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_unicode_oib(self):
        resource = self.resource_unicode_oib
        filename = 'unicode.oib.thumbnail.jpg'
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        self.assertEqual(resource.get('name').encode('utf8'), image_unicode_oib)
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '128',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_unicode_tiff(self):
        resource = self.resource_unicode_tiff
        filename = 'unicode.tiff.thumbnail.jpg'
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        self.assertEqual(resource.get('name').encode('utf8'), image_unicode_tiff)
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '96',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1', 
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_unicode_ims(self):
        resource = self.resource_unicode_ims
        filename = 'unicode.ims.thumbnail.jpg'
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        self.assertEqual(resource.get('name').encode('utf8'), image_unicode_ims)
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '128',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_unicode_dicom(self):
        resource = self.resource_unicode_dicom
        filename = 'unicode.dicom.thumbnail.jpg'
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        self.assertEqual(resource.get('name').encode('utf8'), image_unicode_dicom)
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '128',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_unicode_svs(self):
        resource = self.resource_unicode_svs
        filename = 'unicode.svs.thumbnail.jpg'
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        self.assertEqual(resource.get('name').encode('utf8'), image_unicode_svs)
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '95',
            'image_num_y': '128',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_latin1_tiff(self):
        resource = self.resource_latin1_tiff
        filename = 'latin1_tiff.thumbnail.jpg'
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        self.assertEqual(resource.get('name').encode('utf8'), image_latin1_tiff)
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '96',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

#def suite():
#    tests = ['test_thumbnail']
#    return unittest.TestSuite(map(ImageServiceTests, tests))

if __name__=='__main__':
    if not os.path.exists('images'):
        os.makedirs('images')
    if not os.path.exists('tests'):
        os.makedirs('tests')
    unittest.main(verbosity=2)
