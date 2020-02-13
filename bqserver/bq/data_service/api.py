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

  Interface to an data server for other bisquik components.
  Abstract access to local, remote and multiple actual datas servers

"""
import logging

from bq.core.service import service_registry

RESOURCE_READ=0
RESOURCE_EDIT=1

log = logging.getLogger('bq.data_service')


def find_server(server):
    return service_registry.find_service ('data_service')

def uri():
    server = find_server('')
    return server.uri

#def servers():
#    '''return list of dataservers
#    '''
#    return service_registry.get_services ('data_service').instances

def new_image(server=None, **kw):
    ''' Find the preferred data server and store the data there
    Excess named arguments are used as attributes for the image object
    '''

    if server is None: server = service_registry.find_service ('data_service')

    return server.new_image(**kw)

def append_resource(resource, tree, server = None, **kw):
    '''Append (an) element(s) to an existing resource
    '''
    if server is None: server = service_registry.find_service ('data_service')

    return server.append_resource(resource, tree, **kw)

def new_resource(resource, server=None, **kw):
    ''' Create a new resource
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.new_resource(resource, **kw)

def resource_load(uniq=None, server=None, **kw):
    ''' Create a new resource
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.resource_load(uniq=uniq, **kw)

def get_resource(resource, server=None, **kw):
    ''' Create a new resource
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.get_resource(resource, **kw)

def del_resource(resource, server=None, **kw):
    ''' Create a new resource
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.del_resource(resource, **kw)

def auth_resource(resource, server=None, **kw):
    ''' Create a new resource
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.auth_resource(resource, **kw)

def update_resource(resource, server=None, new_resource=None, replace=True,  **kw):
    ''' Create a new resource
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.update_resource(resource=resource, new_resource=new_resource, replace=replace, **kw)

def resource_uniq(server=None, **kw):
    ''' Create a new resource
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.resource_uniq(**kw)

def load(resource_url, **kw):
    '''Return XML resource document
    '''
    #log.debug("user currently logged in is: " + identity.current.user)
    server = find_server(resource_url)
    if server:
        return server.load(resource_url, **kw)
    log.debug('no server found')
    return None

def query(resource_type=None, server=None, **kw):
    '''Return query results as list of XML documents
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.query(resource_tag=resource_type, **kw)

def count(resource_type, server=None, **kw):
    '''Return query results as list of XML documents
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.count(resource_type, **kw)

def retrieve(resource_type, token, server=None, **kw):
    if server is None: server = service_registry.find_service ('data_service')

    return server.retrieve(resource_type, token, **kw)

def update(resource_tree, server = None, replace_all=False, **kw):
    '''Update an existing resource with the given tree
    '''
    if server is None: server = service_registry.find_service ('data_service')
    return server.update (resource_tree, replace_all, **kw)


def resource_controller(token, server = None, **kw):
    if server is None: server = service_registry.find_service ('data_service')
    return server.get_child_resource(token, **kw)

def cache_invalidate(url, user_id = None, server = None):
    if server is None: server = service_registry.find_service ('data_service')
    return server.cache_invalidate(url, user_id)

def default (*path, **kw):
    server = service_registry.find_service ('data_service')
    return server._default(*path, **kw)
