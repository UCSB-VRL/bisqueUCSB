from ctypes import CDLL, c_void_p, c_int, c_double, c_char_p, c_bool
from numpy import ctypeslib, asarray, empty
from numpy.ctypeslib import ndpointer
import numpy as np
import sys
import os
import inspect
from bq.util.paths import run_path

#Notes
#    add documentation
#    add the other features
#    have all the features return the correct type

#path=os.path.dirname(__file__) #os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentfname()))) #find current dir of the file
#path = os.path.join(path,'..','..','..','..','src','extractors','WNDCharm','lib')
#_WNDCharmLib = np.ctypeslib.load_library('_WNDCharmLib', path)

_WNDCharmLib=None
def load_lib():
    global _WNDCharmLib
    if _WNDCharmLib is None:
        path = run_path ('bqfeature', 'bq', 'src','extractors', 'WNDCharm','lib')
        _WNDCharmLib = np.ctypeslib.load_library('_WNDCharmLib', path)
    return _WNDCharmLib



def extractChebyshevCoefficients(im):
    """
    Chebyshev Coefficients -

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 32
    """
    load_lib()
    descSize = 32

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape

    #initalizing function arguments
    _WNDCharmLib.Chebyshev_Coefficients.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Chebyshev_Coefficients.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Chebyshev_Coefficients(im, int(height), int(width), result)
    return result


def extractChebyshevFourierCoefficients(im):
    """
    Chebyshev Fourier Coefficients -

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 32
    """
    load_lib()
    descSize = 32

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Chebyshev_Fourier_Coefficients.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Chebyshev_Fourier_Coefficients.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Chebyshev_Fourier_Coefficients(im, int(height), int(width), result)
    return result


def extractCombFirstFourMoments(im):
    """
    Comb First Four Moments -

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type int feature of length 48
    """
    load_lib()
    descSize = 48

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Comb_First_Four_Moments.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Comb_First_Four_Moments.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Comb_First_Four_Moments(im, int(height), int(width), result)
    return result

def extractGaborTextures(im):
    """
    Gabor Textures -

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 7

    broken right now
    needs to have imaginary number implemented correctly
    """
    load_lib()
    descSize = 7

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Gabor_Textures.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Gabor_Textures.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Gabor_Textures(im,  int(height), int(width), result)
    return result

def extractHaralickTextures(im):
    """
    Haralick Textures -

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 28
    """
    load_lib()
    descSize = 28

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Haralick_Textures.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Haralick_Textures.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Haralick_Textures(im, int(height), int(width), result)
    return result

def extractMultiscaleHistograms(im):
    """
    Multiscale Histograms

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 24
    """
    load_lib()
    descSize = 24

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Multiscale_Histograms.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Multiscale_Histograms.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Multiscale_Histograms(im, int(height), int(width), result)
    return result

def extractRadonCoefficients(im):
    """
    Radon Coefficients

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 12
    """
    load_lib()
    descSize = 12

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Radon_Coefficients.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Radon_Coefficients.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Radon_Coefficients(im, int(height), int(width), result)
    return result

def extractTamuraTextures(im):
    """
    Tamura Testures:

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 6
    """
    load_lib()
    descSize = 6

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Tamura_Textures.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Tamura_Textures.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Tamura_Textures(im, int(height), int(width), result)
    return result

def extractZernikeCoefficients(im):
    """
    Zernike Coefficients:

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 72
    """
    load_lib()
    descSize = 72

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Zernike_Coefficients.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Zernike_Coefficients.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Zernike_Coefficients(im, int(height), int(width), result)
    return result

def extractPixelIntensityStatistics(im):
    """
    Pixel Intensity Statistics

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 5
    """
    load_lib()
    descSize = 5

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Pixel_Intensity_Statistics.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Pixel_Intensity_Statistics.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Pixel_Intensity_Statistics(im, int(height), int(width), result)
    return result

def extractColorHistogram(im):
    """
    Color Histogram

    @im   - a mxnx3 numpy unit matrix (rgb image matrix) (will except mxn but will convert it to s mxnx3 uint matrix)

    @result - a type double feature of length 20
    """
    load_lib()
    descSize = 20

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

    height, width, channel = tmp.shape
    _WNDCharmLib.Color_Histogram.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Color_Histogram.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Color_Histogram(im, int(height), int(width), result)
    return result

def extractFractalFeatures(im):
    """
    Fractal Features

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 20
    """
    load_lib()
    descSize = 20

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Fractal_Features.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Fractal_Features.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Fractal_Features(im, int(height), int(width), result)
    return result

def extractEdgeFeatures(im):
    """
    Fractal Features

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 28
    """
    load_lib()
    descSize = 28

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Edge_Features.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Edge_Features.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Edge_Features(im, int(height), int(width), result)
    return result

def extractObjectFeatures(im):
    """
    Object Features

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 34
    """
    load_lib()
    descSize = 34

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Object_Features.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Object_Features.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Object_Features(im, int(height), int(width), result)
    return result

def extractInverseObjectFeatures(im):
    """
    Inverse Object Features -

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 34
    """
    load_lib()
    descSize = 34

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Inverse_Object_Features.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Inverse_Object_Features.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Inverse_Object_Features(im, int(height), int(width), result)
    return result

def extractGiniCoefficient(im):
    """
    Gini Coefficient -

    @im - a mxn numpy double matrix (grayscale image matrix) (convert everything to double)

    @result - a type double feature of length 1
    """
    load_lib()
    descSize = 1

    #check if the image is in the correct format
    tmp = np.asarray(im)
    if not len(tmp.shape)==2:
        raise TypeError("Requires a grayscale image")

    height, width = tmp.shape
    _WNDCharmLib.Gini_Coefficient.argtypes = [ \
            np.ctypeslib.ndpointer(dtype = np.double ),\
            c_int, c_int,\
            np.ctypeslib.ndpointer(dtype = np.double)]
    _WNDCharmLib.Gini_Coefficient.restype = c_void_p

    im = tmp.astype(np.double)
    result = np.empty([descSize], dtype=np.double)
    _WNDCharmLib.Gini_Coefficient(im, int(height), int(width), result)
    return result

if __name__ == '__main__':
    import cv2
    import time
    im=cv2.imread('test.jpg',cv2.CV_LOAD_IMAGE_GRAYSCALE) #CV_LOAD_IMAGE_GRAYSCALE CV_LOAD_IMAGE_COLOR
    start=time.time()
    feature=extractChebyshevFourierCoefficients(im)
    end=time.time()
    print 'time elapsed: %s'%str(end-start)
