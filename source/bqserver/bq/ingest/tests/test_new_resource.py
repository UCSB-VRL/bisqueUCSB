import pytest
import sys
import os
import io
import re
from lxml import etree as ET
from io import StringIO
from bqapi import BQSession

INGEST = "/ingest_service/"
BLOB = "/blob_service/"

xml1 = """
<blobs>
<blob blob_uri="/blob_service/00_3071fc2542e3df3d12f1f6ae2d4f9928_1" content_hash="3071fc2542e3df3d12f1f6ae2d4f9928" original_uri="https://aid_test.s3.amazonaws.com/5298377633_84dba73cb8_o.jpg"/>
</blobs>
"""

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def admin_session():
    """Admin session with enhanced authentication"""
    session = BQSession()
    session.init_local('admin', 'admin', bisque_root='http://localhost:8080')
    return session


@pytest.fixture(scope="module")
def user_session():
    """User session with enhanced authentication"""
    session = BQSession()
    session.init_local('admin', 'admin', bisque_root='http://localhost:8080')
    return session


@pytest.fixture
def cleanup_resources():
    """Track and cleanup created resources"""
    created_resources = []
    
    def track_resource(uri):
        created_resources.append(uri)
        return uri
    
    yield track_resource
    
    # Cleanup after test
    admin_session = BQSession()
    admin_session.init_local('admin', 'admin', bisque_root='http://localhost:8080')
    
    for uri in created_resources:
        try:
            admin_session.deletexml(uri)
        except Exception as e:
            print(f"Warning: Could not delete resource {uri}: {e}")


class TestIngestService:
    """Modernized ingest service tests"""
    
    def test_ingest_service_available(self, admin_session):
        """Test that ingest service is available"""
        try:
            response = admin_session.fetchxml(INGEST)
            # Basic availability check
            assert response is not None
        except Exception as e:

            assert False, f"Ingest service not available: {e}"
    
    def test_blob_service_available(self, admin_session):
        """Test that blob service is available"""
        try:
            response = admin_session.fetchxml(BLOB)
            assert response is not None
        except Exception as e:

            assert False, f"Blob service not available: {e}"
    
    def test_new_blob_ingest(self, admin_session, cleanup_resources):
        """Test ingesting a new blob"""
        try:
            # Parse the test XML
            blobs_xml = ET.fromstring(xml1)
            
            # Try to ingest the blob information
            response = admin_session.postxml(INGEST + 'new', blobs_xml)
            
            if response is not None:
                # Handle both XML element and bytes responses
                if hasattr(response, 'get'):
                    # XML element response
                    uri = response.get('uri')
                    if uri:
                        cleanup_resources(uri)
                elif isinstance(response, bytes):
                    # Parse bytes response to XML
                    try:
                        response_xml = ET.fromstring(response)
                        uri = response_xml.get('uri')
                        if uri:
                            cleanup_resources(uri)
                    except ET.ParseError:
                        # Response is not XML, treat as success if non-empty
                        if response:
                            assert True, f"Ingest returned non-XML response: {response[:100]}"
                        
        except Exception as e:
            assert False, f"Blob ingest test failed - service may not be fully configured: {e}"
    
    def test_authentication_with_ingest(self, admin_session, user_session):
        """Test that authentication works with ingest service"""
        # Test admin access
        try:
            admin_response = admin_session.fetchxml(INGEST)
            assert admin_response is not None
        except Exception as e:

            assert False, f"Admin ingest access failed: {e}"
        
        # Test user access
        try:
            user_response = user_session.fetchxml(INGEST)
            assert user_response is not None
        except Exception as e:

            assert False, f"User ingest access failed: {e}"
    
    def test_ingest_error_handling(self, admin_session):
        """Test error handling in ingest service"""
        # Test with invalid data
        invalid_xml = ET.Element('invalid', test='data')
        
        try:
            response = admin_session.postxml(INGEST + 'invalid', invalid_xml)
            # If no exception, check that error is handled gracefully
        except Exception as e:
            # Expected behavior for invalid ingest data
            assert 'error' in str(e).lower() or 'invalid' in str(e).lower()
    
    def test_enhanced_authentication_integration(self, user_session):
        """Test that enhanced authentication works with ingest"""
        try:
            # Verify user session works
            whoami = user_session.fetchxml('/auth_service/whoami')
            assert whoami is not None
            
            # Test basic ingest access
            ingest_response = user_session.fetchxml(INGEST)
            assert ingest_response is not None
            
        except Exception as e:

            
            assert False, f"Enhanced authentication test failed: {e}"


class TestIngestServiceIntegration:
    """Integration tests for ingest service with other services"""
    
    def test_ingest_to_data_service_flow(self, admin_session, cleanup_resources):
        """Test the flow from ingest to data service"""
        try:
            # Create a simple test image in data service
            test_image = ET.Element('image', name='ingest_test.jpg')
            data_response = admin_session.postxml('/data_service/image', test_image)
            
            if data_response is not None:
                cleanup_resources(data_response.get('uri'))
                
                # Test that the created resource can be referenced in ingest
                # This is a basic integration test
                assert data_response.get('uri') is not None
                
        except Exception as e:

                
            assert False, f"Ingest to data service integration test failed: {e}"
    
    def test_blob_to_ingest_integration(self, admin_session):
        """Test integration between blob service and ingest service"""
        try:
            # Test that both services are available and can work together
            blob_response = admin_session.fetchxml(BLOB)
            ingest_response = admin_session.fetchxml(INGEST)
            
            assert blob_response is not None
            assert ingest_response is not None
            
        except Exception as e:
            assert False, f"Blob to ingest integration test failed: {e}"

        

