import pytest

from collections import OrderedDict, namedtuple
import os
from lxml import etree
import urllib
from datetime import datetime
import time

from bqapi import BQSession

TEST_PATH = 'tests_%s'%urllib.quote(datetime.now().strftime('%Y%m%d%H%M%S%f'))  #set a test dir on the system so not too many repeats occur

# default mark is function.. may be overridden
pytestmark = pytest.mark.functional

#############################
###   BQServer
#############################
@pytest.mark.unit
def test_prepare_url_1(server):
    """
    """
    check_url = 'http://bisque.ece.ucsb.edu/image/00-123456789?remap=gray&format=tiff'
    url = 'http://bisque.ece.ucsb.edu/image/00-123456789'
    odict = OrderedDict([('remap','gray'),('format','tiff')])
    url = server.prepare_url(url, odict=odict)
    assert url == check_url

@pytest.mark.unit
def test_prepare_url_2(server):
    """
    """
    check_url = 'http://bisque.ece.ucsb.edu/image/00-123456789?remap=gray&format=tiff'
    url = 'http://bisque.ece.ucsb.edu/image/00-123456789'
    url = server.prepare_url(url, remap='gray', format='tiff')
    assert url == check_url

@pytest.mark.unit
def test_prepare_url_3(server):
    """
    """
    check_url = 'http://bisque.ece.ucsb.edu/image/00-123456789?format=tiff&remap=gray'
    url = 'http://bisque.ece.ucsb.edu/image/00-123456789'
    odict = OrderedDict([('remap','gray')])
    url = server.prepare_url(url, odict=odict, format='tiff')
    assert url == check_url



#Test BQSession
def test_open_session(config):
    """
        Test Initalizing a BQSession locally
    """
    host = config.get ('host.root')
    user = config.get ('host.user')
    pwd = config.get ('host.password')

    bqsession = BQSession().init_local(user, pwd, bisque_root=host, create_mex=False)
    bqsession.close()


def test_initalize_mex_locally(config):
    """
        Test initalizing a mex locally
    """
    host = config.get ('host.root')
    user = config.get ('host.user')
    pwd = config.get ('host.password')
    bqsession = BQSession().init_local(user, pwd, bisque_root=host, create_mex=True)
    assert bqsession.mex.uri
    bqsession.close()


def test_initalize_session_From_mex(config):
    """
        Test initalizing a session from a mex
    """
    host = config.get ('host.root')
    user = config.get ('host.user')
    pwd = config.get ('host.password')
    bqsession = BQSession().init_local(user, pwd, bisque_root=host)
    mex_url = bqsession.mex.uri
    token = bqsession.mex.resource_uniq
    bqmex = BQSession().init_mex(mex_url, token, user, bisque_root=host)
    bqmex.close()
    bqsession.close()


def test_fetchxml_1(session):
    """
        Test fetch xml
    """
    user = session.config.get ('host.user')
    #bqsession = BQSession().init_local(user, pwd, bisque_root=root)
    response_xml = session.fetchxml('/data_service/'+user) #fetches the user
    session.close()
    if not isinstance(response_xml, etree._Element):
        assert False , 'Did not return XML!'

def test_fetchxml_2(session, stores):
    """
        Test fetch xml and save the document to disk
    """
    user = session.config.get ('host.user')
    filename = 'fetchxml_test_2.xml'
    path = os.path.join(stores.results,filename)
    path = session.fetchxml('/data_service/'+user, path=path) #fetches the user

    try:
        with open(path,'r') as f:
            etree.XML(f.read()) #check if xml was returned

    except etree.Error:
        assert False , 'Did not return XML!'


def test_postxml_1(session):
    """
        Test post xml
    """

    test_document ="""
    <file name="test_document">
        <tag name="my_tag" value="test"/>
    </file>
    """
    response_xml = session.postxml('/data_service/file', xml=test_document)
    if not isinstance(response_xml, etree._Element):
        assert False ,'Did not return XML!'


def test_postxml_2(session, stores):
    """
        Test post xml and save the document to disk
    """

    test_document ="""
    <file name="test_document">
        <tag name="my_tag" value="test"/>
    </file>
    """
    filename = 'postxml_test_2.xml'
    path = os.path.join(stores.results,filename)

    path = session.postxml('/data_service/file', test_document, path=path)

    try:
        with open(path,'r') as f:
            etree.XML(f.read()) #check if xml was returned

    except etree.Error:
        assert False ,'Did not return XML!'


def test_postxml_3(session):
    """
        Test post xml and read immediately
    """

    test_document ="""
    <file name="test_document">
        <tag name="my_tag" value="test"/>
    </file>
    """
    response0_xml = session.postxml('/data_service/file', xml=test_document)
    uri0 = response0_xml.get ('uri')
    response1_xml = session.fetchxml(uri0)
    uri1 = response0_xml.get ('uri')
    session.deletexml (url = uri0)
    if not isinstance(response0_xml, etree._Element):
        assert False , 'Did not return XML!'

    assert uri0 == uri1, "Posted and Fetched uri do not match"




def test_fetchblob_1():
    """

    """
    pass


def test_postblob_1(session, stores):
    """ Test post blob """
    resource = etree.Element ('resource', name=u'%s/%s'%(TEST_PATH, stores.files[0].name))
    content = session.postblob(stores.files[0].location, xml=resource)
    assert len(content), "No content returned"


def test_postblob_2(session, stores):
    """ Test post blob and save the returned document to disk """
    filename = 'postblob_test_2.xml'
    path = os.path.join(stores.results,filename)
    resource = etree.Element ('resource', name=u'%s/%s'%(TEST_PATH, stores.files[0].name))
    path = session.postblob(stores.files[0].location, xml=resource, path=path)

    try:
        with open(path,'r') as f:
            etree.XML(f.read()) #check if xml was returned

    except etree.Error:
        assert False , 'Did not return XML!'

def test_postblob_3(session, stores):
    """
        Test post blob with xml attached
    """

    test_document = """
    <image name="%s">
        <tag name="my_tag" value="test"/>
    </image>
    """%u'%s/%s'%(TEST_PATH, stores.files[0].name)
    content = session.postblob(stores.files[0].location, xml=test_document)


def test_run_mex(mexsession):
    """
        Test run mex
    """
    session = mexsession
    mex_uri = session.mex.uri
    session.update_mex(status="IN PROGRESS", tags = [], gobjects = [], children=[], reload=False)
    response_xml = session.fetchxml(mex_uri) #check xml
    session.finish_mex()

    response_xml = session.fetchxml(mex_uri) #check xml
    assert mex_uri == response_xml.get ('uri')
