
import pytest

import sys
import os
import logging
from lxml import etree as ET
from bq.core.tests import TestController, teardown_db, DBSession

log = logging.getLogger('bq.test.doc_resource')

xml1 = '<image name="test.jpg"><tag name="foo" value="bar"/></image>'
DS = "/data_service/image"


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

pytestmark = pytest.mark.unit


@pytest.mark.usefixtures ('testapp')
class TestDocController():
    app = None
    application_under_test = 'main'

    def test_services(self):
        response = self.app.get ('/services')
        assert 'data_service' in response

    def test_a_new(self):
        "new --> create a new document"
        environ = {'REMOTE_USER': 'admin'}
        response = self.app.post (DS, params=xml1, content_type="text/xml", extra_environ=environ)
        assert response.status == '200 OK'
        assert '00-' in response.lxml.get('uri'), 'Invalid resource uniq in uri'

    def test_b_fetch(self):
        "Fetch a created document"
        environ = {'REMOTE_USER': 'admin'}
        response = self.app.post (DS, params=xml1, content_type="text/xml", extra_environ=environ)
        #print "post-> %s" % response.body
        uri = response.lxml.get('uri')
        response = self.app.get (uri, extra_environ=environ)
        #print ('fetch -> %s' % response.body)
        assert response.status == '200 OK'
        assert '00-' in response.lxml.get('uri')


    def test_c_fetch_replace(self):
        "Replace a document"
        environ = {'REMOTE_USER': 'admin'}
        response = self.app.post (DS, params=xml1, content_type="text/xml", extra_environ=environ)
        uri = response.lxml.get('uri')
        response = self.app.get (uri, params={ 'view' : 'deep' }, extra_environ=environ)
        assert response.status == '200 OK'
        tag = response.lxml.xpath('./tag')[0]
        tag.set('value', 'barnone')
        response = self.app.put (tag.get('uri'), ET.tostring(tag), content_type="text/xml", extra_environ=environ)
        print response.body
        assert 'barnone' == response.lxml.get('value')


    def test_d_fetch_partial(self):
        "Fetch partial document"
