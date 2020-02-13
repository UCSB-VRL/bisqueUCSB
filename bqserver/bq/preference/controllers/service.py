###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007 by the Regents of the University of California     ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========


DESCRIPTION
===========

"""
import os
import re
import logging
from collections import namedtuple
from collections import OrderedDict
from datetime import datetime
from lxml import etree
from tg import expose, controllers, flash, url, response, request
from repoze.what.predicates import is_user, in_group, Any, not_anonymous
from bq.data_service.controllers.resource_query import RESOURCE_READ, RESOURCE_EDIT
from pylons.controllers.util import abort

import bq
from bq import data_service
from bq.core.service import ServiceController
from bq.core import identity

from bq.util.hash import is_uniq_code
from bq.util.paths import defaults_path

log = logging.getLogger('bq.preference')



LEVEL = {
            'system':0,
            'user':1,
            'resource':2
         }





#TagValueNode: leaf node is a node no other tag resources in its first level children
#    - value: the value of the tag resource (in prepartation for .06 xml syntax change since the value will not be stored in he attribute node)
#    - node_attrib: dictionary of the node attributes for the node
#    - sub_node: list of sub nodes attached to the TagValueNode
TagValueNode = namedtuple('TagValueNode',['value','node_attrib','sub_node'])
TagValueNode.__new__.__defaults__ = ('', {}, [])

#TagNameNode: parent node is a node with tag resources in its first level children (values will be removed during dict 2 etree conversion)
#    - sub_node_dict: stores an ordered dictionary of either TagValueNode or TagNomeNode referenced by the tag resource's name attribute
#    - node_attrib: dictionary of the node attributes for the node (Note: value attribute will be removed)
#    - sub_none_tag_node: list of none tag resource elements (ex. templates)
TagNameNode = namedtuple('TagNameNode',['sub_node_dict','node_attrib', 'sub_none_tag_node'])
TagNameNode.__new__.__defaults__ = (OrderedDict(), {}, [])

def mergeDocuments(current, new, **attrib):
    """
        Merges two xml documents. Current document elements are replace with new document elements.


        @param: current - preference etree document
        @param: new - preference etree document
        @param: attrib - top level attribute for the new merged document
    """
    currentDict = to_dict(current)
    newDict = to_dict(new)

    def merge(new, current):
        #merges the new docucument to the current one
        for k in new.sub_node_dict.keys():
            if k in current.sub_node_dict:
                #deals with the cases when the current needs to be merged with the new document
                #case 1: both current and new are parent nodes
                if (type(current.sub_node_dict[k]) is TagNameNode) and (type(new.sub_node_dict[k]) is TagNameNode):
                    node_attrib = new.sub_node_dict[k].node_attrib
                    #type and templates are added from the current node and all other attributes are appended from the
                    #new node
                    if 'type' in current.sub_node_dict[k].node_attrib:
                        node_attrib['type'] = current.sub_node_dict[k].node_attrib['type']
                    current.sub_node_dict[k] = TagNameNode(
                        sub_node_dict = current.sub_node_dict[k].sub_node_dict,
                        node_attrib = node_attrib,
                        sub_none_tag_node = current.sub_node_dict[k].sub_none_tag_node
                    )
                    #merge the parents' children
                    merge(new.sub_node_dict[k], current.sub_node_dict[k])

                #case 2: both are leaf nodes
                elif (type(current.sub_node_dict[k]) is TagValueNode) and (type(new.sub_node_dict[k]) is TagValueNode):
                    #type and templates are added from the minor node and all other attributes are appended from the
                    #major node
                    node_attrib = new.sub_node_dict[k].node_attrib
                    if 'type' in current.sub_node_dict[k].node_attrib:
                        node_attrib['type'] = current.sub_node_dict[k].node_attrib['type']
                    current.sub_node_dict[k] = TagValueNode(
                        value = new.sub_node_dict[k].value,
                        node_attrib = node_attrib,
                        sub_node = current.sub_node_dict[k].sub_node
                    )

                #case 3: current node is a parent node and new node is a leaf
                elif (type(current.sub_node_dict[k]) is TagNameNode) and (type(new.sub_node_dict[k]) is TagValueNode):
                    # replaces the parent node of the current node with the leaf node unless the value node has nothing
                    if new.sub_node_dict[k].value:
                        current.sub_node_dict[k] = TagValueNode(
                            value = new.sub_node_dict[k].value,
                            node_attrib = new.sub_node_dict[k].node_attrib,
                        )
                    else: #value does not equal anything set it back to the tag name node
                        pass

                #case 4: current node is a leaf node and new node is a parent
                elif (type(current.sub_node_dict[k]) is TagNameNode) and (type(new.sub_node_dict[k]) is TagValueNode):
                    #nothing is changed in the current node and the new node is skipped
                    #keeps users from modifying existing structure of the preferences
                    pass

            #deals with the case when the major document appends new nodes
            else:
                #add the child node to the document
                if (type(new.sub_node_dict[k]) is TagValueNode):
                    current.sub_node_dict[k] = TagValueNode(
                        value = new.sub_node_dict[k].value,
                        node_attrib = new.sub_node_dict[k].node_attrib,
                    )

                #adds the parent node to the document with all of its children
                elif (type(new.sub_node_dict[k]) is TagNameNode):
                    current.sub_node_dict[k] = new.sub_node_dict[k]

            #all nodes in the current are added to the document by default

        return current

    m_dict = merge(newDict, currentDict)

    return to_etree(m_dict, **attrib)


def to_dict(tree):
    """
        @param: etree
        @return: preference dictionary structure
    """
    def build(tree):
        sub_node_dict = OrderedDict()
        sub_none_tag_node = []
        for e in tree:
            if e.tag == 'tag': #check if tag
                if len(e.xpath('tag'))<1:  #if nodes has no tag children
                    sub_node_dict[e.attrib.get('name','')] = TagValueNode(
                        value = e.attrib.get('value'),
                        node_attrib = e.attrib,
                        sub_node = e.getchildren(),
                    )
                else: #remove the value and add it as a parent node
                    if 'value' in e.attrib: e.attrib.pop('value')
                    sub_node_dict[e.attrib.get('name','')] = build(e)
            else: #append it to the parent node as a none tag element
                sub_none_tag_node.append(e)
        return TagNameNode(
            sub_node_dict = sub_node_dict,
            sub_none_tag_node = sub_none_tag_node,
            node_attrib = tree.attrib
        )
    return build(tree)


def to_etree(dictionary, **attrib):
    """
        @param: preference dictionary stucture (TagNameNode)
        @return: etree
    """
    def build(dict, node):
        for k in dict.keys():
            if type(dict[k]) is TagValueNode:
                subNode = etree.Element('tag', **dict[k].node_attrib)
                for e in dict[k].sub_node:
                    subNode.append(e)
            else:
                subNode = etree.Element('tag', **dict[k].node_attrib)
                for e in dict[k].sub_none_tag_node:
                    subNode.append(e) #adding none tag nodes to subnode
                build(dict[k].sub_node_dict, subNode)
            node.append(subNode)
        return node

    if 'hidden' in attrib: del attrib['hidden']
    node = etree.Element('preference', hidden='true', **attrib)
    for e in dictionary.sub_none_tag_node:
        node.append(e)
    return build(dictionary.sub_node_dict, node)


def update_level(new_doc, current_doc, **attrib):
    """
        prepares the new elements to be place in the preference resource
    """
    log.debug('update_level')
    new_dict = to_dict(new_doc)
    current_dict = to_dict(current_doc)
    def build(new, current):
        """
            merges TagNameNode elements
        """
        for nk in new.sub_node_dict.keys():
            if nk in current.sub_node_dict: #set current node
                if type(new.sub_node_dict[nk]) is TagNameNode and type(current.sub_node_dict[nk]) is TagNameNode:
                    #both new and current are TagNameNodes
                    build(new.sub_node_dict[nk], current.sub_node_dict[nk])
                elif type(new.sub_node_dict[nk]) is TagNameNode: #over write the value node on the current document
                    current.sub_node_dict[nk] = new.sub_node_dict[nk]
                elif type(new.sub_node_dict[nk]) is TagValueNode: #over write the value node
                    if type(current.sub_node_dict[nk]) is TagValueNode:
                        attrib = current.sub_node_dict[nk].node_attrib
                        #add value and maybe type
                        attrib['value'] = new.sub_node_dict[nk].node_attrib.get('value', '')
                        tt = new.sub_node_dict[nk].node_attrib.get('type', None)
                        if tt is not None:
                            attrib['type'] = tt
                    current.sub_node_dict[nk] = TagValueNode(
                        value = new.sub_node_dict[nk].value,
                        node_attrib = attrib,
                        #non system preferences never get subnodes
                    )
            else: #set new node
                if type(new.sub_node_dict[nk]) is TagValueNode:
                    attrib = {}
                    #add value and name; type always cascades
                    attrib['name'] = new.sub_node_dict[nk].node_attrib.get('name', '')
                    attrib['value'] = new.sub_node_dict[nk].node_attrib.get('value', '')
                    tt = new.sub_node_dict[nk].node_attrib.get('type', None)
                    if tt is not None:
                        attrib['type'] = tt
                    current.sub_node_dict[nk] = TagValueNode(
                        value = new.sub_node_dict[nk].value,
                        node_attrib = attrib,
                        #non system preferences never get subnodes
                    )
                elif type(new.sub_node_dict[nk]) is TagNameNode:
                    current.sub_node_dict[nk] = new.sub_node_dict[nk]
        return current

    update_dict = build(new_dict, current_dict)



    return to_etree(update_dict, **attrib)


class PreferenceController(ServiceController):
    """
        The preference controller is a central point for
        a special resource that cascades all the resource levels
        meant as guidance for the bisque UI
        (System -> User -> all other Resource) providing


        General Format of <preference> resource

        <preference>
            <tag name="UI Component"/>
                <tag name="UI preference name 1" value="preference value"/>
                    <template>
                        <tag name="template parameter name" value="template parameter value"/>
                        ...
                    </template>
                <tag name="sub UI component"/>
                    <tag name="sub UI preference name 1" value="preference value"/>
                ...
            ...
        </preference>
    """
    service_type = "preference"

    @expose(content_type='text/xml')
    def _default(self, *arg, **kw):
        """
            The entry point for the system level preferences
        """
        self.log_start()
        xp = '/'.join(['tag[@name="%s"]'%a for a in arg]) or None
        method = request.method.upper()
        try:
            if method == 'GET':
                return self.get(resource_uniq=None, xpath=xp, level=0, **kw)
            self.ensure_admin()
            if method == 'DELETE':
                return self.system_delete(xpath=xp, **kw)
            elif method == 'PUT' and request.body is not None:
                return self.system_put(request.body, xpath=xp, **kw)
            elif method == 'POST' and request.body is not None:
                return self.system_post(request.body, xpath=xp, **kw)
            abort(404)
        finally:
            self.log_finish()

    @expose(content_type='text/xml')
    def user(self, *arg, **kw):
        """
            The entry point for the user and resource level preferences
        """
        self.log_start()
        not_annon = not_anonymous().is_met(request.environ)
        http_method = request.method.upper()

        resource_uniq = None
        xpath = None
        arg = list(arg)
        if len(arg)>0:
            xpath = []
            if is_uniq_code(arg[0]):       #check if resource uniq is provided
                resource_uniq = arg.pop(0)  #this will block first level tags that are resource_uniq so be reasonable.
            for a in arg:
                xpath.append('tag[@name="%s"]'%a)
            xpath = '/'.join(xpath) or None #create xpath

        try:
            if resource_uniq: #resource level
                if http_method == 'GET':
                    log.info('GET /preference/user/%s -> fetching resource level preference for %s', resource_uniq, resource_uniq)
                    return self.get(resource_uniq=resource_uniq, xpath=xpath, level=2, **kw)
                elif not_annon and http_method == 'POST' and request.body:
                    log.info('POST /preference/user/%s -> updating resource level preference for %s', resource_uniq, resource_uniq)
                    return self.resource_post(resource_uniq, request.body, xpath=xpath, **kw)
                elif not_annon and http_method == 'PUT' and request.body:
                    log.info('PUT /preference/user/%s ->  over writing resource level preference for %s', resource_uniq, resource_uniq)
                    return self.resource_put(resource_uniq, xpath=xpath, body=request.body, **kw)
                elif not_annon and http_method == 'DELETE':
                    log.info('DELETE /preference/user/%s -> removing resource level preference for %s', resource_uniq, resource_uniq)
                    return self.resource_delete(resource_uniq, xpath=xpath, **kw)
            else: #user level
                if http_method == 'GET':
                    log.info('GET /preference/user -> fetching user level preference')
                    return self.get(resource_uniq=resource_uniq, xpath=xpath, level=1, **kw)
                elif  not_annon and http_method == 'POST' and request.body:
                    log.info('POST /preference/user -> updating user level preference')
                    return self.user_post(body=request.body, xpath=xpath, **kw)
                elif  not_annon and http_method == 'PUT' and request.body:
                    log.info('PUT /preference/user ->  over writing user level preference')
                    return self.user_put(body=request.body, xpath=xpath, **kw)
                elif not_annon and http_method == 'DELETE':
                    log.info('DELETE /preference/user -> removing user level preference')
                    return self.user_delete(xpath=xpath, **kw)
            abort(404)
        finally:
            self.log_finish()

    @expose(content_type='text/xml')
    def reset(self, *arg, **kw):
        """
        replaces the system preferences with the default document
        """
        self.log_start()
        try:
            self.ensure_admin()
            return self.system_reset(**kw)
        finally:
            self.log_finish()

    def ensure_admin(self):
        is_admin = Any(in_group('admin'), in_group('admins')).is_met(request.environ)
        if is_admin is not True:
            if identity.not_anonymous():
                abort(403)
            else:
                abort(401)

    def log_start(self):
        log.info ("STARTING: %s", request.url)

    def log_finish(self):
        log.info ("FINISHED: %s", request.url)

    def get(self, resource_uniq=None, xpath=None, level=0, **kw):
        """
            Returns the virtual prefence document of the requested document for the
            specified level

            @param: resource_uniq - the resource_uniq of the resource document to be fetched. Not required if
            the level is 0-1. (default: None)
            @param: path -  (default: None)
            @param: level - the level to cascade the virtual document. (default: 0)
                0: system
                1: user
                2: resource
            @param: kw - pass through query parameters to data_service
        """
        #check system preference
        #system = data_service.get_resource('/data_service/system', view='full', wpublic=1)
        system = data_service.query(resource_type= 'system', view='full', wpublic=1)
        system_preference_list = system.xpath('//system/preference')
        if len(system_preference_list) > 0:
            system_preference = data_service.get_resource(system_preference_list[0].attrib.get('uri'), wpublic=1, **kw)
        else:
            system_preference  = etree.Element('preference') #no preference found
        if level <= LEVEL['system']:
            if xpath:
                system_preference = system_preference.xpath('/preference/%s'%xpath)
                if len(system_preference)>0:
                    return etree.tostring(system_preference[0])
                else:
                    abort(404)
            else:
                return etree.tostring(system_preference)

        #check user preference
        user = self.get_current_user(view='full')
        user_preference_list = user.xpath('preference')
        if len(user_preference_list)>0: #if user is not signed in no user preferences are added
            user_preference = data_service.get_resource(user_preference_list[0].attrib.get('uri'), **kw)
            if not user_preference: #handles a bug in the data_service with permissions and full verse deep views
                user_preference = etree.Element('prefererence')
            attrib = {}
            if 'clean' not in kw.get('view', ''):
                attrib = system_preference.attrib
            user_preference = mergeDocuments(system_preference, user_preference, **attrib)
        else:
            user_preference  = system_preference

        if level <= LEVEL['user']:
            if 'clean' not in kw.get('view', ''):
                user_preference.attrib['uri'] = request.url.replace('&','&amp;')
                user_preference.attrib['owner'] = user.attrib.get('uri', system_preference.attrib.get('owner', ''))
            if xpath:
                user_preference = user_preference.xpath('/preference/%s'%xpath)
                if len(user_preference)>0:
                    return etree.tostring(user_preference[0])
                else:
                    abort(404)
            else:
                return etree.tostring(user_preference)

        #check resource preference
        resource = data_service.get_resource('/data_service/%s'%resource_uniq, view='full')
        if resource is None:
            abort(404)

        resource_preference_list = resource.xpath('preference')
        if len(resource_preference_list)>0:
            resource_preference = data_service.get_resource(resource_preference_list[0].attrib.get('uri'), **kw)
            if not resource_preference: #handles a bug in the data_service with permissions and full verse deep views
                resource_preference = etree.Element('prefererence', hidden='true')
            else:
                resource_preference.set('hidden', 'true')
            attrib = {}
            if 'clean' not in kw.get('view',''):
                attrib.update(user_preference.attrib)
                attrib.update(resource_preference.attrib)
            resource_preference = mergeDocuments(user_preference, resource_preference, **attrib)
        else:
            resource_preference = user_preference

        #check annotations preference
        annotation = self.get_current_user_annotation(resource_uniq, view='full')
        #annotation_resource = data_service.get_resource('/data_service/annotation/%s'%annotation_uniq, view='full')
        resource_preference_list = annotation.xpath('preference')
        if len(resource_preference_list)>0:
            annotation_preference = data_service.get_resource(resource_preference_list[0].attrib.get('uri'), **kw)
            attrib = {}
            if 'clean' not in kw.get('view', ''):
                attrib.update(resource_preference.attrib)
                attrib.update(annotation_preference.attrib)
            annotation_preference = mergeDocuments(resource_preference, annotation_preference, **attrib)
        else:
            annotation_preference = resource_preference

        if level <= LEVEL['resource']:
            if 'clean' not in kw.get('view', ''):
                annotation_preference.attrib['uri'] = request.url.replace('&','&amp;')
                annotation_preference.attrib['owner'] = user.attrib.get('uri', resource.attrib.get('owner', ''))
            if xpath:
                annotation_preference = annotation_preference.xpath('/preference/%s'%xpath)
                if len(annotation_preference)>0:
                    return etree.tostring(annotation_preference[0])
                else:
                    abort(404)
            else:
                return etree.tostring(annotation_preference)
        #raise exception level not known


    def get_current_user(self, **kw):
        """
            get_current_user

            Looks up and fetches the current users document. If no user document is
            found and empty user document is turned.

            @param: kw - pass through query parameters to data_service
            @return: etree element

        """
        user = identity.get_username()
        #user =  request.identity.get('user')
        if user:
            u = data_service.query(resource_type='user', name=user, wpublic=1)
            user_list = u.xpath('user')
            if len(user_list)>0:
                return data_service.get_resource('/data_service/%s'%u[0].attrib.get('resource_uniq'), **kw)
        return etree.Element('user') #return empty user


    def get_current_user_annotation(self, resource_uniq, **kw):
        """
            get_current_user_annotation

            Get the annotation document for the provided resource_uniq under the current user. \
            If none found will return an empty annotation document

            @param: resource_uniq
            @param: kw - pass through query parameters to data_service

            @return: etree element
        """
        annotation_resource = data_service.get_resource('/data_service/annotation', view='short')
        annotation = annotation_resource.xpath('annotation[@value="%s"]'%resource_uniq)
        if len(annotation)>0:
            log.debug('Annotation document found for document (%s) at /%s'%(resource_uniq,annotation[0].attrib.get('resource_uniq')))
            return data_service.get_resource('/data_service/%s'%annotation[0].attrib.get('resource_uniq'), **kw)
        else:
            log.debug('No annotation document found for document (%s)'%resource_uniq)
            return etree.Element('annotation', value=resource_uniq)


    def strip_attributes(self, xml, save_attrib=['name','value', 'type']):
        """
        """
        def strip(node):
            for a in node.attrib.keys():
                if a not in set(save_attrib):
                    del node.attrib[a]
            for n in node:
                strip(n)
            return node

        return strip(xml)


    def system_post(self, body, xpath=None, **kw):
        """
            Creates a new preferences or merges the existing one with
            the document provided
            Only admin can change the system level
            the user has to be logged in to make any changes

            @param: path
            @param: body
        """
        log.debug('system_post')
        try:
            preference_doc = etree.fromstring(body)
        except etree.XMLSyntaxError:
            abort(400, 'XML parsing error')

        #system = data_service.get_resource('/data_service/system', view='full', wpublic=1)
        system = data_service.query(resource_type='system', view='full', wpublic=1)
        system_preference_list = system.xpath('/resource/system/preference')
        if len(system_preference_list)>0:
            system_preference = data_service.get_resource(system_preference_list[0].attrib.get('uri'), wpublic=1, view='deep')
            if xpath:
                tagNames = re.findall('tag\[@name="(?P<name>[A-Za-z0-9_\- ]+)"\]',xpath) #only alphanumeric tag names are allowed right now
                if len(tagNames)>0 and preference_doc.attrib.get('name')==tagNames[-1]:
                    #parse xpath and form the xml doc to merge
                    preference = etree.Element('preference')
                    tagElement = preference
                    for t in tagNames[:-1]: #last element should already be included
                        tagElement = etree.SubElement(tagElement, 'tag', name = t)
                    tagElement.append(preference_doc) #add path the preference doc
                    current_preference_etree = update_level(preference, system_preference)

                    data_service.update_resource(resource=system_preference, new_resource=current_preference_etree)
                    #data_service.del_resource(system_preference.attrib.get('uri'))
                    #data_service.new_resource(current_preference_etree, parent='/data_service/%s' % system[0].attrib.get('resource_uniq'))
                    return self.get(xpath=xpath, **kw) #return the correct resource
                else:
                    abort(400)
            elif preference_doc.tag == 'preference': #merge the old with the new
                current_preference_etree = update_level(preference_doc, system_preference)
                resource = data_service.update_resource(resource=system_preference, new_resource=current_preference_etree, **kw)
                #data_service.del_resource(system_preference.attrib.get('uri'))
                #resource = data_service.new_resource(current_preference_etree, parent='/data_service/%s' % system[0].attrib.get('resource_uniq'), **kw)
            else:
                abort(400)
        else:
            if preference_doc.tag == 'preference': #creating a new preference
                system_list = system.xpath('/resource/system')
                if system_list>0:
                    resource = data_service.new_resource(preference_doc, parent='/data_service/%s' % system_list.attrib.get('resource_uniq'), **kw)
                else: #system document is not there
                    abort(400)
            else: #not correct format and no xpath
                abort(400)

        return etree.tostring(resource)


    def system_put(self, body, xpath=None, **kw):
        """
            Replaces all the preferences with the document
            Only admin can change the system level
            the user has to be logged in to make any changes

            @param: xpath
            @param: body
        """
        log.debug('system_put')
        try:
            new_doc = etree.fromstring(body)
        except etree.XMLSyntaxError:
            abort(400, 'XML parsing error')

        system = data_service.query(resource_type='system', view='full', wpublic=1)
        prefs = system.xpath('/resource/system/preference')
        if len(prefs)>0:
            old_doc = data_service.get_resource(prefs[0].get('uri'), wpublic=1, view='deep')
            if xpath:
                tagNames = re.findall('tag\[@name="(?P<name>[A-Za-z0-9_\- ]+)"\]',xpath) #only alphanumeric tag names are allowed right now
                if len(tagNames)>0 and new_doc.attrib.get('name')==tagNames[-1]:
                    #parse xpath and form the xml doc to merge
                    preference = etree.Element('preference')
                    tagElement = preference
                    for t in tagNames[:-1]: #last element should already be included
                        tagElement = etree.SubElement(tagElement, 'tag', name = t)
                    tagElement.append(new_doc) #add path the preference doc
                    current_preference_etree = update_level(preference, old_doc)

                    data_service.update_resource(resource=old_doc, new_resource=current_preference_etree)
                    #data_service.del_resource(old_doc.attrib.get('uri'))
                    #data_service.new_resource(current_preference_etree, parent='/data_service/%s' % system[0].attrib.get('resource_uniq'))
                    return self.get(xpath=xpath, **kw) #return the correct resource
                else:
                    abort(400)
            elif new_doc.tag == 'preference': #merge the old with the new
                #current_preference_etree = update_level(new_doc, old_doc)
                #resource = data_service.update_resource(resource=old_doc, new_resource=current_preference_etree, **kw)

                # dima: this is a PUT of a whole prefs document, merging is not supposed to happen
                for el in new_doc.getiterator(tag=etree.Element):
                    el.set ('permission', 'published')
                resource = data_service.update_resource(old_doc.get('uri'), new_resource=new_doc)
            else:
                abort(400)
        else:
            if new_doc.tag == 'preference': #creating a new preference
                system_list = system.xpath('/resource/system')
                if system_list>0:
                    resource = data_service.new_resource(new_doc, parent='/data_service/%s' % system_list.attrib.get('resource_uniq'), **kw)
                else: #system document is not there
                    abort(400)
            else: #not correct format and no xpath
                abort(400)

        return etree.tostring(resource)

    def system_reset(self, xpath=None, **kw):
        """

        """
        #self.system_delete() # deletes only preference section and not the whole doc
        system = data_service.query(resource_type='system', view='full', wpublic=1)
        prefs = system.xpath('system')
        if len(prefs)<1:
            abort(400)
        data_service.del_resource(prefs[0].get('uri'))


        # post a new document from config-defaults/preferences.xml.default
        system = etree.parse(defaults_path('preferences.xml.default')).getroot()
        for el in system.getiterator(tag=etree.Element):
            el.set ('permission', 'published')
        system = data_service.new_resource(system) #, view='deep')
        log.debug('New system pref: %s', etree.tostring(system))
        return system

    def system_delete(self, xpath=None, **kw):
        """
            removes all or a part of the preferences
            Only admin can change the system level and
            the user has to be logged in to make any changes

            @param: resource_uniq
            @param: doc
        """
        #requires admin privileges
        #system = data_service.get_resource('/data_service/system', view='full', wpublic=1)
        system = data_service.query(resource_type='system', view='full', wpublic=1)
        prefs = system.xpath('/resource/system/preference')
        if len(prefs)<1:
            abort(400)
        self.delete(prefs[0].get('uri'), xpath=xpath)


    def user_post(self, body, xpath=None, **kw):
        """
            user_post

            Merges preference document put to the preference on the user current sign in user document provided.

            @param: body - an xml string of the element being posted back (default: None)
            @param: kw - pass through query parameters to data_service
        """
        log.debug('user_post')
        try:
            preference_doc = etree.fromstring(body)
        except etree.XMLSyntaxError:
            abort(400, 'XML parsing error')
        user = self.get_current_user(view='full')
        if 'name' in user.attrib:
            user_preference_list = user.xpath('/user/preference')
        else:
            #raise error
            log.debug('User was not found')
            abort(404)

        self.post(user, user_preference_list, preference_doc, xpath=xpath)
        return self.get(xpath=xpath, level=1, **kw) #return the correct resource


    def user_put(self,  body=None, xpath=None, **kw):
        """
            user_put

            Merges preference document put to the preference on the user current sign in user document provided.

            @param: body - an xml string of the element being posted back (default: None)
            @param: kw - pass through query parameters to data_service
        """
        log.debug('user_put')
        try:
            preference_doc = etree.fromstring(body)
        except etree.XMLSyntaxError:
            abort(400, 'XML parsing error')
        user = self.get_current_user(view='full')
        if 'name' in user.attrib:
            user_preference_list = user.xpath('/user/preference')
        else:
            #raise error
            log.debug('User was not found')
            abort(404)

        self.post(user, user_preference_list, preference_doc, xpath=xpath)
        return self.get(xpath=xpath, level=1, **kw) #return the correct resource


    def user_delete(self, xpath=None, **kw):
        """
            user_delete

            Deletes the preference resource from the user current sign in user document or the element to the path
            provided in this document

            @param: path - path after preferences to the document element to be deleted (default: None)
            @param: kw - pass through query parameters to data_service
        """
        user = self.get_current_user(view='full')
        user_preference_list = user.xpath('preference')
        if len(user_preference_list)<1:
            abort(404)
        preference_uri = user_preference_list[0].attrib.get('uri')
        self.delete(preference_uri, xpath=xpath)


    def resource_post(self, resource_uniq, body, xpath=None, **kw):
        """
            resource_post

            Merges preference document put to the preference on the resource document provided.

            @param: resource_uniq - the resource_uniq to document being addressed
            @param: body - an xml string of the element being posted back(default: None)
            @param: kw - pass through query parameters to data_service
        """
        log.debug('resource_post')
        try:
            preference_doc = etree.fromstring(body)
        except etree.XMLSyntaxError:
            abort(400, 'XML parsing error')
        resource = data_service.resource_load(resource_uniq, action=RESOURCE_READ, view='short')
        if resource is not None:
            resource = data_service.resource_load(resource_uniq, action=RESOURCE_EDIT, view='full')
            if resource is not None:
                log.debug('Reading preference from resource document.')
                resource_preference_list = resource.xpath('/*/preference')
            else:
                log.debug('Reading preference from resource annotation document.')
                resource = self.get_current_user_annotation(resource_uniq, view='full')
                if 'resource_uniq' in resource.attrib:
                    resource_preference_list = resource.xpath('/annotation/preference')
                else: #create annotations document
                    log.debug('No annotation document found. Creating an annotation for document at (%s)'%resource_uniq)
                    resource = data_service.new_resource(resource)
                    resource_preference_list = []
        else:
            abort(404)
        self.post(resource, resource_preference_list, preference_doc, xpath=xpath)

        return self.get(resource_uniq, xpath=xpath, level=2, **kw) #return the correct resource



    def resource_put(self, resource_uniq, xpath=None, body=None, **kw):
        """
            resource_put

            Merges preference document put to the preference on the resource document provided.

            @param: resource_uniq - the resource_uniq to document being addressed
            @param: body - an xml string of the element being posted back(default: None)
            @param: kw - pass through query parameters to data_service
        """
        log.debug('resource_put')
        try:
            preference_doc = etree.fromstring(body)
        except etree.XMLSyntaxError:
            abort(400, 'XML parsing error')
        resource = data_service.resource_load(resource_uniq, action=RESOURCE_READ, view='short')
        if resource is not None:
            resource = data_service.resource_load(resource_uniq, action=RESOURCE_EDIT, view='full')
            if resource is not None:
                log.debug('Reading preference from resource document.')
                resource_preference_list = resource.xpath('/*/preference')
            else:
                log.debug('Reading preference from resource annotation document.')
                resource = self.get_current_user_annotation(resource_uniq, view='full')
                if 'resource_uniq' in resource.attrib:
                    resource_preference_list = resource.xpath('/annotation/preference')
                else: #create annotations document
                    log.debug('No annotation document found. Creating an annotation for document at (%s)'%resource_uniq)
                    resource = data_service.new_resource(resource)
                    resource_preference_list = []
        else:
            abort(404)
        self.post(resource, resource_preference_list, preference_doc, xpath=xpath)

        return self.get(resource_uniq, xpath=xpath, level=2, **kw) #return the correct resource


    def resource_delete(self, resource_uniq, xpath=None, **kw):
        """
            Removes the tag on the level requested. If there is not
            tag nothing happens. Returns back the updated document.
            Allows the default value to be set for the level above.

            @param: resource_uniq - the resource_uniq to document being addressed
            @param: path - path after preferences to the document element to be deleted
            @param: kw - pass through query parameters to data_service
        """
        # get the preference resource
        resource = data_service.resource_load(resource_uniq, action=RESOURCE_READ, view='short')
        if resource is not None:
            resource = data_service.resource_load(resource_uniq, action=RESOURCE_EDIT, view='full')
            if resource is not None:
                log.debug('Reading preference from resource document.')
                resource_preference_list = resource.xpath('/*/preference')
            else:
                log.debug('Reading preference from resource annotation document.')
                resource = self.get_current_user_annotation(resource_uniq, view='full')
                if 'resource_uniq' in resource.attrib:
                    resource_preference_list = resource.xpath('/annotation/preference')
                else: #create annotations document
                    log.debug('No annotation document found. Creating an annotation for document at (%s)'%resource_uniq)
                    resource = data_service.new_resource(resource)
                    resource_preference_list = []
        else:
            abort(404)

        if len(resource_preference_list)<1:
            abort(404)
        preference_uri = resource_preference_list[0].attrib.get('uri')
        self.delete(preference_uri, xpath=xpath)


    def post(self, resource, resource_preference_list, preference_doc, xpath=None):
        """
        """
        log.debug('post')
        resource_preference = None
        if len(resource_preference_list)>0:
            resource_preference = data_service.get_resource(resource_preference_list[0].attrib.get('uri'), view='deep')

        if xpath:
            tagNames = re.findall('tag\[@name="(?P<name>[A-Za-z0-9_\- ]+)"\]', xpath) #only alphanumeric tag names are allowed right now
            if len(tagNames)>0 and preference_doc.attrib.get('name')==tagNames[-1]:
                #parse xpath and form the xml doc to merge
                preference = etree.Element('preference', hidden='true')
                tagElement = preference
                for t in tagNames[:-1]: #last element should already be included
                    tagElement = etree.SubElement(tagElement, 'tag', name = t)
                tagElement.append(preference_doc) #add path the preference doc
                preference_doc = preference
            else:
                abort(400)

        if resource_preference:
            current_preference_etree = update_level(preference_doc, resource_preference)
        elif preference_doc.tag == 'preference':
            current_preference_etree = preference_doc
        else:
            abort(400)

        if resource_preference: #replace element
            log.debug('post current_preference_etree: %s'%etree.tostring(current_preference_etree))
            log.debug('post resource_preference: %s'%etree.tostring(resource_preference))
            data_service.update_resource(resource=resource_preference, new_resource=current_preference_etree)
            #data_service.del_resource(resource_preference.attrib.get('uri'))
        else: #create new element
            log.debug('post current_preference_etree: %s'%etree.tostring(current_preference_etree))
            data_service.new_resource(current_preference_etree, parent='/data_service/%s' % resource.attrib.get('resource_uniq'))


    def put(self):
        """
        """
        pass

    def delete(self, preference_uri, xpath=None):
        """
        """
        if xpath:
            preference = data_service.get_resource(preference_uri, view='deep')
            if preference is None:
                abort(404)
            tag_uri = preference.xpath('/preference/%s'%xpath)
            if len(tag_uri)<1:
                abort(404)
            preference_uri = tag_uri[0]
        data_service.del_resource(preference_uri)


def initialize(url):
    """ Initialize the top level server for this microapp"""
    log.debug ("initialize " + url)
    return PreferenceController(url)


#def get_static_dirs():
#    """Return the static directories for this server"""
#    package = pkg_resources.Requirement.parse ("bqserver")
#    package_path = pkg_resources.resource_filename(package,'bq')
#    return [(package_path, os.path.join(package_path, 'admin_service', 'public'))]



__controller__ = PreferenceController
__staticdir__ = None
__model__ = None
