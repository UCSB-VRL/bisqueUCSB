#global variables for the test script
import ConfigParser
import os
import ntpath
from lxml import etree
import urllib
import urlparse
import zipfile
from bqapi import BQSession, BQCommError
from bqapi.util import save_blob # local
import posixpath
import sys
from bq.util.mkdir import _mkdir
import glob
from libtiff import TIFF
import numpy as np

from var import *

class TestNameSpace(object):
    """
        A container for variable that need
        to be passed between the setups/teardowns
        and tests themselves
    """
    def __init__(self):
        pass


def image_tiles(bqsession, image_service_url, tile_size=64):
    """
        Breaks an image_service_url into a list of tiled requests of that same
        image.

        @param: bqsession
        @param: image_service_url
        @param: tile_size (default: 64)
    """
    o = urlparse.urlparse(image_service_url)
    query = urlparse.parse_qsl(o.query, keep_blank_values=True)
    meta = [('meta','')]
    meta_query = urllib.urlencode( query + meta)
    meta = bqsession.fetchxml(urlparse.urlunparse([o.scheme, o.netloc, o.path, o.params, meta_query, o.fragment]))
    x = int(meta.xpath('tag[@name="image_num_x"]')[0].attrib[ 'value'])
    y = int(meta.xpath('tag[@name="image_num_y"]')[0].attrib[ 'value'])

    for ix in range(int( x/tile_size)-1):
        for iy in range(int( y/tile_size)-1):
            tile = [( 'tile', '0,%s,%s,%s'%( str(ix), str(iy), str(tile_size)))]
            tile_query = urllib.unquote(urllib.urlencode( query + tile))
            yield urlparse.urlunparse([o.scheme, o.netloc, o.path, o.params, tile_query, o.fragment])


#test initalization
def ensure_bisque_file( bqsession, filename, achieve = False, local_dir='.'):
    """
        Checks for test files stored locally
        If not found fetches the files from a store
    """

    path = fetch_file(filename,local_dir)
    if achieve:
        return upload_achieve_file( bqsession, path)
    else:
        return upload_new_file(bqsession, path)


def check_for_file(filename, zip_filename, local_dir='.'):
    """
        Checks for test files stored locally
        If not found fetches the files from a store
    """

    path = os.path.join(local_dir, filename)

    if not os.path.exists(path):
        fetch_zip(zip_filename, local_dir)
        if not os.path.exists(path):
            raise DownloadError(filename)


def fetch_zip( filename, local_dir='.'):
    """
        Fetches and unpacks a zip file into the same dir
    """

    url = posixpath.join( URL_FILE_STORE, filename)
    path = os.path.join( local_dir, filename)
    if not os.path.exists( local_dir):
        os.makedirs( local_dir)

    if not os.path.exists(path):
        urllib.urlretrieve(url, path)

    Zip = zipfile.ZipFile(path)
    Zip.extractall(local_dir)
    return


def fetch_file(filename, store_location, local_dir='.'):
    """
        fetches files from a store as keeps them locally
    """
    url = posixpath.join(store_location, filename)
    path = os.path.join(local_dir, filename)
    if not os.path.exists(path):
        urllib.urlretrieve(url, path)
    return path


def upload_new_file(bqsession, path):
    """
        uploads files to bisque server
    """
    r = save_blob(bqsession,  path)
    print 'Uploaded id: %s url: %s'%(r.get('resource_uniq'), r.get('uri'))
    return r


def upload_image_resource(bqsession, path, filename):
    """
        uploads image to bisque
    """
    resource = etree.Element ('image', name=filename)
    content = bqsession.postblob(path, xml=resource) #upload image
    content = etree.XML(content)[0] #pull the resource out
    print 'Uploaded id: %s url: %s'%(content.get('resource_uniq'), content.get('uri'))
    return content

#test breakdown
def delete_resource(bqsession, url):
    """
        Remove uploaded resource from bisque server
    """
    print 'Deleting url: %s' % url
    bqsession.deletexml(url)


def cleanup_dir():
    """
        Removes files downloaded into the local store
    """
    print 'Cleaning-up %s'%TEMP_DIR
    for root, dirs, files in os.walk(TEMP_DIR, topdown=False):
        for name in files:
            try:
                os.remove(os.path.join(root, name))
            except Exception:
                pass

#upload functions
def zipfiles(filelist, zipped_filename, root = '.'):
    with zipfile.ZipFile(zipped_filename,'w') as zip:
        for fname in filelist:
            zip.write(fname, os.path.relpath(fname, root))
    return


#setup comm test
def setup_simple_feature_test(ns):
    """
        Setup feature requests test
    """
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    root = config.get('Host', 'root') or DEFAULT_ROOT
    user = config.get('Host', 'user') or DEFAULT_USER
    pwd = config.get('Host', 'password') or DEFAULT_PASSWORD
    results_location = config.get('Store', 'results_dir') or DEFAULT_RESULTS_DIR
    store_location = config.get('Store', 'location') or None
    store_local_location = config.get('Store', 'local_dir') or DEFAULT_LOCAL_DIR
    temp_store = config.get('Store', 'temp_dir') or DEFAULT_TEMPORARY_DIR
    test_image = config.get('SimpleTest', 'test_image') or None
    feature_response_results = config.get('SimpleTest', 'feature_response') or DEFAULT_FEATURE_RESPONSE_HDF5
    feature_past_response_results = config.get('SimpleTest','feature_sample') or DEFAULT_FEATURE_SAMPLE_HDF5

    if store_location is None: raise NameError('Requre a store location to run test properly')
    if test_image is None: raise NameError('Requre an image to run test properly')

    _mkdir(store_local_location)
    _mkdir(results_location)
    _mkdir(temp_store)

    results_table_path = os.path.join(results_location, feature_response_results)
    if os.path.exists(results_table_path):
        os.remove(results_table_path)


    test_image_location = fetch_file(test_image, store_location, store_local_location)

    #initalize session
    session = BQSession().init_local(user, pwd, bisque_root=root)

    #set to namespace
    ns.root = root
    ns.store_location = store_location
    ns.session = session
    ns.results_location = results_location
    ns.store_local_location = store_local_location
    ns.test_image_location = test_image_location
    ns.feature_response_results = feature_response_results
    ns.feature_past_response_results = feature_past_response_results
    ns.test_image = test_image
    ns.temp_store = temp_store


def tear_down_simple_feature_test(ns):
    """ Teardown feature requests test """
    #import shutil
    #shutil.rmtree(ns.temp_store)
    ns.session.close()


def setup_parallel_feature_test(ns):
    """
        Setup feature requests test
    """
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    test_image = config.get('ParallelTest', 'test_image') or None
    threads = config.get('ParallelTest', 'threads') or '4'
    feature_response_results = config.get('ParallelTest', 'feature_response') or DEFAULT_FEATURE_PARALLEL_RESPONSE_HDF5
    feature_past_response_results = config.get('ParallelTest', 'feature_sample') or DEFAULT_FEATURE_PARALLEL_SAMPLE_HDF5


    setup_simple_feature_test(ns)

    results_table_path = os.path.join(ns.results_location, feature_response_results)
    if os.path.exists(results_table_path):
        os.remove(results_table_path)

    if test_image is None: raise NameError('Requre an image to run test properly')

    test_image_location = fetch_file(test_image, ns.store_location, ns.store_local_location)

    ns.threads = int(threads)
    ns.test_image_location = test_image_location
    ns.test_image = test_image
    ns.feature_response_results = feature_response_results
    ns.feature_past_response_results = feature_past_response_results


def tear_down_parallel_feature_test(ns):
    """ Teardown feature requests test """
    tear_down_simple_feature_test(ns)



def setup_image_upload(ns):
    """
        Uploads a single image
    """
    content = upload_image_resource(ns.session, ns.test_image_location, u'%s/%s'%(TEST_PATH, ns.test_image))
    resource_uri = content.attrib['uri']
    image_uri = '%s/image_service/image/%s'%(ns.root, content.attrib['resource_uniq'])

    ns.image_uri = image_uri
    ns.resource_uri = resource_uri


def teardown_image_remove(ns):
    """
        Removes the uploaded image
    """
    delete_resource(ns.session, ns.resource_uri)
    del ns.image_uri
    del ns.resource_uri


def setup_parallel_image_upload(ns):
    """
        Uploads a single image
    """
    content = upload_image_resource(ns.session, ns.test_image_location, u'%s/%s'%(TEST_PATH, ns.test_image))
    resource_uri = content.attrib['uri']
    image_uri = '%s/image_service/image/%s'%(ns.root, content.attrib['resource_uniq'])

    ns.image_uri = image_uri
    ns.resource_uri = resource_uri


def teardown_parallel_image_remove(ns):
    """
        Removes the uploaded image
    """
    delete_resource(ns.session, ns.resource_uri)
    del ns.image_uri
    del ns.resource_uri


def setup_dataset_upload(ns):
    """
        Uploads a many image image
    """
    content = upload_image_resource(ns.session, ns.test_image_location, u'%s/%s'%(TEST_PATH, ns.test_image))
    resource_uri1 = content.attrib['uri']
    image_uri1 = '%s/image_service/image/%s'%(ns.root, content.attrib['resource_uniq'])

    content = upload_image_resource(ns.session, ns.test_image_location, u'%s/%s'%(TEST_PATH, ns.test_image))
    resource_uri2 = content.attrib['uri']
    image_uri2 = '%s/image_service/image/%s'%(ns.root, content.attrib['resource_uniq'])

    content = upload_image_resource(ns.session, ns.test_image_location, u'%s/%s'%(TEST_PATH, ns.test_image))
    resource_uri3 = content.attrib['uri']
    image_uri3 = '%s/image_service/image/%s'%(ns.root, content.attrib['resource_uniq'])


    ns.image_uri1 = image_uri1 #image_service uri
    ns.resource_uri1 = resource_uri1 #data_service uri
    ns.image_uri2 = image_uri2 #image_service uri
    ns.resource_uri2 = resource_uri2 #data_service uri
    ns.image_uri3 = image_uri3 #image_service uri
    ns.resource_uri3 = resource_uri3 #data_service uri


def teardown_dataset_remove(ns):
    """
        Removes the uploaded images
    """
    delete_resource(ns.session, ns.resource_uri1)
    delete_resource(ns.session, ns.resource_uri2)
    delete_resource(ns.session, ns.resource_uri3)
    del ns.image_uri1
    del ns.resource_uri1
    del ns.image_uri2
    del ns.resource_uri2
    del ns.image_uri3
    del ns.resource_uri3


def setup_mask_upload(ns):
    """
        Uploads a mask over the uploaded image
    """

    #check meta to make the mask
    xml = ns.session.fetchxml(ns.image_uri, meta='')
    size_x = int(xml.xpath('tag[@name="image_num_x"]/@value')[0])
    size_y = int(xml.xpath('tag[@name="image_num_y"]/@value')[0])
    mask = np.zeros([size_y, size_x])
    mask[size_y/4:(3*size_y)/4,size_x/4:(3*size_x)/4] = 1 #create mask

    #save mask
    maskname = 'mask.tif'
    tif = TIFF.open(os.path.join(ns.store_local_location, maskname), mode='w')
    tif.write_image(mask)

    content = upload_image_resource(ns.session, os.path.join(ns.store_local_location, maskname), u'%s/%s'%(TEST_PATH, maskname))
    mask_resource_uri = content.attrib['uri']
    mask_uri = '%s/image_service/image/%s'%(ns.root, content.attrib['resource_uniq'])

    ns.mask_uri = mask_uri #image_service uri
    ns.mask_resource_uri = mask_resource_uri #data_service uri


def teardown_mask_remove(ns):
    """
        Removes the uploaded image
    """
    delete_resource(ns.session, ns.mask_resource_uri)
    del ns.mask_uri  #image_service uri
    del ns.mask_resource_uri  #data_service uri


def setup_polygon_upload(ns):
    """
    """
    #check meta to make the mask
    xml = ns.session.fetchxml(ns.image_uri, meta='')
    size_x = int(xml.xpath('tag[@name="image_num_x"]/@value')[0])
    size_y = int(xml.xpath('tag[@name="image_num_y"]/@value')[0])

    vertices = np.array([[1, 0], [.3, .3], [0, 1],[-.3, .3], [-1, 0], [-.3, -.3], [0, -1], [.3, -.3]]) #shape
    min = np.min([size_y, size_x])
    scale = .4*min
    vertices = vertices*scale#scale
    vertices[:,0] = vertices[:,0]+size_y*.5#center y
    vertices[:,1] = vertices[:,1]+size_x*.5#center x

    polygon = etree.Element('polygon', name='test')
    for i, (y, x) in enumerate(vertices):
        etree.SubElement(polygon,'vertex',index=str(i), y=str(y),x=str(x))
    xml = ns.session.postxml(ns.resource_uri, xml=etree.tostring(polygon))
    gobject_uri = xml.attrib['uri']

    ns.gobject_uri = gobject_uri


def teardown_gobject_remove(ns):
    """
    """
    del ns.gobject_uri


def setup_rectangle_upload(ns):
    """
    """
    #check meta to make the mask
    xml = ns.session.fetchxml(ns.image_uri, meta='')
    size_x = int(xml.xpath('tag[@name="image_num_x"]/@value')[0])
    size_y = int(xml.xpath('tag[@name="image_num_y"]/@value')[0])

    #vertices = np.array([[1,0],[0,.75],[-1,0],[0,-.75]]) #shape
    vertices = np.array([[-.5,-.5], [.5,.5]])

    min = np.min([size_y, size_x])
    scale = .4*min
    vertices = vertices*scale #scale
    vertices[:,0] = vertices[:,0] + size_y*.5 #center y
    vertices[:,1] = vertices[:,1] + size_x*.5 #center x

    polygon = etree.Element('rectangle', name='test')
    for i, (y, x) in enumerate(vertices):
        etree.SubElement(polygon, 'vertex', index=str(i), y=str(y), x=str(x))
    xml = ns.session.postxml(ns.resource_uri, xml=etree.tostring(polygon))
    gobject_uri = xml.attrib['uri']

    ns.gobject_uri = gobject_uri


def setup_circle_upload(ns):
    """
    """
    #check meta to make the mask
    xml = ns.session.fetchxml(ns.image_uri, meta='')
    size_x = int(xml.xpath('tag[@name="image_num_x"]/@value')[0])
    size_y = int(xml.xpath('tag[@name="image_num_y"]/@value')[0])

    vertices = np.array([[0,0],[-.3,.3]]) #shape

    min = np.min([size_y,size_x])
    scale = .4*min
    vertices = vertices*scale#scale
    vertices[:,0] = vertices[:,0]+size_y*.5#center y
    vertices[:,1] = vertices[:,1]+size_x*.5#center x

    polygon = etree.Element('circle', name='test')
    for i,(y,x) in enumerate(vertices):
        etree.SubElement(polygon,'vertex', index=str(i), y=str(y), x=str(x))
    xml = ns.session.postxml(ns.resource_uri, xml=etree.tostring(polygon))
    gobject_uri = xml.attrib['uri']

    ns.gobject_uri = gobject_uri

def setup_point_upload(ns):
    """
    """
    #check meta to make the mask
    xml = ns.session.fetchxml(ns.image_uri, meta='')
    size_x = int(xml.xpath('tag[@name="image_num_x"]/@value')[0])
    size_y = int(xml.xpath('tag[@name="image_num_y"]/@value')[0])

    vertices = np.array([[0,0]]) #shape

    min = np.min([size_y,size_x])
    scale = .4*min
    vertices = vertices*scale#scale
    vertices[:,0] = vertices[:,0]+size_y*.5#center y
    vertices[:,1] = vertices[:,1]+size_x*.5#center x

    polygon = etree.Element('point', name='test')
    for i,(y,x) in enumerate(vertices):
        etree.SubElement(polygon,'vertex',index=str(i), y=str(y),x=str(x))
    xml = ns.session.postxml(ns.resource_uri, xml=etree.tostring(polygon))
    gobject_uri = xml.attrib['uri']

    ns.gobject_uri = gobject_uri

