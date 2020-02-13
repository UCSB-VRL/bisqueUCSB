# -*- mode: python -*-
""" OpenCV Feature

No opencv supprot for bisque.
"""
import cv2
from lxml import etree
import numpy as np
from bq.features.controllers import Feature
from bq.features.controllers.utils import image2numpy, gobject2mask, except_image_only, gobject2keypoint
from bq.features.controllers.exceptions import FeatureImportError, FeatureExtractionError
from bqapi import BQServer
import tables
import logging

log = logging.getLogger("bq.features.openCV")


try:
    cv2_v = [int(s) for s in cv2.__version__.split('.')]
    if (cv2_v < [2, 4, 0] or cv2_v > [2, 4, 9]):
        raise FeatureImportError('OpenCV','Must use OpenCV version >= 2.4.0 and <= 2.4.9')
except ValueError:
    raise FeatureImportError('OpenCV','Must use OpenCV version >= 2.4.0 and <= 2.4.9')


class KeyPointFeatures(Feature.BaseFeature):

    #parameters
    disabled = True
    additional_resource = ['gobject']
    parameter = ['x','y','response','size','angle','octave']

    def cached_columns(self):
        """
            Columns for the cached tables
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length ))
        return {
            'idnumber'  : tables.StringCol(32,pos=1),
            'feature'   : tables.Col.from_atom(featureAtom, pos=2),
            'x'         : tables.Float32Col(pos=3),
            'y'         : tables.Float32Col(pos=4),
            'response'  : tables.Float32Col(pos=5),
            'size'      : tables.Float32Col(pos=6),
            'angle'     : tables.Float32Col(pos=7),
            'octave'    : tables.Float32Col(pos=8)
                }

    def workdir_columns(self):
        """
            Columns for the output table for the feature column
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length ))
        return {
                'image'     : tables.StringCol(2000,pos=1),
                'mask'      : tables.StringCol(2000,pos=2),
                'gobject'   : tables.StringCol(2000,pos=3),
                'feature'   : tables.Col.from_atom(featureAtom, pos=4),
                'x'         : tables.Float32Col(pos=5),
                'y'         : tables.Float32Col(pos=6),
                'response'  : tables.Float32Col(pos=7),
                'size'      : tables.Float32Col(pos=8),
                'angle'     : tables.Float32Col(pos=9),
                'octave'    : tables.Float32Col(pos=10)
                }

class BRISK(KeyPointFeatures):
    """
        Initalizes table and calculates the ORB descriptor to be
        placed into the HDF5 table.
    """

    #parameters
    name = 'BRISK'
    description = """Scale-invariant feature transform also know as SIFT """
    length = 64
    disabled = False

    def calculate(self, resource):
        """ Append descriptors to BRISK h5 table """

        (image_url, mask_url, gobject_url) = resource
        if image_url is '':
            raise FeatureExtractionError(resource, 400, 'Image resource is required')
        if mask_url is not '':
            raise FeatureExtractionError(resource, 400, 'Mask resource is not accepted')

        #image_url = BQServer().prepare_url(image_url, remap='gray')
        im = image2numpy(image_url, remap='gray')
        im = np.uint8(im)

        if gobject_url is '':
            fs = cv2.BRISK().detect(im) # keypoints

        if gobject_url:
            (x, y, size) = gobject2keypoint(gobject_url)
            fs = [cv2.KeyPoint(x, y, size)]       # keypoints

        # extract the feature keypoints and descriptor
        descriptor_extractor = cv2.DescriptorExtractor_create("BRISK")
        (kpts, descriptors) = descriptor_extractor.compute(im,fs)

        if descriptors == None: #taking Nonetype into account
            raise FeatureExtractionError(resource, 500, 'No feature was calculated')

        x=[]; y=[]; response=[]; size=[]; angle=[]; octave=[]

        for k in kpts[:500]:
            x.append(k.pt[0])
            y.append(k.pt[1])
            response.append(k.response)
            size.append(k.size)
            angle.append(k.angle)
            octave.append(k.octave)

        return (descriptors, x, y, response, size, angle, octave)


class ORB(KeyPointFeatures):
    """
        Initalizes table and calculates the ORB descriptor to be
        placed into the HDF5 table.
    """

    #parameters
    name = 'ORB'
    description = """The algorithm uses FAST in pyramids to detect stable keypoints, selects the
    strongest features using FAST response, finds their orientation using first-order moments and
    computes the descriptors using BRIEF (where the coordinates of random point pairs (or k-tuples)
    are rotated according to the measured orientation).
    This explination was taken from opencv documention on orb and the algorithm iself was taken from
    the opencv library"""
    length = 32
    disabled = False

    def calculate(self, resource):
        """ Append descriptors to ORB h5 table """
        (image_url, mask_url, gobject_url) = resource
        if image_url is '':
            raise FeatureExtractionError(resource, 400, 'Image resource is required')
        if mask_url is not '':
            raise FeatureExtractionError(resource, 400, 'Mask resource is not accepted')

        #image_url = BQServer().prepare_url(image_url, remap='display')
        im = image2numpy(image_url, remap='display')
        im = np.uint8(im)

        if gobject_url is '':
            fs = cv2.ORB().detect(im)

        if gobject_url:
            (x, y, size) = gobject2keypoint(gobject_url)
            fs = [cv2.KeyPoint(x, y, size)]       # keypoints

        descriptor_extractor = cv2.DescriptorExtractor_create("ORB")
        (kpts, descriptors) = descriptor_extractor.compute(im,fs)

        if descriptors == None: #no feature was returned
            raise FeatureExtractionError(resource, 500, 'No feature was calculated')

        x=[]; y=[]; response=[]; size=[]; angle=[]; octave=[]

        for k in kpts[:500]:
            x.append(k.pt[0])
            y.append(k.pt[1])
            response.append(k.response)
            size.append(k.size)
            angle.append(k.angle)
            octave.append(k.octave)

        return (descriptors, x, y, response, size, angle, octave)


class SIFT(KeyPointFeatures):
    """
        Initalizes table and calculates the ORB descriptor to be
        placed into the HDF5 table.
    """

    #parameters
    name = 'SIFT'
    description = """Scale-invariant feature transform also know as SIFT """
    length = 128
    feature_format = "int32"
    disabled = False

    def calculate(self, resource):
        """ Append descriptors to SIFT h5 table """
        (image_url, mask_url, gobject_url) = resource
        if image_url is '':
            raise FeatureExtractionError(resource, 400, 'Image resource is required')
        if mask_url is not '':
            raise FeatureExtractionError(resource, 400, 'Mask resource is not accepted')

        #image_url = BQServer().prepare_url(image_url, remap='display')
        im = image2numpy(image_url, remap='display')
        im = np.uint8(im)

        if gobject_url is '':
            fs = cv2.SIFT().detect(im)

        if gobject_url:
            (x, y, size) = gobject2keypoint(gobject_url)
            fs = [cv2.KeyPoint(x, y, size)]      # keypoints

        # extract the feature keypoints and descriptor
        descriptor_extractor = cv2.DescriptorExtractor_create("SIFT")
        (kpts, descriptors) = descriptor_extractor.compute(im,fs)

        if descriptors == None: #taking Nonetype into account
            raise FeatureExtractionError(resource, 500, 'No feature was calculated')

        x=[]; y=[]; response=[]; size=[]; angle=[]; octave=[]

        for k in kpts[:500]:
            x.append(k.pt[0])
            y.append(k.pt[1])
            response.append(k.response)
            size.append(k.size)
            angle.append(k.angle)
            octave.append(k.octave)

        return (descriptors, x, y, response, size, angle, octave)


class SURF(KeyPointFeatures):
    """
        Initalizes table and calculates the SURF descriptor to be
        placed into the HDF5 table.
    """

    #parameters
    name = 'SURF'
    description = """Speeded Up Robust Features also know as SURF"""
    length = 64
    disabled = False

    def calculate(self, resource):
        """ Append descriptors to SURF h5 table """
        #initalizing
        extended = 0
        HessianThresh = 400
        nOctaves = 3
        nOctaveLayers = 4

        (image_url, mask_url, gobject_url) = resource
        if image_url is '':
            raise FeatureExtractionError(resource, 400, 'Image resource is required')
        if mask_url is not '':
            raise FeatureExtractionError(resource, 400, 'Mask resource is not accepted')

        #image_url = BQServer().prepare_url(image_url, remap='display')
        im = image2numpy(image_url, remap='display')
        im = np.uint8(im)

        if gobject_url is '':
            fs = cv2.SURF().detect(im)

        if gobject_url:
            (x, y, size) = gobject2keypoint(gobject_url)
            fs = [cv2.KeyPoint(x, y, size)]      # keypoints

        descriptor_extractor = cv2.DescriptorExtractor_create("SURF")
        (kpts, descriptors) = descriptor_extractor.compute(im, fs)

        if descriptors == None: #taking Nonetype into account
            raise FeatureExtractionError(resource, 500, 'No feature was calculated')

        x = []; y = []; response = []; size = []; angle = []; octave = []

        for k in kpts[:500]:
            x.append(k.pt[0])
            y.append(k.pt[1])
            response.append(k.response)
            size.append(k.size)
            angle.append(k.angle)
            octave.append(k.octave)

        return (descriptors, x, y, response, size, angle, octave)


class Moments(Feature.BaseFeature):

    name = 'Moments'
    description = """Takes a binary image and calculates Moments on it"""
    length = 24
    disabled = False

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        binary_im = np.uint8(im>0)
        m = cv2.moments(binary_im)
        return m.values()


class HuMoments(Feature.BaseFeature):

    name = 'HuMoments'
    description = """Takes a binary image and calculates Hu Moments on it"""
    length = 7
    disable = False

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        binary_im = np.uint8(im>0)
        m = cv2.moments(binary_im)
        hu = cv2.HuMoments(m)
        return [hu.T]



