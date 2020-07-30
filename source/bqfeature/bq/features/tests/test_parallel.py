"""
    test_parallel.py

    Checks all the feature inputs and vectors output
    - features
    
    Only tests against the bisque features with hdf
    response.
    Checks against a pre-calculated features.
"""
from nose.plugins.attrib import attr
import utils
from utils import TestNameSpace
from nose import with_setup
from assert_util import parallel_check_feature as check_feature

#############################################
###   TEST SETUP AND FIXTURES
#############################################

NS = TestNameSpace()

def setUp():
    """ Setup feature requests test """
    utils.setup_parallel_feature_test(NS)
    utils.setup_parallel_image_upload(NS)

def tearDown():
    """ Teardown feature requests test """
    utils.tear_down_parallel_feature_test(NS)
    utils.teardown_parallel_image_remove(NS)

def setup_image_upload():
    pass
    #utils.setup_parallel_image_upload(NS)
    
def teardown_image_remove():
    pass
    #utils.teardown_parallel_image_remove(NS)
    

##################################
###     Test Features
##################################

@attr('Test')
@with_setup(setup_image_upload, teardown_image_remove)
def test_SimpleTestFeature(): #failed WindowsError: exception: access violation reading 0x0000000000000000
    """
        Parallel Test SimpleTestFeature
    """
    name = 'SimpleTestFeature'
    test_name = 'test_SimpleTestFeature'
    check_feature(NS, test_name, name, NS.image_uri)


@attr('Test')
@with_setup(setup_image_upload, teardown_image_remove)
def test_UncachedTestFeature():
    """
        Parallel Test UncachedTestFeature
    """
    name = 'UncachedTestFeature'
    test_name = 'test_UncachedTestFeature'
    check_feature(NS, test_name, name, NS.image_uri)   

###################################
####     VRL Features
###################################

@attr('VRL')
@with_setup(setup_image_upload, teardown_image_remove)
def test_HTD(): #failed WindowsError: exception: access violation reading 0x0000000000000000
    """
        Test HTD request
    """
    name = 'HTD'
    test_name = 'test_HTD'
    check_feature(NS, test_name, name, NS.image_uri)


@attr('VRL')
@with_setup(setup_image_upload, teardown_image_remove)
def test_EHD():
    """
        Test EHD request
    """
    name = 'EHD'
    test_name = 'test_EHD'
    check_feature(NS, test_name, name, NS.image_uri)   
    
    
###################################
#### MPEG7Flex Features
###################################
@attr('MPEG7Flex')
@with_setup(setup_image_upload, teardown_image_remove)
def test_CLD():
    """
        Test CLD
    """
    name = 'CLD'
    test_name = 'test_CLD'
    check_feature(NS, test_name, name, NS.image_uri)
    

@attr('MPEG7Flex')
@with_setup(setup_image_upload, teardown_image_remove)
def test_CSD():
    """
        Test CSD
    """
    name = 'CSD'
    test_name = 'test_CSD'
    check_feature(NS, test_name, name, NS.image_uri)
    

@attr('MPEG7Flex')
@with_setup(setup_image_upload, teardown_image_remove)
def test_SCD():
    """
        Test SCD
    """
    name = 'SCD'
    test_name = 'test_SCD'
    check_feature(NS, test_name, name, NS.image_uri)


@attr('MPEG7Flex')
@with_setup(setup_image_upload, teardown_image_remove)
def test_DCD(): #error is occuring
    """
        Test DCD
    """
    name = 'DCD'
    test_name = 'test_DCD'
    check_feature(NS, test_name, name, NS.image_uri)


@attr('MPEG7Flex')
@with_setup(setup_image_upload, teardown_image_remove)
def test_HTD2():
    """
        Test HTD2
    """
    name = 'HTD2'
    test_name = 'test_HTD2'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('MPEG7Flex')
@with_setup(setup_image_upload, teardown_image_remove)
def test_EHD2():
    """
        Test EHD2
    """
    name = 'EHD2'
    test_name = 'test_EHD2'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('MPEG7Flex')
@with_setup(setup_image_upload, teardown_image_remove)
def test_RSD():
    """
        Test RSD
    """
    name = 'RSD'
    test_name = 'test_RSD'
    check_feature(NS, test_name, name, NS.image_uri)

    
####################################
##### WNDCharm Features
####################################
@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Chebishev_Statistics():
    """
        Test Chebishev Statistics
    """
    name = 'Chebishev_Statistics'
    test_name = 'test_Chebishev_Statistics'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Chebyshev_Fourier_Transform():
    """
        Test Chebyshev Fourier Transform
    """
    name = 'Chebyshev_Fourier_Transform'
    test_name = 'test_Chebyshev_Fourier_Transform'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Color_Histogram():
    """
        Test Color Histogram
    """
    name = 'Color_Histogram'
    test_name = 'test_Color_Histogram'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_TestComb_Moments():
    """
        Test TestComb Moments
    """
    name = 'Comb_Moments'
    test_name = 'test_TestComb_Moments'
    check_feature(NS, test_name, name, NS.image_uri)
    
@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Edge_Features():
    """
        Test Edge Features
    """
    name = 'Edge_Features'
    test_name = 'test_Edge_Features'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Fractal_Features():
    """
        Test Fractal Features
    """
    name = 'Fractal_Features'
    test_name = 'test_Fractal_Features'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Gini_Coefficient():
    """
        Test Gini Coefficient
    """
    name = 'Gini_Coefficient'
    test_name = 'test_Gini_Coefficient'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm') #has fftw
@with_setup(setup_image_upload, teardown_image_remove)
def test_Gabor_Textures():
    """
        Test Gabor Textures
    """
    name = 'Gabor_Textures'
    test_name = 'test_Gabor_Textures'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Haralick_Textures():
    """
        Test Haralick Textures
    """
    name = 'Haralick_Textures'
    test_name = 'test_Haralick_Textures'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Multiscale_Historgram():
    """
        Test Multiscale Historgram
    """
    name = 'Multiscale_Historgram'
    test_name = 'test_Multiscale_Historgram'
    check_feature(NS, test_name, name, NS.image_uri)

# Giving removing from the feature set
# WindowsError: exception: access violation reading 0x0000000415AE314C
@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Object_Feature():
    """
        Test Object Feature
    """
    name = 'Object_Feature'
    test_name = 'test_Object_Feature'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Inverse_Object_Features():
    """
        Test Inverse Object Features
    """
    name = 'Inverse_Object_Features'
    test_name = 'test_Inverse_Object_Features'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Pixel_Intensity_Statistics():
    """
        Test Pixel Intensity Statistics
    """
    name = 'Pixel_Intensity_Statistics'
    test_name = 'test_Pixel_Intensity_Statistics'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Radon_Coefficients():
    """
        Test Radon Coefficients
    """
    name = 'Radon_Coefficients'
    test_name = 'test_Radon_Coefficients'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Tamura_Textures():
    """
        Test Tamura Textures
    """
    name = 'Tamura_Textures'
    test_name = 'test_Tamura_Textures'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('WNDCharm')
@with_setup(setup_image_upload, teardown_image_remove)
def test_Zernike_Coefficients():
    """
        Test Zernike Coefficients
    """
    name = 'Zernike_Coefficients'
    test_name = 'test_Zernike_Coefficients'
    check_feature(NS, test_name, name, NS.image_uri)


# return an exception since the area is too small
# to find any keypoints
#############################################
#### OpenCV Features
#############################################
#@attr('opencv')
#@with_setup(setup_image_upload, teardown_image_remove)
#def test_BRISK():
#    """
#        Test BRISK
#    """
#    name = 'BRISK'
#    test_name = 'test_BRISK'
#    check_feature(NS, test_name, name, NS.image_uri)
#
#
#@attr('opencv')
#@with_setup(setup_image_upload, teardown_image_remove)
#def test_ORB():
#    """
#        test ORB
#    """
#    name = 'ORB'
#    test_name = 'test_ORB'
#    check_feature(NS, test_name, name, NS.image_uri)
#      
#
#@attr('opencv')
#@with_setup(setup_image_upload, teardown_image_remove)
#def test_SIFT():
#    """
#        Test SIFT
#    """
#    name = 'SIFT'
#    test_name = 'test_SIFT'
#    check_feature(NS, test_name, name, NS.image_uri)
#    
#    
#@attr('opencv')
#@with_setup(setup_image_upload, teardown_image_remove)
#def test_SURF():
#    """
#        Test SURF
#    """
#    name = 'SURF'
#    test_name = 'test_SURF'
#    check_feature(NS, test_name, name, NS.image_uri)
#    

##############################################
##### Mahotas Features
##############################################
@attr('Mahotas')
@with_setup(setup_image_upload, teardown_image_remove)
def test_LBP():
    """
        Test LBP
    """
    name = 'LBP'
    test_name = 'test_LBP'
    check_feature(NS, test_name, name, NS.image_uri)
    
@attr('Mahotas')
@with_setup(setup_image_upload, teardown_image_remove)
def test_PFTAS():
    """
        Test PFTAS
    """
    name = 'PFTAS'
    test_name = 'test_PFTAS'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('Mahotas')
@with_setup(setup_image_upload, teardown_image_remove)
def test_PFTASColored():
    """
        Test PFTASColored
    """
    name = 'PFTASColored'
    test_name = 'test_PFTASColored'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('Mahotas')
@with_setup(setup_image_upload, teardown_image_remove)
def test_TAS():
    """
        Test TAS 
    """
    name = 'TAS'
    test_name = 'test_TAS'
    check_feature(NS, test_name, name, NS.image_uri)
    
@attr('Mahotas')
@with_setup(setup_image_upload, teardown_image_remove)
def test_TASColored():
    """
        Test TASColored
    """
    name = 'TASColored'
    test_name = 'test_TASColored'    
    check_feature(NS, test_name, name, NS.image_uri)

@attr('Mahotas')
@with_setup(setup_image_upload, teardown_image_remove)
def test_ZM():
    """
        Test ZM
    """
    name = 'ZM'
    test_name = 'test_ZM'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('Mahotas')
@with_setup(setup_image_upload, teardown_image_remove)
def test_HARColored():
    """
        Test HARColored
    """
    name = 'HARColored'
    test_name = 'test_HARColored'
    check_feature(NS, test_name, name, NS.image_uri)

@attr('Mahotas')
@with_setup(setup_image_upload, teardown_image_remove)
def test_HAR():
    """
        Test HAR
    """
    name = 'HAR'
    test_name = 'test_HAR'
    check_feature(NS, test_name, name, NS.image_uri)
    
#def test_FFTSD(FeatureBase):
#    name = 'FFTSD'
#    family_name = 'MyFeatures'
#    test_name = 500
#    input_resource = ['polygon']