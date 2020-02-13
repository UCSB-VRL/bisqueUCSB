###############################################################################
##  BisQue                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2015 by the Regents of the University of California     ##
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
Plug-in class manager

"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

# default imports
import os
import imp
import inspect
import logging
import pkg_resources

log = logging.getLogger("bq.pipeline.plugins")

__all__ = [ 'PluginManager' ]

#---------------------------------------------------------------------------------------
# misc
#---------------------------------------------------------------------------------------

def walk_deep(path, ext='py'):
    """Splits sub path that follows # sign if present
    """
    files = []
    for root, _, filenames in os.walk(path):
        for f in filenames:
            if os.path.splitext(f)[1][1:] in ext:
                files.append(os.path.join(root, f))
    return files

#---------------------------------------------------------------------------------------
# Pipeline base
#---------------------------------------------------------------------------------------

class PluginManager(object):

    def __init__(self, name, path_plugins, NeededClass):
        self.name = name
        self.plugins = {}
        self.path_plugins = path_plugins

        files = walk_deep(self.path_plugins)
        for f in files:
            module_name = os.path.splitext(os.path.basename(f))[0]
            try:
                o = imp.load_source(module_name, f)
                for n,item in inspect.getmembers(o):
                    if inspect.isclass(item) and issubclass(item, NeededClass):
                        if item.name != '':
                            log.debug('Adding plugin: %s', item.name)
                            self.plugins[item.name] = item
            except Exception:
                log.exception('Could not load: %s', module_name)

        log.info('Available %s plugins: %s', self.name, ','.join(self.plugins.keys()))
