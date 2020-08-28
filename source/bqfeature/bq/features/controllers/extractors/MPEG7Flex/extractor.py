#features included
# SCD,HTD2,EHD2,DCD,CSD,CLD,RSD
import tables
import numpy as np
from pyMPEG7FlexLib import extractCSD,extractSCD,extractCLD,extractDCD,extractHTD,extractEHD,extractRSD
from bq.features.controllers.utils import image2numpy, gobject2mask, except_image_only , calculation_lock
from bq.features.controllers import Feature
from bq.features.controllers.exceptions import FeatureExtractionError
from bqapi import BQServer
import logging
log = logging.getLogger("bq.features.MPEG7")


#getting a double pointer error when run with multible threads
class SCD(Feature.BaseFeature):
    """
        Initalizes table and calculates the SURF descriptor to be
        placed into the HDF5 table.
    """
    #parameters
    name = 'SCD'
    description = """Scalable Color Descriptor"""
    length = 256
    type = ['color']
    confidence = 'good'

    @calculation_lock
    def calculate(self, resource):
        """ Append descriptors to h5 table """
        except_image_only(resource)
        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='display')
        im = np.uint8(im)
        descriptors = extractSCD(im, descSize=256) #calculating descriptor
        return descriptors

#FFTW is not thread-safe
class HTD2(Feature.BaseFeature):
    """
    """
    #initalize parameters
    name = 'HTD2'
    description = """Homogenious Texture Descritpor (Image\'s width and height must be greater than 128)"""
    length = 62
    type = ['texture']
    confidence = 'good'

    @calculation_lock
    def calculate(self, resource):
        #initalizing
        except_image_only(resource)
        image_uri = resource.image

        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        im = image2numpy(image_uri, remap='gray')
        im = np.uint8(im)
        width, height = im.shape
#        if width<128 and height<128:
#            raise FeatureExtractionError(resource, 415, 'Image\'s width and height must be greater than 128')
        descriptors = extractHTD(im) #calculating descriptor

        return descriptors


class EHD2(Feature.BaseFeature):
    """
        Initalizes table and calculates the Edge Histogram descriptor to be
        placed into the HDF5 table

        scale = 6
        rotation = 4
    """
    #initalize parameters
    name = 'EHD2'
    description = """Edge histogram descriptor also known as EHD"""
    length = 80
    type = ['texture']
    confidence = 'good'

    @calculation_lock
    def calculate(self, resource):
        #initalizing
        except_image_only(resource)
        image_uri = resource.image
        #image_uri = BQServer().prepare_url(image_uri, remap='gray')
        im = image2numpy(image_uri, remap='gray')
        im = np.uint8(im)
        descriptors = extractEHD(im) #calculating descriptor

        return descriptors


class MaskedMPEG7(Feature.BaseFeature):
    """
        Base Class for all the features that have
        masked parameters
    """
    #parameters
    resource = ['image']
    additional_resource = ['mask','gobject']
    parameter = ['label']
    disabled = True

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


class DCD(MaskedMPEG7):
    """
    """
    #parameters
    name = 'DCD'
    description = """Dominant Color Descriptor can be of any length. The arbitrary length decided to be stored in the
    tables is 100"""
    length = 100
    type = ['color']
    confidence = 'good'
    disabled = False

    @calculation_lock
    def calculate(self, resource):
        """ Append descriptors to DCD h5 table """

        (image_uri, mask_uri, gobject_uri) = resource

        if image_uri and mask_uri and gobject_uri:
            raise FeatureExtractionError(400, 'Can only take either a mask or a gobject not both')

        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='display')
        im = np.uint8(im)

        if mask_uri is '' and gobject_uri is '':
            #calculating descriptor
            DCD = extractDCD(im)

            #DCD has a potentional to be any length
            #the arbitrary decided length to store in the tables is 100
            if len(DCD)>self.length:
                log.debug('Warning: greater than 100 dimensions')
                DCD = DCD[:self.length]

            descriptors = np.zeros((self.length))
            descriptors[:len(DCD)] = DCD

            #initalizing rows for the table
            return [descriptors],[0]

        if mask_uri:
            #mask_uri = BQServer().prepare_url(mask_uri, remap='gray')
            mask = image2numpy(mask_uri, remap='gray')

        if gobject_uri:
            #creating a mask from gobject
            mask = gobject2mask(gobject_uri, im)

        descritptor_list = []
        label_list = []
        #calculating descriptor
        for label in np.unique(mask):
            lmask = np.array((mask==label)*255, dtype='uint8')
            DCD = extractDCD(im, mask = lmask)

            #DCD has a potentional to be any length
            #the arbitrary decided length to store in the tables is 100
            if len(DCD)>self.length:
                log.debug('Warning: greater than 100 dimensions')
                DCD=DCD[:self.length]

            descriptors = np.zeros((self.length))
            descriptors[:len(DCD)]=DCD
            descritptor_list.append(descriptors)
            label_list.append(label)

        #initalizing rows for the table
        return descritptor_list, label_list



class CSD(MaskedMPEG7):
    """
        Initalizes table and calculates the SURF descriptor to be
        placed into the HDF5 table.
    """

    #parameters
    name = 'CSD'
    description = """Color Structure Descriptor"""
    length = 64
    type = ['color']
    confidence = 'good'
    disabled = False

    @calculation_lock
    def calculate(self, resource):
        """ Append descriptors to CSD h5 table """

        (image_uri, mask_uri, gobject_uri) = resource

        if image_uri and mask_uri and gobject_uri:
            raise FeatureExtractionError(400, 'Can only take either a mask or a gobject not both')

        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='display')
        im = np.uint8(im)

        if mask_uri is '' and gobject_uri is '':
            #calculating descriptor
            CSD = extractCSD(im)

            #initalizing rows for the table
            return [CSD], [0]

        if mask_uri:
            #mask_uri = BQServer().prepare_url(mask_uri, remap='gray')
            mask = image2numpy(mask_uri, remap='gray')

        if gobject_uri:
            #creating a mask from gobject
            mask = gobject2mask(gobject_uri, im)

        descritptor_list = []
        label_list = []
        #calculating descriptor
        for label in np.unique(mask):
            lmask = np.array((mask==label)*255, dtype='uint8')
            CSD = extractCSD(im, mask=lmask, descSize=64)
            label_list.append(label)
            descritptor_list.append(CSD)

        #initalizing rows for the table
        return descritptor_list, label_list


class CLD(MaskedMPEG7):
    """
        Initalizes table and calculates the SURF descriptor to be
        placed into the HDF5 table.
    """

    #parameters
    name = 'CLD'
    description = """Color Layout Descriptor"""
    length = 120
    type = ['color']
    confidence = 'good'
    disabled = False

    @calculation_lock
    def calculate(self, resource):
        """ Append descriptors to CSD h5 table """

        (image_uri, mask_uri, gobject_uri) = resource

        if image_uri and mask_uri and gobject_uri:
            raise FeatureExtractionError(400, 'Can only take either a mask or a gobject not both')

        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='display')
        im = np.uint8(im)

        if mask_uri is '' and gobject_uri is '':
            #calculating descriptor
            CLD = extractCLD(im, numYCoef=64, numCCoef=28)

            #initalizing rows for the table
            return [CLD], [0]

        if mask_uri:
            #mask_uri = BQServer().prepare_url(mask_uri, remap='gray')
            mask = image2numpy(mask_uri, remap='gray')

        if gobject_uri:
            #creating a mask from gobject
            mask = gobject2mask(gobject_uri, im)

        descritptor_list = []
        label_list = []
        #calculating descriptor
        for label in np.unique(mask):
            lmask = np.array((mask==label)*255,dtype='uint8')
            CLD = extractCLD(im,mask=lmask,numYCoef=64, numCCoef = 28)
            label_list.append(label)
            descritptor_list.append(CLD)

        #initalizing rows for the table
        return descritptor_list, label_list



class RSD(MaskedMPEG7):
    """
    """
    name = 'RSD'
    description = """Region Shape Descritpor"""
    length = 35
    type = ['shape','texture']
    confidence = 'good'
    disabled = False

    @calculation_lock
    def calculate(self, resource):
        """ Append descriptors to CSD h5 table """

        (image_uri, mask_uri, gobject_uri) = resource

        if image_uri and mask_uri and gobject_uri:
            raise FeatureExtractionError(400, 'Can only take either a mask or a gobject not both')

        #image_uri = BQServer().prepare_url(image_uri, remap='display')
        im = image2numpy(image_uri, remap='display')
        im = np.uint8(im)

        if mask_uri is '' and gobject_uri is '':
            #calculating descriptor
            RSD = extractRSD(im)

            #initalizing rows for the table
            return [RSD], [0]

        if mask_uri:
            #mask_uri = BQServer().prepare_url(mask_uri, remap='gray')
            mask = image2numpy(mask_uri, remap='gray')

        if gobject_uri:
            #creating a mask from gobject
            mask = gobject2mask(gobject_uri, im)

        descritptor_list = []
        label_list = []
        #calculating descriptor
        for label in np.unique(mask):
            lmask = np.array((mask==label)*255,dtype='uint8')
            RSD = extractRSD(im, mask=lmask)
            label_list.append(label)
            descritptor_list.append(RSD)

        #initalizing rows for the table
        return descritptor_list, label_list


