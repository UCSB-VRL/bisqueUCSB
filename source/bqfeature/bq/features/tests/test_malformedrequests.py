"""
    test_malformedrequest.py

    Checks all the malformed feature request types
    - documentation
    - features format responses (using the test features)
    - uncached, cached, w/ parameters, multivector features
    
    Does not test against any really features only
    custom test features to test the functionality
    of the feature service. 
"""
from nose.plugins.attrib import attr
import utils
from utils import TestNameSpace
from nose import with_setup
from assert_util import check_response

    
NS = TestNameSpace()

def setUp():
    """ Setup feature requests test """
    utils.setup_simple_feature_test(NS)

def tearDown():
    """ Teardown feature requests test """
    utils.tear_down_simple_feature_test(NS)

def setup_image_upload():
    utils.setup_image_upload(NS)
    
def teardown_image_remove():
    utils.teardown_image_remove(NS)

############################################
###     Malformed Requests
############################################

@attr('malformed')
@with_setup(setup_image_upload, teardown_image_remove)
def test_multible_same_element_types():
    name = 'multible_same_element_types'
    response_code = 400
    request = '%s/features/SimpleTestFeature/xml?image=%s&image=%s' % (NS.root, NS.image_uri, NS.image_uri)
    check_response(NS.session, request, response_code)

@attr('malformed')
@with_setup(setup_image_upload, teardown_image_remove)
def test_nonlisted_feature():
    name = 'nonlisted_feature'
    response_code = 404
    request = '%s/features/asdf/xml?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)

@attr('malformed')
@with_setup(setup_image_upload, teardown_image_remove)
def test_nonlisted_format():
    name = 'nonlisted_format' 
    response_code = 404
    request = '%s/features/SimpleTestFeature/sadf?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)
    
@attr('malformed')
@with_setup(setup_image_upload, teardown_image_remove)
def test_incorrect_resource_input_type():
    name = 'incorrect_resource_input_type'
    response_code = 400
    request = '%s/features/SimpleTestFeature/xml?stuff=%s'%(NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)
                     
@attr('malformed')
def test_documentation_incorrect_feature():
    name = 'documentation_of_incorrect_feature'
    response_code = 404
    request = '%s/features/asdf' % NS.root
    check_response(NS.session, request, response_code)

@attr('malformed')
def test_documentation_incorrect_format():
    name = 'documentation_of_incorrect_format'
    response_code = 404
    request = '%s/features/format/asdf' % NS.root
    check_response(NS.session, request, response_code)

@attr('malformed')
def test_get_without_a_resource():
    name = 'get_without_a_resource'
    response_code = 400
    request = '%s/features/SimpleTestFeature/xml' % NS.root
    check_response(NS.session, request, response_code)
    
@attr('malformed')
def test_post_without_a_body():
    name = 'post_without_a_body'
    response_code = 400
    request = '%s/features/SimpleTestFeature/xml' % NS.root
    check_response(NS.session, request, response_code, method='POST')

#############################################
####     Malformed or Inaccesable Resources
#############################################

def test_simple_test_feature_resource_type_not_found_xml():
    name = 'simple_test_feature_resource_type_not_found_simple'
    response_code = 200
    request = '%s/features/SimpleTestFeature/xml?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_simple_test_feature_resource_type_not_found_csv():
    name = 'simple_test_feature_resource_type_not_found_simple'
    response_code = 200
    request = '%s/features/SimpleTestFeature/csv?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_simple_test_feature_resource_type_not_found_hdf():
    name = 'simple_test_feature_resource_type_not_found_simple'
    response_code = 200
    request = '%s/features/SimpleTestFeature/hdf?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_uncached_test_feature_resource_type_not_found_xml():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/UncachedTestFeature/xml?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_uncached_test_feature_resource_type_not_found_csv():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/UncachedTestFeature/csv?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_uncached_test_feature_resource_type_not_found_hdf():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/UncachedTestFeature/hdf?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)


def test_parameter_test_feature_resource_type_not_found_xml():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/ParametersTestFeature/xml?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_parameter_test_feature_resource_type_not_found_csv():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/ParametersTestFeature/csv?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_parameter_test_feature_resource_type_not_found_hdf():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/ParametersTestFeature/hdf?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_uncached_parameter_test_feature_resource_type_not_found_xml():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/UncachedParametersTestFeature/xml?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_uncached_parameter_test_feature_resource_type_not_found_csv():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/UncachedParametersTestFeature/csv?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)
    
def test_uncached_parameter_test_feature_resource_type_not_found_hdf():
    name = 'resource_type_not_found'
    response_code = 200
    request = '%s/features/UncachedParametersTestFeature/hdf?image=%s/image_service/image/notaresource'%(NS.root, NS.root)
    check_response(NS.session, request, response_code)

@with_setup(setup_image_upload, teardown_image_remove)
def test_simple_test_feature_gobject_not_found():
    name = 'feature_calculation_error'
    response_code = 200
    request = '%s/features/SimpleTestFeature/xml?image=%s&gobject=%s/image_service/image/notaresource'%(NS.root, NS.image_uri, NS.root)
    check_response(NS.session, request, response_code)

@with_setup(setup_image_upload, teardown_image_remove)
def test_feature_calculation_error():
    name = 'feature_calculation_error'
    response_code = 200
    request = '%s/features/ExceptionTestFeature/xml?image=%s'%(NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)

    
    
                                                            