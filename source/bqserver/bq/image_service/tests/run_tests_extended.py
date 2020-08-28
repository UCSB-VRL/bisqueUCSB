#!/usr/bin/python

""" Image service operational testing framework
update config to your system: config.cfg
call by: python run_tests_thirdpartysupport.py
"""

__module__    = "run_tests_thirdpartysupport"
__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

#pylint: skip-file

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

# imarisconvert supported files
image_imaris_hela      = 'HeLaCell.ims'
image_imaris_r18       = 'R18Demo.ims'
image_zeiss_czi_rat    = '40x_RatBrain-AT-2ch-Z-wf.czi'

# bioformats supported files
image_dicom_3d         = 'MR-MONO2-8-16x-heart'
image_dicom_2d         = 'ADNI_002_S_0295_MR_3-plane_localizer__br_raw_20060418193538653_1_S13402_I13712.dcm'




##################################################################
# ImageServiceTests
##################################################################

class ImageServiceTestsThirdParty(ImageServiceTestBase):

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
        self.resource_imaris_hela       = self.ensure_bisque_file(image_imaris_hela)
        self.resource_imaris_r18        = self.ensure_bisque_file(image_imaris_r18)
        self.resource_zeiss_czi_rat     = self.ensure_bisque_file(image_zeiss_czi_rat)
        self.resource_dicom_3d          = self.ensure_bisque_file(image_dicom_3d)
        self.resource_dicom_2d          = self.ensure_bisque_file(image_dicom_2d)

    @classmethod
    def tearDownClass(self):
        self.delete_resource(self.resource_imaris_hela)
        self.delete_resource(self.resource_imaris_r18)
        self.delete_resource(self.resource_zeiss_czi_rat)
        self.delete_resource(self.resource_dicom_3d)
        self.delete_resource(self.resource_dicom_2d)
        self.cleanup_tests_dir()

    # tests

    # ---------------------------------------------------
    # imaris_hela
    # ---------------------------------------------------
    def test_thumbnail_imaris_hela (self):
        resource = self.resource_imaris_hela
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'imaris_hela.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '115',
            'image_num_y': '128',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_meta_imaris_hela (self):
        resource = self.resource_imaris_hela
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'imaris_hela.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '136' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '151' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '2' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '5' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '22' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]', 'attr': 'value', 'val': 'IMARIS5' },
            #{ 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.279015' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.27902' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '2.5' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'um' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'um' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'um' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    def test_slice_imaris_hela (self):
        resource = self.resource_imaris_hela
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'imaris_hela.slice.tif'
        commands = [('slice', ',,1,1')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '136',
            'image_num_y': '151',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_imaris_hela (self):
        resource = self.resource_imaris_hela
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'imaris_hela.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '136',
            'image_num_y': '151',
            'image_num_c': '2',
            'image_num_z': '5',
            'image_num_t': '22',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # imaris_r18
    # ---------------------------------------------------
    def test_thumbnail_imaris_r18 (self):
        resource = self.resource_imaris_r18
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'imaris_r18.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '128',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_meta_imaris_r18 (self):
        resource = self.resource_imaris_r18
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'imaris_r18.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '256' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '256' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '6' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '30' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]', 'attr': 'value', 'val': 'IMARIS5' },
            #{ 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.817973' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.817973' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '5.38483' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'um' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'um' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'um' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    def test_slice_imaris_r18 (self):
        resource = self.resource_imaris_r18
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'imaris_r18.slice.tif'
        commands = [('slice', ',,1,1')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '256',
            'image_num_y': '256',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_imaris_r18 (self):
        resource = self.resource_imaris_r18
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'imaris_r18.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '256',
            'image_num_y': '256',
            'image_num_c': '1',
            'image_num_z': '6',
            'image_num_t': '30',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # zeiss_czi_rat
    # ---------------------------------------------------
    def test_thumbnail_zeiss_czi_rat (self):
        resource = self.resource_zeiss_czi_rat
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'zeiss_czi_rat.thumbnail.jpg'
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

    def test_meta_zeiss_czi_rat (self):
        resource = self.resource_zeiss_czi_rat
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'zeiss_czi_rat.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '400' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '400' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '2' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '97' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '16' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]', 'attr': 'value', 'val': 'CZI' },
            #{ 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.16125' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.16125' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '0.2' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'um' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'um' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'um' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    def test_slice_zeiss_czi_rat (self):
        resource = self.resource_zeiss_czi_rat
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'zeiss_czi_rat.slice.tif'
        commands = [('slice', ',,1,1')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '400',
            'image_num_y': '400',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_zeiss_czi_rat (self):
        resource = self.resource_zeiss_czi_rat
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'zeiss_czi_rat.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '400',
            'image_num_y': '400',
            'image_num_c': '2',
            'image_num_z': '97',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # DICOM 3D
    # ---------------------------------------------------
    def test_thumbnail_dicom_3d(self):
        resource = self.resource_dicom_3d
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'dicom_3d.thumbnail.jpg'
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

    def test_meta_dicom_3d(self):
        resource = self.resource_dicom_3d
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'dicom_3d.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '256' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '256' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '16' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]', 'attr': 'value', 'val': 'DICOM' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '10.0' },
            { 'xpath': '//tag[@name="pixel_resolution_t"]', 'attr': 'value', 'val': '69.47' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'mm' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'mm' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'mm' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_t"]', 'attr': 'value', 'val': 'seconds' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    def test_slice_dicom_3d(self):
        resource = self.resource_dicom_3d
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'dicom_3d.slice.tif'
        commands = [('slice', ',,1,1')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '256',
            'image_num_y': '256',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_dicom_3d(self):
        resource = self.resource_dicom_3d
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'dicom_3d.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '256',
            'image_num_y': '256',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '16',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # DICOM 2D
    # ---------------------------------------------------
    def test_thumbnail_dicom_2d(self):
        resource = self.resource_dicom_2d
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'dicom_2d.thumbnail.jpg'
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

    def test_meta_dicom_2d(self):
        resource = self.resource_dicom_2d
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'dicom_2d.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '256' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '256' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '16' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'signed integer' },
            { 'xpath': '//tag[@name="format"]', 'attr': 'value', 'val': 'DICOM' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '1.01562' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '1.01562' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '5' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'mm' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'mm' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'mm' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_dicom_2d(self):
        resource = self.resource_dicom_2d
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'dicom_2d.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '256',
            'image_num_y': '256',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'signed integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_dicom_2d(self):
        resource = self.resource_dicom_2d
        self.assertIsNotNone(resource, 'Resource was not uploaded')
        filename = 'dicom_2d.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '256',
            'image_num_y': '256',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'signed integer'
        }
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
