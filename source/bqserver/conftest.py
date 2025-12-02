"""
Global pytest configuration for bqserver tests
"""
import pytest
import configparser
import os
from bqapi import BQSession

@pytest.fixture(scope="session")
def bisque_config():
    """Load BisQue test configuration"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'test.ini')
    config.read(config_path)
    
    return {
        'root': config.get('test', 'host.root'),
        'test_user': config.get('test', 'host.user'), 
        'test_pass': config.get('test', 'host.password'),
        'host': config.get('server:main', 'host'),
        'port': config.get('server:main', 'port')
    }

@pytest.fixture(scope="session")
def admin_session(bisque_config):
    """Create admin BQSession for tests"""
    session = BQSession().init_local(
        bisque_config['test_user'],
        bisque_config['test_pass'], 
        bisque_root=bisque_config['root'],
        create_mex=False
    )
    return session

@pytest.fixture(scope="session") 
def user_session(bisque_config):
    """Create user BQSession for tests"""
    # For now, use same credentials as admin
    # This can be extended to create actual user accounts
    session = BQSession().init_local(
        bisque_config['test_user'],
        bisque_config['test_pass'],
        bisque_root=bisque_config['root'],
        create_mex=False
    )
    return session

@pytest.fixture
def cleanup_resources():
    """Track resources for cleanup after tests"""
    resources_to_cleanup = []
    
    def track_resource(resource_uri):
        resources_to_cleanup.append(resource_uri)
        
    yield track_resource
    
    # Cleanup logic would go here
    # For now, just clear the list
    resources_to_cleanup.clear()

@pytest.fixture
def xml_parser():
    """XML parser for tests"""
    from lxml import etree
    parser = etree.XMLParser(strip_cdata=False)
    return parser
