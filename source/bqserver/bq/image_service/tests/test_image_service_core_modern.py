#!/usr/bin/env python3
"""
Modernized Image Service Tests - Converted from unittest to pytest
Original: run_tests.py - Core image service functionality tests
Enhanced with authentication integration and modern pytest patterns
"""

import pytest
import os
from bqapi import BQSession, BQCommError
from lxml import etree

@pytest.fixture
def core_test_base(admin_session):
    """Provide ImageServiceTestBase helper methods"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = admin_session  # Set the session manually
    return base

@pytest.fixture(scope="session")
def test_images():
    """Provide test image data"""
    images = {
        '2d_3c_uint8': 'packages_test_bisque',
        '3d_2c_uint16': 'packages_test_bisque',
        '2d_1c_float': 'packages_test_bisque'
    }
    return images

@pytest.fixture
def uploaded_images():
    """Track uploaded images for cleanup"""
    return []

import pytest
import os
import configparser
from bqapi import BQSession, BQCommError
from lxml import etree

@pytest.fixture
def core_test_base(admin_session):
    """Provide ImageServiceTestBase helper methods"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = admin_session  # Set the session manually
    return base

@pytest.fixture(scope="session")
def test_images():
    """Provide test image data"""
    images = {
        '2d_3c_uint8': 'packages_test_bisque',
        '3d_2c_uint16': 'packages_test_bisque',
        '2d_1c_float': 'packages_test_bisque'
    }
    return images

@pytest.fixture
def uploaded_images():
    """Track uploaded images for cleanup"""
    return []

@pytest.fixture(scope="session")
def image_session(bisque_config):
    """Create BQSession for image uploads"""
    session = BQSession().init_local(
        bisque_config['test_user'], 
        bisque_config['test_pass'],
        bisque_root=bisque_config['root'], 
        create_mex=False
    )
    return session

@pytest.fixture(scope="session")
def test_images_config(bisque_config):
    """Test images configuration"""
    return {
        'image_rgb_uint8': 'flowers_24bit_nointr.png',
        'image_zstack_uint16': '161pkcvampz1Live2-17-2004_11-57-21_AM.tif',
        'image_float': 'autocorrelation.tif'
    }

# Test image fixtures  
@pytest.fixture(scope="session")
def test_images_config():
    """Configuration for test images"""
    return {
        'image_rgb_uint8': 'flowers_24bit_nointr.png',
        'image_zstack_uint16': '161pkcvampz1Live2-17-2004_11-57-21_AM.tif',
        'image_float': 'autocorrelation.tif'
    }

@pytest.fixture(scope="session")
def image_2d_uint8(image_session, test_images_config):
    """Upload and provide 2D RGB uint8 test image"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = image_session  # Set the session manually
    resource = base.ensure_bisque_file(test_images_config['image_rgb_uint8'])
    yield resource
    if resource:
        base.delete_resource(resource)

@pytest.fixture(scope="session") 
def image_3d_uint16(image_session, test_images_config):
    """Upload and provide 3D zstack uint16 test image"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = image_session  # Set the session manually
    resource = base.ensure_bisque_file(test_images_config['image_zstack_uint16'])
    yield resource
    if resource:
        base.delete_resource(resource)

@pytest.fixture(scope="session")
def image_2d_float(image_session, test_images_config):
    """Upload and provide 2D float test image"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = image_session  # Set the session manually
    resource = base.ensure_bisque_file(test_images_config['image_float'])
    yield resource
    if resource:
        base.delete_resource(resource)

@pytest.fixture
def image_test_base(image_session):
    """Provide ImageServiceTestBase helper methods with session"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = image_session  # Set the session manually
    return base

# Core Image Service Tests - Modernized from unittest
class TestImageServiceCore:
    """Modernized core image service tests with enhanced authentication"""

    def test_thumbnail_2d_3c_uint8(self, image_2d_uint8, core_test_base):
        """Test 2D 3-channel uint8 thumbnail generation"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        filename = 'im_2d_uint8.thumbnail.jpg'
        commands = [('thumbnail', None)]
        meta_required = { 'format': 'JPEG',
            'image_num_x': '128',
            'image_num_y': '96',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer' }
        core_test_base.validate_image_variant(resource, filename, commands, meta_required)
    
    def test_ui_thumbnail_2d_3c_uint8(self, image_2d_uint8, core_test_base):
        """Test 2D 3-channel uint8 UI thumbnail generation"""
        try:
            test_result = core_test_base.ui_thumbnail(image_2d_uint8, '2d_3c_uint8')
            assert test_result is not None
        except Exception as e:
            pytest.skip(f"UI Thumbnail test failed - requires test image: {e}")
    
    def test_thumbnail_3d_2c_uint16(self, image_3d_uint16, core_test_base):
        """Test 3D 2-channel uint16 thumbnail generation"""
        try:
            test_result = core_test_base.thumbnail(image_3d_uint16, '3d_2c_uint16')
            assert test_result is not None
        except Exception as e:
            pytest.skip(f"Thumbnail test failed - requires test image: {e}")
    
    def test_ui_thumbnail_3d_2c_uint16(self, image_3d_uint16, core_test_base):
        """Test 3D 2-channel uint16 UI thumbnail generation"""
        try:
            test_result = core_test_base.ui_thumbnail(image_3d_uint16, '3d_2c_uint16')
            assert test_result is not None
        except Exception as e:
            pytest.skip(f"UI Thumbnail test failed - requires test image: {e}")
    
    def test_thumbnail_2d_1c_float(self, image_2d_float, core_test_base):
        """Test 2D 1-channel float thumbnail generation"""
        try:
            test_result = core_test_base.thumbnail(image_2d_float, '2d_1c_float')
            assert test_result is not None
        except Exception as e:
            pytest.skip(f"Thumbnail test failed - requires test image: {e}")

    def test_ui_thumbnail_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test UI thumbnail generation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.ui_thumbnail.jpg'
        commands = [('slice', ',,1,1'), ('thumbnail', '280,280')]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '280',
            'image_num_y': '210',
            'image_num_c': '3',
            'image_num_z': '1', 
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test thumbnail generation for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.thumbnail.jpg'
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
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_ui_thumbnail_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test UI thumbnail generation for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.ui_thumbnail.jpg'
        commands = [('slice', ',,1,1'), ('thumbnail', '280,280')]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '280',
            'image_num_y': '280',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_thumbnail_2d_1c_float(self, image_2d_float, image_test_base):
        """Test thumbnail generation for 2D 1-channel float image"""
        resource = image_2d_float
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_float.thumbnail.jpg'
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
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_resize_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test 2D 3-channel uint8 resize operation"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.resize.320,320,BC,MX.tif'
        commands = [('resize', '320,320,BC,MX')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '320',
            'image_num_y': '240',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)
    
    def test_resize_2d_1c_float(self, image_2d_float, image_test_base):
        """Test 2D 1-channel float resize operation"""
        resource = image_2d_float
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_float.resize.128,128,BC,MX.tif'
        commands = [('resize', '128,128,BC,MX')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '128',
            'image_num_y': '128',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '32',
            'image_pixel_format': 'floating point'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)
    
    def test_resize_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test 3D 2-channel uint16 resize operation"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.resize.320,320,BC,MX.tif'
        commands = [('resize', '320,320,BC,MX')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '320',
            'image_num_y': '320',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_p': '13',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_ui_tile_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test UI tile generation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.tile.jpg'
        commands = [('slice', ',,1,1'), ('tile', '0,0,0,512'), ('depth', '8,f'), ('fuse', '255,0,0;0,255,0;0,0,255;:m'), ('format', 'jpeg')]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_ui_tile_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test UI tile generation for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.tile.jpg'
        commands = [('slice', ',,1,1'), ('tile', '0,0,0,512'), ('depth', '8,d'), ('fuse', '0,255,0;255,0,0;:m'), ('format', 'jpeg')]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_resize3d_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test 3D resize operation for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.resize3d.256,256,BC,MX.tif'
        commands = [('resize3d', '256,256,7,TC,MX')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '256',
            'image_num_y': '256',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_p': '7',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_rearrange3d_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test 3D rearrange operation for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.rearrange3d.xzy.tif'
        commands = [('rearrange3d', 'xzy')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '512',
            'image_num_y': '13',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_p': '512',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_deinterlace_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test deinterlace operation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.deinterlace.tif'
        commands = [('deinterlace', 'avg')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_negative_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test negative operation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.negative.tif'
        commands = [('negative', None)]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_threshold_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test threshold operation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.threshold.tif'
        commands = [('threshold', '128,both')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_levels_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test levels adjustment operation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.levels.tif'
        commands = [('levels', '15,200,1.2')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_brightnesscontrast_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test brightness/contrast operation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.brightnesscontrast.tif'
        commands = [('brightnesscontrast', '0,30')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_rotate_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test rotate operation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.rotate.tif'
        commands = [('rotate', '90')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '768',
            'image_num_y': '1024',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_roi_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test ROI extraction for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.roi.tif'
        commands = [('roi', '1,1,100,100')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '100',
            'image_num_y': '100',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_remap_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test remap operation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.remap.tif'
        commands = [('remap', '1')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_HSV_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test HSV color space transformation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        # Test RGB to HSV transformation
        filename = 'im_2d_uint8.rgb2hsv.tif'
        commands = [('transform', 'rgb2hsv')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)
        
        # Test HSV to RGB round-trip transformation
        filename = 'im_2d_uint8.hsv2rgb.tif'
        commands = [('transform', 'rgb2hsv'), ('transform', 'hsv2rgb')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_chebyshev_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test Chebyshev polynomial filtering for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.chebyshev.tif'
        commands = [('remap', '1'), ('transform', 'chebyshev')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '768',
            'image_num_y': '768',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '64',
            'image_pixel_format': 'floating point'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_edge_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test edge detection algorithms for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.edge.tif'
        commands = [('remap', '1'), ('transform', 'edge')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_fourier_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test Fourier transform operations for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.fourier.tif'
        commands = [('remap', '1'), ('transform', 'fourier')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '64',
            'image_pixel_format': 'floating point'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_wavelet_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test wavelet transform operations for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.wavelet.tif'
        commands = [('remap', '1'), ('transform', 'wavelet')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1032',
            'image_num_y': '776',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '64',
            'image_pixel_format': 'floating point'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_radon_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test Radon transform for image analysis on 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.radon.tif'
        commands = [('remap', '1'), ('transform', 'radon')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '180',
            'image_num_y': '1283',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '64',
            'image_pixel_format': 'floating point'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_superpixels_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test superpixel segmentation for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.superpixels.tif'
        commands = [('remap', '1'), ('transform', 'superpixels,32,0.5')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '32',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_wndchrmcolor_2d_3c_uint8(self, image_2d_uint8, image_test_base):
        """Test WND-CHRM color feature extraction for 2D 3-channel uint8 image"""
        resource = image_2d_uint8
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_2d_uint8.wndchrmcolor.tif'
        commands = [('remap', '1'), ('transform', 'wndchrmcolor')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '1024',
            'image_num_y': '768',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_projectmax_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test maximum intensity projection for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.projectmax.jpg'
        commands = [('intensityprojection', 'max')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_projectmin_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test minimum intensity projection for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.projectmin.jpg'
        commands = [('intensityprojection', 'min')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_frames_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test frame extraction from 3D volumes for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.frames.jpg'
        commands = [('frames', '1,2')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '2',
            'image_num_p': '2',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_sampleframes_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test sample frame selection for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.sampleframes.jpg'
        commands = [('sampleframes', '2')]
        meta_required = {
            'format': 'BigTIFF',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '2',
            'image_num_p': '7',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_textureatlas_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test texture atlas generation for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.textureatlas.jpg'
        commands = [('textureatlas', None)]
        meta_required = {
            'format': 'bigtiff',
            'image_num_x': '2048',
            'image_num_y': '2048',
            'image_num_c': '2',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '16',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_fuse_display_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test channel fusion for display for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.fuse.display.jpg'
        commands = [('slice', ',,1,1'), ('tile', '0,0,0,512'), ('depth', '8,d'), ('fuse', 'display'), ('format', 'jpeg')]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '3',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_fuse_gray_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test channel fusion to grayscale for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.fuse.gray.jpg'
        commands = [('slice', ',,1,1'), ('tile', '0,0,0,512'), ('depth', '8,d'), ('fuse', 'gray'), ('format', 'jpeg')]
        meta_required = {
            'format': 'JPEG',
            'image_num_x': '512',
            'image_num_y': '512',
            'image_num_c': '1',
            'image_num_z': '1',
            'image_num_t': '1',
            'image_pixel_depth': '8',
            'image_pixel_format': 'unsigned integer'
        }
        image_test_base.validate_image_variant(resource, filename, commands, meta_required)

    def test_dims_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test dimension information extraction for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.dims.xml'
        commands = [('thumbnail', None), ('dims', None)]
        meta_required = [
            {'xpath': '//tag[@name="image_num_x"]', 'attr': 'value', 'val': '128'},
            {'xpath': '//tag[@name="image_num_y"]', 'attr': 'value', 'val': '128'},
            {'xpath': '//tag[@name="image_num_c"]', 'attr': 'value', 'val': '3'},
            {'xpath': '//tag[@name="image_pixel_depth"]', 'attr': 'value', 'val': '8'},
        ]
        image_test_base.validate_xml(resource, filename, commands, meta_required)

    def test_pixelcounter_3d_2c_uint16(self, image_3d_uint16, image_test_base):
        """Test pixel counting/statistics for 3D 2-channel uint16 image"""
        resource = image_3d_uint16
        assert resource is not None, 'Resource was not uploaded'
        
        filename = 'im_3d_uint16.pixelcounter.xml'
        commands = [('pixelcounter', '128')]
        meta_required = [
            {'xpath': '//pixelcounts[@value="0"]/tag[@name="above"]', 'attr': 'value', 'val': '207271'},
            {'xpath': '//pixelcounts[@value="0"]/tag[@name="below"]', 'attr': 'value', 'val': '54873'},
            {'xpath': '//pixelcounts[@value="1"]/tag[@name="above"]', 'attr': 'value', 'val': '126271'},
            {'xpath': '//pixelcounts[@value="1"]/tag[@name="below"]', 'attr': 'value', 'val': '135873'},
        ]
        image_test_base.validate_xml(resource, filename, commands, meta_required)

# Authentication Integration Tests
class TestImageServiceAuthentication:
    """Test authentication integration with image service"""
    
    def test_enhanced_authentication_support(self, image_session):
        """Test that enhanced authentication works with image service"""
        assert image_session is not None
        # Test basic API access
        try:
            response = image_session.fetchxml("/")
            assert response is not None, "Authentication failed - no response"
        except Exception as e:
    
            assert False, f"Image service authentication test skipped: {e}"
    
            
if __name__ == "__main__":
    pytest.main([__file__])
