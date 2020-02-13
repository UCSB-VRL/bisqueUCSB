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

__all__ = [ 'ExporterXML' ]

log = logging.getLogger("bq.table.export.xml")

import collections

from lxml import etree
try:
    import numpy as np
except ImportError:
    log.info('Numpy was not found but required for table service!')

try:
    import pandas as pd
except ImportError:
    log.info('Pandas was not found but required for table service!')


from bq.table.controllers.table_exporter import TableExporter


def _nested_list_to_str(l):
    # flatten nested list in l via depth first traversal
    if hasattr(l, '__iter__'):
        try:
            return ','.join([_nested_list_to_str(cell) for cell in l])
        except TypeError:
            pass   # not iterable => just return string
    return str(l)


#---------------------------------------------------------------------------------------
# exporters: XML
#---------------------------------------------------------------------------------------

class ExporterXML (TableExporter):
    '''Formats tables as XML'''

    name = 'xml'
    version = '1.0'
    ext = 'xml'
    mime_type = 'text/xml'

    def info(self, table):
        super(ExporterXML, self).info(table)
        xml = etree.Element ('resource', uri=table.url)
        if table.headers:
            # has headers => this is a leaf object (table or matrix)
            if isinstance(table.data, pd.core.frame.DataFrame):
                etree.SubElement (xml, 'tag', name='type', value='table')
            else:
                etree.SubElement (xml, 'tag', name='type', value='matrix')

            el = etree.SubElement (xml, 'tag', name='headers', value=','.join([str(i) for i in table.headers]))
            el = etree.SubElement (xml, 'tag', name='types', value=','.join([str(t) for t in table.types]))
            if table.sizes is not None:
                el = etree.SubElement (xml, 'tag', name='sizes', value=','.join([str(i) for i in table.sizes]))
        else:
            # no headers => this is a group/subfolder
            etree.SubElement (xml, 'tag', name='type', value='group')
            el = etree.SubElement (xml, 'tag', name='group')
            for tab in table.tables:
                etree.SubElement (el, 'tag', name=tab['path'], type=tab['type'])

        if table.meta is not None and len(table.meta)>0:
            for n,v in table.meta.iteritems():
                etree.SubElement (xml, 'tag', name='%s'%n, value='%s'%v)

        return etree.tostring(xml)

    def format(self, table):
        """ converts table to XML """
        m = table.as_array()
        ndim = m.ndim
        if ndim > 0:
            v = []
            for i in range(m.shape[0]):
                v.append( _nested_list_to_str(m[i]) )
        else:
            # 0-dimensional array => single value
            v = [str(m)]
        xml = etree.Element ('resource', uri=table.url)
        doc = etree.SubElement (xml, 'tag', name='table', value=';'.join(v))
        el = etree.SubElement (doc, 'tag', name='offset', value=str(table.offset))
        el = etree.SubElement (doc, 'tag', name='headers', value=','.join([str(i) for i in table.headers]))
        el = etree.SubElement (doc, 'tag', name='types', value=','.join([str(t) for t in table.types]))
        if table.sizes is not None:
            el = etree.SubElement (doc, 'tag', name='sizes', value=','.join([str(i) for i in table.sizes]))
        return etree.tostring(xml)

