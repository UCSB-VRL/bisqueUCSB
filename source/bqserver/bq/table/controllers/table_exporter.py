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
Table base for exporterters

"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

# default imports
import os
import logging
import pkg_resources

from tg import response

log = logging.getLogger("bq.table.exporter")

__all__ = [ 'TableExporter' ]

#---------------------------------------------------------------------------------------
# Exporters: Table base
#---------------------------------------------------------------------------------------

class TableExporter(object):
    '''Formats tables into output format'''

    name = ''
    version = '1.0'
    ext = 'table'
    mime_type = 'text/plain'

    def __init__(self):
        pass

    # needs implementation for particular format
    def info(self, table):
        response.headers['Content-Type'] = self.mime_type

    def format(self, table):
        pass

    def export(self, table):
        """Add your first page here.. """
        fname = '%s.%s' % (table.resource.get('name'), self.ext)
        # try:
        #     fname.encode('ascii')
        #     disposition = 'filename="%s"'%(fname)
        # except UnicodeEncodeError:
        #     disposition = 'filename="%s"; filename*="%s"'%(fname.encode('utf8'), fname.encode('utf8'))
        # response.headers['Content-Disposition'] = disposition

        response.headers['Content-Type'] = self.mime_type
        return self.format(table)
