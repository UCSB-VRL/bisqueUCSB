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
CSV table importer
"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

# default imports
import os
import sys
import sys
import logging
import csv

from pylons.controllers.util import abort
import pandas as pd


from bq import blob_service
from bq.table.controllers.table_base import TableLike

__all__ = [ 'TableCSV' ]

log = logging.getLogger("bq.table.import.csv")



################################################################################
# misc
################################################################################

def extjs_safe_header(s):
    # need to keep original names; otherwise queries may not work
    #if isinstance(s, basestring):
    #    return s.replace('.', '_')
    return s

def _get_headers_types(data, startcol=None, endcol=None, has_header=False):
    if has_header:
        headers = [extjs_safe_header(x) for x in data.columns.values.tolist()[slice(startcol, endcol, None)]] # extjs errors loading strings with dots
    else:
        headers = [str(i) for i in range(startcol or 0, endcol or data.shape[1])]
    types = [t.name for t in data.dtypes.tolist()[slice(startcol, endcol, None)]] #data.dtypes.tolist()[0].name
    return (headers, types)

def get_cb_csv(filename):
    def cb_csv(slices):
        # read only slices (skip header line)
        return pd.read_csv(filename, skiprows=xrange(1,slices[0].start+1), nrows=slices[0].stop-slices[0].start, usecols=range(slices[1].start, slices[1].stop))  # TODO: use chunked reading to handle large datasets
    return cb_csv

#---------------------------------------------------------------------------------------
# Importer: CSV
#---------------------------------------------------------------------------------------

class TableCSV(TableLike):
    '''Formats tables into output format'''

    name = 'csv'
    version = '1.0'
    ext = ['csv']
    mime_type = 'text/csv'

    def __init__(self, uniq, resource, path, **kw):
        """ Returns table information """
        super(TableCSV, self).__init__(uniq, resource, path, **kw)

        if self.t is None:
            # try to load the resource binary
            b = blob_service.localpath(uniq, resource=resource) or abort (404, 'File not available from blob service')
            self.filename = b.path
            self.has_header = True
            self.info()

    def close(self):
        """Close table"""
        log.debug("closing CSV file")
        self.t = None

    def info(self, **kw):
        """ Returns table information """
        if self.data is None:
            # load headers and types if empty
            with open(self.filename, 'rb') as f:
                buf = f.read(1024)
                try:
                    self.has_header = csv.Sniffer().has_header(buf)
                except csv.Error:
                    self.has_header = True
            if self.has_header is True:
                data = pd.read_csv(self.filename, skiprows=0, nrows=10 )
            else:
                data = pd.read_csv(self.filename, skiprows=0, nrows=10, header=None )
            # TODO: rows set to maxint for now
            self.sizes = (sys.maxint, data.shape[1]) # pylint: disable=no-member
            self.cb = get_cb_csv(self.filename)  # for lazy fetching
        else:
            data = self.data
            self.sizes = list(data.shape)
            
        self.headers, self.types = _get_headers_types(data, has_header=self.has_header)
        self.t = True
        log.debug('CSV types: %s, header: %s, sizes: %s', str(self.types), str(self.headers), str(self.sizes))
        return { 'headers': self.headers, 'types': self.types, 'sizes': self.sizes }

    def write(self, data, **kw):
        """ Write cells into a table"""
        abort(501, 'CSV write not implemented')

    def delete(self, **kw):
        """ Delete cells from a table"""
        abort(501, 'CSV delete not implemented')
