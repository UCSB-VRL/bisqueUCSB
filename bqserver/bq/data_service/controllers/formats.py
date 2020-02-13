###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008                                               ##
##      by the Regents of the University of California                       ##
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

"""
import logging
from StringIO import StringIO
import csv
import mimeparse

from lxml import etree
import  simplejson as json

from bq.util.xmldict import xml2d, d2xml

log = logging.getLogger ("bq.data_service.formats")

def format_tree(tree, view=None):
    "For internal use.. just return the tree"
    return tree
def input_tree (inpf):
    return inpf

def format_xml(tree, view=None):
    pretty = True if  view and 'pretty' in view else False
    return etree.tounicode(tree, pretty_print=pretty).encode('utf-8')

def input_xml (inpf, inplen=None):
    return etree.parse (inpf).getroot()

def format_json(tree, **kw):
    return json.dumps(xml2d(tree),indent=' ')
def input_json (inpf, **kw):
    return  d2xml (json.load (inpf))


def format_csv (tree, view=None):
    ''' <response>
           <gobject type="mytpe" name="myx" >
             <gobject type="point">
               <vertex x="1" y="1" z="1" />
             </gobject?
          </gobject
          <rectange name="yy">
             <vertex ...>
             <vertex


        </response>
        ===>>

        type    name    x1 y1 z1 t ch
        ============================================
        mytpe   myx
        point
        vertwx          1  1  1

        rectangle
        vertex          x  x  x
        vertex          x  x  x
        '''

    buffer = StringIO()
    writer = csv.writer(buffer)
    stack = []

    if tree.tag == 'response':
        for sub in tree:
                stack.append ( (sub, None) )
    else:
        stack = [ (tree, None) ]

    writer.writerow (['type', 'name', 'value', 'x', 'y', 'z', 't', 'ch'])

    while len(stack) :
        element, parent = stack.pop(-1)
        #log.debug (" processing %s " % (str (element)) )
        if element is None:
            writer.writerow( [])
            continue
        attrs = element.attrib
        if element.tag == 'vertex':
            writer.writerow ( [ 'vertex', None, None,
                                attrs.get('x', None),
                                attrs.get('y', None),
                                attrs.get('z', None),
                                attrs.get('t', None),
                                attrs.get('ch', None) ] )
        else:
            if element.tag != 'gobject':
                gtype = element.tag
            else:
                gtype = attrs.get('type', None)
            writer.writerow ( [ gtype , attrs.get('name', None), attrs.get('value', None)] )
            stack.append ( (None, None))
            for sub in element:
                stack.append ( (sub, element) )
    return buffer.getvalue()

def input_csv (inpf, **kw):
    pass


FORMATTERS = { 'xml' : (format_xml, 'text/xml' ),
               'csv' : (format_csv, 'text/csv'), #text/csv application/vnd.ms-excel or text/plain
               'tree': (format_tree, 'application'),
               'json': (format_json, 'application/json'),
             }


CONTENT_TYPE_CONVERTERS = {
    'text/xml' : (format_xml, input_xml, 'xml'),
    'text/csv' : (format_csv, input_csv, 'csv'),
    'appication/tree' : (format_tree, input_tree, 'tree'),
    'application/json' : (format_json, input_json, 'json'),
    'application/xml' : (format_xml, input_xml, 'xml'),
}
NO_CONV=(None,None,None)

def find_formatter (format=None, accept_header=None, **kw):
    if format is not None:
        return FORMATTERS.get(format, (format_xml, 'text/xml' ))
    # Parse accept header until acceptable is found
    if accept_header is None:
        accept_header = "application/xml"
    accept_header  = mimeparse.best_match (CONTENT_TYPE_CONVERTERS.keys(), accept_header)
    converter =  CONTENT_TYPE_CONVERTERS.get (accept_header, NO_CONV)[0]
    return (converter, accept_header)

def find_formatter_type (accept_header=None, **kw):
    if accept_header is None:
        accept_header = "application/xml"
    accept_header  = mimeparse.best_match (CONTENT_TYPE_CONVERTERS.keys(), accept_header)
    type_ =  CONTENT_TYPE_CONVERTERS.get (accept_header, NO_CONV)[2]
    return type_

def find_inputer  (content_type):
    content_type = content_type.split(';')[0].strip()
    return CONTENT_TYPE_CONVERTERS.get (content_type, NO_CONV)[1]
