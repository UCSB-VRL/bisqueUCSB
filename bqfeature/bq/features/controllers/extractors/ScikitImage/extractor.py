# -*- mode: python -*-
""" MyFeature library
"""

import logging
from lxml import etree
import tables
import numpy as np
from bqapi import BQServer
import random
from bq.features.controllers.utils import image2numpy, except_image_only, fetch_resource
from bq.features.controllers import Feature
from skimage.feature import corner_harris, corner_peaks # pylint: disable=import-error
from skimage.feature import BRIEF as BRIEF_ # pylint: disable=import-error
from skimage.feature import ORB # pylint: disable=import-error
from skimage.feature import hog # pylint: disable=import-error
from skimage.feature import local_binary_pattern # pylint: disable=import-error
from skimage.transform import resize # pylint: disable=import-error


log = logging.getLogger("bq.features.ScikitImage")

class BRIEF(Feature.BaseFeature):

    #parameters
    name = 'BRIEF'
    description = """Binary Robust Independent Elementary Features using the corner harris as the keypoint selector"""
    length = 256
    #confidence = 'good'
    parameter = ['x','y']

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
        }


    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        keypoints = corner_peaks(corner_harris(im), min_distance=1)
        extractor = BRIEF_()
        extractor.extract(im, keypoints)

        #initalizing rows for the table
        return (extractor.descriptors, keypoints[:,0], keypoints[:,1])


class ORB2(Feature.BaseFeature):

    name = 'ORB2'
    description = """Oriented FAST and rotated BRIEF feature detector and binary descriptor extractor"""
    length = 256
    #confidence = 'good'
    parameter = ['x','y','response','scale','orientation']

    def cached_columns(self):
        """
            Columns for the cached tables
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length ))
        return {
            'idnumber'    : tables.StringCol(32,pos=1),
            'feature'     : tables.Col.from_atom(featureAtom, pos=2),
            'x'           : tables.Float32Col(pos=3),
            'y'           : tables.Float32Col(pos=4),
            'response'    : tables.Float32Col(pos=5),
            'scale'       : tables.Float32Col(pos=6),
            'orientation' : tables.Float32Col(pos=7),
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
                'response'    : tables.Float32Col(pos=7),
                'scale'       : tables.Float32Col(pos=8),
                'orientation' : tables.Float32Col(pos=9),
        }

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        extractor = ORB()
        extractor.detect_and_extract(im)
        return (extractor.descriptors,
                extractor.keypoints[:,0],
                extractor.keypoints[:,1],
                extractor.responses,
                extractor.scales,
                extractor.orientations)


class HOG(Feature.BaseFeature):
    name = 'HOG'
    description = """Extract Histogram of Oriented Gradients orientation: 9 pixels per cell: length,width
    cells per block 1,1. Crops the image into a square and extracts HOG"""
    length = 9
    #confidence = 'good'

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        min_length = np.min(im.shape) # pylint: disable=no-member
        return hog(im, pixels_per_cell=(min_length, min_length), cells_per_block=(1,1))


class HOG2(Feature.BaseFeature):
    name = 'HOG2'
    description = """Extract Histogram of Oriented Gradients: Orientation: 4, Pixels per Cell: (8,8)
    Cells per Block (2,2). Returns a vector for each block. Concatinate all the vectors together
    for the complete hog feature vector"""
    #length = 74576
    length = 16
    parameter = ['block']


    def cached_columns(self):
        """
            Columns for the cached tables
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length ))
        return {
            'idnumber'  : tables.StringCol(32,pos=1),
            'feature'   : tables.Col.from_atom(featureAtom, pos=2),
            'block'     : tables.Int32Col(pos=3)
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
                'block'     : tables.Int32Col(pos=5),
        }

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        feature = hog(im, orientations=4, pixels_per_cell=(8, 8), cells_per_block=(2, 2))
        feature = np.reshape(feature, (feature.size/16, 16)) # pylint: disable=no-member
        block_count = np.arange(feature.shape[0])
        return (feature, block_count)


def raw_moments(im, i, j):
    nx, ny = im.shape
    lx = np.arange(nx)
    ly = np.arange(ny)
    yv, xv = np.meshgrid(lx,ly, indexing='ij')
    return np.sum(im*((xv)**i)*((yv)**j))

def central_moments(im, i, j):
    nx, ny = im.shape
    lx = np.arange(nx)
    ly = np.arange(ny)
    yv, xv = np.meshgrid(lx,ly, indexing='ij')
    m00 = np.sum(im)
    m10 = np.sum(xv*im)
    m01 = np.sum(yv*im)
    xavg = m10/(m00)
    yavg = m01/(m00)
    xavg = np.ones([nx,ny])*xavg
    yavg = np.ones([nx,ny])*yavg
    return np.sum(im*((xv-xavg)**i)*((yv-yavg)**j))

def scale_invarient_moments(im,i,j):
    """
        Scale Invariant Moments
    """
    return central_moments(im, i, j)/(np.sum(im)**(1+((i+j)/2)))

def rotation_invariant_moments(im):
    """
    A few scale, rotation and position invarient moment features
    """
    n11 = scale_invarient_moments(im, 1, 1)
    n02 = scale_invarient_moments(im, 0, 2)
    n20 = scale_invarient_moments(im, 2, 0)
    n30 = scale_invarient_moments(im, 3, 0)
    n03 = scale_invarient_moments(im, 0, 3)
    n21 = scale_invarient_moments(im, 2, 1)
    n12 = scale_invarient_moments(im, 1, 2)

    I1 = n20 + n02
    I2 = (n20 - n02)**2+4*n11**2
    I3 = (n30 - 3*n12)**2 + (3*n21 - n03)**2
    I4 = (n30 + n12)**2 + (n21 + n03)**2
    I5 = (n30 - 3*n12)*(n30 + n12)*(((n30 + n12)**2 - 3*(n21 + n30)**2) + (3*n21 - n03)*(n21 - n03)*(3*(n30 + n12)**2 - (n21 + n30)**2))
    I6 = (n20 - n02)*((n30 + n12)**2 - (n21 + n03)**2) + 4*n11*(n30 + n12)*(n21 + n03)
    I7 = (3*n21 - n03)*(n30 + n21)*(((n30 + n12)**2 - 3*(n21 + n03)**2) - (n30 - 3*n12)*(n21 + n03)*(3*(n30 + n12)**2 - (n21 + n03)**2))
    I8 = n11*((n30 + n21)**2 - (n03 + n21)**2) - (n20 - n02)*(n30 + n21)*(n03 + n21)
    return np.array([I1,I2,I3,I4,I5,I6,I7,I8])



class RotationInvMoments(Feature.BaseFeature):
    name = 'RotationInvMoments'
    description = """Rotation Inveriant Moments"""
    length = 8

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        return rotation_invariant_moments(im)


class ScaleInvMoments(Feature.BaseFeature):
    name = 'ScaleInvMoments'
    description = """Scale Invariant Moments for grayscale image in the order n00, n01, n10, n11, n02, n20, n03, n30, n21, n12"""
    length = 10

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        n00 = scale_invarient_moments(im, 0, 0)
        n01 = scale_invarient_moments(im, 0, 1)
        n10 = scale_invarient_moments(im, 1, 0)
        n11 = scale_invarient_moments(im, 1, 1)
        n02 = scale_invarient_moments(im, 0, 2)
        n20 = scale_invarient_moments(im, 2, 0)
        n03 = scale_invarient_moments(im, 0, 3)
        n30 = scale_invarient_moments(im, 3, 0)
        n21 = scale_invarient_moments(im, 2, 1)
        n12 = scale_invarient_moments(im, 1, 2)
        return np.array([n00, n01, n10, n11, n02, n02, n03, n30, n21, n12])


class CentralMoments(Feature.BaseFeature):
    name = 'CentralMoments'
    description = """Moments for grayscale image in the order n00, n01, n10, n11, n02, n20, n03, n30, n21, n12"""
    length = 10

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        u00 = central_moments(im, 0, 0)
        u01 = central_moments(im, 0, 1)
        u10 = central_moments(im, 1, 0)
        u11 = central_moments(im, 1, 1)
        u02 = central_moments(im, 0, 2)
        u20 = central_moments(im, 2, 0)
        u03 = central_moments(im, 0, 3)
        u30 = central_moments(im, 3, 0)
        u21 = central_moments(im, 2, 1)
        u12 = central_moments(im, 1, 2)
        return np.array([u00, u01, u10, u11, u02, u02, u03, u30, u21, u12])

class RawMoments(Feature.BaseFeature):
    name = 'RawMoments'
    description = """Raw moments with out any invariants in the order n00, n01, n10, n11, n02, n20, n03, n30, n21, n12"""
    length = 10

    def calculate(self, resource):
        except_image_only(resource)
        im = image2numpy(resource.image, remap='gray')
        m00 = raw_moments(im, 0, 0)
        m01 = raw_moments(im, 0, 1)
        m10 = raw_moments(im, 1, 0)
        m11 = raw_moments(im, 1, 1)
        m02 = raw_moments(im, 0, 2)
        m20 = raw_moments(im, 2, 0)
        m03 = raw_moments(im, 0, 3)
        m30 = raw_moments(im, 3, 0)
        m21 = raw_moments(im, 2, 1)
        m12 = raw_moments(im, 1, 2)
        return  np.array([m00, m01, m10, m11, m02, m02, m03, m30, m21, m12])

#requires the implimetation of input parameters to fs
#class LBP2(Feature.BaseFeature):
#    name = 'LBP2'
#    description =
#    length =
#
#    def calculate(self, resource, **kwargs):
#        """
#            resource: image
#            P: (int) Number of circularly symmetric neighbour set points (quantization of the angular space).
#            R: (float) Radius of circle (spatial resolution of the operator).
#            method: {'default': 'original local binary pattern which is gray scale but not rotation invariant',
#                     'ror': 'extension of default implementation which is gray scale and rotation invariant'
#                     'uniform': 'improved rotation invariance with uniform patterns and finer quantization of
#                     the angular space which is gray scale and rotation invariant.'
#                     'var': 'rotation invariant variance measures of the contrast of local image texture which
#                     is rotation but not gray scale invariant.'}
#        """
#        except_image_only(resource)
#        P = kwargs['P']
#        R = kwargs['R']
#        method = kwargs['method']
#        local_binary_pattern(resource.image, P, R, method=method)
