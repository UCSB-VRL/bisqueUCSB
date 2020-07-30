from bqapi import BQSession
from bqapi import BQCommError
from lxml import etree
from nose import with_setup
from copy import deepcopy
from test_func import compare_etree


class TestNameSpace(object):
    """
        A container for variable that need
        to be passed between the setups/teardowns
        and tests themselves
    """
    def __init__(self):
        pass
    
class TestException(Exception):
    pass
    
    
XMLPARSER = etree.XMLParser(remove_blank_text=True)
    
TESTPREF = etree.XML("""
        <preference>
            <tag name="Viewer">
                <tag name="autoUpdate" value="false"/>
                <tag name="negative" value="false"/>
                <tag name="enhancement" value="d"/>
            </tag>
            <tag name="ResourceBrowser">
                <tag name="Browser">
                    <tag name="Tag Query" value=""/>
                    <tag name="Layout" value="Compact"/>
                    <tag name="Include Public Resources" value="true"/>
                </tag>
                <tag name="Images">
                    <tag name="ImageParameters" value=""/>
                </tag>
            </tag>
        </preference>
    """, parser=XMLPARSER)

    
NS = TestNameSpace() #global name space to pass around variables
    
def make_public(etree):
    """
        Adds permission attribute to all nodes and sets that attribute to published
        
        @param: etree - etree
        @return: etree
    """
    def publish(xml):
        xml.attrib['permission'] = "published"
        for e in xml:
            publish(e)
        return xml
    return publish(deepcopy(etree))
    
def check_request_response(answer, result):
    """
        
    """
    pass
    
    
def setup_module():
    """ Setup feature requests test """
    NS.bq_admin = BQSession()
    NS.bq_admin.init_local('admin', 'admin', bisque_root='http://128.111.185.26:8080')
    NS.bq_user = BQSession()
    NS.bq_user.init_local('test', 'test', bisque_root='http://128.111.185.26:8080')
    NS.bq_no_user = BQSession() #setting root for the session
    NS.bq_no_user.bisque_root='http://128.111.185.26:8080'
    NS.bq_no_user.c.root='http://128.111.185.26:8080'
    
    #copy system document locally to be re-uploaded after test
    system_list = NS.bq_admin.fetchxml('/data_service/system').xpath('/resource/system')
    if len(system_list)<1: raise TestException('No system resource found. Please initalize one and rerun the test.')
    NS.systemDoc = NS.bq_admin.fetchxml('/data_service/%s'%system_list[0].attrib.get('resource_uniq'), view='deep')
    NS.systemDocSave = NS.systemDoc
    
    
    user_list_doc = NS.bq_admin.fetchxml('/data_service/user?wpublic=1')
    
    
    admin_list = user_list_doc.xpath('/resource/user[@name="admin"]')
    if len(admin_list)<1: raise TestException('No admin user found. Create an admin user with admin credentials and rerun the test.')
    NS.adminDoc = NS.bq_admin.fetchxml('/data_service/%s'%admin_list[0].attrib.get('resource_uniq'), view='deep')
    NS.adminDocSave = NS.adminDoc
    
    user_list = user_list_doc.xpath('/resource/user[@name="test"]')
    if len(user_list)<1: raise TestException('No test user found. Create an test user and rerun the test.')
    NS.userDoc = NS.bq_admin.fetchxml('/data_service/%s'%user_list[0].attrib.get('resource_uniq'), view='deep')
    NS.userDocSave = NS.userDoc
    
    
    file = etree.Element('file', name="preference test")
    
    NS.resourceDocUser = NS.bq_user.postxml('/data_service/file', file)
    NS.resourceDocAdmin = NS.bq_admin.postxml('/data_service/file', make_public(file))
    
    
def teardown_module():
    """ Teardown feature requests test """
    #remove admin test file
    resource_uniq = NS.resourceDocAdmin.attrib.get('resource_uniq')
    NS.bq_admin.deletexml('/data_service/%s'%resource_uniq)
    
    #remove user test file
    resource_uniq = NS.resourceDocUser.attrib.get('resource_uniq')
    NS.bq_user.deletexml('/data_service/%s'%resource_uniq)
    
    #reset system document
    NS.bq_admin.postxml('/data_service/%s'%NS.systemDocSave.attrib.get('resource_uniq'), NS.systemDocSave, method = 'PUT')
    
    #reset admin document
    NS.bq_admin.postxml('/data_service/%s'%NS.adminDocSave.attrib.get('resource_uniq'), NS.adminDocSave, method = 'PUT')
    
    #reset user document
    NS.bq_user.postxml('/data_service/%s'%NS.userDocSave.attrib.get('resource_uniq'), NS.userDocSave, method = 'PUT')
    
    
def resetPref(resource, doc, session):
    preference = getattr(NS, doc).xpath('/%s/preference'%resource)
    for p in preference:
        getattr(NS, session).deletexml(p.attrib.get('uri'))
    resource_uniq = getattr(NS, doc).attrib.get('resource_uniq')
    setattr(NS, doc, getattr(NS, session).fetchxml('/data_service/%s'%resource_uniq, view='deep'))
    
    
def setUpGenerator(resource, doc, session, preference=None):
    """
        Generates a setup function that 
    
        @resource: the name of the resource the preference resource will be edited
        @doc: the name of the etree element reference in the setup
        @session: the name of the session
        @preference: the etree element containing the preference resource (default: None)
    """
    def setup():
        resetPref(resource, doc, session)
        if preference is not None:
            resource_uniq = getattr(NS, doc).attrib.get('resource_uniq')
            getattr(NS, session).postxml('/data_service/%s'%resource_uniq, preference, view='deep')
            setattr(NS, doc, getattr(NS, session).fetchxml('/data_service/%s'%resource_uniq, view='deep'))
    return setup
    
    
def tearDownGenerator(resource, doc, session, orignalPref=None):
    """
        Generates a tearDown function to remove any preference documents added by the test
        and to return the preference document to the original state
        
        @resource: the name of the resource the preference resource will be edited
        @doc: the name of the etree element reference in the setup
        @session: the name of the session
        @preference: the etree element containing the preference resource (default: None)
    """
    def teardown():
        resetPref(resource, doc, session)
        
#        if orignalPref is not None:
#            resource_uniq = getattr(NS, doc).attrib.get('resource_uniq')
#            getattr(NS, session).postxml('/data_service/%s'%resource_uniq, orignalPref, view='deep')
#            setattr(NS, doc, getattr(NS, session).fetchxml('/data_service/%s'%resource_uniq, view='deep'))
    return teardown

###########################
###
### GET
###
########################### 
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_get_system_preference():
#    result = NS.bq_admin.fetchxml('/preference', view='clean,deep')
#    answer = TESTPREF
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_get_system_preference_path():
#    result = NS.bq_admin.fetchxml('/preference/Viewer', view='clean,deep')
#    answer = TESTPREF.xpath('/preference/tag[@name="Viewer"]')[0]
#    compare_etree(answer, result)
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_get_system_preference_path():
#    """
#        GET tag name with spaces
#    """
#    result = NS.bq_admin.fetchxml('/preference/ResourceBrowser/Browser/Include Public Resources', view='clean,deep')
#    answer = TESTPREF.xpath('/preference/tag[@name="ResourceBrowser"]/tag[@name="Browser"]/tag[@name="Include Public Resources"]')[0]
#    compare_etree(answer, result)

#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_get_system_preference_path_not_found():
#    result = None
#    try:
#        result = NS.bq_admin.fetchxml('/preference/asdf', view='clean,deep')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#        
#    if result is not None:
#        assert 0, 'A 404 error should be returned.'
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'adminDoc', 'bq_admin'),
#    tearDownGenerator('user', 'adminDoc', 'bq_admin')
#)
#def test_admin_get_user_preference():
#    result = NS.bq_admin.fetchxml('/preference/user', view='clean,deep')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'adminDoc', 'bq_admin'),
#    tearDownGenerator('user', 'adminDoc', 'bq_admin')
#)
#def test_admin_get_user_preference_path():
#    result = NS.bq_admin.fetchxml('/preference/user/Viewer', view='clean,deep')
#    answer = TESTPREF.xpath('/preference/tag[@name="Viewer"]')[0]
#    compare_etree(answer, result)
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'adminDoc', 'bq_admin'),
#    tearDownGenerator('user', 'adminDoc', 'bq_admin')
#)
#def test_admin_get_user_preference_path_not_found():
#    result = None
#    try:
#        result = NS.bq_admin.fetchxml('/preference/user/sadf', view='clean,deep')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#    if result is not None:
#        assert 0, 'A 404 error should be returned.'
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'adminDoc', 'bq_admin'),
#    tearDownGenerator('user', 'adminDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin'),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_admin_get_resource_preference():
#    resource_uniq = NS.adminDoc.attrib.get('resource_uniq')
#    result = NS.bq_admin.fetchxml('/preference/user/%s' % resource_uniq, view='clean,deep')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'adminDoc', 'bq_admin'),
#    tearDownGenerator('user', 'adminDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin'),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_admin_get_resource_preference_path():
#    result = NS.bq_admin.fetchxml('/preference/user/%s/Viewer' % NS.resourceDocAdmin)
#    answer = TESTPREF.xpath('/preference/tag[@name="Viewer"]')[0] 
#    check_response(answer, result)
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'adminDoc', 'bq_admin'),
#    tearDownGenerator('user', 'adminDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin'),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_admin_get_resource_preference_path_not_found():
#    result = NS.bq_admin.fetchxml('/preference/user/%s/asdf' % NS.resourceDocAdmin)
#    check_response(answer, result)
#    
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_user_get_system_preference():
#    result = NS.bq_user.fetchxml('/preference', view='clean,deep')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_get_user_preference():
#    result = NS.bq_user.fetchxml('/preference/user', view='clean,deep')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user'),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_user_get_resource_preference():
#    result = NS.bq_user.fetchxml('/preference/user/%s' % NS.resourceDocUser.attrib.get('resource_uniq'), view='deep,clean')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin'),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_user_get_admin_resource_preference():
#    result = NS.bq_user.fetchxml('/preference/user/%s' % NS.resourceDocAdmin.attrib.get('resource_uniq'), view='deep,clean')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_nouser_get_user_resource_preference():
#    result = NS.bq_no_user.fetchxml('/preference', view='deep,clean')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_nouser_get_user_preference():
#    result = NS.bq_no_user.fetchxml('/preference/user', view='deep,clean')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin'),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_nouser_get_user_public_resource_preference():
#    result = NS.bq_no_user.fetchxml('/preference/user/%s'%NS.resourceDocAdmin.attrib.get('resource_uniq'), view='deep,clean')
#    answer = TESTPREF
#    compare_etree(answer, result)
#    
#    
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user'),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_nouser_get_private_resource_preference():
#    result = None
#    try:
#        result = NS.bq_no_user.fetchxml('/preference/user/%s' % NS.resourceDocUser.attrib.get('resource_uniq'))
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#        
#    if result is not None:
#        assert 0, 'A 404 error should be returned.'





###########################
###
### PUT
###
###########################

NEW_PREFERENCE = etree.XML("""
        <preference>
            <tag name="Toolbar">
                <tag name="registration" value="/auth_service/login"/>
                <tag name="password_recovery" value="/auth_service/login"/>
                <tag name="user_profile" value="/registration/edit_user"/>
            </tag>
            <tag name="Uploader">
                <tag name="initial_path" type="string" value="{date_iso}">
                    <template>
                        <tag name="allowBlank" type="boolean" value="true"/>
                        <tag name="Editable" type="boolean" value="true"/>
                    </template>
                </tag>
            </tag>
        </preference>
""", parser=XMLPARSER)

#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_put_system_preference_1():
#    """
#        PUT entire prefrence
#    """
#
#    result = NS.bq_admin.postxml('/preference', make_public(NEW_PREFERENCE), method='PUT', view='deep,clean')
#    del result.attrib['resource_uniq']
#    answer = NEW_PREFERENCE
#    compare_etree(answer, result)
#
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_put_system_preference_2():
#    """
#        PUT change an element using xpath
#    """
#    body = etree.XML("""
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="true"/>
#                <tag name="newTag" value="newValue"/>
#            </tag>
#    """, parser=XMLPARSER)
#
#    result = NS.bq_admin.postxml('/preference/Viewer', make_public(body), method='PUT', view='deep,clean')
#    answer = body
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_put_system_preference_3():
#    """
#        PUT a new value on a tag
#    """
#    body = etree.XML("""
#        <tag name="autoUpdate" value="true"/>
#    """, parser=XMLPARSER)
#    result = NS.bq_admin.postxml('/preference/Viewer/autoUpdate', make_public(body), method='PUT', view='deep,clean')
#    answer = body
#
#    compare_etree(answer, result)
#
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="negative" value="false"/>
#                <tag name="enhancement" value="d"/>
#                <tag name="autoUpdate" value="true"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    result = NS.bq_admin.fetchxml('/preference', view='deep,clean')
#    #check full document
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_put_system_preference_4():
#    """
#        PUT try to put to a name there is no xpath for
#    """
#    body = etree.XML("""
#        <tag name="asdf">
#            <tag name="autoUpdate" value="false"/>
#        </tag>
#    """, parser=XMLPARSER)
#    
#    result = None
#    try:
#        result = NS.bq_admin.postxml('/preference/asdf', make_public(body), method='PUT', view='deep,clean')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#        
#    if result is not None:
#        assert 0, 'A 404 error should be returned.'
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_put_system_preference_5():
#    """
#        PUT try to put to a name with the wrong name in the body
#    """
#    body = etree.XML("""
#        <tag name="asdf">
#            <tag name="autoUpdate" value="false"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = None
#    try:
#        result = NS.bq_admin.postxml('/preference/Viewer', make_public(body), method='PUT', view='deep,clean')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#        
#    if result is not None:
#        assert 0, 'A 404 error should be returned.'
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_user_put_system_preference():
#    """
#        user PUT to system document
#    """
#    result = None
#    try:
#        result = NS.bq_user.postxml('/preference', make_public(NEW_PREFERENCE), method='PUT', view='deep,clean')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#        
#    if result is not None:
#        assert 0, 'A 404 error should be returned.'

#skip for now need to think about xpath to an unknown element
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public,
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_put_user_preference_1():
#    """
#        PUT replace main document
#    """
#    result = NS.bq_user.postxml('/preference/user', make_public(NEW_PREFERENCE), method='PUT', view='deep,clean')
#    del result.attrib['resource_uniq']
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="false"/>
#                <tag name="enhancement" value="d"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#            <tag name="Toolbar">
#                <tag name="registration" value="/auth_service/login"/>
#                <tag name="password_recovery" value="/auth_service/login"/>
#                <tag name="user_profile" value="/registration/edit_user"/>
#            </tag>
#            <tag name="Uploader">
#                <tag name="initial_path" type="string" value="{date_iso}">
#                    <template>
#                        <tag name="allowBlank" type="boolean" value="true"/>
#                        <tag name="Editable" type="boolean" value="true"/>
#                    </template>
#                </tag>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_put_user_preference_2():
#    """
#        PUT change an element using xpath 
#    """
#    #get system preference
#    
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_put_user_preference_3():
#    """
#        PUT a new tag
#    """
#    #get system preference
#    compare_etree(answer, result)

#def test_user_put_resource_preference_1():
#    """
#        PUT change an element using xpath
#    """
#    #get system preference
#    compare_etree(answer, result)
#
#
#def test_user_put_resource_preference_2():
#    """
#        PUT change an element using xpath
#    """
#    #get system preference
#    compare_etree(answer, result)
#
#
#def test_user_put_resource_preference_3():
#    """
#        PUT a new tag
#    """
#    #get system preference
#    compare_etree(answer, result)
#
##404 user does not have access to change system doc
#def test_user_put_system_preference_1():
#    """
#        PUT entire prefrence
#    """
#    #get system preference
#    compare_etree(answer, result)
#    
#
#def test_user_put_public_resource_preference_1():
#    """
#        PUT change an element using xpath
#    """
#    #get system preference
#    compare_etree(answer, result)
#
#
#def test_user_put_public_resource_preference_2():
#    """
#        PUT change an element using xpath
#    """
#    #get system preference
#    compare_etree(answer, result)
#
#
#def test_user_put_public_resource_preference_3():
#    """
#        PUT a new tag
#    """
#    compare_etree(answer, result)


###########################
###
### POST
###
###########################


#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_post_system_preference_1():
#    """
#        POST entire preference
#    """
#    result = NS.bq_admin.postxml('/preference', make_public(POST_NEW_PREFERENCE), view='deep,clean')
#    del result.attrib['resource_uniq']
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#                <tag name="autoUpdate" value="true"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#            <tag name="Toolbar">
#                <tag name="registration" value="/auth_service/login"/>
#                <tag name="password_recovery" value="/auth_service/login"/>
#                <tag name="user_profile" value="/registration/edit_user"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)

#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_post_system_preference_2():
#    """
#        POST change an element using xpath
#    """
#    body = etree.XML("""
#        <tag name="Viewer">
#            <tag name="negative" value="true"/>
#            <tag name="enhancement" value="d"/>
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_admin.postxml('/preference/Viewer', make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="Viewer">
#            <tag name="negative" value="true"/>
#            <tag name="enhancement" value="d"/>
#            <tag name="autoUpdate" value="true"/>
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#    
#    #check the entire resource
#    
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_get_system_preference_path():
#    """
#        POST tag name with spaces
#    """
#    body = etree.XML("""<tag name="Include Public Resources" value="true"/>""", parser=XMLPARSER)
#    result = NS.bq_admin.postxml('/preference/ResourceBrowser/Browser/Include Public Resources', make_public(body), view='clean,deep')
#    answer = body
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_post_system_preference_3():
#    """
#        POST change a second level element
#    """
#    body = etree.XML("""
#        <tag name="ResourceBrowser">
#            <tag name="Browser">
#                <tag name="Include Public Resources" value="false"/>
#            </tag>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_admin.postxml('/preference/ResourceBrowser', make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="ResourceBrowser">
#            <tag name="Browser">
#                <tag name="Tag Query" value=""/>
#                <tag name="Layout" value="Compact"/>
#                <tag name="Include Public Resources" value="false"/>
#            </tag>
#            <tag name="Images">
#                <tag name="ImageParameters" value=""/>
#            </tag>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_post_system_preference_4():
#    """
#        POST a new tag
#    """
#    body = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_admin.postxml('/preference/NewPath/NewTag', make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_post_system_preference_4():
#    """
#        POST a new tag
#    """
#    body = etree.XML("""
#        <tag name="NotMyName">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = None
#    try:
#        result = NS.bq_admin.postxml('/preference/NewPath/NewTag', make_public(body), view='deep,clean')
#    except BQCommError as e:
#        assert e.status == 400, 'A 400 error should be returned.'
#        
#    if result is not None:
#        assert 0, 'A 400 error should be returned.'
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_user_post_system_preference():
#    """
#        user POST to system level who is not admin 
#    """
#    body = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = None
#    try:
#        result = NS.bq_user.postxml('/preference/NewTag', make_public(body), view='deep,clean')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#        
#    if result is not None:
#        assert 0, 'A 404 error should be returned.'
#
#
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_post_user_preference_1():
#    """
#        POST a new preference document
#    """
#    body = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#                <tag name="NewName" value="NewValue"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user', make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#                <tag name="autoUpdate" value="false"/>
#                <tag name="NewName" value="NewValue"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_post_user_preference_2():
#    """
#        POST change an element using xpath
#    """
#    body = etree.XML("""
#        <tag name="Viewer">
#            <tag name="negative" value="true"/>
#            <tag name="enhancement" value="d"/>
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/Viewer', make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="Viewer">
#            <tag name="autoUpdate" value="true"/>
#            <tag name="negative" value="true"/>
#            <tag name="enhancement" value="d"/>
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_post_user_preference_3():
#    """
#        POST merge nested tags
#    """
#    body = etree.XML("""
#        <tag name="ResourceBrowser">
#            <tag name="Browser">
#                <tag name="Include Public Resources" value="false"/>
#            </tag>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/ResourceBrowser', make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="ResourceBrowser">
#            <tag name="Browser">
#                <tag name="Tag Query" value=""/>
#                <tag name="Layout" value="Compact"/>
#                <tag name="Include Public Resources" value="false"/>
#            </tag>
#            <tag name="Images">
#                <tag name="ImageParameters" value=""/>
#            </tag>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_post_user_preference_4():
#    """
#        POST a new tag
#    """
#    body = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/NewPath/NewTag', make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)


#untested
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_post_user_preference_5():
#    """
#        POST a new tag on new document
#    """
#    body = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/NewPath/NewTag', make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_post_user_preference_6():
#    """
#        POST a new tag with the wrong name
#    """
#    body = etree.XML("""
#        <tag name="NotMyName">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = None
#    try:
#        result = NS.bq_admin.postxml('/preference/NewPath/NewTag', make_public(body), view='deep,clean')
#    except BQCommError as e:
#        assert e.status == 400, 'A 400 error should be returned.'
#        
#    if result is not None:
#        assert 0, 'A 400 error should be returned.'


#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user'),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_user_post_resource_preference_1():
#    """
#        POST a new preference document
#    """
#    body = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#                <tag name="NewName" value="NewValue"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/%s'%NS.resourceDocUser.attrib.get('resource_uniq'), make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#                <tag name="NewName" value="NewValue"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)


#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_user_post_resource_preference_2():
#    """
#        POST change an element using xpath
#    """
#    body = etree.XML("""
#        <tag name="Viewer">
#            <tag name="negative" value="true"/>
#            <tag name="enhancement" value="d"/>
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/%s/Viewer'%NS.resourceDocUser.attrib.get('resource_uniq'), make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="Viewer">
#            <tag name="autoUpdate" value="true"/>
#            <tag name="negative" value="true"/>
#            <tag name="enhancement" value="d"/>
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_user_post_resource_preference_3():
#    """
#        POST a new tag
#    """
#    body = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/%s/NewPath/NewTag'%NS.resourceDocUser.attrib.get('resource_uniq'), make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)


#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_admin'),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_admin')
#)
#def test_user_post_public_resource_preference_1():
#    """
#        POST change an element using xpath
#    """
#    body = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#                <tag name="NewName" value="NewValue"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/%s'%NS.resourceDocAdmin.attrib.get('resource_uniq'), make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#                <tag name="NewName" value="NewValue"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_user_post_public_resource_preference_2():
#    """
#        POST change an element using xpath
#    """
#    body = etree.XML("""
#        <tag name="Viewer">
#            <tag name="negative" value="true"/>
#            <tag name="enhancement" value="d"/>
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/%s/Viewer'%NS.resourceDocAdmin.attrib.get('resource_uniq'), make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="Viewer">
#            <tag name="autoUpdate" value="true"/>
#            <tag name="negative" value="true"/>
#            <tag name="enhancement" value="d"/>
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_user_post_public_resource_preference_3():
#    """
#        POST a new tag
#    """
#    body = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    result = NS.bq_user.postxml('/preference/user/%s/NewPath/NewTag'%NS.resourceDocAdmin.attrib.get('resource_uniq'), make_public(body), view='deep,clean')
#    answer = etree.XML("""
#        <tag name="NewTag">
#            <tag name="NewName" value="NewValue"/>
#        </tag>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)

###########################
###
### DELETE
###
###########################



POST_NEW_PREFERENCE = etree.XML("""
        <preference>
            <tag name="Viewer">
                <tag name="negative" value="true"/>
                <tag name="enhancement" value="d"/>
                <tag name="autoUpdate" value="true"/>
            </tag>
            <tag name="Toolbar">
                <tag name="registration" value="/auth_service/login"/>
                <tag name="password_recovery" value="/auth_service/login"/>
                <tag name="user_profile" value="/registration/edit_user"/>
            </tag>
        </preference>
""", parser=XMLPARSER)


#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_delete_system_preference_1():
#    """
#        Delete the entire document
#    """
#    NS.bq_admin.deletexml('/preference')
#    result = NS.bq_admin.fetchxml('/data_service/%s'%NS.systemDoc.attrib.get('resource_uniq'), view='deep')
#    assert len(result.xpath('/preference')) == 0, 'The preference resource should be removed.'
#    NS.systemDoc = result #reset system doc
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_delete_system_preference_2():
#    """
#        Delete a tag with xpath
#    """
#    NS.bq_admin.deletexml('/preference/Viewer')
#    result = NS.bq_admin.fetchxml('/preference', view='clean,deep')
#    answer = etree.XML("""
#        <preference>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_delete_system_preference_3():
#    """
#        Delete a sub tag with xpath
#    """
#    NS.bq_admin.deletexml('/preference/Viewer/autoUpdate')
#    result = NS.bq_admin.fetchxml('/preference', view='clean,deep')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="negative" value="false"/>
#                <tag name="enhancement" value="d"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_admin_delete_system_preference_4():
#    """
#        Delete a tag not in the preference document
#    """
#    result = None
#    try:
#        NS.bq_admin.deletexml('/preference/asdf')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#def test_user_delete_system_preference():
#    """
#        Delete a tag not in the preference document
#    """
#    result = None
#    try:
#        NS.bq_user.deletexml('/preference')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_delete_user_preference_1():
#    """
#        Delete the entire document
#    """
#    NS.bq_user.deletexml('/preference/user')
#    result = NS.bq_user.fetchxml('/preference/user', view='deep,clean')
#    userDoc = NS.bq_user.fetchxml('/data_service/%s'%NS.userDoc.attrib.get('resource_uniq'), view='deep')
#    NS.userDoc = userDoc #reset user doc
#    answer = TESTPREF
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_delete_user_preference_2():
#    """
#        Delete a tag with xpath
#    """
#    NS.bq_user.deletexml('/preference/user/Viewer')
#    result = NS.bq_user.fetchxml('/preference/user', view='clean,deep')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="false"/>
#                <tag name="enhancement" value="d"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#            <tag name="Toolbar">
#                <tag name="registration" value="/auth_service/login"/>
#                <tag name="password_recovery" value="/auth_service/login"/>
#                <tag name="user_profile" value="/registration/edit_user"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_delete_user_preference_3():
#    """
#        Delete a sub tag with xpath
#    """
#    NS.bq_user.deletexml('/preference/user/Viewer/autoUpdate')
#    result = NS.bq_user.fetchxml('/preference/user', view='clean,deep')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#            <tag name="Toolbar">
#                <tag name="registration" value="/auth_service/login"/>
#                <tag name="password_recovery" value="/auth_service/login"/>
#                <tag name="user_profile" value="/registration/edit_user"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    asdf
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#def test_user_delete_user_preference_4():
#    """
#        Delete a tag not in the preference document
#    """
#    result = None
#    try:
#        NS.bq_user.deletexml('/preference/user/asdf')
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_user_delete_resource_preference_1():
#    """
#        Delete the entire document
#    """
#    NS.bq_user.deletexml('/preference/user/%s'%NS.resourceDocUser.attrib.get('resource_uniq'))
#    result = NS.bq_user.fetchxml('/preference/user/%s'%NS.resourceDocUser.attrib.get('resource_uniq'), view='deep,clean')
#    resourceDocUser = NS.bq_user.fetchxml('/data_service/%s'%NS.resourceDocUser.attrib.get('resource_uniq'), view='deep')
#    NS.resourceDocUser = resourceDocUser #reset user doc
#    answer = TESTPREF
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_user_delete_resource_preference_2():
#    """
#        Delete a tag with xpath
#    """
#    NS.bq_user.deletexml('/preference/user/%s/Viewer' % NS.resourceDocUser.attrib.get('resource_uniq'))
#    result = NS.bq_user.fetchxml('/preference/user/%s'%NS.resourceDocUser.attrib.get('resource_uniq'), view='deep,clean')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="false"/>
#                <tag name="enhancement" value="d"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#            <tag name="Toolbar">
#                <tag name="registration" value="/auth_service/login"/>
#                <tag name="password_recovery" value="/auth_service/login"/>
#                <tag name="user_profile" value="/registration/edit_user"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_user_delete_resource_preference_3():
#    """
#        Delete a sub tag with xpath
#    """
#    NS.bq_user.deletexml('/preference/user/%s/Viewer/autoUpdate' % NS.resourceDocUser.attrib.get('resource_uniq'))
#    result = NS.bq_user.fetchxml('/preference/user/%s'%NS.resourceDocUser.attrib.get('resource_uniq'), view='deep,clean')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#            <tag name="Toolbar">
#                <tag name="registration" value="/auth_service/login"/>
#                <tag name="password_recovery" value="/auth_service/login"/>
#                <tag name="user_profile" value="/registration/edit_user"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#



##requires annotation service to work!!!!!! untested!!!!
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocUser', 'bq_user', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocUser', 'bq_user')
#)
#def test_user_delete_resource_preference_4():
#    """
#        Delete a tag not in the preference document
#    """
#    result = None
#    try:
#        NS.bq_user.deletexml('/preference/user/%s/asdf'%  NS.resourceDocUser.attrib.get('resource_uniq'))
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'


#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_user_delete_resource_preference_1():
#    """
#        Delete the entire document
#    """
#    NS.bq_user.deletexml('/preference/user/%s'%NS.resourceDocAdmin.attrib.get('resource_uniq'))
#    result = NS.bq_user.fetchxml('/preference/user/%s'%NS.resourceDocAdmin.attrib.get('resource_uniq'), view='deep,clean')
#    resourceDocAdmin = NS.bq_user.fetchxml('/data_service/%s'%NS.resourceDocAdmin.attrib.get('resource_uniq'), view='deep')
#    NS.resourceDocAdmin = resourceDocAdmin #reset user doc
#    answer = TESTPREF
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_user_delete_resource_preference_2():
#    """
#        Delete a tag with xpath
#    """
#    NS.bq_user.deletexml('/preference/user/%s/Viewer' % NS.resourceDocAdmin.attrib.get('resource_uniq'))
#    result = NS.bq_user.fetchxml('/preference/user/%s'%NS.resourceDocAdmin.attrib.get('resource_uniq'), view='deep,clean')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="false"/>
#                <tag name="enhancement" value="d"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#            <tag name="Toolbar">
#                <tag name="registration" value="/auth_service/login"/>
#                <tag name="password_recovery" value="/auth_service/login"/>
#                <tag name="user_profile" value="/registration/edit_user"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_user_delete_resource_preference_3():
#    """
#        Delete a sub tag with xpath
#    """
#    NS.bq_user.deletexml('/preference/user/%s/Viewer/autoUpdate' % NS.resourceDocAdmin.attrib.get('resource_uniq'))
#    result = NS.bq_user.fetchxml('/preference/user/%s'%NS.resourceDocAdmin.attrib.get('resource_uniq'), view='deep,clean')
#    answer = etree.XML("""
#        <preference>
#            <tag name="Viewer">
#                <tag name="autoUpdate" value="false"/>
#                <tag name="negative" value="true"/>
#                <tag name="enhancement" value="d"/>
#            </tag>
#            <tag name="ResourceBrowser">
#                <tag name="Browser">
#                    <tag name="Tag Query" value=""/>
#                    <tag name="Layout" value="Compact"/>
#                    <tag name="Include Public Resources" value="true"/>
#                </tag>
#                <tag name="Images">
#                    <tag name="ImageParameters" value=""/>
#                </tag>
#            </tag>
#            <tag name="Toolbar">
#                <tag name="registration" value="/auth_service/login"/>
#                <tag name="password_recovery" value="/auth_service/login"/>
#                <tag name="user_profile" value="/registration/edit_user"/>
#            </tag>
#        </preference>
#    """, parser=XMLPARSER)
#    compare_etree(answer, result)
#
#
#@with_setup(
#    setUpGenerator('system', 'systemDoc', 'bq_admin', preference=make_public(TESTPREF)),
#    tearDownGenerator('system', 'systemDoc', 'bq_admin')
#)
#@with_setup(
#    setUpGenerator('user', 'userDoc', 'bq_user'),
#    tearDownGenerator('user', 'userDoc', 'bq_user')
#)
#@with_setup(
#    setUpGenerator('file', 'resourceDocAdmin', 'bq_admin', preference=make_public(POST_NEW_PREFERENCE)),
#    tearDownGenerator('file', 'resourceDocAdmin', 'bq_admin')
#)
#def test_user_delete_resource_preference_4():
#    """
#        Delete a tag not in the preference document
#    """
#    result = None
#    try:
#        NS.bq_user.deletexml('/preference/user/%s/asdf'%  NS.resourceDocAdmin.attrib.get('resource_uniq'))
#    except BQCommError as e:
#        assert e.status == 404, 'A 404 error should be returned.'
