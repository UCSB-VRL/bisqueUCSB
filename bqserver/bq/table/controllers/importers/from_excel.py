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
Excel table importer
"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

# default imports
import os
import sys
import logging
import pkg_resources
from pylons.controllers.util import abort

from bq import blob_service

__all__ = [ 'TableExcel' ]

log = logging.getLogger("bq.table.import.excel")

try:
    import numpy as np
except ImportError:
    log.info('Numpy was not found but required for table service!')

try:
    import xlrd
except ImportError:
    log.info('Xlrd was not found but required for Excel tables!')

try:
    import pandas as pd
except ImportError:
    log.info('Pandas was not found but required for table service!')

from bq.table.controllers.table_base import TableLike


################################################################################
# misc
################################################################################

def extjs_safe_header(s):
    # need to keep original names; otherwise queries may not work
    #if isinstance(s, basestring):
    #    return s.replace('.', '_')
    return s

def _get_headers_types(data, startcol=None, endcol=None):
    headers = [extjs_safe_header(x) for x in data.columns.values.tolist()[slice(startcol, endcol, None)]] # extjs errors loading strings with dots
    types = [t.name for t in data.dtypes.tolist()[slice(startcol, endcol, None)]] #data.dtypes.tolist()[0].name
    return (headers, types)
            
def get_cb_excel(t, path):
    def cb_excel(slices):
        # read only slices
        data = pd.read_excel(t, path, skiprows=xrange(1,slices[0].start+1), parse_cols=range(slices[1].start, slices[1].stop))  # TODO: use chunked reading to handle large datasets
        # excel cannot read only a specified number of rows, select now
        return data[0:slices[0].stop-slices[0].start]
    return cb_excel

#---------------------------------------------------------------------------------------
# Importer: Excel
# TODO: identify if header is present
# TODO: only read the requested number of rows
#---------------------------------------------------------------------------------------

class TableExcel(TableLike):
    '''Formats tables into output format'''

    name = 'excel'
    version = '1.0'
    ext = ['xls', 'xlsx']
    mime_type = 'application/vnd.ms-excel'

    def __init__(self, uniq, resource, path, **kw):
        """ Returns table information """
        super(TableExcel, self).__init__(uniq, resource, path, **kw)

        if self.t is None:
            # try to load the resource binary
            b = blob_service.localpath(uniq, resource=resource) or abort (404, 'File not available from blob service')
            self.filename = b.path
            self.info()

    def get_queriable(self):
        return self
    
    def close(self):
        """Close table"""
        if self.t is not None:
            log.debug("closing Excel file")
            self.t.close()

    def info(self, **kw):
        """ Returns table information """
        if self.data is None:
            # load headers and types if empty
            if self.tables is None:
                try:
                    self.t = pd.ExcelFile(self.filename)
                except Exception:
                    raise RuntimeError("Excel file cannot be read")
                self.tables = [ { 'path':name, 'type':'sheet' } for name in self.t.sheet_names ]
    
            if len(self.tables)==1: # if only one sheet is present
                self.subpath = self.tables[0]['path']
                if len(self.path)>0 and self.path[0] == self.subpath:
                    self.path.pop(0)
            elif len(self.path)>0 and self.path[0] in [tab['path'] for tab in self.tables]: # if path is provided for a sheet
                self.subpath = self.path.pop(0)
            else: # if no path is provided, use first sheet
                self.subpath = self.tables[0]['path']
    
            data = pd.read_excel(self.t, self.subpath, nrows=1)
            self.sizes = (sys.maxint, data.shape[1])  # pylint: disable=no-member
            self.cb = get_cb_excel(self.t, self.subpath)  # for lazy fetching
        else:
            data = self.data
            self.sizes = list(data.shape)
            
        self.headers, self.types = _get_headers_types(data)
        log.debug('Excel types: %s, header: %s, sizes: %s', str(self.types), str(self.headers), str(self.sizes))
        return { 'headers': self.headers, 'types': self.types, 'sizes': self.sizes }

    def write(self, data, **kw):
        """ Write cells into a table"""
        abort(501, 'Excel write not implemented')

    def delete(self, **kw):
        """ Delete cells from a table"""
        abort(501, 'Excel delete not implemented')

