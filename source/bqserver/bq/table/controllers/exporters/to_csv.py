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
CSV table exporter
"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

# default imports
import os
import logging

__all__ = [ 'ExporterCSV' ]

log = logging.getLogger("bq.table.export.csv")

import csv
try:
    import numpy as np
except ImportError:
    log.info('Numpy was not found but required for table service!')

try:
    import pandas as pd
except ImportError:
    log.info('Pandas was not found but required for table service!')

from pylons.controllers.util import abort
from bq.table.controllers.table_exporter import TableExporter

#---------------------------------------------------------------------------------------
# exporters: Csv
#---------------------------------------------------------------------------------------

class ExporterCSV (TableExporter):
    '''Formats tables as CSV'''

    name = 'csv'
    version = '1.0'
    ext = 'csv'
    mime_type = 'text/csv'

    def info(self, table):
        super(ExporterCSV, self).info(table)
        if table.headers:
            # has headers => this is a leaf object (table or matrix)
            v = [
                "headers,%s"%','.join([str(i) for i in table.headers]),
                "types,%s"%','.join([str(t) for t in table.types]),
            ]
            if table.sizes is not None:
                v.append("sizes,%s"%','.join([str(i) for i in table.sizes]))
        else:
            # no headers => this is a group/subfolder
            v = [ "group,%s"%','.join(["%s;%s"%(tab['path'],tab['type']) for tab in table.tables]), ]

        return ';'.join(v)

    def format(self, table):
        """ converts table to CSV """
        try:
            headers = ','.join([str(i) for i in table.headers])
            if isinstance(table.data, pd.DataFrame):
                t = table.data
            else:
                t = table.as_table()
            return '\n'.join([headers, t.to_csv(header=False, sep=',', line_terminator='\n', index=False)])
        except Exception:
            abort(400, 'Data cannot be converted to CSV')