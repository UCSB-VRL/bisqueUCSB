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
        assert 'resource' in response.body
        # You can also access a BeautifulSoup'ed version
        # first run $ easy_install BeautifulSoup and then run this test
        #links = response.html.findAll('a')
        #assert_true(links, "Mummy, there are no links here!")



    def test_b_newimage_noauth (self):
        environ = {'REMOTE_USER': 'admin'}
        req = etree.Element ('image', name='new', value = "image.jpg" )
        response = self.app.post ('/data_service/image',
                                  params = etree.tostring(req),
                                  content_type='application/xml',
                                  status = 401,
#                                  extra_environ=environ,
                                  )
    def test_c_newimage_auth (self):
        req = etree.Element ('image', name='new', value="image.jpg" )
        environ = {'REMOTE_USER': 'admin'}
        response = self.app.post ('/data_service/image',
                                  params = etree.tostring(req),
                                  headers=[('content-type', 'application/xml')],
                                  extra_environ=environ,
                                  )
        assert 'image' in response
        print response
