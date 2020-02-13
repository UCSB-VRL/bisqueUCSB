#!/usr/bin/python

""" Image service operational testing framework
update config to your system: config.cfg
call by: python run_tests_thirdpartysupport.py
"""

__module__    = "run_tests_multifile"
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
import shortuuid
from lxml import etree
from datetime import datetime
import urllib

from bqapi import BQSession
from bqapi import BQResource, BQImage

from bq.image_service.tests.tests_base import ImageServiceTestBase

#TEST_PATH = u'tests_multifile_%s'%shortuuid.uuid()
#TEST_PATH = u'tests_multifile_%s'%urllib.quote(datetime.now().isoformat())
TEST_PATH = u'tests_multifile_%s'%urllib.quote(datetime.now().strftime('%Y%m%d%H%M%S%f'))

package_bisque = {
    'file': 'bisque-20140804.143944.tar.gz',
    'resource': '<resource name="%s/bisque-20140804.143944.tar.gz"><tag name="ingest" ><tag name="type" value="zip-bisque" /></tag></resource>'%TEST_PATH,
    'count': 20,
    'values': 1,
    'name': 'COPR Subset',
}

package_different = {
    'file': 'different_images.tar.gz',
    'resource': '<resource name="%s/different_images.tar.gz"><tag name="ingest" ><tag name="type" value="zip-multi-file" /></tag></resource>'%TEST_PATH,
    'count': 4,
    'values': 1,
    'name': 'different_images.tar.gz',
}

package_tiff_5d = {
    'file': 'smith_4d_5z_4t_simple.zip',
    'resource': '<resource name="%s/bill_smith_cells_5D_5Z_4T.zip" ><tag name="ingest" ><tag name="type" value="zip-5d-image" /><tag name="number_z" value="5" /><tag name="number_t" value="4" /><tag name="resolution_x" value="0.4" /><tag name="resolution_y" value="0.4" /><tag name="resolution_z" value="0.8" /><tag name="resolution_t" value="2" /></tag></resource>'%TEST_PATH,
    'count': 1,
    'values': 20,
    'name': 'bill_smith_cells_5D_5Z_4T.zip.series',
}

package_tiff_time = {
    'file': 'smith_t_stack_simple.zip',
    'resource': '<resource name="%s/smith_t_stack_simple.zip" ><tag name="ingest" ><tag name="type" value="zip-time-series" /><tag name="resolution_x" value="0.5" /><tag name="resolution_y" value="0.5" /><tag name="resolution_t" value="0.8" /></tag></resource>'%TEST_PATH,
    'count': 1,
    'values': 11,
    'name': 'smith_t_stack_simple.zip.series',
}

package_tiff_depth = {
    'file': 'smith_z_stack_tiff.zip',
    'resource': '<resource name="%s/smith_z_stack_tiff.zip" ><tag name="ingest" ><tag name="type" value="zip-z-stack" /><tag name="resolution_x" value="0.4" /><tag name="resolution_y" value="0.4" /><tag name="resolution_z" value="0.9" /></tag></resource>'%TEST_PATH,
    'count': 1,
    'values': 5,
    'name': 'smith_z_stack_tiff.zip.series',
}


######################################
# imarisconvert supported files
######################################

image_leica_lif = {
    'file': 'APDnew.lif',
    'resource': '<resource name="%s/APDnew.lif" />'%TEST_PATH,
    'count': 2,
    'values': 1,
    'name': 'APDnew.lif',
}

image_zeiss_czi = {
    'file': 'Mouse_stomach_20x_ROI_3chZTiles(WF).czi',
    'resource': '<resource name="%s/Mouse_stomach_20x_ROI_3chZTiles(WF).czi" />'%TEST_PATH,
    'count': 4,
    'values': 1,
    'name': 'Mouse_stomach_20x_ROI_3chZTiles(WF).czi',
    'subpath': '%s/Mouse_stomach_20x_ROI_3chZTiles(WF).czi#%s',
}

package_andor_iq = {
    'file': 'AndorMM.zip',
    'resource': '<resource name="%s/AndorMM.zip" ><tag name="ingest" ><tag name="type" value="zip-proprietary" /></tag></resource>'%TEST_PATH,
    'count': 3,
    'values': 243,
    'name': 'AndorMM.zip',
    'subpath': '%s/AndorMM/AndorMM/DiskInfo5.kinetic#%s',
}

package_imaris_leica = {
    'file': 'bad_beads_2stacks_chart.zip',
    'resource': '<resource name="%s/bad_beads_2stacks_chart.zip" ><tag name="ingest" ><tag name="type" value="zip-proprietary" /></tag></resource>'%TEST_PATH,
    'count': 3,
    'values': 26,
    'name': 'bad_beads_2stacks_chart.zip',
    'subpath': '%s/bad_beads_2stacks_chart/bad_beads_2stacks_chart/bad_beads_2stacks_chart.lei#%s',
}

######################################
# bioformats/imarisconvert supported files
######################################

image_slidebook = {
    'file': 'cx-11.sld',
    'resource': '<resource name="%s/cx-11.sld" />'%TEST_PATH,
    'count': 16,
    'values': 1,
    'name': 'cx-11.sld',
    'subpath': '%s/cx-11.sld#%s',
}


##################################################################
# ImageServiceTests
##################################################################

class ImageServiceTestsThirdParty(ImageServiceTestBase):

    # setups

    @classmethod
    def setUpClass(cls):
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')

        cls.root = config.get('Host', 'root') or 'localhost:8080'
        cls.user = config.get('Host', 'user') or 'test'
        cls.pswd = config.get('Host', 'password') or 'test'

        cls.session = BQSession().init_local(cls.user, cls.pswd,  bisque_root=cls.root, create_mex=False)

        # download and upload test packages
        cls.ensure_bisque_package(package_bisque)
        cls.ensure_bisque_package(package_different)
        cls.ensure_bisque_package(package_tiff_depth)
        cls.ensure_bisque_package(package_tiff_time)
        cls.ensure_bisque_package(package_tiff_5d)
        cls.ensure_bisque_package(image_leica_lif)
        cls.ensure_bisque_package(image_slidebook)
        cls.ensure_bisque_package(image_zeiss_czi)
        cls.ensure_bisque_package(package_andor_iq)
        cls.ensure_bisque_package(package_imaris_leica)

    @classmethod
    def tearDownClass(cls):
        cls.delete_package(package_bisque)
        cls.delete_package(package_different)
        cls.delete_package(package_tiff_depth)
        cls.delete_package(package_tiff_time)
        cls.delete_package(package_tiff_5d)
        cls.delete_package(image_leica_lif)
        cls.delete_package(image_slidebook)
        cls.delete_package(image_zeiss_czi)
        cls.delete_package(package_andor_iq)
        cls.delete_package(package_imaris_leica)

        cls.cleanup_tests_dir()
        pass

    # tests

    # ---------------------------------------------------
    # bisque package
    # ---------------------------------------------------
    def test_contents_package_bisque (self):
        package = package_bisque

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        self.assertTrue('%s/COPR%%20Subset'%TEST_PATH in resource.get('value'), 'Last item\'s path is wrong')
        self.assertEqual(len(resource.xpath('tag[@name="Genus"]')), 1, 'Tag Genus was not found in the last item')

    def test_thumbnail_package_bisque (self):
        package = package_bisque
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_bisque.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '85',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_meta_package_bisque (self):
        package = package_bisque
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_bisque.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '2592' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '1728' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '3' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'JPEG' },
            { 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '0' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # different package
    # ---------------------------------------------------
    def test_contents_package_different (self):
        package = package_different

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        self.assertTrue('%s/different_images.tar.gz.unpacked/'%TEST_PATH in resource.get('value'))

    def test_thumbnail_package_different (self):
        package = package_different
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_different.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '96',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)


    # ---------------------------------------------------
    # package_tiff_depth
    # ---------------------------------------------------

    def test_contents_package_tiff_depth (self):
        package = package_tiff_depth

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        if resource.get('value') is None:
            values = [x.text for x in resource.xpath('value')]
        else:
            values = [resource.get('value')]
        self.assertEqual(len(values), package['values'], 'Number of sub-values differs from expected')
        self.assertTrue('%s/%s/'%(TEST_PATH, package['name']) in values[0])


    def test_thumbnail_package_tiff_depth (self):
        package = package_tiff_depth
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_depth.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '116',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_meta_package_tiff_depth (self):
        package = package_tiff_depth
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_depth.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '386' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '350' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '5' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'TIFF' },
            #{ 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '0' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.4' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.4' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '0.9' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'microns' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'microns' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'microns' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_package_tiff_depth (self):
        package = package_tiff_depth
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_depth.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '386',
            'image_num_y': '350',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_package_tiff_depth (self):
        #print 'dima: This test will fail, IS is not using external meta for export yet'
        package = package_tiff_depth
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_depth.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '386',
            'image_num_y': '350',
            'image_num_c': '1',
            'image_num_z': '5',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)


    # ---------------------------------------------------
    # package_tiff_time
    # ---------------------------------------------------

    def test_contents_package_tiff_time (self):
        package = package_tiff_time

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        if resource.get('value') is None:
            values = [x.text for x in resource.xpath('value')]
        else:
            values = [resource.get('value')]
        self.assertEqual(len(values), package['values'], 'Number of sub-values differs from expected')
        self.assertTrue('%s/%s/'%(TEST_PATH, package['name']) in values[0])


    def test_thumbnail_package_tiff_time (self):
        package = package_tiff_time
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_time.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '116',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_meta_package_tiff_time (self):
        package = package_tiff_time
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_time.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '386' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '350' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '11' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'PNG' },
            #{ 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '0' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.5' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.5' },
            { 'xpath': '//tag[@name="pixel_resolution_t"]', 'attr': 'value', 'val': '0.8' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'microns' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'microns' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'microns' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_package_tiff_time (self):
        package = package_tiff_time
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_time.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '386',
            'image_num_y': '350',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_package_tiff_time (self):
        #print 'dima: This test will fail, IS is not using external meta for export yet'
        package = package_tiff_time
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_time.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '386',
            'image_num_y': '350',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '11',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # package_tiff_5d
    # ---------------------------------------------------

    def test_contents_package_tiff_5d (self):
        package = package_tiff_5d

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        if resource.get('value') is None:
            values = [x.text for x in resource.xpath('value')]
        else:
            values = [resource.get('value')]
        self.assertEqual(len(values), package['values'], 'Number of sub-values differs from expected')
        self.assertTrue('%s/%s/'%(TEST_PATH, package['name']) in values[0])


    def test_thumbnail_package_tiff_5d (self):
        package = package_tiff_5d
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_5d.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '116',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_meta_package_tiff_5d (self):
        package = package_tiff_5d
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_5d.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '386' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '350' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '5' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '4' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'PNG' },
            #{ 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '0' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.4' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.4' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '0.8' },
            { 'xpath': '//tag[@name="pixel_resolution_t"]', 'attr': 'value', 'val': '2' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'microns' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'microns' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'microns' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_package_tiff_5d (self):
        package = package_tiff_5d
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_5d.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '386',
            'image_num_y': '350',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_package_tiff_5d (self):
        #print 'dima: This test will fail, IS is not using external meta for export yet'
        package = package_tiff_5d
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_tiff_5d.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '386',
            'image_num_y': '350',
            'image_num_c': '1',
            'image_num_z': '5',
            'image_num_t': '4',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)


    # ---------------------------------------------------
    # image_leica_lif
    # ---------------------------------------------------

    def test_contents_image_leica_lif (self):
        package = image_leica_lif

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        name = "%s#%s"%(package['file'], len(package['items'])-1)
        self.assertEqual(resource.get('name'), name)
        self.assertTrue('%s/%s'%(TEST_PATH, name) in resource.get('value'))

    def test_thumbnail_image_leica_lif (self):
        package = image_leica_lif
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_leica_lif.thumbnail.jpg'
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

    def test_meta_image_leica_lif (self):
        package = image_leica_lif
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_leica_lif.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '512' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '512' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '16' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'Leica: Image File Format LIF' },
            { 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '2' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.160490234375' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.160490234375' },
            #{ 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '1.0' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'microns' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'microns' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'microns' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_image_leica_lif (self):
        package = image_leica_lif
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_leica_lif.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-BigTIFF',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_image_leica_lif (self):
        package = image_leica_lif
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_leica_lif.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-BigTIFF',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # image_slidebook
    # ---------------------------------------------------

    def test_contents_image_slidebook (self):
        package = image_slidebook

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        name = "%s#%s"%(package['file'], len(package['items'])-1)
        self.assertEqual(resource.get('name'), name)
        self.assertTrue('%s/%s'%(TEST_PATH, name) in resource.get('value'))

    def test_thumbnail_image_slidebook (self):
        package = image_slidebook
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_slidebook.thumbnail.jpg'
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

    def test_meta_image_slidebook (self):
        package = image_slidebook
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_slidebook.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '2048' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '2048' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '2' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '16' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'Intelligent Imaging Innovations: SlideBook' },
            { 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '16' },
            { 'xpath': '//tag[@name="image_series_index"]', 'attr': 'value', 'val': '15' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.37' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.37' },
            #{ 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '1.0' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'microns' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'microns' },
            #{ 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'microns' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_image_slidebook (self):
        package = image_slidebook
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_slidebook.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            #'format': 'OME-BigTIFF', # bioformats and ImarisConvert use different formats
            'image_num_x': '2048',
            'image_num_y': '2048',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_image_slidebook (self):
        package = image_slidebook
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_slidebook.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            #'format': 'OME-BigTIFF', # bioformats and ImarisConvert use different formats
            'image_num_x': '2048',
            'image_num_y': '2048',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # image_zeiss_czi
    # ---------------------------------------------------

    def test_contents_image_zeiss_czi (self):
        package = image_zeiss_czi

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        name = "%s#%s"%(package['file'], len(package['items'])-1)
        self.assertEqual(resource.get('name'), name)
        pathpart = '%s/%s#%s'%(TEST_PATH, urllib.quote(package['file']), len(package['items'])-1)
        self.assertTrue(pathpart in resource.get('value'))

    def test_thumbnail_image_zeiss_czi (self):
        package = image_zeiss_czi
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_zeiss_czi.thumbnail.jpg'
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

    def test_meta_image_zeiss_czi (self):
        package = image_zeiss_czi
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_zeiss_czi.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '512' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '512' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '3' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '18' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '16' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'Zeiss: CZI' },
            { 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '4' },
            { 'xpath': '//tag[@name="image_series_index"]', 'attr': 'value', 'val': '3' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.3225' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.3225' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '0.6' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'microns' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'microns' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'microns' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_image_zeiss_czi (self):
        package = image_zeiss_czi
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_zeiss_czi.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-TIFF',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_image_zeiss_czi (self):
        package = image_zeiss_czi
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'image_zeiss_czi.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-BigTIFF',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '3',
            'image_num_z': '18',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # package_andor_iq
    # ---------------------------------------------------

    def test_contents_package_andor_iq (self):
        package = package_andor_iq

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        name = "AndorMM#%s"%(len(package['items'])-1)
        self.assertEqual(resource.get('name'), name)

        if resource.get('value') is None:
            values = [x.text for x in resource.xpath('value')]
        else:
            values = [resource.get('value')]
        self.assertEqual(len(values), 243)
        self.assertTrue('%s/AndorMM/AndorMM/DiskInfo5.kinetic#%s'%(TEST_PATH, len(package['items'])-1) in values[0])


    def test_thumbnail_package_andor_iq (self):
        package = package_andor_iq
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_andor_iq.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '125',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_meta_package_andor_iq (self):
        package = package_andor_iq
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_andor_iq.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '1024' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '1024' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '3' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '16' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'Andor: iQ ImageDisk' },
            { 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '3' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '1.09262695313' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '1.06738574219' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '1.08' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'microns' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'microns' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'microns' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_package_andor_iq (self):
        package = package_andor_iq
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_andor_iq.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '1024',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_package_andor_iq (self):
        package = package_andor_iq
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_andor_iq.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '1024',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    # ---------------------------------------------------
    # package_imaris_leica
    # ---------------------------------------------------

    def test_contents_package_imaris_leica (self):
        package = package_imaris_leica

        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertEqual(package['count'], len(package['items']), 'Package count differs from expected')
        self.assertEqual(package['name'], package['resource'].get('name'), 'Package name differs from expected')

        resource = package['last']
        name = "%s#%s"%(os.path.splitext(package['file'])[0], len(package['items'])-1)
        self.assertEqual(resource.get('name'), name, 'Sub resource name differs from expected')
        if resource.get('value') is None:
            values = [x.text for x in resource.xpath('value')]
        else:
            values = [resource.get('value')]
        self.assertEqual(len(values), 26)
        self.assertTrue('%s/bad_beads_2stacks_chart/bad_beads_2stacks_chart/bad_beads_2stacks_chart.lei#%s'%(TEST_PATH, len(package['items'])-1) in values[0])


    def test_thumbnail_package_imaris_leica (self):
        package = package_imaris_leica
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_imaris_leica.thumbnail.jpg'
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

    def test_meta_package_imaris_leica (self):
        package = package_imaris_leica
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_imaris_leica.meta.xml'
        commands = [('meta', None)]
        meta_required = [
            { 'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '1004' },
            { 'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '1004' },
            { 'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '3' },
            { 'xpath': '//tag[@name="image_num_z"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_num_t"]', 'attr': 'value', 'val': '1' },
            { 'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8' },
            { 'xpath': '//tag[@name="image_pixel_format"]', 'attr': 'value', 'val': 'unsigned integer' },
            { 'xpath': '//tag[@name="format"]',      'attr': 'value', 'val': 'Leica: Vista LCS' },
            { 'xpath': '//tag[@name="image_num_series"]', 'attr': 'value', 'val': '3' },
            { 'xpath': '//tag[@name="pixel_resolution_x"]', 'attr': 'value', 'val': '0.0' },
            { 'xpath': '//tag[@name="pixel_resolution_y"]', 'attr': 'value', 'val': '0.0' },
            { 'xpath': '//tag[@name="pixel_resolution_z"]', 'attr': 'value', 'val': '1.0' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_x"]', 'attr': 'value', 'val': 'microns' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_y"]', 'attr': 'value', 'val': 'microns' },
            { 'xpath': '//tag[@name="pixel_resolution_unit_z"]', 'attr': 'value', 'val': 'microns' },
        ]
        self.validate_xml(resource, filename, commands, meta_required)

    # combined test becuase this file has 1 T and 1 Z and so the slice will shortcut and will not be readable by imgcnv
    def test_slice_format_package_imaris_leica (self):
        package = package_imaris_leica
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_imaris_leica.slice.tif'
        commands = [('slice', ',,1,1'), ('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-BigTIFF',
            'image_num_x': '1004',
            'image_num_y': '1004',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def test_format_package_imaris_leica (self):
        package = package_imaris_leica
        self.assertIsNotNone(package['resource'], 'Resource was not uploaded')
        self.assertIsNotNone(package['last'], 'Item was not found')
        resource = package['last']

        filename = 'package_imaris_leica.format.ome.tif'
        commands = [('format', 'ome-tiff')]
        meta_required = {
            'format': 'OME-BigTIFF',
            'image_num_x': '1004',
            'image_num_y': '1004',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
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
