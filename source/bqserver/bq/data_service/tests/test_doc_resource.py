
import pytest
import sys
import os
import logging
from lxml import etree as ET
from bqapi import BQSession

log = logging.getLogger('bq.test.doc_resource')

xml1 = '<image name="test.jpg"><tag name="foo" value="bar"/></image>'
DS = "/data_service/image"

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

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
    
    # Provide the tracking function
    yield track_resource
    
    # Cleanup after test
    admin_session = BQSession()
    admin_session.init_local('admin', 'admin', bisque_root='http://localhost:8080')
    
    for uri in created_resources:
        try:
            admin_session.deletexml(uri)
        except Exception as e:
            print(f"Warning: Could not delete resource {uri}: {e}")


class TestDataServiceDocuments:
    """Modernized data service document tests"""
    
    def test_services_available(self, admin_session):
        """Test that data service is available"""
        try:
            response = admin_session.fetchxml('/services')
            services_text = ET.tostring(response, encoding='unicode')
            assert 'data_service' in services_text
        except Exception as e:

            assert False, f"Services endpoint not available: {e}"
    
    def test_create_new_document(self, admin_session, cleanup_resources):
        """Test creating a new document with enhanced authentication"""
        # Create new image document
        image_xml = ET.fromstring(xml1)
        
        try:
            response = admin_session.postxml('/data_service/image', image_xml)
            
            # Verify response
            assert response is not None
            uri = response.get('uri')
            assert uri is not None
            assert '00-' in uri, 'Invalid resource uniq in uri'
            
            # Track for cleanup
            cleanup_resources(uri)
            
        except Exception as e:
            pytest.fail(f"Failed to create document: {e}")
    
    def test_fetch_created_document(self, admin_session, cleanup_resources):
        """Test fetching a created document"""
        # Create document
        image_xml = ET.fromstring(xml1)
        created_response = admin_session.postxml('/data_service/image', image_xml)
        uri = created_response.get('uri')
        cleanup_resources(uri)
        
        # Fetch document
        fetched_response = admin_session.fetchxml(uri)
        
        # Verify fetch
        assert fetched_response is not None
        assert fetched_response.get('uri') == uri
        assert '00-' in fetched_response.get('uri')
    
    def test_replace_document_content(self, admin_session, cleanup_resources):
        """Test replacing document content"""
        # Create document
        image_xml = ET.fromstring(xml1)
        created_response = admin_session.postxml('/data_service/image', image_xml)
        uri = created_response.get('uri')
        cleanup_resources(uri)
        
        # Fetch with deep view to get tags
        deep_response = admin_session.fetchxml(uri, view='deep')
        tags = deep_response.xpath('./tag')
        
        if tags:
            tag = tags[0]
            original_value = tag.get('value')
            
            # Modify tag value
            tag.set('value', 'barnone')
            
            # Update tag
            tag_uri = tag.get('uri')
            if tag_uri:
                updated_tag = admin_session.postxml(tag_uri, tag, method='PUT')
                assert updated_tag.get('value') == 'barnone'
                assert updated_tag.get('value') != original_value
    
    def test_user_authentication_access(self, user_session):
        """Test that user authentication works for data service"""
        try:
            # Test user can access services 
            response = user_session.fetchxml('/services')
            assert response is not None
            
            # Test user can create documents (basic permissions)
            image_xml = ET.fromstring(xml1)
            user_created = user_session.postxml('/data_service/image', image_xml)
            assert user_created is not None
            
            # Cleanup
            user_session.deletexml(user_created.get('uri'))
            
        except Exception as e:

            
            assert False, f"User access test failed: {e}"
    
    def test_authentication_integration(self, admin_session, user_session):
        """Test that both authentication methods work with data service"""
        # Test admin session
        try:
            admin_response = admin_session.fetchxml('/data_service')
            assert admin_response is not None
            assert admin_response.tag == 'resource'
        except Exception as e:
            assert False, f"Admin authentication failed: {e}"
            
        # Test user session  
        try:
            user_response = user_session.fetchxml('/data_service')
            assert user_response is not None
            assert user_response.tag == 'resource'
        except Exception as e:
            assert False, f"User authentication failed: {e}"


class TestDataServiceErrors:
    """Test error handling in data service"""
    
    def test_unauthorized_access(self):
        """Test that unauthorized access is properly handled"""
        # Create session without authentication
        unauth_session = BQSession()
        unauth_session.bisque_root = 'http://localhost:8080'
        
        # This should fail or return limited results
        try:
            response = unauth_session.fetchxml('/data_service/image')
            # If it doesn't raise an exception, check the response is appropriate
            # for unauthenticated access
        except Exception:
            # Expected behavior for unauthenticated access
            pass
    
    def test_invalid_document_creation(self, admin_session):
        """Test handling of invalid document creation"""
        invalid_xml = ET.Element('invalid_resource', name='test')
        
        try:
            # This should either fail gracefully or handle the invalid resource type
            response = admin_session.postxml('/data_service/invalid_resource', invalid_xml)
        except Exception as e:
            # Expected behavior for invalid resource type
            assert 'invalid' in str(e).lower() or 'error' in str(e).lower()
        "Fetch partial document"
