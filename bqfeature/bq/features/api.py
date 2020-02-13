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

  Interface to an feature server for other bisquik components.
  Abstract access to local feature server

"""
import logging
import urlparse
import functools
from tg import config

from bq.core.service import service_registry
from .controllers.TablesInterface import Tables

log = logging.getLogger('bq.features')

def find_server():
    return service_registry.find_service ('features')


def return_feature_vector(feature_name,**resource):
    """
        returns feature on the resource from the feature service
    """
    server = find_server()
    feature_init = server.FEATURE_ARCHIVE[feature_name]()
    resource_list = server.ResourceList( None, feature_name, 'none')
    resource_list.append(**resource)
    format = server.NumPy(feature_init, None)
    feature_table = Tables(feature_init)
    return format.return_from_tables( feature_table, resource_list)


def return_feature_location_in_tables(feature_name, **resource):
    """
        returns the location of the features requested on the resource from the stored tables
    """
    server = find_server()
    feature_init = server.FEATURE_ARCHIVE[feature_name]()
    resource_list = server.ResourceList( None, feature_name, 'none')
    resource_list.append(**resource)
    format = server.LocalPath(feature_init, None)
    feature_table = Tables(feature_init)
    localpath = format.return_from_tables( feature_table, resource_list)
    if len(localpath)==1:
        return localpath[0]
    else:
        return (None, None)


def return_feature_list():
    """returns a list of registered features"""
    server = find_server()
    return server.FEATURE_ARCHIVE.keys()


#def return_feature_info(feature_name):
#    """
#        returns information in the xml format
#    """
#    return

#def return_table_length(feature_name):
#    """returns amount of features in the feature table storage"""
#    server = find_server()
#    feature_init = server.FEATURE_ARCHIVE[feature_name]()
#    return len(server.Tables(feature_init))

#def cached_feature(feature_name,**resource):
#    """Checks to see if the features are stored in the feature tables"""
#    return

#def delete(feature_name,**resource):
#    """Delete feature vectors attached to this resource"""
#    pass
#
#def delete_table(feature_name):
#    """Deletes a feature tables"""
#    pass
#
#def delete_cache(feature_name):
#    """Deletes a table in the workdir"""
#    pass
