# -*- mode: python -*-
"""
"""

import numpy as np
from mahotas.features import haralick,lbp,pftas,tas,zernike_moments
from pylons.controllers.util import abort
from bq.features.controllers import Feature
from bq.features.controllers.utils import image2numpy, except_image_only
from bq.features.controllers.exceptions import FeatureExtractionError
from bqapi import BQServer
import logging

log = logging.getLogger("bq.features.Mahotas")

class HAR(Feature.BaseFeature):
    """
    """
    #parameters
    name = 'HAR'
    description = """Haralick Texure Features"""
    length = 13*4
    confidence = 'good'

    def calculate(self, resource):
        #initalizing
        except_image_only(resource)

        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        im = image2numpy(image_uri, remap='gray')
        im = np.uint8(im)
        #calculate descriptor
        descritptors = np.hstack(haralick(im))

        #initalizing rows for the table
        return descritptors


class HARColored(Feature.BaseFeature):
    """
    """
    #parameters
    name = 'HARColored'
    description = """Haralick Texure Features with colored image input"""
    length = 169

    def calculate(self, resource):
        #initalizing
        except_image_only(resource)

        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='display')
        im = np.uint8(im)

        #calculate descriptor
        descritptors = np.hstack(haralick(im))

        #initalizing rows for the table
        return descritptors


class LBP(Feature.BaseFeature):
    """
    """

    #parameters
    name = 'LBP'
    description = """Linear Binary Patterns: radius = 5 and points = 5"""
    length = 8
    confidence = 'good'

    def calculate(self, resource):
        #initalizing
        except_image_only(resource)

        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        im = image2numpy(image_uri, remap='gray')
        im = np.uint8(im)

        #calculating descriptor
        radius = 5
        points = 5
        descriptor = lbp(im,radius,points)

        #initalizing rows for the table
        return descriptor


class PFTAS(Feature.BaseFeature):
    """
    """

    #parameters
    name = 'PFTAS'
    description = """parameter free Threshold Adjacency Statistics"""
    length = 54
    confidence = 'good'

    def calculate(self, resource):
        """ Append descriptors to SURF h5 table """
        #initalizing
        except_image_only(resource)

        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        im = image2numpy(image_uri, remap='gray')
        im = np.uint8(im)
        descriptor = pftas(im)

        #initalizing rows for the table
        return descriptor

class PFTASColored(Feature.BaseFeature):
    """
    """

    #parameters
    name = 'PFTASColored'
    description = """parameter free Threshold Adjacency Statistics"""
    length = 162
    confidence = 'good'

    def calculate(self, resource):
        """ Append descriptors to SURF h5 table """
        #initalizing
        except_image_only(resource)

        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='display')
        im = np.uint8(im)
        descriptor = pftas(im)

        #initalizing rows for the table
        return descriptor

class TAS(Feature.BaseFeature):
    """
    """
    #parameters
    name = 'TAS'
    description = """Threshold Adjacency Statistics"""
    length = 54
    confidence = 'good'

    def calculate(self, resource):
        """ Append descriptors to TAS h5 table """
        #initalizing
        except_image_only(resource)

        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        im = image2numpy(image_uri, remap='gray')
        im = np.uint8(im)
        descriptor = tas(im)

        #initalizing rows for the table
        return descriptor

class TASColored(Feature.BaseFeature):
    """
    """
    #parameters
    name = 'TASColored'
    description = """Threshold Adjacency Statistics"""
    length = 162
    confidence = 'good'

    def calculate(self, resource):
        #initalizing
        except_image_only(resource)

        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='display')
        im = np.uint8(im)
        descriptor = tas(im)

        #initalizing rows for the table
        return descriptor


class ZM(Feature.BaseFeature):
    """
    """
    #parameters
    name = 'ZM'
    description = """Zernike Moment"""
    length = 25
    confidence = 'good'

    def calculate(self, resource):
        #initalizing
        except_image_only(resource)

        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        im = image2numpy(image_uri, remap='gray')
        im = np.uint8(im)
        radius=8
        degree=8
        descritptor = zernike_moments(im,radius,degree)

        #initalizing rows for the table
        return descritptor

