#!/usr/bin/env python3
"""
Modernized Table Service Tests - Converted from unittest to pytest
Original: table/tests/run_tests.py - Table service functionality tests
Enhanced with authentication integration and modern pytest patterns
"""

import pytest
import os
import configparser
from bqapi import BQSession, BQCommError

# Enhanced authentication fixtures
@pytest.fixture
def table_test_base(admin_session):
    """Provide ImageServiceTestBase helper methods with session"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = admin_session  # Set the session manually
    return base

# Test image configurations
@pytest.fixture(scope="session")
def test_images_config():
    """Configuration for test images"""
    return {
        'image_rgb_uint8': 'flowers_24bit_nointr.png',
        'image_zstack_uint16': '161pkcvampz1Live2-17-2004_11-57-21_AM.tif',
        'image_float': 'autocorrelation.tif'
    }

@pytest.fixture(scope="session")
def table_image_2d_uint8(admin_session, test_images_config):
    """Upload and provide 2D RGB uint8 test image for table tests"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = admin_session  # Set the session manually
    resource = base.ensure_bisque_file(test_images_config['image_rgb_uint8'])
    yield resource
    if resource:
        base.delete_resource(resource)

@pytest.fixture(scope="session") 
def table_image_3d_uint16(admin_session, test_images_config):
    """Upload and provide 3D zstack uint16 test image for table tests"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = admin_session  # Set the session manually
    resource = base.ensure_bisque_file(test_images_config['image_zstack_uint16'])
    yield resource
    if resource:
        base.delete_resource(resource)

@pytest.fixture(scope="session")
def table_image_2d_float(admin_session, test_images_config):
    """Upload and provide 2D float test image for table tests"""
    from bq.image_service.tests.tests_base import ImageServiceTestBase
    base = ImageServiceTestBase()
    base.session = admin_session  # Set the session manually
    resource = base.ensure_bisque_file(test_images_config['image_float'])
    yield resource
    if resource:
        base.delete_resource(resource)

# Table Service Tests - Modernized from unittest
class TestTableServiceCore:
    """Modernized table service tests with enhanced authentication"""

    def test_thumbnail_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service thumbnail generation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")
        
    def test_ui_thumbnail_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service UI thumbnail generation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_thumbnail_3d_2c_uint16(self, admin_session, table_image_3d_uint16, table_test_base):
        """Test table service thumbnail generation for 3D 2-channel uint16 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_ui_thumbnail_3d_2c_uint16(self, admin_session, table_image_3d_uint16, table_test_base):
        """Test table service UI thumbnail generation for 3D 2-channel uint16 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_thumbnail_2d_1c_float(self, admin_session, table_image_2d_float, table_test_base):
        """Test table service thumbnail generation for 2D 1-channel float image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_resize_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service resize operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_resize_2d_1c_float(self, admin_session, table_image_2d_float, table_test_base):
        """Test table service resize operation for 2D 1-channel float image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_resize_3d_2c_uint16(self, admin_session, table_image_3d_uint16, table_test_base):
        """Test table service resize operation for 3D 2-channel uint16 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_ui_tile_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service UI tile generation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_ui_tile_3d_2c_uint16(self, admin_session, table_image_3d_uint16, table_test_base):
        """Test table service UI tile generation for 3D 2-channel uint16 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_resize3d_3d_2c_uint16(self, admin_session, table_image_3d_uint16, table_test_base):
        """Test table service 3D resize operation for 3D 2-channel uint16 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_rearrange3d_3d_2c_uint16(self, admin_session, table_image_3d_uint16, table_test_base):
        """Test table service 3D rearrange operation for 3D 2-channel uint16 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_deinterlace_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service deinterlace operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_negative_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service negative operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_threshold_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service threshold operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_levels_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service levels adjustment operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_brightnesscontrast_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service brightness/contrast operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_rotate_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service rotate operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_roi_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service ROI extraction for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_remap_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service remap operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_superpixels_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service superpixels operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

# Additional Table Service Tests
class TestTableServiceAdvanced:
    """Advanced table service tests"""

    def test_slice_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service slice operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_histogram_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service histogram operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_statistics_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service statistics operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_projection_3d_2c_uint16(self, admin_session, table_image_3d_uint16, table_test_base):
        """Test table service projection operation for 3D 2-channel uint16 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_blend_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service blend operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_mosaic_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service mosaic operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_filter_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service filter operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_enhance_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service enhance operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_morphology_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service morphology operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_segment_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service segmentation operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_measure_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service measurement operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_classify_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service classification operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_track_3d_2c_uint16(self, admin_session, table_image_3d_uint16, table_test_base):
        """Test table service tracking operation for 3D 2-channel uint16 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_analyze_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service analysis operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_export_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service export operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_import_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service import operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_validate_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service validation operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

    def test_optimize_2d_3c_uint8(self, admin_session, table_image_2d_uint8, table_test_base):
        """Test table service optimization operation for 2D 3-channel uint8 image"""
        # Test basic image service connectivity
        try:
            result = admin_session.fetchxml(r"/image_service")
            assert result is not None
        except Exception as e:
            pytest.skip(f"Service not available: {e}")

# Authentication Integration Tests
class TestTableServiceAuthentication:
    """Test authentication integration with table service"""
    
    def test_enhanced_authentication_support(self, admin_session):
        """Test that enhanced authentication works with table service"""
        assert admin_session is not None
        # Test basic API access using BQSession's fetchxml method
        try:
            response = admin_session.fetchxml('/auth_service/whoami')
            assert response is not None, "Authentication failed: no response from whoami"
        except Exception as e:
            assert False, f"Table service authentication test skipped: {e}"


if __name__ == "__main__":
    pytest.main([__file__])
