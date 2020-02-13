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
BQ API - a set of classes that represent Bisque objects

"""

__module__    = "bqapi.py"
__author__    = "Dmitry Fedorov and Kris Kvilekval"
__version__   = "0.1"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

from lxml import etree
import sys
import math
import inspect
import logging
from urllib import quote

log = logging.getLogger('bisquik.API')

__all__ = [ 'BQFactory', 'BQNode', 'BQResource', 'BQValue', 'BQTag', 'BQVertex', 'BQGObject', 'gobject_primitives',
            'BQPoint', 'BQLabel', 'BQPolyline', 'BQPolygon', 'BQCircle', 'BQEllipse', 'BQRectangle', 'BQSquare', 'BQLine' ]

gobject_primitives = set(['point', 'label', 'polyline', 'polygon', 'circle', 'ellipse', 'rectangle', 'square', 'line'])


################################################################################
# Base class for bisque resources
################################################################################

class BQNode (object):
    '''Base class for parsing Bisque XML'''
    xmltag = ''
    xmlfields = []
    def __init__(self, element=None):
        if not element is None: self.fromEtree(element)

    def __repr__(self):
        return '(%s:%s)'%(self.xmltag, self.xmlfields)

    def getAttr(self, a):
        if hasattr(self, a) and not getattr(self, a) is None:
            return getattr(self, a)
        else:
            return ''

    def fromEtree(self, element):
        #if element.tag != xmltag: return # in case of gobjects tag name many be different...
        for a in self.xmlfields:
            if a in element.attrib:
                setattr(self, a, element.attrib[a])

    def toEtree(self, parent=None):
        no_parent = False
        if parent is None: parent = etree.Element ('resource'); no_parent = True
        tag = etree.SubElement (parent, self.xmltag)
        for f in self.xmlfields:
            if hasattr(self, f) and not getattr(self, f) is None:
                tag.attrib[f] = getattr(self, f)
        if no_parent: return parent
        else: return tag

    def toTuple (self):
        return tuple( [ x for x in self.xmlfields ] )


################################################################################
# Base class for bisque resources
################################################################################

class BQResource (BQNode):
    '''Base class for Bisque resources'''
    xmltag = 'resource'
    xmlfields = ['name', 'uri', 'ts']


################################################################################
# Tag
################################################################################

class BQValue (BQNode):
    '''tag value'''
    xmltag = "value"
    xmlfields = ['value']
    def __init__(self, element=None, value=None):
        if value is None:
            self.values = []
        else:
            self.values = [value]
        if not element is None: self.fromEtree(element)

    def __call__(self):
        if len(self.values<=0): return ''
        elif len(self.values==1): return self.values[0]
        def str_join(x,y): return '%s,%s'%(x,y)
        return reduce(str_join, self.values)

    def fromEtree(self, element):
        if 'value' in element.attrib:
            self.values.append(element.attrib['value'])
            return
        for v in element.iter('value'):
            self.values.append( v.text )

    def toEtree(self, element):
        if len(self.values)==1 and len(str(self.values[0]))<100:
            element.attrib['value'] = self.values[0]
        else:
            for v in self.values:
                val = etree.SubElement (element, 'value')
                val.text = v

    def toString(self):
        return u','.join(  self.values )


class BQTag (BQNode):
    '''tag resource'''
    xmltag = "tag"
    xmlfields = ['name', 'type', 'uri', 'ts']
    def __init__(self, element=None, name='', value=None):
        self.name = name
        self.value = BQValue(value=value)
        self.tags = []
        if not element is None: self.fromEtree(element)

    def fromEtree(self, element):
        super(BQTag, self).fromEtree(element=element)
        self.value.fromEtree(element)

    def toEtree(self, parent=None):
        response = super(BQTag, self).toEtree(parent=parent)
        if not self.value is None:
           if parent is None:
               self.value.toEtree(response.find(self.xmltag))
           else:
               self.value.toEtree(response)
        return response


################################################################################
# GObject
################################################################################

class BQVertex (BQNode):
    '''gobject vertex'''
    xmltag = "vertex"
    xmlfields = ['x', 'y', 'z', 't', 'ch', 'index']

    def __init__(self, element=None):
        self.x = None; self.y = None; self.z = None; self.t = None; self.c = None; self.index = None;
        super(BQVertex, self).__init__(element=element)

    def fromEtree(self, element):
        super(BQVertex, self).fromEtree(element=element)
        # now convert all coordinates to floats
        for a in self.xmlfields:
            if hasattr(self, a) and not getattr(self, a) is None:
                setattr(self, a, float(getattr(self, a)))

    def __repr__(self):
        return 'vertex(x:%s,y:%s,z:%s,t:%s,c:%s,i:%s)'%(self.x, self.y, self.z, self.t, self.c, self.index)

    def toTuple(self):
        return (self.x, self.y, self.z, self.t)

    def fromTuple(self, v):
        x,y,z,t = v
        self.x=x; self.y=y; self.z=z; self.t=t

    def toString(self):
        def toStr(a):
            return '' if a is None else a
        return '%s, %s, %s, %s, %s, %s'%(toStr(self.x), toStr(self.y), toStr(self.z), toStr(self.t), toStr(self.c), toStr(self.index))


class BQGObject (BQNode):
    '''tag resource'''
    type = 'gobject'
    xmltag = "gobject"
    xmlfields = ['name', 'type', 'uri']
    def __init__(self, element=None):
        self.vertices = []
        self.tags     = []
        self.name  = None
        if not element is None: self.fromEtree(element)

    def __repr__(self):
        return '(type: %s, name: %s, %s)'%(self.type, self.name, self.vertices)

    def fromEtree(self, element):
        super(BQGObject, self).fromEtree(element=element)
        for v in element.iter('vertex'):
            self.vertices.append( BQVertex(v) )

    def verticesAsTuples(self):
        return [v.toTuple() for v in self.vertices ]

    def perimeter(self):
        return -1

    def area(self):
        return -1


class BQPoint (BQGObject):
    '''point gobject resource'''
    xmltag = "point"
    pass

class BQLabel (BQGObject):
    '''label gobject resource'''
    xmltag = "label"
    pass

class BQPolyline (BQGObject):
    '''polyline gobject resource'''
    xmltag = "polyline"
    def perimeter(self):
        vx = self.verticesAsTuples()
        d = 0
        for i in range(0, len(vx)-1):
            x1,y1,z1,t1 = vx[i]
            x2,y2,z2,t2 = vx[i+1]
            d += math.sqrt( math.pow(x2-x1,2.0) + math.pow(y2-y1,2.0) )
        return d

class BQLine (BQPolyline):
    '''line gobject resource'''
    xmltag = "line"
    pass

# only does 2D version right now, polygon area is flawed if the edges are intersecting
# implement better algorithm based on triangles
class BQPolygon (BQGObject):
    '''Polygon gobject resource'''
    xmltag = "polygon"
    # only does 2D version right now
    def perimeter(self):
        vx = self.verticesAsTuples()
        vx.append(vx[0])
        d = 0
        for i in range(0, len(vx)-1):
            x1,y1,z1,t1 = vx[i]
            x2,y2,z2,t2 = vx[i+1]
            d += math.sqrt( math.pow(x2-x1,2.0) + math.pow(y2-y1,2.0) )
        return d

    # only does 2D version right now
    # area is flawed if the edges are intersecting implement better algorithm based on triangles
    def area(self):
        vx = self.verticesAsTuples()
        vx.append(vx[0])
        d = 0
        for i in range(0, len(vx)-1):
            x1,y1,z1,t1 = vx[i]
            x2,y2,z2,t2 = vx[i+1]
            d += x1*y2 - y1*x2
        return 0.5 * math.fabs(d)

class BQCircle (BQGObject):
    '''circle gobject resource'''
    xmltag = "circle"
    def perimeter(self):
        vx = self.verticesAsTuples()
        x1,y1,z1,t1 = vx[0]
        x2,y2,z2,t2 = vx[1]
        return 2.0 * math.pi * max(math.fabs(x1-x2), math.fabs(y1-y2))

    def area(self):
        vx = self.verticesAsTuples()
        x1,y1,z1,t1 = vx[0]
        x2,y2,z2,t2 = vx[1]
        return math.pi * pow( max(math.fabs(x1-x2), math.fabs(y1-y2)), 2.0)

class BQEllipse (BQGObject):
    '''ellipse gobject resource'''
    xmltag = "ellipse"
    def perimeter(self):
        vx = self.verticesAsTuples()
        x1,y1,z1,t1 = vx[0]
        x2,y2,z2,t2 = vx[1]
        x3,y3,z3,t3 = vx[2]
        a = max(math.fabs(x1-x2), math.fabs(y1-y2))
        b = max(math.fabs(x1-x3), math.fabs(y1-y3))
        return math.pi * ( 3.0*(a+b) - math.sqrt( 10.0*a*b + 3.0*(a*a + b*b)) )

    def area(self):
        vx = self.verticesAsTuples()
        x1,y1,z1,t1 = vx[0]
        x2,y2,z2,t2 = vx[1]
        x3,y3,z3,t3 = vx[2]
        a = max(math.fabs(x1-x2), math.fabs(y1-y2))
        b = max(math.fabs(x1-x3), math.fabs(y1-y3))
        return math.pi * a * b

class BQRectangle (BQGObject):
    '''rectangle gobject resource'''
    xmltag = "rectangle"
    def perimeter(self):
        vx = self.verticesAsTuples()
        x1,y1,z1,t1 = vx[0]
        x2,y2,z2,t2 = vx[1]
        return math.fabs(x1-x2)*2.0 + math.fabs(y1-y2)*2.0

    def area(self):
        vx = self.verticesAsTuples()
        x1,y1,z1,t1 = vx[0]
        x2,y2,z2,t2 = vx[1]
        return math.fabs(x1-x2) * math.fabs(y1-y2)

class BQSquare (BQRectangle):
    '''square gobject resource'''
    xmltag = "square"
    pass

################################################################################
# Factory
################################################################################

class BQFactory (object):
    '''Factory for Bisque resources'''
    resources = dict([ (x[1].xmltag, x[1]) for x in inspect.getmembers(sys.modules[__name__]) if inspect.isclass(x[1]) and hasattr(x[1], 'xmltag') ])

    def __init__(self):
        pass

    @classmethod
    def make(cls, element):
        c = cls.resources[element.tag]
        if (element.tag == 'gobject'
            and element.get('type') in gobject_primitives):
            c = cls.resources[element.attrib['type']]
        return c(element)
