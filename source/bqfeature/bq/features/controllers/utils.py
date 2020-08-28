# -*- mode: python -*-
""" Utils for feature service
"""
import os
import numpy as np
import re
import logging
import tempfile
import urlparse
import urllib
from lxml import etree
from tg import request

from webob.request import Request, environ_from_url
from libtiff import TIFF
import threading
from PIL import Image, ImageDraw

from bq import image_service
from bq import data_service
from bq.core import identity
from bqapi import BQServer, BQCommError
from bq.util.mkdir import _mkdir
from bq.features.controllers.exceptions import InvalidResourceError, FeatureExtractionError
from .var import FEATURES_TEMP_DIR


log = logging.getLogger("bq.features.utils")

global GLOBAL_FEATURE_CALC_LOCK
GLOBAL_FEATURE_CALC_LOCK = {}

def calculation_lock(calc):
    """
        Some feature calculation functions are not thread-safe.
        This decorator will force calculations to be run concurrently
        in threads. Place on calculation functions in Feature classes.
    """
    def locker(self, resource):
        """
            Applies and releases the lock on the calculation function
            in the Feature class.

            @param: self - Feature class
            @param: resource - FeatureResource namedtuple
        """
        if self.name not in GLOBAL_FEATURE_CALC_LOCK:
            GLOBAL_FEATURE_CALC_LOCK[self.name] = threading.Lock()
        log.debug('Calculation Lock: %s acquired' % self.name)
        GLOBAL_FEATURE_CALC_LOCK[self.name].acquire()
        try:
            results = calc(self, resource)
        finally:
            GLOBAL_FEATURE_CALC_LOCK[self.name].release()
            log.debug('Calculation Lock: %s release' % self.name)
        return results
    return locker


#def request_internally(url):
#    """
#        Makes a request on the give url internally. If it finds url without errors the content
#        of the body is returned else None is returned
#
#        @param url - the url that is requested internally
#
#        @return webob response object
#    """
#    from bq.config.middleware import bisque_app
#    req = Request.blank('/')
#    req.environ.update(request.environ)
#    req.environ.update(environ_from_url(url))
#    log.debug("Mex %s" % identity.mex_authorization_token())
#    req.headers['Authorization'] = "Mex %s" % identity.mex_authorization_token()
#    req.headers['Accept'] = 'text/xml'
#    log.debug("begin routing internally %s" % url)
#    resp = req.get_response(bisque_app)
#    log.debug("end routing internally: status %s" % resp.status_int)
#    return resp


def request_externally(url):
    """
        Makes a request on the give url externally. If it finds url without errors the content
        of the body is returned else None is returned

        @param url - the url that is requested externally

        @return requests response object
    """
    session = BQServer()
    #session = root
    session.authenticate_mex(identity.mex_authorization_token())
    session.root = request.host_url
    url = session.prepare_url(url)
    log.debug("begin routing externally: %s" % url)
    try:
        resp = session.get(url, headers={'Content-Type':'text/xml'})
    except BQCommError as e:
        log.debug('%s' % str(e))
        return

    log.debug("end routing externally: status %s" % resp.status_code)
    return resp


def check_access(ident):
    """
        Checks for element in the database. If found returns True else returns
        False

        @param ident  - resource uniq or resource id
        @param action - resource action on the database (default: RESOURCE_READ)

        @return bool
    """
    resource = data_service.resource_load(uniq = ident)
    log.debug('Result from the database: %s'%resource)
    if resource is None:
        return False
    return True


#def bq_url_parser(url):
#    o = urlparse.urlsplit(url)
#    m = re.match('\/(?P<service>[\w-]+)\/(image[s]?\/|)(?P<id>[\w-]+)|\/(?P<id>[\w-]+)', o.path)
#
#    m=re.match('\/((?P<service>[\[A-Za-z_]-]+)\/(image[s]?\/|)|)(?P<id>[\w-]+)', url_path)

#needs to be replaced with a HEAD instead of using a GET
def mex_validation(resource):
    """
        First checks the access of the token if the url is image_service or data_service.
        If the token is not found on the url an internal request is made to check the
        response status. If a 302 is returned the redirect url is added to the resource.
        If an internal request fails an external request is made in the same way as the
        internal request. If all fails an InvalidResourceError is returned.

        @param: resource - a feature_resource namedtuple

        @return: resource - feature_resource namedtuple with redirected urls added

        @exception: InvalidResourceError - if the resource could not be found
    """
    resource_name = [n for n in list(resource._fields) if getattr(resource,n) != '']
    for name in list(resource_name):
        url = getattr(resource,name)
        log.debug("resource: %s" % url)
        try:
            o = urlparse.urlsplit(url)
            url_path = o.path
            log.debug('url_path :%s' % url_path)
            m = re.match('\/(?P<service>[\w-]+)\/(image[s]?\/|)(?P<id>[\w-]+)', url_path)
            if m is not None:
                if m.group('service') == 'image_service' or m.group('service') == 'data_service': #check for data_service
                    if 'pixels' not in url_path: #if false requires a redirect
                        ident = m.group('id') #seaching a plan image_service or data_service url
                        if check_access(ident) is True:
                            continue #check next resource

#            # Try to route internally through bisque
#            resp = request_internally(url)
#            if resp.status_int < 400:
#                if resp.status_int == 302:
#                    #reset the url to the redirected url
#                    redirect_url = resp.headers.get('Location')
#                    if redirect_url is not None: #did not find the redirect
#                        log.debug('Redirect Url: %s' % redirect_url)
#                        resource = resource._replace(**{name:redirect_url})
#                        continue
#                else:
#                    continue

            # Try to route externally
            resp = request_externally(url)
            if resp.status_code < 400:
                if resp.status_code == 302:
                    #reset the url to the redirected url
                    redirect_url = resp.headers.get('Location')
                    if redirect_url is not None: #did not find the redirect
                        log.debug('Redirect Url: %s' % redirect_url)
                        resource = resource._replace(**{name:redirect_url})
                        continue
                else:
                    continue

            raise InvalidResourceError(resource_url=url, error_code=403, error_message='Resource: %s Not Found' % url)

        except StandardError:
            log.exception ("While retrieving URL %s" %str(resource))
            raise InvalidResourceError(resource_url=url, error_code=403, error_message='Resource: %s Not Found' % url)

    return resource

def except_image_only(resource):
    """
        Returns only if the resource contains an image url else a FeatureExtractorError
        is raised.

        @param: resource

        @exception: FeatureExtractionError
    """
    if resource.image is None:
        raise FeatureExtractionError(resource, 400, 'Image resource is required')
    if resource.mask:
        raise FeatureExtractionError(resource, 400, 'Mask resource is not accepted')
    if resource.gobject:
        raise FeatureExtractionError(resource, 400, 'Gobject resource is not accepted')


def fetch_resource(uri):
    """
        Attempts to make a request first internally and then externally.
        If one request returns a 200 the content is return else an
        InvalidResourceError is raised.
        @param: url - the url the request is made with

        @return: body of the request

        @exception: InvalidResourceError
    """
    try:
        # Try to route internally through bisque
#        resp = request_internally(uri)
#        if int(resp.status_int) == 200:
#            return resp.body

        # Try to route externally
        resp = request_externally(uri)
        if int(resp.status_code) in set([200,304]):
            return resp.content

        log.debug("User is not authorized to read resource externally: %s" % uri)
        raise InvalidResourceError(resource_url=uri, error_code=403, error_message='Resource: %s Not Found' % uri)

    except StandardError:
        log.exception ("While retrieving URL %s" % uri)
        raise InvalidResourceError(resource_url=uri, error_code=403, error_message='Resource: %s Not Found' % uri)


def image2numpy(uri, **kw):
    """
        Converts image url to numpy array.
        For bisque image_service it changes the format
        to ome-tiff and reads in the tiff with pylibtiff
        If the uri does not return a tiff file
        and then the pillow reader is used instead.

        @param: takes in an image_url
        @param: query parameters added to only image service urls

        @return numpy image
    """
    o = urlparse.urlsplit(uri)

    if 'image_service' in o.path:
        #finds image resource though local image service
        if kw:
            uri = BQServer().prepare_url(uri, **kw)
        uri = BQServer().prepare_url(uri, format='OME-BigTIFF')
        log.debug("Image Service uri: %s" % uri)
        image_path = image_service.local_file(uri)
        log.debug("Image Service path: %s" % image_path)
        if image_path is None:
            log.debug('Not found in image_service internally: %s' % uri)
        else:
            return convert_image2numpy(image_path)

    _mkdir(FEATURES_TEMP_DIR)
    with tempfile.NamedTemporaryFile(dir=FEATURES_TEMP_DIR, prefix='image', delete=False) as f:
        content = fetch_resource(uri)
        f.write(content)

    im = convert_image2numpy(f.name)
    os.remove(f.name)
    return im


def convert_image2numpy(image_path):
    """
        Converts the image at the given path to a numpy array.
        First attempts to read the image with pylibtiff. If
        the image is not a tiff file, Pillow is used to try
        to read the file. IF all fails an InvalidResourceError
        is returned.

        @param: image_path

        @return: image numpy array

        @exception InvalidResourceError
    """
    try:
        tif = TIFF.open(image_path, mode = 'r')
        image = []
        for im in tif.iter_images():
            image.append(im)

        if len(image)>1:
            image = np.dstack(image)
        else:
            image = image[0]
        # pylint: disable=no-member
        if len(image.shape) == 2:
            return image
        elif len(image.shape) == 3:
            if image.shape[2] == 3:
                return image

        raise InvalidResourceError(error_code=415, error_message='Not a grayscale or RGB image')

    except (IOError, TypeError):
        log.debug("Not a tiff file!")
        log.debug("Trying to read in image with pillow")
        try:
            return np.array(Image.open(image_path)) #try to return something, pil doesnt support bigtiff
        except IOError:
            log.debug("File type not supported!")
            raise InvalidResourceError(error_code=415, error_message='Unsupported media type')


def gobject2mask(uri, im):
    """
        Converts a gobject with a shape into
        a binary mask

        @param: uri - gobject uris
        @param: im - image matrix

        @return: mask
    """
    valid_gobject = set(['polygon','circle','square','ellipse','rectangle','gobject'])

    mask = np.zeros([])
    #add view deep to retrieve vertices

    uri_full = BQServer().prepare_url(uri, view='full')

    response = fetch_resource(uri_full)
    #need to check if value xml
    try:
        xml = etree.fromstring(response)
    except etree.XMLSyntaxError:
        raise FeatureExtractionError(None, 415, 'Url: %s, was not xml for gobject' % uri)

    #need to check if its a valid gobject
    if xml.tag not in valid_gobject:
        raise FeatureExtractionError(None, 415, 'Url: %s, Gobject tag: %s is not a valid gobject to make a mask' % (uri,xml.tag))

    if xml.tag in set(['gobject']):
        tag = xml.attrib.get('type')
        if tag is None:
            raise FeatureExtractionError(None, 415, 'Url: %s, Not an expected gobject' % uri)
    else:
        tag = xml.tag

    col = im.shape[0]
    row = im.shape[1]
    img = Image.new('L', (row, col), 0)

    if tag in set(['polygon']):
        contour = []
        for vertex in xml.xpath('vertex'):
            x = vertex.attrib.get('x')
            y = vertex.attrib.get('y')
            if x is None or y is None:
                raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have x or y coordinate' % uri)
            contour.append((int(float(x)),int(float(y))))
        if len(contour)<2:
            raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have enough vertices' % uri)
#        import pdb
#        pdb.set_trace()
        ImageDraw.Draw(img).polygon(contour, outline=255, fill=255)
        mask = np.array(img)

    if tag in set(['square']):
        #takes only the first 2 points
        contour = []
        for vertex in xml.xpath('vertex'):
            x = vertex.attrib.get('x')
            y = vertex.attrib.get('y')
            if x is None or y is None:
                raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have x or y coordinate' % uri)
            contour.append((int(float(x)),int(float(y))))
        if len(contour)<2:
            raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have enough vertices' % uri)

        (x1,y1)= contour[0]
        (x2,y2)= contour[1]
        py = np.min([y1, y2])
        px = np.min([x1, x2])
        side = np.abs(x1-x2)
        contour = [(px,py),(px,py+side),(px+side,py+side),(px+side, py)]
        ImageDraw.Draw(img).polygon(contour, outline=255, fill=255)
        mask = np.array(img)


    if tag in set(['rectangle']):
        #takes only the first 2 points
        contour = []
        for vertex in xml.xpath('vertex'):
            x = vertex.attrib.get('x')
            y = vertex.attrib.get('y')
            if x is None or y is None:
                raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have x or y coordinate' % uri)
            contour.append((int(float(x)),int(float(y))))
        if len(contour)<2:
            raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have enough vertices' % uri)

        (x1,y1)= contour[0]
        (x2,y2)= contour[1]
        y_min = np.min([y1, y2])
        x_min = np.min([x1, x2])
        y_max = np.max([y1, y2])
        x_max = np.max([x1, x2])
        contour = [(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)]
        ImageDraw.Draw(img).polygon(contour, outline=255, fill=255)
        mask = np.array(img)


    if tag in set(['circle','ellipse']): #ellipse isnt supported really, its just a circle also
        #takes only the first 2 points
        contour = []
        for vertex in xml.xpath('vertex'):
            x = vertex.attrib.get('x')
            y = vertex.attrib.get('y')
            if x is None or y is None:
                raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have x or y coordinate' % uri)
            contour.append((int(float(x)),int(float(y))))
        if len(contour)<2:
            raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have enough vertices' % uri)

        (x1,y1) = contour[0]
        (x2,y2) = contour[1]

        r = np.sqrt(np.square(int(float(x2))-int(float(x1)))+
                    np.square(int(float(y2))-int(float(y1))))
        bbox = (int(float(x1))-r, int(float(y1))-r, int(float(x1))+r, int(float(y1))+r)
        ImageDraw.Draw(img).ellipse(bbox, outline=255, fill=255)
        mask = np.array(img)
    return mask


def gobject2keypoint(uri):
    """
        Given a gobject data_service url which is either
        a circle or point. The vertices are extracted
        and parameters for an opencv keypoint.
        @param: uri - circle or point gobject url

        @return: circle (x,y,r), point (x,y,1)

        @exception FeatureExtractionError - if the xml is
        not complete or not correctly formatted
    """
    valid_gobject = set(['circle', 'point'])
    uri_full = BQServer().prepare_url(uri, view='full')
    response = fetch_resource(uri_full)

    try:
        xml = etree.fromstring(response)
    except etree.XMLSyntaxError:
        raise FeatureExtractionError(None, 415, 'Url: %s, was not xml for gobject' % uri)

    #need to check if its a valid gobject
    if xml.tag not in valid_gobject:
        raise FeatureExtractionError(None, 415, 'Url: %s, Gobject tag: %s is not a valid gobject to make a mask' % (uri,xml.tag))

    if xml.tag == 'circle':
        vertices = xml.xpath('vertex')
        center_x = vertices[0].attrib.get('x')
        center_y = vertices[0].attrib.get('y')
        outer_vertex_x = vertices[1].attrib.get('x')
        outer_vertex_y = vertices[1].attrib.get('y')

        if center_x is None or center_y is None or outer_vertex_x is None or outer_vertex_y is None:
            raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have x or y coordinate' % uri)

        r = np.sqrt(np.square(int(float(outer_vertex_x))-int(float(center_x)))+
                    np.square(int(float(outer_vertex_y))-int(float(center_y))))

        return (int(float(center_x)), int(float(center_y)), 2*r)

    if xml.tag == 'point':
        point = xml.xpath('vertex')[0]
        point_x = point.attrib.get('x')
        point_y = point.attrib.get('y')
        if point_x is None or point_y is None:
            raise FeatureExtractionError(None, 415, 'Url: %s, gobject does not have x or y coordinate' % uri)
        return (int(float(point_x)), int(float(point_y)), 1.0)
