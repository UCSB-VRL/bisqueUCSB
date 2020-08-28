import pytest
import os
import numpy as np
#import urllib
from six.moves import urllib
from datetime import datetime



from bqapi import BQSession, BQServer
from bqapi.util import  fetch_dataset
from bq.util.mkdir import _mkdir
from .util import fetch_file
from bqapi.comm import BQCommError
from bqapi.util import *
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

TEST_PATH = 'tests_%s'%urllib.parse.quote(datetime.now().strftime('%Y%m%d%H%M%S%f'))  #set a test dir on the system so not too many repeats occur

pytestmark = pytest.mark.skip("Unported tests")


@pytest.fixture(scope='module')
def image_uri(session, stores):
    """
        uploads an image
    """
    resource = etree.Element ('resource', name=u'%s/%s'%(TEST_PATH, stores.files[0].name))
    content = bqsession.postblob(store.files[0].location, xml=resource)
    return etree.XML(content)[0].attrib['uri']


def setup_fetchimageplanes():
    """
        uploads an image
    """
    global image_uri
    resource = etree.Element ('resource', name=u'%s/%s'%(TEST_PATH, filename1))
    content = bqsession.postblob(stores.files[0].location, xml=resource)
    image_uri = etree.XML(content)[0].attrib['uri']


def teardown_fetchimageplanes():
    pass



def setup_fetchimagepixels():
    """
        uploads an image
    """
    global image_uri
    resource = etree.Element('resource', name=u'%s/%s'%(TEST_PATH, filename1))
    content = bqsession.postblob(stores.files[0].location, xml=resource)
    image_uri = etree.XML(content)[0].attrib['uri']

def teardown_fetchimagepixels():
    pass


def setup_fetchdataset():
    """
        uploads an dataset
    """
    global dataset_uri
    dataset = etree.Element('dataset', name='test')
    for _ in xrange(4):
        resource = etree.Element('resource', name=u'%s/%s'%(TEST_PATH, filename1))
        content = bqsession.postblob(stores.files[0].location, xml=resource)
        value=etree.SubElement(dataset,'value', type="object")
        value.text = etree.XML(content)[0].attrib['uri']
    content = bqsession.postxml('/data_service/dataset', dataset)
    dataset_uri = content.attrib['uri']

def teardown_fetchdataset():
    pass



def setup_fetchDataset():
    """
        uploads an dataset
    """
    global dataset_uri
    dataset = etree.Element('dataset', name='test')
    for _ in xrange(4):
        resource = etree.Element ('resource', name=u'%s/%s'%(TEST_PATH, filename1))
        content = bqsession.postblob(stores.files[0].location, xml=resource)
        value=etree.SubElement(dataset,'value', type="object")
        value.text = etree.XML(content)[0].attrib['uri']
    content = bqsession.postxml('/data_service/dataset', dataset)
    dataset_uri = content.attrib['uri']


def teardown_fetchDataset():
    pass



def setup_saveimagepixels():
    """
        uploads an image
    """
    global image_uri
    resource = etree.Element('resource', name=u'%s/%s'%(TEST_PATH, filename1))
    content = bqsession.postblob(stores.files[0].location, xml=resource)
    image_uri = etree.XML(content)[0].attrib['uri']


def teardown_saveimagepixels():
    pass


def setup_fetchImage():
    """
        uploads an image
    """
    global image_uri
    resource = etree.Element ('resource', name=u'%s/%s'%(TEST_PATH, filename1))
    content = bqsession.postblob(stores.files[0].location, xml=resource)
    image_uri = etree.XML(content)[0].attrib['uri']


def teardown_fetchImage():
    pass



###################################################




def test_saveblob_1(session,stores):
    """
        Saves an image to the blob service
    """
    try:
        result = save_blob(bqsession, localfile=stores.files[0].location)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status
    if result is None:
        assert False, 'XML Parsing error'


def test_saveblob_2(session,stores):
    """
        Save an image to the blob service with xml tags
    """

    try:
        result = save_blob(bqsession, localfile=stores.files[0].location)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status
    if result is None:
        assert False, 'XML Parsing error'





def test_fetchblob_1(session, stores, image_uri):
    """
        fetch blob and return path
    """
    try:
        result = fetch_blob(bqsession, image_uri, dest=stores.results)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status



def test_fetchblob_2(session, image_uri):
    """
        fetch blob and return local path
    """
    try:
        result = fetch_blob(bqsession, image_uri, uselocalpath=True)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status




#@with_setup(setup_fetchimageplanes, teardown_fetchimageplanes)
def test_fetchimageplanes_1():
    """
        fetch image planes and return path
    """
    try:
        result = fetch_image_planes(bqsession, image_uri, results_location, uselocalpath=False)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status


#@with_setup(setup_fetchimageplanes, teardown_fetchimageplanes)
def test_fetchimageplanes_2():
    """
        Fetch image planes and return path. Routine is run on same host as server.
    """
    try:
        result = fetch_image_planes(bqsession, image_uri, results_location,uselocalpath=True)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status



#@with_setup(setup_fetchimagepixels, teardown_fetchimagepixels)
def test_fetchimagepixels_1():
    """
        fetch image planes and return path
    """
    try:
        result = fetch_image_pixels(bqsession, image_uri, results_location,uselocalpath=True)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status

#@with_setup(setup_fetchimagepixels, teardown_fetchimagepixels)
def test_fetchimagepixels_2():
    """
        fetch image planes and return path. Routine is run on same host as server.
    """
    try:
        result = fetch_image_pixels(bqsession, image_uri, results_location,uselocalpath=True)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status


#@with_setup(setup_fetchdataset, teardown_fetchdataset)
def test_fetchdataset():
    """
        fetch dataset images
    """
    try:
        result = fetch_dataset(bqsession, dataset_uri, results_location)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status


#@with_setup(setup_fetchImage, teardown_fetchImage)
def test_fetchImage_1():
    """
        fetch Image
    """
    try:
        result = fetchImage(bqsession, image_uri, results_location)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status


#@with_setup(setup_fetchImage, teardown_fetchImage)
def test_fetchImage_2():
    """
        fetch Image with localpath
    """
    try:
        result = fetchImage(bqsession, image_uri, results_location, uselocalpath=True)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status



#@with_setup(setup_fetchDataset, teardown_fetchDataset)
def test_fetchDataset():
    """
        fetch Dataset images
    """
    try:
        result = fetchDataset(bqsession, dataset_uri, results_location)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status



#@with_setup(setup_saveimagepixels, teardown_saveimagepixels)
def test_saveimagepixels():
    """
        Test save image pixels
    """
    #doesnt work without name on image
    xmldoc = """
    <image name="%s">
        <tag name="my_tag" value="test"/>
    </image>
    """%u'%s/%s'%(TEST_PATH, filename1)
    #bqimage = fromXml(etree.XML(xmldoc))
    bqimage = bqsession.factory.from_string (xmldoc)
    try:
        result = save_image_pixels(bqsession, stores.files[0].location, image_tags=bqimage)
    except BQCommError, e:
        assert False, 'BQCommError: Status: %s'%e.status
