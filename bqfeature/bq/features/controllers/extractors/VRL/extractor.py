# -*- mode: python -*-
""" EHD library
"""
import tables
import numpy as np
from bq.features.controllers.exceptions import FeatureExtractionError
from bq.features.controllers.utils import image2numpy, gobject2mask, except_image_only, calculation_lock
from bqapi import BQServer
from bq.features.controllers import Feature
from pyVRLLib import extractEHD, extractHTD
import logging

from bq.features.controllers.utils import image2numpy, except_image_only
log = logging.getLogger("bq.features.VRL")

class EHD(Feature.BaseFeature):
    """
        Initalizes table and calculates the Edge Histogram descriptor to be
        placed into the HDF5 table

        scale = 6
        rotation = 4
    """
    #initalize parameters
    name = 'EHD'
    resource = ['image']
    description = """Edge histogram descriptor also known as EHD"""
    length = 80
    confidence = 'poor' #gets different values on different machines, not sure what is causing the issue

    @calculation_lock
    def calculate(self, resource):
        #initalizing
        except_image_only(resource)
        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        im = image2numpy(image_uri, remap='gray')
        descriptors=extractEHD(im)

        #initalizing rows for the table
        return descriptors


class HTD(Feature.BaseFeature):
    """
        Initalizes table and calculates the HTD descriptor to be
        placed into the HDF5 table

        scale = 6
        rotation = 4
    """
    #initalize parameters
    name = 'HTD'
    #disabled = True #not thread-safe due to lib fftw
    resource = ['image']
    additional_resource = ['mask','gobject']
    parameter = ['label']
    description = """Homogenious Texture Descriptor also called HTD is a texture descritpor
    which applies the gabor filter with 6 different scales and 4 orientations. After applying
    the 24 different gabor filters the mean and standard deviation of all the pixels are
    calculated and the descriptor is returned"""
    length = 48
    confidence = 'good'

    def cached_columns(self):
        """
            Columns for the cached tables
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length ))
        return {
                'idnumber' : tables.StringCol(32,pos=1),
                'feature'  : tables.Col.from_atom(featureAtom, pos=2),
                'label'    : tables.Int32Col(pos=3)
                }


    def workdir_columns(self):
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length ))
        return {
                'image'   : tables.StringCol(2000,pos=1),
                'mask'    : tables.StringCol(2000,pos=2),
                'gobject' : tables.StringCol(2000,pos=3),
                'feature' : tables.Col.from_atom(featureAtom, pos=4),
                'label'   : tables.Int32Col(pos=5)
                }

    @calculation_lock
    def calculate(self, resource):
        """ Append descriptors to DCD h5 table """
        (image_uri, mask_uri, gobject_uri) = resource
        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        if image_uri and mask_uri and gobject_uri:
            raise FeatureExtractionError(400, 'Can only take either a mask or a gobject not both')

        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='gray')

        if mask_uri is '' and gobject_uri is '':
            #calculating descriptor
            descriptor, label = extractHTD(im)

            #initalizing rows for the table
            return [descriptor], [0]

        if mask_uri:
            #mask_uri = BQServer().prepare_url(mask_uri, remap='gray')
            mask = image2numpy(mask_uri, remap='gray')

        if gobject_uri:
            #creating a mask from gobject
            mask = gobject2mask(gobject_uri, im)

        descriptors, labels = extractHTD(im, mask=mask)

        #initalizing rows for the table
        return descriptors, labels


