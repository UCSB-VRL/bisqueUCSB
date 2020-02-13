from ctypes import CDLL, c_void_p, c_int, c_double, c_char_p, c_bool
from numpy import ctypeslib, asarray, empty
from numpy.ctypeslib import ndpointer
import numpy as np
import sys
import os
import inspect
from bq.util.paths import run_path

#Notes
#    add masks to all
#    add documentation
#    add the other features

#path = os.path.dirname(__file__) #find current dir of the file#find current dir of the file
#path = os.path.join(path,'..','..','..','..','src','extractors','MPEG7Flex','lib')
#_MPEG7FlexLib = np.ctypeslib.load_library('_MPEG7FlexLib', path)
_MPEG7FlexLib = None


def load_MPEG7FlexLib():
    global _MPEG7FlexLib
    if _MPEG7FlexLib is None:
        path = run_path ('bqfeature', 'bq', 'src','extractors','MPEG7Flex','lib')
        _MPEG7FlexLib = np.ctypeslib.load_library('_MPEG7FlexLib', path)
    return _MPEG7FlexLib

def extractCSD(im, mask = np.array([]), descSize=64):
    """
    Color Structure Descriptor -

    @im   - a mxnx3 numpy unit matrix (rgb image matrix) (will except mxn but will convert it to s mxnx3 uint matrix)
    @mask - a mxn numpy binary matrix (will except mxn non bool but will threshold the image)
    @descSize - length of the descriptor (only excepts 16,32,64,128,256, if not those values will default to 64)

    @result - a uint feature of length specified
    """
    load_MPEG7FlexLib()
    #check descSize
    if descSize not in set([16,32,64,128,256]):
        descSize = 64

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if len(tmp.shape)==3:
        if not tmp.shape[2]==3:
            raise TypeError("Requires a 3 channel rgb image")
    elif len(tmp.shape)==2:
        #convert gray scale to 3 channeled
        tmp = np.concatenate([tmp[..., np.newaxis] for i in range(3)], axis=2)
    else:
        raise TypeError("Requires a 3 channel rgb image")

    cols, rows, channel = tmp.shape

    #check for correctly formated mask
    if mask.any(): # pylint: disable=no-member
        if len(mask.shape)==2:
            hasmask = True
            mask = np.asarray(mask)
            mcols , mrows= mask.shape
            if mcols!=cols or mrows!=rows:
                raise TypeError("The column and row vectors must be equal between")
        else:
            raise TypeError("Mask is required to be a mxn bool matrix")
    else:
        hasmask = False
        mask = np.asarray(np.ones([cols,rows]))

    _MPEG7FlexLib.computeCSD.argtypes = [ \
            ndpointer(dtype = np.uint8 ),  c_int,\
            c_int, c_int,\
            c_bool, ndpointer(dtype = np.bool_ ),\
            ndpointer(dtype = np.uint8)]
    _MPEG7FlexLib.computeCSD.restype = c_void_p

    im = tmp.astype(np.uint8)
    mask = mask.astype(np.bool_) # pylint: disable=no-member

    result = np.empty([descSize], dtype=np.uint8)
    _MPEG7FlexLib.computeCSD(im, descSize, int(rows), int(cols), hasmask , mask, result)
    return result


def extractSCD(im, mask = np.array([]), descSize=64):
    """
    Scalable Color Descriptor -

    @im   - a mxnx3 numpy unit matrix (rgb image matrix) (will except mxn but will convert it to s mxnx3 uint matrix)
    @mask - a mxn numpy binary matrix (will except mxn non bool but will threshold the image)
    @descSize - length of the descriptor (only excepts 16,32,64,128,256, if not those values will default to 64)

    @result - a uint feature of length specified
    """
    load_MPEG7FlexLib()
    #check descSize
    if descSize not in set([16,32,64,128,256]):
        descSize = 64

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if len(tmp.shape)==3:
        if not tmp.shape[2]==3:
            raise TypeError("Requires a 3 channel rgb image")
    elif len(tmp.shape)==2:
        #convert gray scale to 3 channeled
        tmp = np.concatenate([tmp[..., np.newaxis] for i in range(3)], axis=2)
    else:
        raise TypeError("Requires a 3 channel rgb image")

    cols, rows, channel = tmp.shape

    #check for correctly formated mask
    if mask.any(): # pylint: disable=no-member
        if len(mask.shape)==2:
            hasmask = True
            mask = np.asarray(mask)
            mcols , mrows= mask.shape
            if mcols!=cols or mrows!=rows:
                raise TypeError("The column and row vectors must be equal between")
        else:
            raise TypeError("Mask is required to be a mxn bool matrix")
    else:
        hasmask = False
        mask = np.asarray(np.ones([cols,rows]))

    _MPEG7FlexLib.computeSCD.argtypes = [ \
            ndpointer(dtype = np.uint8 ),  c_int,\
            c_int, c_int,\
            c_bool, ndpointer(dtype = np.bool_ ),\
            ndpointer(dtype = np.uint8)]
    _MPEG7FlexLib.computeSCD.restype = c_void_p

    im = tmp.astype(np.uint8)
    mask = mask.astype(np.bool_) # pylint: disable=no-member

    result = np.empty([descSize], dtype=np.uint8)

    _MPEG7FlexLib.computeSCD(im, descSize, int(rows), int(cols), hasmask , mask, result)
    return result


def extractCLD(im, mask = np.array([]), numYCoef=64, numCCoef = 28):
    """
    Color Layout Descriptor -

    @im   - a mxnx3 numpy unit matrix (rgb image matrix) (will except mxn but will convert it to s mxnx3 uint matrix)
    @mask - a mxn numpy binary matrix (will except mxn non bool but will threshold the image)
    @numYCoef - number of y coeffiencts (only excepts 3,6,10,15,21,28,64 if not those values will default to 64)
    @numCCoef - number of c coeffiencts (for both Cb and Cr) (only excepts 3,6,10,15,21,28,64 if not those values will default to 28)

    @result - a uint feature of length specified as a combination of number of y and c coeffiences (length = y+2*c)
    """
    load_MPEG7FlexLib()
    #check descSize
    if numYCoef not in set([3,6,10,15,21,28,64]):
        numYCoef = 64

    if numCCoef not in set([3,6,10,15,21,28,64]):
        numCCoef = 28

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if len(tmp.shape)==3:
        if not tmp.shape[2]==3:
            raise TypeError("Requires a 3 channel rgb image")
    elif len(tmp.shape)==2:
        #convert gray scale to 3 channeled
        tmp = np.concatenate([tmp[..., np.newaxis] for i in range(3)], axis=2)
    else:
        raise TypeError("Requires a 3 channel rgb image")

    cols, rows, channel = tmp.shape

    #check for correctly formated mask
    if mask.any(): # pylint: disable=no-member
        if len(mask.shape)==2:
            hasmask = True
            mask = np.asarray(mask)
            mcols , mrows= mask.shape
            if mcols!=cols or mrows!=rows:
                raise TypeError("The column and row vectors must be equal between")
        else:
            raise TypeError("Mask is required to be a mxn bool matrix")
    else:
        hasmask = False
        mask = np.asarray(np.ones([cols,rows]))

    _MPEG7FlexLib.computeCLD.argtypes = [ \
            ndpointer(dtype = np.uint8 ),  c_int, c_int,\
            c_int, c_int,\
            c_bool, ndpointer(dtype = np.bool_ ),\
            ndpointer(dtype = np.uint8)]
    _MPEG7FlexLib.computeCLD.restype = c_void_p

    im = tmp.astype(np.uint8)
    mask = mask.astype(np.bool_) # pylint: disable=no-member

    result = np.empty([(numYCoef+2*numCCoef)], dtype=np.uint8)
    _MPEG7FlexLib.computeCLD(im, numYCoef, numCCoef, int(rows), int(cols), hasmask, mask, result)
    return result


def extractDCD(im, mask = np.array([]), normalize=True, variance=False, spatial=False, bin1=32, bin2=32, bin3=32):
    """
    Dominent Color Descriptor -

    @im   - a mxnx3 numpy unit matrix (rgb image matrix) (will except mxn but will convert it to s mxnx3 uint matrix)
    @mask - a mxn numpy binary matrix (will except mxn non bool but will threshold the image)
    @normalize - flag to normalize the output feature (default: True)
    @variance - flag to return the varience of the feature (default: False)
    @spatial - flag to return spatial information of the feature (default: False)
    @bin1 - number of bins for the first channel (1-255)(default: 32)
    @bin2 - number of bins for the second channel (1-255)(default: 32)
    @bin3 - number of bins for the third channel (1-255)(default: 32)

    @result - the resulting dominent color descriptor
    @spatial - spactial information, will be returned if the spatial flag is set
    """
    load_MPEG7FlexLib()

    #check parameters
    if normalize not in set([True,False]):
        normalize = True

    if variance not in set([True,False]):
        variance = False

    if spatial not in set([True,False]):
        spatial = False

    if bin1<=0 or bin1>=256:
        bin1 = 32

    if bin2<=0 or bin2>=256:
        bin2 = 32

    if bin3<=0 or bin3>=256:
        bin3 = 32


    #check if the image is in the correct format
    tmp = np.asarray(im)
    if len(tmp.shape)==3:
        if not tmp.shape[2]==3:
            raise TypeError("Requires a 3 channel rgb image")
    elif len(tmp.shape)==2:
        #convert gray scale to 3 channeled
        tmp = np.concatenate([tmp[..., np.newaxis] for i in range(3)], axis=2)
    else:
        raise TypeError("Requires a 3 channel rgb image")

    cols, rows, channel = tmp.shape

    #check for correctly formated mask
    if mask.any(): # pylint: disable=no-member
        if len(mask.shape)==2:
            hasmask = True
            mask = np.asarray(mask)
            mcols , mrows= mask.shape
            if mcols!=cols or mrows!=rows:
                raise TypeError("The column and row vectors must be equal between")
        else:
            raise TypeError("Mask is required to be a mxn bool matrix")
    else:
        hasmask = False
        mask = np.asarray(np.ones([cols,rows]))

    _MPEG7FlexLib.computeDCD.argtypes = [ \
            ndpointer(dtype = np.uint8 ), \
            c_bool, ndpointer(dtype = np.bool_ ),\
            c_bool, c_bool, c_bool,\
            c_int, c_int, c_int,\
            c_int, c_int,\
            ndpointer(dtype = np.intc),
            ndpointer(dtype = np.uint8),
            ndpointer(dtype = np.uint8)]
    _MPEG7FlexLib.computeDCD.restype = c_void_p

    im = tmp.astype(np.uint8)
    mask = mask.astype(np.bool_) # pylint: disable=no-member

    length = np.empty([1], dtype=np.intc)
    results = np.empty([300], dtype=np.uint8) #has a buffer of 300
    spatial_output = np.empty([1], dtype=np.uint8)
    _MPEG7FlexLib.computeDCD(im, hasmask, mask, normalize, variance, spatial, bin1, bin2, bin3,int(rows), int(cols), length, results, spatial_output)

    if variance:
        dcdlength = 7 * length[0]
    else:
        dcdlength = 4 * length[0]
    if dcdlength>300:
        print 'Warning: not all the values to the DCD, buffer was exceeded'

    if spatial:
        return results[:dcdlength], spatial_output
    else:
        return results[:dcdlength]


def extractHTD(im, enrg_dev=True):
    """
    Homogenious Texture Descriptor -

    @im   - a mxn numpy unit matrix (grayscale image matrix)
    @enrg_dev - set to return energy devation along with the mean (lengths the feature from 32 to 64 dimensions)(default: True)

    @result - the resulting Homogenious Texture Descriptor with given length
    """
    load_MPEG7FlexLib()
    #check parameters
    if enrg_dev not in set([True,False]):
        enrg_dev = True


    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    cols, rows = tmp.shape


    _MPEG7FlexLib.computeHTD.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.uint8, flags='C_CONTIGUOUS' ),  c_bool,\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.uint8, flags='C_CONTIGUOUS' )]
    _MPEG7FlexLib.computeHTD.restype = c_void_p

    im = tmp.astype(np.uint8)

    if enrg_dev:
        descSize = 62
    else:
        descSize = 32

    result = np.empty([descSize], dtype=np.uint8)
    _MPEG7FlexLib.computeHTD(im, enrg_dev, int(rows), int(cols), result)
    return result


def extractEHD(im,  mask = np.array([])):
    """
    Edge Histogram Descriptor -

    @im   - a mxnx3 numpy unit matrix (rgb image matrix) (will except mxn but will convert it to s mxnx3 uint matrix)
    @mask - a mxn numpy binary matrix (will except mxn non bool but will threshold the image)

    @result - the resulting dominent color descriptor
    """
    load_MPEG7FlexLib()
    #check if the image is in the correct format
    tmp = np.asarray(im)
    if len(tmp.shape)==3:
        if not tmp.shape[2]==3:
            raise TypeError("Requires a 3 channel rgb image")
    elif len(tmp.shape)==2:
        #convert gray scale to 3 channeled
        tmp = np.concatenate([tmp[..., np.newaxis] for i in range(3)], axis=2)
    else:
        raise TypeError("Requires a 3 channel rgb image")

    cols, rows, channel = tmp.shape

    #check for correctly formated mask
    if mask.any(): # pylint: disable=no-member
        if len(mask.shape)==2:
            hasmask = True
            mask = np.asarray(mask)
            mcols , mrows= mask.shape
            if mcols!=cols or mrows!=rows:
                raise TypeError("The column and row vectors must be equal between")
        else:
            raise TypeError("Mask is required to be a mxn bool matrix")
    else:
        hasmask = False
        mask = np.asarray(np.ones([cols,rows]))

    _MPEG7FlexLib.computeEHD.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.uint8 ),\
            c_int, c_int,\
            c_bool, np.ctypeslib.ndpointer(dtype = np.bool_ ),\
            np.ctypeslib.ndpointer(dtype = np.uint8)]

    _MPEG7FlexLib.computeEHD.restype = c_void_p

    im = tmp.astype( np.uint8)
    mask = mask.astype( np.bool_) # pylint: disable=no-member

    result = np.empty([80], dtype=np.uint8)
    _MPEG7FlexLib.computeEHD(im, int(rows), int(cols), hasmask, mask, result)
    return result


def extractRSD(im, mask = np.array([])):
    """
    Region Shape Descriptor -

    @im   - a mxnx3 numpy unit matrix (rgb image matrix) (will except mxn but will convert it to s mxnx3 uint matrix)
    @mask - a mxn numpy binary matrix (will except mxn non bool but will threshold the image)

    @result - the resulting region shape descriptor
    """
    #check if the image is in the correct format
    tmp = np.asarray(im)
    if len(tmp.shape)==3:
        if not tmp.shape[2]==3:
            raise TypeError("Requires a 3 channel rgb image")
    elif len(tmp.shape)==2:
        #convert gray scale to 3 channeled
        tmp = np.concatenate([tmp[..., np.newaxis] for i in range(3)], axis=2)
    else:
        raise TypeError("Requires a 3 channel rgb image")

    cols, rows, channel = tmp.shape

    #check for correctly formated mask
    if mask.any(): # pylint: disable=no-member
        if len(mask.shape)==2:
            #hasmask = True
            mask = np.asarray(mask)
            mcols , mrows= mask.shape
            if mcols!=cols or mrows!=rows:
                raise TypeError("The column and row vectors must be equal between")
        else:
            raise TypeError("Mask is required to be a mxn bool matrix")
    else:
        #hasmask = False
        mask = np.asarray( np.ones([cols,rows]))

    _MPEG7FlexLib.computeRSD.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.uint8 ),\
            np.ctypeslib.ndpointer(dtype = np.bool_ ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.uint8)]

    _MPEG7FlexLib.computeRSD.restype = c_void_p

    im = tmp.astype( np.uint8)
    mask = mask.astype( np.bool_) # pylint: disable=no-member
    result = np.empty( [35], dtype = np.uint8)
    _MPEG7FlexLib.computeRSD(im, mask, int(rows), int(cols), result)
    return result



if __name__=='__main__':
    import cv2
    import time

    im=cv2.imread('test.png',cv2.CV_LOAD_IMAGE_COLOR)
    #im=cv2.imread('test2.jpg',cv2.CV_LOAD_IMAGE_COLOR) #CV_LOAD_IMAGE_GRAYSCALE CV_LOAD_IMAGE_COLOR
    mask=cv2.imread('mask.png',cv2.CV_LOAD_IMAGE_GRAYSCALE)
    start = time.time()
    feature = extractDCD(im)#, mask=mask)
    print feature
    #invert mask
    #mask==0
    end=time.time()
    print 'time elapsed: %s'%str(end-start)
