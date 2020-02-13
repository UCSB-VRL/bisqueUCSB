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
##        software must display the following acknowledgment: This product   ##
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
light weight representation for gobjects used throughout the service
"""

__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys
from lxml import etree
import logging
import numpy as np
import math
import logging

log = logging.getLogger("bq.connoisseur.gobjects")


primitive_xpath = 'point|polygon|polyline|label|circle|ellipse|rectangle|square|line'
primitives = primitive_xpath.split('|')


def append_row(m, r):
    vx = np.empty((m.shape[0]+1,m.shape[1]))
    vx[:-1,:] = m
    vx[-1,:] = r
    return vx

################################################################################
# Gobjects - light weight representation only
# they contain 3 fields:
#     primitive: a string of a valid primitive: point, polygon, ...
#     type: a string with a user given annotation type, like: cell
#     vertices: a 5-D np array containing vertices as XYZTC
################################################################################

class gobject(object):
    """ light weight gobject representation
    """
    primitive = 'gobject'

    def __init__(self, idx=None, type=None, vertices=None):
        self.type = type
        self.idx = idx
        self.vertices = vertices or np.array([[]], np.float)

    def __str__(self):
        return '{0}({1}, {2}, {3})'.format(self.primitive, self.type, self.idx, self.vertices)

    def centroid(self):
        return np.array([np.nan,np.nan,np.nan,np.nan,np.nan], np.float)

    def bbox(self):
        return np.array([[np.nan,np.nan,np.nan,np.nan,np.nan],[np.nan,np.nan,np.nan,np.nan,np.nan]], np.float)

    def length(self, res=None): # length of major axis
        return np.nan

    def perimeter(self, res=None): # length of convex hull
        return np.nan

    def area(self, res=None): # area of the object
        return np.nan

class point(gobject):
    primitive = 'point'

    def __init__(self, idx=None, type=None, vertices=None, x=None, y=None):
        self.type = type
        self.idx = idx
        self.vertices = vertices if vertices is not None else np.array([[]], np.float)
        if x is not None and y is not None:
            self.vertices = np.array([[x,y,np.nan,np.nan,np.nan]], np.float)

    def centroid(self):
        return self.vertices[0]

    def bbox(self):
        return np.array([self.vertices[0],self.vertices[0]], np.float)

class label(point):
    primitive = 'label'

class polygon(gobject):
    primitive = 'polygon'

    def __init__(self, idx=None, type=None, vertices=None):
        self.type = type
        self.idx = idx
        self.vertices = vertices if vertices is not None else np.array([[]], np.float)

    def centroid(self):
        return np.average(self.vertices, 0)

    def bbox(self):
        return np.array([np.min(self.vertices, 0), np.max(self.vertices, 0)], np.float)

    def perimeter(self, res=None):
        ''' only does 2D version right now
            res = np.array([0.1,0.5,np.nan,np.nan,np.nan], np.float)
        '''
        vx = append_row(self.vertices, self.vertices[0])
        if res is not None:
            vx = vx * res
        d = 0
        for i in range(0, len(vx)-1):
            x1,y1,z1,t1,c1 = vx[i]
            x2,y2,z2,t2,c2 = vx[i+1]
            d += math.sqrt( math.pow(x2-x1,2.0) + math.pow(y2-y1,2.0) )
        return d

    def area(self, res=None):
        ''' only does 2D version right now
            area is flawed if the edges are intersecting, implement better algorithm based on triangles
        '''
        #print 'Area vertices: %s, %s'%(str(self.vertices.shape), str(self.vertices))
        vx = append_row(self.vertices, self.vertices[0])
        #print 'Area vertices: %s, %s'%(str(vx.shape), str(vx))
        if res is not None:
            vx = vx * res

        d = 0
        for i in range(0, len(vx)-1):
            x1,y1,z1,t1,c1 = vx[i]
            x2,y2,z2,t2,c2 = vx[i+1]
            d += x1*y2 - y1*x2
        return 0.5 * math.fabs(d)

class polyline(polygon):
    primitive = 'polyline'

    def length(self, res=None):
        ''' only does 2D version right now
            res = np.array([0.1,0.5,np.nan,np.nan,np.nan], np.float)
        '''
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        d = 0
        for i in range(0, len(vx)-1):
            x1,y1,z1,t1,c1 = vx[i]
            x2,y2,z2,t2,c2 = vx[i+1]
            d += math.sqrt( math.pow(x2-x1,2.0) + math.pow(y2-y1,2.0) )
        return d

    def perimeter(self, res=None):
        return self.length(res=res)

    def area(self, res=None):
        return np.nan

class line(polyline):
    primitive = 'line'

class circle(polygon):
    primitive = 'circle'

    def length(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        return math.sqrt( math.pow(x2-x1,2.0) + math.pow(y2-y1,2.0) )

    def perimeter(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        return 2.0 * math.pi * max(math.fabs(x1-x2), math.fabs(y1-y2))

    def area(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        return math.pi * pow( max(math.fabs(x1-x2), math.fabs(y1-y2)), 2.0)

class ellipse(circle):
    primitive = 'ellipse'

    def length(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        x3,y3,z3,t3,c3 = vx[2]
        a = max(math.fabs(x1-x2), math.fabs(y1-y2))
        b = max(math.fabs(x1-x3), math.fabs(y1-y3))
        return max(a, b)*2.0

    def perimeter(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        x3,y3,z3,t3,c3 = vx[2]
        a = max(math.fabs(x1-x2), math.fabs(y1-y2))
        b = max(math.fabs(x1-x3), math.fabs(y1-y3))
        return math.pi * ( 3.0*(a+b) - math.sqrt( 10.0*a*b + 3.0*(a*a + b*b)) )

    def area(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        x3,y3,z3,t3,c3 = vx[2]
        a = max(math.fabs(x1-x2), math.fabs(y1-y2))
        b = max(math.fabs(x1-x3), math.fabs(y1-y3))
        return math.pi * a * b

class rectangle(polygon):
    primitive = 'rectangle'

    def length(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        return math.sqrt( math.pow(x2-x1,2.0) + math.pow(y2-y1,2.0) )

    def perimeter(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        return math.fabs(x1-x2)*2.0 + math.fabs(y1-y2)*2.0

    def area(self, res=None):
        vx = self.vertices.copy()
        if res is not None:
            vx = vx * res
        x1,y1,z1,t1,c1 = vx[0]
        x2,y2,z2,t2,c2 = vx[1]
        return math.fabs(x1-x2) * math.fabs(y1-y2)

class square(rectangle):
    primitive = 'square'


################################################################################
# factory
################################################################################

class factory(object):
    ''' create gobjects from etree node '''

    @classmethod
    def make(cls, node):
        tp = node.get('type')
        #n = node[0]
        #if n.tag not in primitives:
        try:
            n = node.xpath(primitive_xpath)[0]
        except Exception:
            #log.debug('Parent node: %s', etree.tostring(node))
            #log.debug('Primitive node: %s', str(n))
            log.exception('Problem finding primitive node for gobject')
            return None

        vv = [[i.get('x',np.nan), i.get('y',np.nan), i.get('z',np.nan), i.get('t',np.nan), i.get('c',np.nan)] for i in n.xpath('vertex')]
        vertices = np.array(vv, np.float)
        #print 'Factory vertices: %s, %s'%(str(vertices.shape), str(vertices))

        path = node.get('uri').split('/data_service/', 1)[1].split('/')
        idx = '%s-%s'%(path[0],path[-1])

        try:
            return globals()[n.tag](idx=idx, type=tp, vertices=vertices)
        except AttributeError:
            #log.debug('Parent node: %s', etree.tostring(node))
            log.debug('Could not make gobject for empty node')
            return None
        except KeyError:
            #log.debug('Parent node: %s', etree.tostring(node))
            log.debug('Could not make gobject for unknown primitive: %s, type: %s, idx: %s, vertices: %s', n.tag, tp, idx, str(vertices))
            return None
        except Exception:
            #log.debug('Parent node: %s', etree.tostring(node))
            log.exception('Could not make gobject for primitive: %s, type: %s, idx: %s, vertices: %s', n.tag, tp, idx, str(vertices))
            return None
        return None
