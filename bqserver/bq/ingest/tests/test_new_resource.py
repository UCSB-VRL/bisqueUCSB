import sys
import os
import StringIO
import re
import transaction

from lxml import etree as ET
from StringIO import StringIO
from nose import with_setup
from nose.tools import assert_true, assert_equal, assert_false
from bq.core.tests import TestController


INGEST="/ingest_service/"
BLOB="/blob_service/"




xml1="""
<blobs>
<blob blob_uri="/blob_service/00_3071fc2542e3df3d12f1f6ae2d4f9928_1" content_hash="3071fc2542e3df3d12f1f6ae2d4f9928" original_uri="https://aid_test.s3.amazonaws.com/5298377633_84dba73cb8_o.jpg"/>
</blobs>
"""



# <blobs><blob blob_uri="http://localhost:8080/blob_service/00_3071fc2542e3df3d12f1f6ae2d4f9928_1" content_hash="3071fc2542e3df3d12f1f6ae2d4f9928" original_uri="https://aid_test.s3.amazonaws.com/5298377633_84dba73cb8_o.jpg" /></blobs>

# <resource uri="http://localhost/data_service/images"><image src="http://localhost:8080//image_service/5" ch="3" uri="http://localhost:8080//data_service/images/2" perm="1" ts="2011-06-03 16:55:57.367421" owner="http://localhost:8080//data_service/users/1" t="1" y="2448" x="3264" z="1" type="images"/></resource>


class TestIngest(TestController):
    application_under_test = 'main'
    def login (self):
        resp = self.app.get('/auth_service/login', status=200)
        form = resp.form
        # Submitting the login form:
        form['login'] = u'admin'
        form['password'] = 'admin'
        post_login = form.submit(status=302)

    def test_a1_new(self):
        'check ingest index'
        response = self.app.get(INGEST) #extra_environ = environ)
        assert response.status == '200 OK'
        assert 'Hello' in response.body

    def test_a2_new(self):
        "new --> new blob"
        self.login()
        ty, body = self.app.encode_multipart(params=[('https://aid_test.s3.amazonaws.com/5298377633_84dba73cb8_o.jpg 3071fc2542e3df3d12f1f6ae2d4f9928', '')], files = [])
        response = self.app.post (BLOB, params = body, content_type=ty) #extra_environ = environ)
        assert response.status == '200 OK'
        print response.body
        #blob_id = response.lxml

        response = self.app.get('/data_service/images')
        assert response.status_int == 200
        print response.body
        assert False
        
        #assert False

        

