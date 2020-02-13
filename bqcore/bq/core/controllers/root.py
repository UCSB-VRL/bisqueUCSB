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

   Entry point for bisquik web pages.
   Allows sub-services to register and links them into the bisquik application
   Provides login and logout services.

"""
import os
import sys
import logging
import time
import urlparse
import pkg_resources
from datetime import datetime, timedelta
from paste.httpexceptions import HTTPNotFound

#from turbogears import controllers, expose, config
#from turbogears import  redirect
#from turbogears import identity as tgidentity
import simplejson as json
from lxml import etree
from tg import expose,  request, redirect, config, response, abort, session
from tg.controllers import CUSTOM_CONTENT_TYPE
from tg.controllers import WSGIAppController
#from tgext.admin import AdminController

from bq.core.model import DBSession
from bq.core.lib.base import BaseController
from bq.exceptions import ConfigurationError
from bq.core.controllers.proxy import ProxyController, service_proxy
from bq.core.service import ServiceController, service_registry
from bq.core.service import load_services, mount_services, start_services
from bq.core.controllers.error import ErrorController
from bq.util.hash import is_uniq_code
from bq.util.proxy import make_proxy

#from proxy import ProxyRewriteURL

log = logging.getLogger("bq.root")

class MDWrap(object):
    """A Multidictionary that provides attribute-style access.
    """

    def __init__(self, md):
        self.md = md

    def __getitem__(self, key):
        return  self.md.__getitem__(self, key)

    def __getattr__(self, name):
        return self.md.getone(name)

    def __delattr__(self, name):
        try:
            del self.md[name]
        except KeyError:
            raise AttributeError(name)

def session_update():
    timeout = session.get ('timeout', 0)
    length = session.get ('length', 0)
    if timeout and length:
        newexpire =  datetime.utcnow() + timedelta(seconds=length)
        log.debug ("SESSION EXPIRE %s", session['expires'])
        if newexpire >= session['expires'] + timedelta (seconds=timeout):
            session['expires']  = newexpire
            session.save()


class ServiceRegistryController (ServiceController):
    """Access to the nodes services"""
    service_type = "services"

    @expose("etree:resource", content_type="text/xml")
    def index(self):
        #response.content_type = "application/xml"
        resource = etree.Element ('resource')
        for ty, e in  service_registry.get_services().items():
            for i in e.instances :
                service = etree.SubElement (resource, 'tag',
                                            name='service',
                                            type=ty,
                                            value=i.url)
        return dict (resource = resource)


    @expose ()
    def register(self, service_type, service_url):
        """Allow external services to register here for use by our local
        services.. For example several, engine  servers may register with
        the root server. @see register_proxy_services
        """
        service_registry.register_instance(ProxyController(service_type,
                                                           service_url))
        log.debug ("Registered remote %s  %s" % (service_type, service_url))

    @expose ()
    def services(self, service_type, service_url):
        """Return the list of URL of internal services known
        by this instance.  Include only services locally mounted.
        """
        resource = etree.Element ('resource')
        return etree.tostring(resource)


class ProxyCache(object):
    "Cache proxy services"
    def __init__(self):
        self.proxies = {}
    @expose()
    def index(self, **kw):
        return str (self.proxies.keys())
    @expose()
    def _lookup (self, host_addr, *rest):
        log.debug ("Proxy for %s", host_addr)
        proxy = self.proxies.setdefault(host_addr, WSGIAppController (make_proxy(config, "http://%s" % host_addr)))
        log.debug ("PROXIES %s", str (self.proxies))
        return proxy, rest

oldnames = {'imgsrv' : 'image_service',
            'ds'     : 'data_service',
            'ms'     : 'module_service',}

NOLOGGING = set (["/check", "/auth_service/session", ])


#class Root(controllers.RootController):
class RootController(BaseController):
    #service_registry = MultiDict()
    #config['pylons.app_globals'].s = MDWrap(service_registry)

    proxy = ProxyCache()
    error  = ErrorController()
    #root = config.get ('bisque.root', '')

    @classmethod
    def mount_local_services(cls, root, wanted = None, unwanted=None):
        """Find services and add them to the list of available
        web URL for this server
        """
        log.debug ("loading services")
        cls.services = ServiceRegistryController(root + "/services/")
        load_services ()
        for name, service in mount_services (root, wanted, unwanted):
            # This will circumvent the use of lookup below by
            # directly mount the services on the root class controller
            #setattr(cls, name, service)
            pass



    @expose()
    def _lookup(self, service_type, *rest):
        """Default handler for bisque root.

        Search for registered sub-servers that might handle this request.
        return an error if none found

        URL are formed with
        <service_type>/<path>?arguments
        """
        if request.path in NOLOGGING:
            log.debug ('[%s] %s %s', request.identity.get('repoze.who.userid'), request.method, request.url )
        else:
            log.info ('[%s] %s %s', request.identity.get('repoze.who.userid'), request.method, request.url )

        if log.isEnabledFor (logging.DEBUG):
            log.debug ('HEADERS: %s %s', request.url, dict(request.headers))
            log.debug ('PATH %s in DIR %s', request.path, os.getcwd())
        if service_type in oldnames:
            #service_type = oldnames[service_type]
            newreq = request.path_qs[1:].replace (service_type,  oldnames[service_type])
            log.warn ('found oldname( %s ) -> newreq %s' , service_type, newreq)

            redirect(urlparse.urljoin(request.application_url, newreq))


        #log.debug ("find controller for %s  " % (str(service_type) ))
        #log.debug ("lookup for %s/%s" , service_type, rest )
        #import pdb
        #pdb.set_trace()
        service = service_registry.find_service(service_type)
        if service is not None:
            #log.debug ('found %s ' ,  str(service))
            if service.service_type != 'auth_service' and 'expires' in session:
                session_update ()
            return service, rest
        if is_uniq_code(service_type):
            log.debug ("uniq code %s", request.path_qs)
            # Skip 1st /
            redirect(urlparse.urljoin(request.application_url, '/data_service/%s' % request.path_qs[1:]))

        log.warn ('no service found %s with %s', service_type, rest)
        abort(404)

    #@expose('bq.templates.error')
    #def error (self, msg='', status=400):
    #    return dict (code=status, message = msg)

    @expose()
    def index(self, **kw):
        redirect (config.get('bisque.root', request.application_url) + "/client_service/")

    @expose()
    def check(self, **kw):
        return "OK"

#def register_proxy_services (proxy):
#    '''Registers all local services with the requested
#    proxyroot.   This allows the main root service to become
#    aware of the existance of sub-servers
#    '''
#    for service_type, service in service_registry.items():
#        log.debug ("send  proxy to %s" % proxy)
#        http_client.request (proxy + "/services/register_internal"
#                             +"?service_type=%s" % service_type
#                             +"&service_url=%s" % service.uri)


def update_remote_proxies (proxy):
    """Use to determine services available to the local
    bisque server on remote servers.. Requests  a list of
    services available from the root server and adds them
    """
    from bq.util.http import http_client
    count = 0
    while True:
        try:
            header, content = http_client.request (proxy + "/services")
        except Exception, e:
            log.debug ("failed connect to %s with %s" , proxy, e)
            time.sleep (2)
            count += 1
            if count > 5:
                break
            continue
        response = etree.XML (content)
        for service in response:
            service_type  = service.tag
            service_uri   = service.text

            log.debug ('remote %s -> %s' , service_type, service_uri)
            if not service_registry.has_service(service_type, service_uri):
                cls = service_registry.find_class (service_type)
                if cls is not None:
                    service = service_proxy (cls, service_uri)
                    service_registry.register_instance (service )
                else:
                    log.error ("unknown class for service type '%s'" , service_type)
        break


def startup():
    #root = config.get ('bisque.root')
    #if root:
    #  #raise ConfigurationError ('bisque.root not set')
    #  log.warn ("bisque.root setting is not supported")
    #  config.set ('bisque.root', '/')
    root = '/'

    #proxy = config.get('bisque.site', None)
    enabled = os.getenv('BISQUE_SERVICES_ENABLED') or config.get('bisque.services_enabled', None)
    disabled = os.getenv('BISQUE_SERVICES_DISABLED') or config.get('bisque.services_disabled', None)
    enabled  = enabled and [ x.strip() for x in enabled.split(',') ] or []
    disabled = disabled and [ x.strip() for x in disabled.split(',') ] or []
    log.info ('using root=%s with services=%s - %s' , root,  enabled, disabled)

    RootController.mount_local_services(root, enabled, disabled)
    # if proxy:
    #     log.info ("attempt to contact ROOT server %s" % proxy)
    #     # Create service proxy from proxyroot:
    #     root_services = service_proxy (ServiceRegistryController, "%s/services/"%proxy)
    #     # Initialize stubs for remote services
    #     content = None
    #     while True:
    #       try:
    #         content = root_services.index ()
    #         response = etree.XML (content)
    #         if len(response):
    #           break
    #       except RequestError, e:
    #         log.debug ("root_service request failed")
    #       log.debug ("Waiting for Root server %s" % content )
    #       time.sleep(5)
    #     log.debug ("Root response %s " % content )
    #     for service_tag in response:
    #         service_type = service_tag.get('type')
    #         service_url  = service_tag.get('value')
    #         service_cls = service_registry.find_class(service_type)
    #         if service_cls is None:
    #           log.warn('Could not find service %s' % service_type)
    #           continue
    #         service_registry.register_instance(service_proxy(service_cls,
    #                                                          service_url))
    #     # Register this instance
    #     for service_type, entry in service_registry.get_services().items():
    #         for instance in entry.instances:
    #             if hasattr(instance, 'proxy_url' ):
    #                 continue
    #             root_services.register (service_type, instance.uri)


    #  Startup any local services that need it.
    config['pylons.app_globals'].services = \
          json.dumps (dict( (ty , [ i.url for i in e.instances ] )
                            for ty,e in service_registry.get_services().items()))
    #
    # Encoding issues
    import locale
    log.debug ("Using locale %s local.preferredencoding %s sys.defaultencoding %s",  locale.getlocale(), locale.getpreferredencoding(), sys.getdefaultencoding())
    if locale.getpreferredencoding() != "UTF-8" and os.name != 'nt':
         log.warn('locale encoding will not allow Unicode to work properly:  Please try to set LANG="en_US.UTF-8" in your environment')

    # http://stackoverflow.com/questions/3828723/why-we-need-sys-setdefaultencodingutf-8-in-a-py-script
    # reload(sys)
    # sys.setdefaultencoding('utf8') or 'latin1'


    log.debug ("STARTIN")
    start_services(root, enabled, disabled)



#if  server_type == 'root' and ProxyRewriteURL.active_proxy:
#    cherrypy.filters.input_filters.append(ProxyRewriteURL)

class CoreService:
    service_type = "core"

def initialize (url):
    return None


def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqcore")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'core', 'public'))]


__controller__ =  CoreService
