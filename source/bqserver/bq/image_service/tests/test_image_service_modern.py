#!/usr/bin/python

"""
Modernized Image service testing framework for pytest
Converted from legacy unittest framework to pytest
"""

import configparser
import logging
import os
import urllib.parse
from datetime import datetime
from pathlib import Path
from subprocess import PIPE, Popen

import pytest
from bqapi import BQCommError, BQSession
from bqapi.util import save_blob
from lxml import etree

from bq.util.mkdir import _mkdir

IMGCNV = "imgcnv"
REPO_ROOT = Path(__file__).resolve().parents[5]
test_artifacts_root = Path(
    os.environ.get("BISQUE_TEST_ARTIFACTS_DIR", REPO_ROOT / ".bisque" / "test-artifacts")
)
test_artifacts = test_artifacts_root / "image-service"
local_store_tests = test_artifacts / "results"
image_fixture_dir = Path(
    os.environ.get(
        "BISQUE_TEST_IMAGE_FIXTURES_DIR",
        REPO_ROOT / "source" / "bqserver" / "bq" / "image_service" / "tests" / "fixtures",
    )
)
fallback_image_fixture_dirs = [
    image_fixture_dir,
    REPO_ROOT / "source" / "bqapi" / "bqapi" / "tests" / "fixtures",
]

service_data = "data_service"
service_image = "image_service"
resource_image = "image"

TEST_PATH = "tests_%s" % urllib.parse.quote(datetime.now().strftime("%Y%m%d%H%M%S%f"))

# Test image files
image_rgb_uint8 = "flowers_24bit_nointr.png"
image_zstack_uint16 = "161pkcvampz1Live2-17-2004_11-57-21_AM.tif"

pytestmark = [pytest.mark.unit, pytest.mark.server, pytest.mark.converter]

###############################################################
# Helper functions and classes
###############################################################


def print_failed(s, f="-"):
    print("FAILED %s" % (s))


class InfoComparator(object):
    """Compares two info dictionaries"""

    def compare(self, iv, tv):
        return False

    def fail(self, k, iv, tv):
        print_failed("%s failed comparison [%s] [%s]" % (k, iv, tv))
        pass


class InfoEquality(InfoComparator):
    def compare(self, iv, tv):
        return iv.lower() == tv.lower()

    def fail(self, k, iv, tv):
        print_failed("%s failed comparison %s = %s" % (k, iv, tv))
        pass


class InfoNumericLessEqual(InfoComparator):
    def compare(self, iv, tv):
        return int(iv) <= int(tv)

    def fail(self, k, iv, tv):
        print_failed("%s failed comparison %s <= %s" % (k, iv, tv))
        pass


def compare_info(meta_req, meta_test, cc=InfoEquality()):
    if meta_req is None:
        return False
    if meta_test is None:
        return False
    for tk in meta_req:
        if tk not in meta_test:
            return False
        if not cc.compare(meta_req[tk], meta_test[tk]):
            cc.fail(tk, meta_req[tk], meta_test[tk])
            return False
    return True


def compare_xml(meta_req, meta_test, cc=InfoEquality()):
    for t in meta_req:
        req_xpath = t["xpath"]
        req_attr = t["attr"]
        req_val = t["val"]
        l = meta_test.xpath(req_xpath)
        if len(l) < 1:
            print_failed("xpath did not return any results")
            return False
        e = l[0]
        if req_val is None:
            return e.get(req_attr, None) is not None
        v = e.get(req_attr)
        if not cc.compare(req_val, v):
            cc.fail("%s attr %s" % (req_xpath, req_attr), req_val, v)
            return False
    return True


def parse_imgcnv_info(s):
    d = {}
    for l in s.splitlines():
        k = l.split(": ", 1)
        if len(k) > 1:
            d[k[0]] = k[1]
    return d


def metadata_read(filename):
    command = [IMGCNV, "-i", filename, "-meta"]
    try:
        r = Popen(command, stdout=PIPE).communicate()[0]
        if r is None or b"Input format is not supported" in r:
            return None
        return parse_imgcnv_info(r.decode("utf-8"))
    except Exception:
        return None


###############################################################
# Pytest fixtures
###############################################################


@pytest.fixture(scope="session")
def image_session():
    """Image service session with enhanced authentication"""
    # Try to read config, fallback to defaults
    config = configparser.ConfigParser()
    try:
        config.read("config.cfg")
        root = config.get("Host", "root", fallback="http://localhost:8080")
        user = config.get("Host", "user", fallback="admin")
        pswd = config.get("Host", "password", fallback="admin")
    except Exception:
        # Use enhanced authentication defaults
        root = "http://localhost:8080"
        user = "admin"
        pswd = "admin"

    session = BQSession()
    session.init_local(user, pswd, bisque_root=root, create_mex=False)
    return session


@pytest.fixture(scope="session")
def uploaded_resources(image_session):
    """Track uploaded image resources and remove them after the suite."""
    uris = []
    yield uris

    for uri in reversed(uris):
        try:
            image_session.deletexml(uri)
        except Exception as e:
            print(f"Warning: Could not delete uploaded image resource {uri}: {e}")


@pytest.fixture(scope="session", autouse=True)
def setup_directories():
    """Setup test directories"""
    _mkdir(str(local_store_tests))
    yield
    # Cleanup after tests
    print("Cleaning-up %s" % local_store_tests)
    try:
        for root, dirs, files in os.walk(local_store_tests, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
    except Exception as e:
        print(f"Warning: Could not clean up test directory: {e}")


@pytest.fixture(scope="session")
def test_image_2d(image_session, uploaded_resources):
    """Download and upload 2D test image"""
    return fetch_and_upload_image(image_session, image_rgb_uint8, uploaded_resources)


@pytest.fixture(scope="session")
def test_image_3d(image_session, uploaded_resources):
    """Download and upload 3D test image"""
    return fetch_and_upload_image(image_session, image_zstack_uint16, uploaded_resources)


def find_test_image(filename):
    for fixture_dir in fallback_image_fixture_dirs:
        path = fixture_dir.expanduser() / filename
        if path.exists():
            return path

    searched = ", ".join(str(path.expanduser()) for path in fallback_image_fixture_dirs)
    pytest.fail(f"Missing test image fixture {filename}. Searched: {searched}")


def fetch_and_upload_image(session, filename, uploaded_resources):
    """Helper to fetch and upload test images"""
    try:
        path = find_test_image(filename)

        # Upload to BisQue
        filename_resource = "%s/%s" % (TEST_PATH, filename)
        resource = etree.Element("resource", name=filename_resource)
        r = save_blob(session, str(path), resource=resource)

        if r is None or r.get("uri") is None:
            pytest.fail("Upload did not return a resource URI for %s" % path)

        uploaded_resources.append(r.get("uri"))

        print("Uploaded id: %s url: %s" % (r.get("resource_uniq"), r.get("uri")))
        return r

    except Exception as e:
        pytest.fail(f"Could not fetch/upload image {filename}: {e}")


def require_resource(resource, label):
    if resource is None:
        pytest.skip(f"{label} resource is not available")
    return resource


###############################################################
# Test helper functions
###############################################################


def validate_image_variant(session, resource, filename, commands, meta_required=None):
    """Validate image operations and metadata"""
    resource = require_resource(resource, "Image")

    path = os.path.join(local_store_tests, filename)
    try:
        image = session.factory.from_etree(resource)
        px = image.pixels()
        for c, a in commands:
            px = px.command(c, a)
        px.fetch(path)
    except BQCommError:
        logging.exception("Comm error")
        pytest.fail("Communication error while fetching image")

    if meta_required is not None:
        meta_test = metadata_read(path)
        assert meta_test is not None, "Retrieved image can not be read"
        assert compare_info(meta_required, meta_test), (
            "Retrieved metadata differs from test template"
        )


def validate_xml(session, resource, filename, commands, xml_parts_required):
    """Validate XML operations"""
    resource = require_resource(resource, "Image")

    path = os.path.join(local_store_tests, filename)
    try:
        image = session.factory.from_etree(resource)
        px = image.pixels()
        for c, a in commands:
            px = px.command(c, a)
        px.fetch(path)
    except BQCommError:
        pytest.fail("Communication error")

    xml_test = etree.parse(path).getroot()
    assert compare_xml(xml_parts_required, xml_test), "Retrieved XML differs from test template"


###############################################################
# Modern pytest test classes
###############################################################


class TestImageServiceBasic:
    """Basic image service tests"""

    def test_image_service_available(self, image_session):
        """Test that image service is available"""
        try:
            # Test basic service availability
            response = image_session.fetchxml("/" + service_image)
            assert response is not None
        except Exception as e:
            assert False, f"Image service not available: {e}"

    def test_enhanced_authentication(self, image_session):
        """Test enhanced authentication works with image service"""
        try:
            whoami = image_session.fetchxml("/auth_service/whoami")
            assert whoami is not None
        except Exception as e:
            # Authentication should work with proper setup
            assert False, f"Authentication test failed: {e}"


class TestImageOperations:
    """Test image processing operations"""

    def test_thumbnail_2d_3c_uint8(self, image_session, test_image_2d):
        """Test thumbnail generation for 2D RGB image"""
        test_image_2d = require_resource(test_image_2d, "2D test image")

        filename = "im_2d_uint8.thumbnail.jpg"
        commands = [("thumbnail", None)]
        meta_required = {
            "image_num_x": "128",
            "image_num_y": "96",  # Aspect ratio preserved: 1024x768 -> 128x96
            "image_num_c": "3",
            "image_pixel_format": "unsigned integer",
            "image_pixel_depth": "8",
        }
        validate_image_variant(image_session, test_image_2d, filename, commands, meta_required)

    def test_resize_2d_3c_uint8(self, image_session, test_image_2d):
        """Test resize operation for 2D RGB image"""
        test_image_2d = require_resource(test_image_2d, "2D test image")

        filename = "im_2d_uint8.resize.jpg"
        commands = [("resize", "256,256")]
        meta_required = {
            "image_num_x": "256",
            "image_num_y": "256",
            "image_num_c": "3",
            "image_pixel_format": "unsigned integer",
            "image_pixel_depth": "8",
        }
        validate_image_variant(image_session, test_image_2d, filename, commands, meta_required)

    @pytest.mark.skipif(
        not os.path.exists("imgcnv") and not os.system("which imgcnv") == 0,
        reason="imgcnv tool not available",
    )
    def test_negative_2d_3c_uint8(self, image_session, test_image_2d):
        """Test negative operation for 2D RGB image"""
        test_image_2d = require_resource(test_image_2d, "2D test image")

        filename = "im_2d_uint8.negative.jpg"
        commands = [("negative", None)]
        meta_required = {
            "image_num_c": "3",
            "image_pixel_format": "unsigned integer",
            "image_pixel_depth": "8",
        }
        validate_image_variant(image_session, test_image_2d, filename, commands, meta_required)

    def test_roi_2d_3c_uint8(self, image_session, test_image_2d):
        """Test ROI operation for 2D RGB image"""
        test_image_2d = require_resource(test_image_2d, "2D test image")

        filename = "im_2d_uint8.roi.tif"
        commands = [("roi", "1,1,100,100")]
        meta_required = {
            "format": "BigTIFF",
            "image_num_x": "100",
            "image_num_y": "100",
            "image_num_c": "3",
            "image_num_z": "1",
            "image_num_t": "1",
            "image_pixel_format": "unsigned integer",
            "image_pixel_depth": "8",
        }
        validate_image_variant(image_session, test_image_2d, filename, commands, meta_required)


class TestImageMetadata:
    """Test image metadata operations"""

    def test_localpath_3d_2c_uint16(self, image_session, test_image_3d):
        """Test localpath metadata for 3D image"""
        test_image_3d = require_resource(test_image_3d, "3D test image")

        filename = "im_3d_uint16.localpath.xml"
        commands = [("localpath", None)]
        meta_required = [
            {
                "xpath": "//resource",
                "attr": "value",
                "val": None,
            },  # simply test if attribute is present
            {"xpath": "//resource", "attr": "type", "val": "file"},
        ]
        validate_xml(image_session, test_image_3d, filename, commands, meta_required)

    def test_histogram_3d_2c_uint16(self, image_session, test_image_3d):
        """Test histogram generation for 3D image"""
        test_image_3d = require_resource(test_image_3d, "3D test image")

        filename = "im_3d_uint16.histogram.xml"
        commands = [("histogram", None)]
        # Note: Specific histogram values may vary based on actual image content
        # This test mainly checks that histogram XML is generated correctly
        meta_required = [
            {
                "xpath": '//histogram[@value="0"]/tag[@name="data_bits_per_pixel"]',
                "attr": "value",
                "val": "16",
            },
            {
                "xpath": '//histogram[@value="1"]/tag[@name="data_bits_per_pixel"]',
                "attr": "value",
                "val": "16",
            },
        ]
        validate_xml(image_session, test_image_3d, filename, commands, meta_required)


class TestImageServiceIntegration:
    """Integration tests for image service with other BisQue services"""

    def test_upload_png_creates_fetchable_image(self, image_session, test_image_2d):
        """Test that PNG upload creates a fetchable image resource."""
        test_image_2d = require_resource(test_image_2d, "2D test image")

        image_uri = test_image_2d.get("uri")
        resource_uniq = test_image_2d.get("resource_uniq")

        assert image_uri, "Uploaded image did not include a resource URI"
        assert resource_uniq, "Uploaded image did not include a resource_uniq"

        fetched = image_session.fetchxml(image_uri)
        assert fetched is not None
        assert fetched.tag == "image"
        assert fetched.get("uri") == image_uri

    def test_image_to_data_service_integration(self, image_session, test_image_2d):
        """Test integration between image service and data service"""
        test_image_2d = require_resource(test_image_2d, "2D test image")

        try:
            # Verify the uploaded image is accessible via data service
            image_uri = test_image_2d.get("uri")
            assert image_uri is not None

            # Fetch via data service
            data_response = image_session.fetchxml(image_uri)
            assert data_response is not None
            assert data_response.tag == "image"

        except Exception as e:
            assert False, f"Integration test failed: {e}"

    @pytest.mark.skip(
        reason="Authentication test not part of original test suite - user permission issues"
    )
    def test_enhanced_auth_image_access(self, test_image_2d):
        """Test that enhanced authentication ('admin', 'admin') can access images"""
        try:
            # Create user session with enhanced auth
            user_session = BQSession()
            user_session.init_local(
                "admin", "admin", bisque_root="http://localhost:8080", create_mex=False
            )

            test_image_2d = require_resource(test_image_2d, "2D test image")

            # Test user can access the image
            image_uri = test_image_2d.get("uri")
            user_response = user_session.fetchxml(image_uri)
            assert user_response is not None

        except Exception as e:
            assert False, f"Enhanced auth image access test failed: {e}"


# Example of how to run specific tests
if __name__ == "__main__":
    # This allows running the file directly with pytest
    pytest.main([__file__, "-v"])
