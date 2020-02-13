#!/usr/bin/python

""" Image service operational tile access testing framework
update config to your system: config.cfg
call by: python run_tests.py
"""

__module__    = "run_tests_tiles"
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
from lxml import etree
import numpy

from bq.image_service.tests.tests_base import ImageServiceTestBase

image_pyramid = 'monument_imgcnv_subdirs.tif'
image_planar = 'monument_planar.tif'


##################################################################
# ImageServiceTests
##################################################################

class ImageServiceTestsTiles(ImageServiceTestBase):

    @classmethod
    def setUpClass(self):
        config = ConfigParser.ConfigParser()
        config.read('config.cfg')
        self.root = config.get('Host', 'root') or 'localhost:8080'
        self.user = config.get('Host', 'user') or 'test'
        self.pswd = config.get('Host', 'password') or 'test'
        self.session = BQSession().init_local(self.user, self.pswd,  bisque_root=self.root, create_mex=False)

        print '\nUploading images\n'

        self.resources_plane = []
        self.resources_plane.append( self.ensure_bisque_file(image_planar) )
        self.resources_plane.append( self.ensure_bisque_file(image_planar) )
        self.resources_plane.append( self.ensure_bisque_file(image_planar) )
        self.resources_plane.append( self.ensure_bisque_file(image_planar) )
        self.resources_plane.append( self.ensure_bisque_file(image_planar) )

        self.resources_pyr = []
        self.resources_pyr.append( self.ensure_bisque_file(image_pyramid) )
        self.resources_pyr.append( self.ensure_bisque_file(image_pyramid) )
        self.resources_pyr.append( self.ensure_bisque_file(image_pyramid) )
        self.resources_pyr.append( self.ensure_bisque_file(image_pyramid) )
        self.resources_pyr.append( self.ensure_bisque_file(image_pyramid) )

        self.resources_valid_plane = [self.ensure_bisque_file(image_planar)]
        self.resources_valid_pyr = [self.ensure_bisque_file(image_pyramid)]

        self.coordinates = [(0,0), (1,3), (2,3), (7,1), (2,2), (5,2), (7,2), (1,1), (6,3), (7,3)]

    @classmethod
    def tearDownClass(self):
        # removing resources
        for r in self.resources_plane:
           self.delete_resource(r)
        for r in self.resources_pyr:
           self.delete_resource(r)
        self.cleanup_tests_dir()

    def validate_tile(self, resource=None, coord=None):
        'Validation ensures fetched tiles are correct but due to local validation gives inflated speed measurements'
        filename = '%s.tile.%s,%s.jpg'%(resource.get('resource_uniq'), coord[0], coord[1])
        commands = [('slice', ',,1,1'), ('tile', '0,%s,%s,512'%(coord[0], coord[1])), ('depth', '8,f,u'), ('fuse', '255,0,0;0,255,0;0,0,255;:m'), ('format', 'jpeg')]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        self.validate_image_variant(resource, filename, commands, meta_required)

    def fetch_tile(self, resource=None, coord=None):
        'Fetching tile does not run the validation and thus gives better speed estimate'
        filename = '%s.tile.%s,%s.jpg'%(resource.get('resource_uniq'), coord[0], coord[1])
        commands = [('slice', ',,1,1'), ('tile', '0,%s,%s,512'%(coord[0], coord[1])), ('depth', '8,f,u'), ('fuse', '255,0,0;0,255,0;0,0,255;:m'), ('format', 'jpeg')]
        self.validate_image_variant(resource, filename, commands)

    def forresources(self, resources, op):
        times = []
        for r in resources:
            for c in self.coordinates:
                t1 = time.time()
                op(resource=r, coord=c)
                t2 = time.time()
                times.append(t2-t1)
        #print 'Times: %s'%times
        print '\nTile retreival in seconds, avg: %s max: %s min: %s, std: %s'%(numpy.array(times).mean(), max(times), min(times), numpy.array(times).std())

    def test_speed_planar_tiles_1_uncached(self):
        self.forresources(self.resources_plane, self.fetch_tile)

    def test_speed_planar_tiles_2_cached(self):
        self.forresources(self.resources_plane, self.fetch_tile)

    def test_speed_pyramidal_tiles_1_uncached(self):
       self.forresources(self.resources_pyr, self.fetch_tile)

    def test_speed_pyramidal_tiles_2_cached(self):
       self.forresources(self.resources_pyr, self.fetch_tile)

    def test_valid_planar_tiles_1_uncached(self):
        self.forresources(self.resources_valid_plane, self.validate_tile)

    def test_valid_planar_tiles_2_cached(self):
        self.forresources(self.resources_valid_plane, self.validate_tile)

    def test_valid_pyramidal_tiles_1_uncached(self):
       self.forresources(self.resources_valid_pyr, self.validate_tile)

    def test_valid_pyramidal_tiles_2_cached(self):
       self.forresources(self.resources_valid_pyr, self.validate_tile)


#def suite():
#    tests = ['test_thumbnail']
#    return unittest.TestSuite(map(ImageServiceTests, tests))

if __name__=='__main__':
    if not os.path.exists('images'):
        os.makedirs('images')
    if not os.path.exists('tests'):
        os.makedirs('tests')
    unittest.main(verbosity=2)
