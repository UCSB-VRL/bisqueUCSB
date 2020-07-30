###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008                                               ##
##      by the Regents of the University of California                       ##
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
import inspect
import logging
import posixpath
import pkg_resources

from collections import OrderedDict
from urllib import urlencode
import urlparse
from tg import config, expose, request
from bq.core.lib.base import BaseController

log = logging.getLogger ("bq.service")

__all__=["ServiceController",  "load_services" ]

class ServiceDirectory(object):
    """Specialized dict of service_type -> to bq.service"""

    class Entry(object): #pylint: disable=R0903
        """SeviceDirectory.Entry  maintains information on eash service_type"""
        def __init__ (self):
            self.module = None
            self.name  = None
            self.controller = None
            self.instances = []

    def __init__(self):
        # Services is a hash of service_type : Entry
        self.services = OrderedDict()
        self.root = None

    def __iter__(self):
        for e in self.services:
            for i in e.instances:
                yield i
    def _get_entry (self, service_type):
        return self.services.setdefault (service_type, ServiceDirectory.Entry())

    def register_service (self, name, service, service_type = None):
        """Register a new service (type)"""
        if service is None:
            return
        if service_type is None:
            service_type = service.__controller__.service_type
        e = self._get_entry (service_type)
        e.name = name
        e.module = service
        e.controller = service.__controller__

    def register_instance (self, service):
        """Register a running instance of a service"""
        e = self._get_entry (service.service_type)
        e.instances.append(service)

    def find_class (self, service_type):
        """Find the service class by service type"""
        e = self._get_entry (service_type)
        return  e.controller

    def has_service(self, service_type = None, service_uri = None):
        """Check the existance of a service type and/or service url"""
        r = []
        for ty, entry in self.services.items():
            if service_type and ty != service_type:
                continue
            for s in entry.instances:
                if service_uri and s.uri != service_uri:
                    continue
                r.append(s)
        return r


    def find_service (self, service_type):
        """Return the service instance of service type"""
        entry = self.services.get (service_type, None)
        if not entry:
            log.debug ("Could not find registered service %s", service_type)
            return None
        if len(entry.instances) == 0:
        # Don't automatically try to create instances anymore
            log.warn ("No available instance for service %s", service_type)
            return None
        #    service_url = urlparse.urljoin (self.root , entry.name)
        #    service = entry.module.initialize(service_url)
        #    service_registry.register_instance (service)
        return entry.instances[0]

    def get_services (self, service_type=None):
        """Return all services"""
        if service_type is None:
            return self.services
        return self.services.get (service_type, ServiceDirectory.Entry())


service_registry  = ServiceDirectory()


def load_services ( wanted = None):
    for x in pkg_resources.iter_entry_points ("bisque.services"):
        #log.debug ('found service: ' + str(x))
        try:
            log.debug ('loading %s' % str(x))
            service = x.load()
            log.debug ('found %s' % (service.__file__))
            service_registry.register_service (x.name, service)

        except Exception:
            log.exception ("Failed to load bisque service: %s skipping" % x.name)
        #except Exception, e:
        #    log.exception ("Couldn't load %s -- skipping" % (x.name))



def mount_services (root, enabled = None, disabled = None):
    mounted = []
    pairs   = []
    service_registry.root = root
    for ty, entry in service_registry.get_services().items():
        if (not enabled or  ty in enabled) and ty not in disabled:
            if  hasattr(entry.module, "initialize"):
                service_url = urlparse.urljoin (root , entry.name)
                #service_url = '/' + entry.name
                log.debug ('activating %s at %s' % (str(entry.name), service_url))
                service = entry.module.initialize(service_url)
                if service:
                    service_registry.register_instance (service)
                    pairs.append ( (entry.name, service) )
                    mounted.append(entry.name)
            else:
                log.warn ("SKIPPING %s : no initialize" % entry.name)
        else:
            log.debug ("SKIPPING %s: not wanted " % entry.name)
    missing =  set(enabled) - set (mounted)
    if missing:
        log.warn ("Following service were not found: %s" % missing)
    return pairs



def start_services (root, enabled = None, disabled=None):
    for ty, entry in service_registry.get_services().items():
        if (not enabled or ty in enabled) and ty not in disabled :
            for s in entry.instances:
                if hasattr(s, 'start'):
                    s.start()


def urljoin(base,url, **kw):
    join = urlparse.urljoin(base,url)
    url = urlparse.urlparse(join)
    path = posixpath.normpath(url[2])
    #query = urlparse.parse_qs(url[4])
    if url[4]:
        query = dict ([ q.split('=')  for q in url[4].split('&')])
    else:
        query = {}
    query.update ( urlencode(kw) )
    return urlparse.urlunparse(
        (url.scheme,url.netloc,path,url.params,query,url.fragment)
        )

class ServiceMixin(object):

    def __init__(self, uri):
        """Initialize the Bisque Controller class

        @param url: The base url for this controller
        """
        self.service_type = self.__class__.service_type
        if uri[-1] != '/':
            uri += '/'
        self.fulluri = uri
        #self.baseuri = uri
        self.baseuri = urlparse.urlparse(uri).path
        log.debug ("creating %s at %s" % (self.service_type, self.baseuri))
        urituple = urlparse.urlparse(uri)
        self.host, self.path = urituple.netloc , urituple.path

    def start (self):
        """start the controller.. Used for common operations
        such as background threads and other assorted operations
        before the first request is delivered
        """
        pass


    def get_uri(self):
        try:
            host_url = request.host_url
            #log.debug ("REQUEST %s" , host_url)
        except TypeError:
            #log.warn ("TYPEERROR on request")
            host_url = ''
        return urlparse.urljoin (host_url, self.baseuri)

    uri = property (get_uri)
    url = property (get_uri)


    def makeurl (self, path = "", **kw):
        """Construct a url with a local path and arguments passed
        as named parameters
        i.e.
        self.makeurl ("/view", option='deep', resource="http://aa.com" )
        http://baseuri/view?option=deep&resource=http%2f%fc%fcaa.com
        """

        return urljoin (self.baseuri, path, **kw)
    def __str__(self):
        return self.localuri

    def get_localurl(self):
        return self.path
    localuri = property(get_localurl)

    def get_static (self):
        pass
    staticuri = property (get_static)


    def servicelist(self):
        entries = []
        for name, m in inspect.getmembers (self.__class__, inspect.ismethod):
            if  hasattr(m, 'decoration'):
                args, varargs, kw, df = inspect.getargspec(m)
                tagsargs = [ dict(name='argument', value=arg) for arg in args if arg!='self']
                entries.append ( { 'name' : name,
                                   'type'  : 'service_entry',
                                   'tag' : tagsargs,
                                  })
        return { 'resource' : { 'tag' : entries, 'type': 'service' }}


class ServiceController(BaseController, ServiceMixin):
    def __init__(self, uri):
        ServiceMixin.__init__(self, uri)
