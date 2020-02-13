# -*- mode: python -*-
"""Main server for client_service}
"""
import os
import logging
import pkg_resources



import tg
from tg import expose, flash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from bq.core.service import ServiceController, service_registry
from bq.client_service import model

import client_service 

log = logging.getLogger("bq.client_service")
class clientController(ServiceController):
    service_type = "client_service"

    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()

    def __init__(self, url):
        super(clientController, self).__init__(url)
        self.defer = client_service.ClientServer (url)
        
    #@expose('bq.client_service.templates.index')
    #def index(self, **kw):
    #    """Add your first page here.. """
    #    return dict(msg=_('Hello from client_service'))
    @expose()
    def _lookup(self, *rest):
        log.debug ('headers:'+ str(tg.request.headers))
        return self.defer, rest

    #@expose()
    #def _default(self, *path, **kw):
    #    log.debug ('headers:'+ str(tg.request.headers))
    #    return self.defer._default(*path, **kw)

def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    service =  clientController(uri)
    #directory.register_service ('client_service', service)

    return service

def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'client_service', 'public'))]

def get_model():
    from bq.client_service import model
    return model



__controller__ = clientController
#__staticdir__ = get_static_dirs()
#__model__ = get_model()
