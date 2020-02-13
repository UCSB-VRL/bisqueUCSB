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
HDF table importer
"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

# default imports
import os
import logging
import pkg_resources
import re
from pylons.controllers.util import abort

from bq import blob_service

__all__ = [ 'TableHDF' ]

log = logging.getLogger("bq.table.import.hdf")

try:
    import numpy as np
except ImportError:
    log.info('Numpy was not found but required for table service!')

try:
    import tables
except ImportError:
    log.info('Tables was not found but required for Excel tables!')

try:
    import pandas as pd
except ImportError:
    log.info('Pandas was not found but required for table service!')

from bq.table.controllers.table_base import TableBase, TableLike, ArrayLike

################################################################################
# misc
################################################################################

def extjs_safe_header(s):
    # need to keep original names; otherwise queries may not work
    #if isinstance(s, basestring):
    #    return s.replace('.', '_')
    return s

def _get_type(n):
    if isinstance(n, tables.group.Group):
        return 'group'
    elif isinstance(n, tables.table.Table):
        return 'table'
    elif isinstance(n, tables.array.Array):
        return 'matrix'
    else:
        log.debug("UNKNOWN TABLE TYPE: %s", type(n))
        return '(unknown)'

def _get_headers_types(node, startcol=None, endcol=None):
    if isinstance(node, tables.table.Table):
        headers = node.colnames[slice(startcol, endcol, None)]
        types = [node.coltypes[h] if h in node.coltypes else '(compound)' for h in node.colnames[slice(startcol, endcol, None)]]
    elif isinstance(node, tables.array.Array):
        if node.ndim > 1:
            headers = [str(i) for i in range(startcol or 0, endcol or node.shape[1])]
            types = [node.dtype.name for i in range(startcol or 0, endcol or node.shape[1])]
        elif node.ndim > 0:
            headers = [str(i) for i in range(startcol or 0, endcol or 1)]
            types = [node.dtype.name for i in range(startcol or 0, endcol or 1)]
        else:
            headers = ['']
            types = [node.dtype.name]
    else:
        # group node
        headers = []
        types = []
    return ( headers, types )

def _get_node_attributes(node):
    tags = {}
    for name in node._v_attrs._f_list():
        tags[name] = node._v_attrs[name]
    # try:
    #     for name in node._v_attrs._f_list():
    #         tags[name] = node._v_attrs[name]
    # except Exception:
    #     pass
    log.debug('Metadata: %s', str(tags))
    return tags


#---------------------------------------------------------------------------------------
# Importer: HDF
# TODO: not reading ranges
# TODO: proper parsing of sub paths
#---------------------------------------------------------------------------------------

class TableHDF(TableBase):
    '''Formats tables into output format'''

    name = 'hdf'
    version = '1.0'
    ext = ['h5', 'hdf5', 'h5ebsd', 'dream3d']
    mime_type = 'application/x-hdf'

    def __init__(self, uniq, resource, path, **kw):
        """ Returns table information """
        super(TableHDF, self).__init__(uniq, resource, path, **kw)

        if self.t is None:
            # try to load the resource binary
            b = blob_service.localpath(uniq, resource=resource) or abort (404, 'File not available from blob service')
            self.filename = b.path
            try:
                self.info()
            except Exception:
                # close any open table
                if self.t is not None:
                    self.t.close()
                raise

    def get_queriable(self):
        if self.data is None:
            self.info()

        # this could be either table or array => return based on self.data type
        if isinstance(self.data, tables.table.Table):
            return TableLikeHDF(None, None, None, table=self)
        elif isinstance(self.data, tables.array.Array):
            return ArrayLikeHDF(None, None, None, table=self)
        else:
            return TableLikeHDF(None, None, None, table=self, data=pd.DataFrame(), sizes=[], offset=0, types=[], headers=[])

    def _collect_arrays(self, path='/'):
        try:
            try:
                node = self.t.get_node(path) # v3 API
            except AttributeError:
                node = self.t.getNode(path) # pylint: disable=no-member
        except tables.exceptions.NoSuchNodeError:
            return []
        if not isinstance(node, tables.group.Group):
            return [ { 'path':path, 'type':_get_type(node) } ]

        try:
            r = [ { 'path':path.rstrip('/') + '/' + n._v_name, 'type':_get_type(n) } for n in self.t.iter_nodes(path) ] # v3 API
        except AttributeError:
            r = [ { 'path':path.rstrip('/') + '/' + n._v_name, 'type':_get_type(n) } for n in self.t.iterNodes(path) ] # pylint: disable=no-member
        return r

    def close(self):
        """Close table"""
        if self.t is not None:
            log.debug("closing HDF file")
            self.t.close()

    def info(self, **kw):
        """ Returns table information """
        if self.data is None:
            # load headers and types if empty
            if self.t is None:
                try:
                    # TODO: could lead to problems when multiple workers open same file???
                    # dima: no problems when reading but will have issues when writing and will require file locking
                    try:
                        self.t = tables.open_file(self.filename) # v3 API
                    except AttributeError:
                        self.t = tables.openFile(self.filename) # pylint: disable=no-member
                except Exception:
                    log.exception('HDF file cannot be read')
                    raise RuntimeError("HDF file cannot be read")

            # determine which part of path is group in HDF vs operations
            end = len(self.path)
            for i in range(len(self.path)):
                if '/' + '/'.join([p.strip('"') for p in self.path[0:i+1]]) not in self.t:    # allow quoted path segments to escape slicing, e.g. /bla/"0:100"/bla
                    end = i
                    break
            self.subpath = '/' + '/'.join([p.strip('"') for p in self.path[0:end]])
            self.path = self.path[end:]

            if self.tables is None:
                self.tables = self._collect_arrays(self.subpath)

            if len(self.tables) == 0:
                # subpath not found
                abort(404, "Object '%s' not found" % self.subpath)

            log.debug('HDF subpath: %s, path: %s', self.subpath, str(self.path))

            try:
                node = self.t.get_node(self.subpath or '/') # v3 API
            except AttributeError:
                node = self.t.getNode(self.subpath or '/') # pylint: disable=no-member
            self.data = node
        else:
            node = self.data

        self.headers, self.types = _get_headers_types(node)
        self.meta = _get_node_attributes(node)
        if isinstance(node, tables.array.Array):
            self.sizes = list(node.shape)
        elif isinstance(node, tables.table.Table):
            self.sizes = [node.shape[0], len(self.headers)]
        else:
            self.sizes = []
        log.debug('HDF types: %s, header: %s, sizes: %s, meta size: %s', str(self.types), str(self.headers), str(self.sizes), len(self.meta))
        return { 'headers': self.headers, 'types': self.types, 'sizes': self.sizes, 'meta': self.meta }


class TableLikeHDF(TableHDF, TableLike):
    def __init__(self, uniq, resource, path, **kw):
        super(TableLikeHDF, self).__init__(uniq, resource, path, **kw)

    def write(self, data, **kw):
        """ Write cells into a table"""
        abort(501, 'HDF write not implemented')

    def delete(self, **kw):
        """ Delete cells from a table"""
        abort(501, 'HDF delete not implemented')


class ArrayLikeHDF(TableHDF, ArrayLike):
    def __init__(self, uniq, resource, path, **kw):
        super(ArrayLikeHDF, self).__init__(uniq, resource, path, **kw)

    def write(self, data, **kw):
        """ Write cells into a table"""
        abort(501, 'HDF write not implemented')

    def delete(self, **kw):
        """ Delete cells from a table"""
        abort(501, 'HDF delete not implemented')
