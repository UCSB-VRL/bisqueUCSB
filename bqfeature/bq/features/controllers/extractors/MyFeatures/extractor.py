# -*- mode: python -*-
""" MyFeature library
"""

import logging
from fftsd_extract import FFTSD as fftsd
from lxml import etree
from bqapi import BQServer
import random
from bq.features.controllers.utils import image2numpy, except_image_only, fetch_resource
from bq.features.controllers import Feature
from bq.features.controllers.exceptions import FeatureExtractionError
from hog_extractor import histogram_of_oriented_gradients
#from htd_extractor import homogenious_texture_descriptor

log = logging.getLogger("bq.features.MyFeature")

class FFTSD(Feature.BaseFeature):

    #parameters
    file = 'features_fftsd.h5'
    name = 'FFTSD'
    resource = ['polygon']
    description = """Fast Fourier Transform Shape Descriptor"""
    length = 500
    confidence = 'good'
    disabled = True

    def calculate(self, resource):
        """ Append descriptors to FFTSD h5 table """

        if resource.gobject is None:
            raise FeatureExtractionError(resource, 400, 'Gobject resource is required.')
        if resource.mask:
            raise FeatureExtractionError(resource, 400, 'Mask resource is not accepted.')
        if resource.image:
            raise FeatureExtractionError(resource, 400, 'Image resource is not accepted.')

        uri_full = BQServer().prepare_url(resource.gobject, view='deep')
        response = fetch_resource(uri_full)

        try:
            poly_xml = etree.fromstring(response)
        except etree.XMLSyntaxError:
            raise FeatureExtractionError(resource, 400, 'image resource is not accepted')

        if poly_xml.tag=='polygon':
            vertices = poly_xml.xpath('vertex')
            contour = []
            for vertex in vertices:
                contour.append([int(float(vertex.attrib['x'])),int(float(vertex.attrib['y']))])

        else:
            log.debug('Polygon not found: Must be a polygon gobject')
            raise ValueError('Polygon not found: Must be a polygon gobject') #an excpetion instead of abort so work flow is not interupted

        descriptor = fftsd(contour,self.length)

        #initalizing rows for the table
        return [descriptor[:500]]


# class HOG(Feature.BaseFeature):

#     file = 'features_hog.h5'
#     name = 'HOG'
#     description = """Histogram of Orientated Gradients: bin = 9"""
#     length = 9
#     confidence = 'good'
#     disabled = True

#     def calculate(self, resource):
#         """ Append descriptors to HOG h5 table """

#         except_image_only(resource)
#         image_uri = resource.image

#         with ImageImport(image_uri) as imgimp:
#             im = image2numpy(image_uri, remap='gray')

#         descriptor = histogram_of_oriented_gradients(im)

#         #initalizing rows for the table
#         return [descriptor]


#class HTD(Feature.BaseFeature):
#
#    file = 'feature_htd.h5'
#    name = 'HTD'
#    description = """Homogenious Texture Descriptor"""
#    length = 48
#    confidence = 'good'
#
#    def calculate(self, resource):
#        """ Append descriptors to HOG h5 table """
#        #initalizing
#        image_uri = resource.image
#
#        with ImageImport(image_uri) as imgimp:
#            im = imgimp.from_tiff2D_to_numpy()
#            if len(im.shape)==3:
#                im = rgb2gray(im)
#
#        descriptor = homogenious_texture_descriptor(im)
#
#        #initalizing rows for the table
#        return [descriptor]

