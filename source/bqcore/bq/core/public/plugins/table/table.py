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


__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

from bq.blob_service.controllers.blob_plugins import ResourcePlugin

class TablePlugin (ResourcePlugin):
    '''Supports Tabular Files'''
    name = "TablePlugin"
    version = '1.0'
    ext = 'csv'
    resource_type = 'table'
    mime_type = 'text/csv'

    def __init__(self):
        pass

class CsvTablePlugin (TablePlugin):
    '''Supports CSV file'''
    ext = 'csv'
    mime_type = 'text/csv'

class XlsXTablePlugin (TablePlugin):
    '''Supports Excel file'''
    ext = 'xlsx'
    mime_type = 'application/vnd.ms-excel'

class XlsTablePlugin (TablePlugin):
    '''Supports Excel file'''
    ext = 'xls'
    mime_type = 'application/vnd.ms-excel'

class HdfTablePlugin1 (TablePlugin):
    '''Supports HDF file'''
    ext = 'hdf'
    mime_type = 'application/x-hdf'

class HdfTablePlugin2 (TablePlugin):
    '''Supports HDF5 file'''
    ext = 'hdf5'
    mime_type = 'application/x-hdf'

class HdfTablePlugin3 (TablePlugin):
    '''Supports HDF5 file'''
    ext = 'h5'
    mime_type = 'application/x-hdf'

class HdfTablePlugin4 (TablePlugin):
    '''Supports HDF5 file'''
    ext = 'he5'
    mime_type = 'application/x-hdf'

class HdfTablePlugin5 (TablePlugin):
    '''Supports HDF5 file'''
    ext = 'h5ebsd'
    mime_type = 'application/x-hdf'
    
class HdfTablePlugin6 (TablePlugin):
    '''Supports HDF5 file used by Dream.3D'''
    ext = 'dream3d'
    mime_type = 'application/x-hdf'