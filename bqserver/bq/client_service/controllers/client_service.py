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

  Top level web entry point for bisque system

"""

import os
import sys
import random
import logging

import pkg_resources

from urllib import urlencode
from lxml import etree

from pylons import app_globals
from pylons.i18n import ugettext as _, lazy_ugettext as l_, N_
from pylons.controllers.util import abort
from webob import Request

import tg
from tg import expose, flash, redirect, require, request
from tg import config, tmpl_context as c, session
from repoze.what import predicates


import bq
from bq.core.service import ServiceController, service_registry
from bq.client_service import model
from bq.exceptions import IllegalOperation
from bq.release import  __VERSION__
from bq.core import identity
from bq.util.hash import is_uniq_code

#import aggregate_service
from bq import data_service


log = logging.getLogger('bq.client_service')


#  Allow bq.identity to be accessed from templates
#def addBisqueToTemplate(root_vars):
#    bq = dict (identity=bisquik.identity)
#    root_vars.update (dict (bq=bq))
#
#turbogears.view.root_variable_providers += [addBisqueToTemplate]



class ClientServer(ServiceController):
    service_type = "client_service"

    def viewlink(self, resource):
        return self.baseuri + "view?" + urlencode ({'resource': resource})


    @expose()
    def _default (self, *path, **kw):
        if is_uniq_code(path[0]):
            redirect ("/client_service/view?resource=/data_service/%s" % path[0])

    @expose(content_type="text/xml")
    def version(self):
        response = etree.Element('resource', type='version')
        etree.SubElement (response, 'tag', name='version', value=__VERSION__)
        server = etree.SubElement (response, 'tag', name='server')

        #etree.SubElement (server, 'tag', name='environment', value=config.get('server.environment'))
        return etree.tostring(response)

    @expose(template='bq.client_service.templates.welcome')
    def index(self, **kw):
        log.info("WELCOME %s %s " , request.url, dict ( session ))
        wpublic = kw.pop('wpublic', not bq.core.identity.current)
        pybool = {'True': 'true', 'False': 'false'}
        welcome_message = config.get ('bisque.welcome_message', "Welcome to the Bisque image database")

        return dict(imageurl=None,
                    thumbnail=None,
                    wpublicjs = pybool[str(wpublic)],
                    welcome_message = welcome_message
                    )

    @expose(template='bq.client_service.templates.welcome')
    def welcomebackground(self, **kw):
        log.info("BACKGROUND %s " % session )
        wpublic = kw.pop('wpublic', not bq.core.identity.current)
        thumbnail = None
        imageurl = None
        welcome_resource = config.get ('bisque.background_resource', None)
        thumb_size = kw.get('size', '800,600')
        if welcome_resource:
            imageurl = welcome_resource
            try:
                image = data_service.get_resource(imageurl)
                thumbnail = '/image_service/image/%s?thumbnail=%s'%(image.get('resource_uniq'), thumb_size)
            except Exception:
                log.exception('bisque.background (%s) set but not available' % imageurl)
        else:
            tag_query = config.get('bisque.background_query', "welcome_background:")
            image_count  = data_service.count("image", tag_query=tag_query, wpublic=wpublic)
            wpublic_query = wpublic
            if image_count == 0 and wpublic == False:
                wpublic_query  = True
                image_count  = data_service.count("image", tag_query=tag_query, wpublic=wpublic_query)
            # None found .. pick a random
            if image_count == 0:
                image_count = data_service.count("image", wpublic=wpublic)
                tag_query  = None
                wpublic_query = wpublic
            if image_count:
                im = random.randint(0, image_count-1)
                image  = data_service.query('image', tag_query=tag_query, wpublic=wpublic_query,
                                            offset = im, limit = 1)[0]
                #imageurl = self.viewlink(image.attrib['uri'])
                thumbnail = '/image_service/image/%s?thumbnail=%s'%(image.get('resource_uniq'), thumb_size)

        redirect (base_url=thumbnail)

    @expose(template='bq.client_service.templates.browser')
    def browser(self, **kw):
        #query = kw.pop('tag_query', None)
        c.commandbar_enabled = False
        user = bq.core.identity.get_user()
        if user:
            wpublicVal='false'
        else:
            wpublicVal='true'

        #log.debug ('DDDDDDDDDDDDDDDDDDDDDD'+query)
        return dict(query=kw.pop('tag_query', None),
                    layout=kw.pop('layout', None),
                    tagOrder=kw.pop('tag_order', None),
                    tagQuery=kw.pop('tag_query', None),
                    offset=kw.pop('offset', None),
                    dataset=kw.pop('dataset', None),
                    resource=kw.pop('resource', None),
                    search=0,
                    user_id = "",
                    page = kw.pop('page', 'null'),
                    view  = kw.pop('view', ''),
                    count = kw.pop ('count', '10'),
                    wpublic = kw.pop('wpublic', wpublicVal),
                    analysis = None)

    @expose(template='bq.client_service.templates.about')
    def about(self, **kw):
        from bq.release import __VERSION__
        version = '%s'%__VERSION__
        return dict(version=version)


    # Test

    @expose ()
    def xcheck (self, url):
        from bq.config.middleware import bisque_app
        req = Request.blank (url)
        req.headers['Authorization'] = "Mex %s" % identity.mex_authorization_token()
        response = req.get_response(bisque_app)
        return response.body



    @expose(template='bq.client_service.templates.test')
    def test(self):
        """from bq.export_service.controllers.tar_streamer import TarStreamer
        tarStreamer = TarStreamer()
        tarStreamer.sendResponseHeader('Bisque.tar')
        return tarStreamer.stream(['C:\\Python27\\TarStreamer\\file1.tif', 'C:\\Python27\\TarStreamer\\file2.tif', 'C:\\Python27\\TarStreamer\\file3.tif'])
        """
        return dict()

    # USE /services instead
    # @expose (content_type="application/xml")
    # def services(self):
    #     resource = etree.Element ('resource', uri=tg.url('/client_service/services'))
    #     for service_type, service_list in service_registry.items():
    #         for service in service_list:
    #             etree.SubElement (resource, 'tag', name=service_type, value=service.uri)

    #     #tg.response.content_type = "text/xml"
    #     return etree.tostring(resource)



    @expose("bq.client_service.templates.view")
    def view(self, resource, **kw):
        query = ''
        log.debug ("VIEW")
        #resource=kw.pop('resource', '')
        #if resource is None:
        #    abort(404)

        return dict(resource=resource)

    @expose("bq.client_service.templates.embedded")
    def embedded(self, **kw):
        log.debug ("EMBEDDED")
        return dict()

    @expose("bq.client_service.templates.view")
    def create(self, **kw):
        query = ''
        type_=kw.pop('type', None)

        if type_:
            resource = data_service.new_resource (type_, **kw)

            # Choose widgets to instantiate on the viewer by the type
            # of the resource.
            log.debug ('created %s  -> %s' % (type_, uri))
            return dict(resource=resource) #, tag_views=None, wpublic = None, search = None)
        raise IllegalOperation("create operation requires type")


    @expose("bq.client_service.templates.movieplayer")
    def movieplayer(self, **kw):
        resource=kw.pop('resource', None)
        return dict(resource=resource)

    @expose("bq.client_service.templates.help")
    def help(self, **kw):
        resource=kw.pop('resource', None)
        return dict(resource=resource)

    @expose(content_type='text/html')
    def form(self, **kw):
        bb = tg.request.body_file_raw.seek(0)
        bb = tg.request.body_file_raw.read()


        log.debug ("FORM %s %s" , kw, bb)
        return str(kw)



client_server = None
def initialize(uri):
    global client_server
    client_server = ClientServer(uri)
    return client_server

def uri():
    return client_server.baseuri
