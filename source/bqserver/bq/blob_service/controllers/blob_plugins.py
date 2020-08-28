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
Statistics operatiors : map a vector of object into a vector of strings or numbers

DESCRIPTION
===========

 2) MAP: [vector of objects -> uniform vector of numbers or strings]
    An operator is applied onto the vector of objects to produce a vector of numbers or strings
    The operator is specified by the user and can take specific elements and produces specific result
    for example: operator "area" could take polygon or rect and produce a number
                 operator "numeric-value" can take a "tag" and return tag's value as a number
                 possible operator functions should be extensible and maintained by the stat service

EXTENSIONS
===========

Operations are added by simply deriving from StatOperator and adding your code here

"""

__module__    = "blob_plugins.py"
__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import imp
import os
import inspect
import logging
#from lxml import etree

log = logging.getLogger('bq.blobs.plugins')

#__all__ = [ 'ResourcePlugin', 'ResourcePluginManager' ]

################################################################################
# Base class for resource plugins
################################################################################

#from bq.blob_service.controllers.blob_plugins import ResourcePlugin

class ResourcePlugin (object):
    '''Maps vector of objects into a vector of numbers or strings'''
    name = "ResourcePlugin"
    version = '1.0'
    ext = ''
    resource_type = 'resource'
    mime_type = 'application/octet-stream'

    def __init__(self):
        pass

    def __str__(self):
        return '(%s, %s)'%(self.resource_type, self.ext)

    def is_supported(self, filename):
        ext = os.path.splitext(filename)[1][1:]
        #return os.path.splitext(filename)[1][1:] in self.ext
        return ext.lower() == self.ext.lower()

    def guess_type(self, filename):
        if self.is_supported(filename):
            return self.resource_type
        return None

    def guess_mime(self, filename):
        if self.is_supported(filename):
            return self.mime_type
        return None

    def to_xml(self, filename):
        return None

    # special import processing,
    # inputs:
    #   f - import_service.UploadedResource object
    #
    # outputs:
    #   list of ingested resources
    #def process_on_import(self, f, intags):
    #    # do import processing here
    #    return resources



################################################################################
# Plugin manager
################################################################################

def walk_deep(path, ext=['py']):
    """Splits sub path that follows # sign if present
    """
    files = []
    for root, _, filenames in os.walk(path):
        for f in filenames:
            if os.path.splitext(f)[1][1:] in ext:
                files.append(os.path.join(root, f))
    return files

class ResourcePluginManager(object):

    def __init__(self, path_plugins):
        self.plugins = []
        self.path_plugins = path_plugins

        files = walk_deep(self.path_plugins)
        for f in files:
            module_name = os.path.splitext(os.path.basename(f))[0]
            o = imp.load_source(module_name, f)
            for n,item in inspect.getmembers(o):
                if inspect.isclass(item) and issubclass(item, ResourcePlugin):
                    if item.name != 'ResourcePlugin':
                        log.debug('Adding plugin: %s'%item.name)
                        self.plugins.append(item())
        log.info('Resource plugins: %s', [str(p) for p in self.plugins])

    def guess_type(self, filename):
        for p in self.plugins:
            rt = p.guess_type(filename)
            if rt is not None:
                return rt
        return None

    def guess_mime(self, filename):
        for p in self.plugins:
            rt = p.guess_mime(filename)
            if rt is not None:
                return rt
        return None

    # this will return a list of plugins with an import process function
    def get_import_plugins(self):
        ps = []
        for p in self.plugins:
            if hasattr(p, "process_on_import"):
                ps.append(p)
        return ps
