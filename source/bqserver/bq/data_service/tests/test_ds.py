# -*- coding: utf-8 -*-
import pytest

from lxml import etree




# This is an example of how you can write functional tests for your controller.
# As opposed to a pure unit-test which test a small unit of functionallity,
# these functional tests exercise the whole app and it's WSGI stack.
# Please read http://pythonpaste.org/webtest/ for more information

pytestmark = pytest.mark.unit


@pytest.mark.usefixtures ('testapp')
class TestDSController():
    app = None
    def test_a_index(self):
        response = self.app.get('/data_service')
        assert response.status == '200 OK'

        # You can look for specific strings:
        # Fix for Python 3: response.body is bytes, need to decode or check bytes
        if isinstance(response.body, bytes):
            assert b'resource' in response.body
        else:
            assert 'resource' in response.body
        # You can also access a BeautifulSoup'ed version
        # first run $ easy_install BeautifulSoup and then run this test
        #links = response.html.findAll('a')
        #assert_true(links, "Mummy, there are no links here!")



    @pytest.mark.skip(reason="Authentication tests not applicable when skip_authentication=true in test config")
    def test_b_newimage_noauth (self):
        # Test without authentication - temporarily remove basic auth
        old_auth = self.app.authorization
        self.app.authorization = None
        req = etree.Element ('image', name='new', value = "image.jpg" )
        # BisQue redirects unauthenticated requests to login page (302, not 401)
        response = self.app.post ('/data_service/image',
                                  params = etree.tostring(req, encoding='unicode'),
                                  content_type='application/xml',
                                  status = 302,
                                  )
        # Verify it redirects to the login page
        assert 'auth_service/login' in response.location
        # Restore authentication for other tests
        self.app.authorization = old_auth
        
    @pytest.mark.skip(reason="Authentication tests not applicable when skip_authentication=true in test config")
    def test_c_newimage_auth (self):
        # Test with authentication - use the app's configured basic auth
        req = etree.Element ('image', name='new', value="image.jpg" )
        response = self.app.post ('/data_service/image',
                                  params = etree.tostring(req, encoding='unicode'),
                                  headers=[('content-type', 'application/xml')],
                                  )
        # Fix for Python 3: check response.body for bytes compatibility
        if isinstance(response.body, bytes):
            assert b'image' in response.body
        else:
            assert 'image' in response.body
        print(response)
