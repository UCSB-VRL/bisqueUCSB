"""
    test_request.py

    Checks all the feature request types
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
    
def setup_dataset_upload():
    utils.setup_dataset_upload(NS)
    
def teardown_dataset_remove():
    utils.teardown_dataset_remove(NS)

#######################################
##         documentation
#######################################
@attr('documentation')
def test_feature_main():
    name = 'feature_main'
    response_code = 200
    request = '%s/features' % NS.root
    check_response(NS.session, request, response_code)


@attr('documentation')
def test_feature_list():
    name = 'feature_list' 
    response_code = 200
    request = '%s/features/list' % NS.root
    check_response(NS.session, request, response_code)


@attr('documentation')
def test_formats():
    name = 'formats' 
    response_code = 200
    request = '%s/features/formats' % NS.root
    check_response(NS.session, request, response_code)


@attr('documentation')
def test_test_feature():
    """
        Testing on a Test Features
    """
    name = 'feature' 
    response_code = 200
    request = '%s/features/SimpleTestFeature' % NS.root
    check_response(NS.session, request, response_code)
    
    
@attr('documentation')
def test_feature_cached():
    """
        Testing on a Cached Test Features
    """
    name = 'feature_cached' 
    response_code = 200
    request = '%s/features/UncachedTestFeature' % NS.root
    check_response(NS.session, request, response_code)

###########################################
##    Feature Requests (simple)
###########################################
@with_setup(setup_image_upload, teardown_image_remove)
def test_get_simple_test_feature_xml():
    """
    """
    name = 'simple_test_feature_xml'
    response_code = 200
    request = '%s/features/SimpleTestFeature/xml?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_simple_test_feature_xml_with_redirected_data_service_url():
    """
    """
    name = 'simple_test_feature_xml'
    response_code = 200
    request = '%s/features/SimpleTestFeature/xml?image=%s' % (NS.root, NS.resource_uri+'/pixels')
    check_response(NS.session, request, response_code)



@with_setup(setup_image_upload, teardown_image_remove)
def test_get_simple_test_feature_xml_returned_from_cache():
    """
    """
    name = 'simple_test_feature_xml'
    response_code = 200
    request = '%s/features/SimpleTestFeature/xml?image=%s' % (NS.root, NS.image_uri)
    NS.session.fetchxml(request) #inital request
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_post_simple_test_feature_xml():
    """
        Posting a single element
    """
    name = 'post_simple_test_feature_xml'
    response_code = 200
    request = '%s/features/SimpleTestFeature/xml' % NS.root
    body = """<feature uri="%s?image=%s"/>""" % (request, NS.image_uri)
    check_response(NS.session, request, response_code, xml=body, method='POST')

@with_setup(setup_dataset_upload, teardown_dataset_remove)
def test_post_simple_test_feature_xml2():
    """
        Posting multple elements
    """
    name = 'post_simple_test_feature_xml2'
    response_code = 200
    request = '%s/features/SimpleTestFeature/xml' % NS.root
    body = """<resource>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        </resource>
    """ % (request, NS.image_uri1, request, NS.image_uri2, request, NS.image_uri3)
    check_response(NS.session, request, response_code, xml=body, method='POST')

@with_setup(setup_image_upload, teardown_image_remove)
def test_get_simple_test_feature_xml_with_mask_and_gobject():
    """
    """
    name = 'get_simple_test_feature_xml_with_mask_and_gobject'
    response_code = 200
    request = '%s/features/SimpleTestFeature/xml?image=%s&mask=%s&gobject=%s'%(NS.root, NS.image_uri, NS.image_uri, NS.image_uri)
    check_response(NS.session, request, response_code)

@with_setup(setup_image_upload, teardown_image_remove)
def test_get_simple_test_feature_csv():
    """
    """
    name = 'simple_test_feature_xml'
    response_code = 200
    request = '%s/features/SimpleTestFeature/csv?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_dataset_upload, teardown_dataset_remove)
def test_post_simple_test_feature_csv():
    """
        Posting multiple elements and returning csv
    """
    name = 'post_simple_test_feature_csv'
    response_code = 200
    request = '%s/features/SimpleTestFeature/csv' % NS.root
    body = """<resource>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        </resource>
    """ % (request, NS.image_uri1, request, NS.image_uri2, request, NS.image_uri3)
    check_response(NS.session, request, response_code, xml=body, method='POST')

@with_setup(setup_image_upload, teardown_image_remove)
def test_get_simple_test_feature_csv_with_mask_and_gobject():
    """
    """
    name = 'get_simple_test_feature_csv_with_mask_and_gobject'
    response_code = 200
    request = '%s/features/SimpleTestFeature/csv?image=%s&mask=%s&gobject=%s'%(NS.root, NS.image_uri, NS.image_uri, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_simple_test_feature_hdf():
    """
    """
    name = 'get_simple_test_feature_hdf'
    response_code = 200
    request = '%s/features/SimpleTestFeature/hdf?image=%s&mask=%s&gobject=%s'%(NS.root, NS.image_uri, NS.image_uri, NS.image_uri)
    check_response(NS.session, request, response_code)

@with_setup(setup_dataset_upload, teardown_dataset_remove)
def test_post_simple_test_feature_hdf():
    """
        Posting multiple elements and returning hdf
    """
    name = 'post_simple_test_feature_hdf'
    response_code = 200
    request = '%s/features/SimpleTestFeature/hdf' % NS.root
    body = """<resource>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        </resource>
    """ % (request, NS.image_uri1, request, NS.image_uri2, request, NS.image_uri3)
    check_response(NS.session, request, response_code, xml=body, method='POST')

@with_setup(setup_image_upload, teardown_image_remove)
def test_get_simple_test_feature_hdf_with_mask_and_gobject():
    """
    """
    name = 'get_simple_test_feature_hdf_with_mask_and_gobject'
    response_code = 200
    request = '%s/features/SimpleTestFeature/hdf?image=%s&mask=%s&gobject=%s'%(NS.root, NS.image_uri, NS.image_uri, NS.image_uri)
    check_response(NS.session, request, response_code)


###########################################
##    Feature Requests (uncached)
###########################################

@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_test_feature_xml():
    """
    """
    name = 'get_uncached_test_feature_xml'
    response_code = 200
    request = '%s/features/UncachedTestFeature/xml?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_dataset_upload, teardown_dataset_remove)
def test_post_uncached_test_feature_xml():
    """
    """
    name = 'post_uncached_test_feature_xml'
    response_code = 200
    request = '%s/features/UncachedTestFeature/xml' % NS.root
    body = """<resource>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        </resource>
    """ % (request, NS.image_uri1, request, NS.image_uri2, request, NS.image_uri3)
    check_response(NS.session, request, response_code, xml=body, method='POST')


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_test_feature_xml_with_mask_and_gobject():
    """
    """
    name = 'get_uncached_test_feature_xml_with_mask_and_gobject'
    response_code = 200
    request = '%s/features/UncachedTestFeature/xml?image=%s&mask=%s&gobject=%s'%(NS.root, NS.image_uri, NS.image_uri, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_test_feature_csv():
    """
    """
    name = 'get_uncached_test_feature_xml'
    response_code = 200
    request = '%s/features/UncachedTestFeature/csv?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_dataset_upload, teardown_dataset_remove)
def test_post_uncached_test_feature_csv():
    """
    """
    name = 'post_uncached_test_feature_csv'
    response_code = 200
    request = '%s/features/UncachedTestFeature/csv' % NS.root
    body = """<resource>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        </resource>
    """ % (request, NS.image_uri1, request, NS.image_uri2, request, NS.image_uri3)
    check_response(NS.session, request, response_code, xml=body, method='POST')


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_test_feature_csv_with_mask_and_gobject():
    """
    """
    name = 'get_uncached_test_feature_csv_with_mask_and_gobject'
    response_code = 200
    request = '%s/features/UncachedTestFeature/csv?image=%s&mask=%s&gobject=%s'%(NS.root, NS.image_uri, NS.image_uri, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_test_feature_hdf():
    """
    """
    name = 'get_uncached_test_feature_xml'
    response_code = 200
    request = '%s/features/UncachedTestFeature/hdf?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_test_feature_hdf_with_mask_and_gobject():
    """
    """
    name = 'get_uncached_test_feature_xml'
    response_code = 200
    request = '%s/features/UncachedTestFeature/hdf?image=%s&mask=%s&gobject=%s'%(NS.root, NS.image_uri, NS.image_uri, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_dataset_upload, teardown_dataset_remove)
def test_post_uncached_test_feature_hdf():
    """
    """
    name = 'post_uncached_test_feature_csv'
    response_code = 200
    request = '%s/features/UncachedTestFeature/hdf' % NS.root
    body = """<resource>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        <feature uri="%s?image=%s"/>
        </resource>
    """ % (request, NS.image_uri1, request, NS.image_uri2, request, NS.image_uri3)
    check_response(NS.session, request, response_code, xml=body, method='POST')

###########################################
##    Feature Requests (multivector)
###########################################
@with_setup(setup_image_upload, teardown_image_remove)
def test_get_multivector_test_feature_xml():
    """
    """
    name = 'get_multivector_test_feature_xml'
    response_code = 200
    request = '%s/features/MultiVectorTestFeature/xml?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_multivector_test_feature_csv():
    """
    """
    name = 'get_multivector_test_feature_csv'
    response_code = 200
    request = '%s/features/MultiVectorTestFeature/csv?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_multivector_test_feature_hdf():
    """
    """
    name = 'get_multivector_test_feature_hdf'
    response_code = 200
    request = '%s/features/MultiVectorTestFeature/hdf?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)

###########################################
##    Feature Requests (parameters)
###########################################
@with_setup(setup_image_upload, teardown_image_remove)
def test_get_parameters_test_feature_xml():
    """
    """
    name = 'get_paramters_test_feature_xml'
    response_code = 200
    request = '%s/features/ParametersTestFeature/xml?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_paramters_test_feature_csv():
    """
    """
    name = 'get_paramters_test_feature_csv'
    response_code = 200
    request = '%s/features/ParametersTestFeature/csv?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_paramters_test_feature_hdf():
    """
    """
    name = 'get_paramters_test_feature_hdf'
    response_code = 200
    request = '%s/features/ParametersTestFeature/hdf?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)

##################################################
##    Feature Requests (uncached and multivector)
##################################################

@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_multivector_test_feature_xml():
    """
    """
    name = 'get_multivector_test_feature_xml'
    response_code = 200
    request = '%s/features/UncachedMultiVectorTestFeature/xml?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_multivector_test_feature_csv():
    """
    """
    name = 'get_multivector_test_feature_csv'
    response_code = 200
    request = '%s/features/UncachedMultiVectorTestFeature/csv?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_multivector_test_feature_hdf():
    """
    """
    name = 'get_multivector_test_feature_hdf'
    response_code = 200
    request = '%s/features/UncachedMultiVectorTestFeature/hdf?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)

#################################################
##    Feature Requests (uncached and parameters)
#################################################
@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_paramters_test_feature_xml():
    """
    """
    name = 'get_paramters_test_feature_xml'
    response_code = 200
    request = '%s/features/ParametersTestFeature/xml?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_paramters_test_feature_csv():
    """
    """
    name = 'get_paramters_test_feature_csv'
    response_code = 200
    request = '%s/features/ParametersTestFeature/csv?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)


@with_setup(setup_image_upload, teardown_image_remove)
def test_get_uncached_paramters_test_feature_hdf():
    """
    """
    name = 'get_paramters_test_feature_hdf'
    response_code = 200
    request = '%s/features/ParametersTestFeature/hdf?image=%s' % (NS.root, NS.image_uri)
    check_response(NS.session, request, response_code)




