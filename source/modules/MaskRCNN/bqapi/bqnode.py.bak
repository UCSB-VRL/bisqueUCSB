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

__module__    = "bqnode.py"
__author__    = "Dmitry Fedorov and Kris Kvilekval"
__version__   = "0.1"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys
import math
import inspect
import logging
from urllib import quote
from lxml import etree

log = logging.getLogger('bqapi.bqnode')

__all__ = [ 'BQFactory', 'BQNode', 'BQImage', 'BQResource', 'BQValue', 'BQTag', 'BQVertex', 'BQGObject',
            "BQDataset", "BQUser", "BQMex",
            'gobject_primitives',
            'BQPoint', 'BQLabel', 'BQPolyline', 'BQPolygon', 'BQCircle', 'BQEllipse', 'BQRectangle', 'BQSquare']

gobject_primitives = set(['point', 'label', 'polyline', 'polygon', 'circle', 'ellipse', 'rectangle', 'square'])


################################################################################
# Base class for bisque resources
################################################################################

class BQNode (etree.ElementBase):
    '''Base class for parsing Bisque XML'''
    TAG = xmltag = 'NODE'
    xmlfields = []
    xmlkids = []


    def __getattr__(self, name):
        if name in self.xmlfields:
            return self.get (name)
        ###return etree.ElementBase.__getattr__(self, name)
        #super(etree.ElementBase, self).__getattr__(name)

    def __setattr__(self, name, val):
        if name in self.xmlfields:
            return self.set (name, val)
        print "SETTER"
        object.__setattr__(self, name, val)

    def initialize(self):
        'used for class post parsing initialization'
        pass

    def initializeXml(self, xmlnode):
        for x in self.xmlfields:
            setattr(self, x, xmlnode.get (x, None))

    def set_parent(self, parent):
        pass

    def __repr__(self):
        return '(%s#%s)' % (self.TAG, len(self))

    def __str__(self):
        return etree.tostring(self)
    #    return '(%s:%s:%s)'%(self.TAG,','.join (['%s=%s' % (f, getattr(self,f,'')) for f in self.attrib]), [ str (q) for q in self ] )

    def toTuple (self):
        return tuple( [ x for x in self.attr ] )




################################################################################
# Base class for bisque resources
################################################################################

class BQResource (BQNode):
    '''Base class for Bisque resources'''
    TAG = xmltag = 'resource'
    xmlfields = ['name', 'values', 'type', 'uri', 'ts', 'resource_uniq']
    xmlkids = ['kids', 'tags', 'gobjects']

    #def __repr__(self):
    #    return '(%s:%s)'%(self.xmltag, self.uri)


    def get_tags(self):
        return [ x for x in self.iter ('tag') ]
    tags = property(get_tags)
    def get_gobjects(self):
        return [ x for x in self.iter ('gobject') ]
    gobjects = property(get_gobjects)
    def get_kids(self):
        return [ x for x in self.iter () ]
    kids = property(get_kids)

    #def __init__(self):
    #    self.tags = []
    #    self.gobjects = []
    #    self.kids = []

    def toDict (self):
        objs = {}
        objs.update ( [ (f.name, f) for f in self.tags if f.name ] )
        objs.update ( [ (f.name, f) for f in self.gobjects if f.name ] )
        return objs

    def set_parent(self, parent):
        parent.kids.append(self)

    def add_tag(self, name=None, value=None, type=None, tag=None):
        if tag is None:
            args = dict ( name=name, value=value, type=type)
            tag = BQTag( **dict ((k, v)  for k,v in args.items() if v is not None) )
        self.append(tag)
        return tag
    addTag = add_tag

    def add_gob(self, name=None, value=None, type=None, gob=None):
        if gob is None:
            args = dict ( name=name, value=value, type=type)
            gob = BQGObject( **dict ((k, v)  for k,v in args.items() if v is not None) )
        self.append(gob)
        return gob
    addGObject = add_gob


    # def findall (pathexpress)
    #     Implemented by
    # def tag(self, name):
    #     results = []
    #     for tg in self.tags:
    #         if tg.name == name:
    #             results.append(tg)
    #     if len(results) == 0:
    #         return None
    #     elif len(results) == 1:
    #         return results[0]
    #     else:
    #         return results

    # def gob(self, name):
    #     results = []
    #     for tg in self.gobjects:
    #         if tg.name == name:
    #             results.append(tg)
    #     if len(results) == 0:
    #         return None
    #     elif len(results) == 1:
    #         return results[0]
    #     else:
    #         return results


    def set_parent(self, parent):
        parent.tags.append(self)

    def get_values(self):
        if 'value' in self.attrib:
            return self.attrib['value']
        result = [str(v.text) for v in self.iter ('value')]
        return result

    def set_values(self, values):
        """Assign a list of values
           Maybe single value list or a list of (value, type) tuples where type is object, integer, float, number, string
        """
        if not isinstance(values, list):
            self.set('value', str(values))
        else:
            if 'value' in self.attrib:
                del self.attrib['value']
            for child in self:
                self.remove (child)
            for v in values:
                if isinstance (v, tuple):
                    val = etree.SubElement (self, 'value', type=v[1])
                    v = v[0]
                else:
                    val = etree.SubElement (self, 'value')
                val.text = str(v)

    value = property(get_values, set_values)

    def toetree(self, parent, baseuri):
        xmlkids = list(self.xmlkids)
        if len(self.values)<=1:
            n = create_element(self, parent, baseuri)
        else:
            n = create_element(self, parent, baseuri)
            del n.attrib['value']
            xmlkids.append('values')
        for kid_name in xmlkids:
            for x in getattr(self, kid_name, None):
                toxmlnode (x, n, baseuri)
        return n




################################################################################
# Image
################################################################################

class BQImage(BQResource):
    TAG = xmltag = "image"
    xmlfields = ['name', 'uri', 'ts' , "value", 'resource_uniq' ] #  "x", "y","z", "t", "ch"  ]
    xmlkids = ['tags', 'gobjects']

    #def __init__(self):
    #    super(BQImage, self).__init__()
    #    self._geometry = None

    def geometry(self):
        'return x,y,z,t,ch of image'
        if self._geometry is None:
            info = self.pixels().meta().fetch()
            info = etree.XML(info)
            geom = []
            for n in 'xyztc':
                tn = info.xpath('//tag[@name="image_num_%s"]' % n)
                geom.append(tn[0].get('value'))
            self._geometry = tuple(map(int, geom))
        return self._geometry

    def pixels(self):
        return BQImagePixels(self)

class BQImagePixels(object):
    """manage requests to the image pixels"""
    def __init__(self, image):
        self.image = image
        self.ops = []

    def _construct_url(self):
        """build the final url based on the operation
        """
        image_service = self.image.session.service('image_service')
        return image_service.construct (path = '%s?%s'%(self.image.resource_uniq,
                                                        '&'.join ( "%s=%s" % tp for tp in self.ops )))

    def fetch(self, path=None):
        """resolve the current and fetch the pixel
        """
        url = self._construct_url()
        session = self.image.session
        return session.c.fetch (url, path=path)

    def command(self, operation, arguments=''):
        self.ops.append((operation, arguments))
        return self

    def slice(self, x='', y='',z='',t=''):
        """Slice the current image"""
        return self.command('slice', '%s,%s,%s,%s' % (x,y,z,t))

    def format(self, fmt):
        return self.command('format', fmt)

    def resize(self, w='',h='', interpolation='NN'):
        """ interpoaltion may be,[ NN|,BL|,BC][,AR]
        """
        return self.command('resize', '%s,%s,%s' % (w,h,interpolation))

    def localpath(self):
        return self.command('localpath')

    def meta(self):
        return self.command('meta')

    def info(self):
        return self.command('info')

    def asarray(self):
        try:
            import tifffile
        except ImportError:
            log.error ("Please install Tifffile (Optional)")
            return None
        # Force format to be tiff by removing any format and append format tiff
        self.ops = [ tp for tp in self.ops if tp[0] != 'format' ]
        self.format ('tiff')
        url = self._construct_url()
        image_service = self.image.session.service ('image_service')
        with  image_service.fetch (url, stream=True) as response:
            #response.raw.decode_content = True
            return tifffile.imread (io.BytesIO (response.content))



################################################################################
# Tag
################################################################################

class BQValue (BQNode):
    '''tag value'''
    TAG = xmltag = "value"
    xmlfields = ['value', 'type', 'index']

    #def __init__(self,  value=None, type=None, index=None):
    #    self.value = value
    #    self.type = type
    #    self.index = index

    def set_parent(self, parent):
        if self.index is not None:
            parent.values.extend([None for x in range((self.index+1)-len(parent.values))])
            parent.values[self.index] = self
        else:
            parent.values.append(self)

    def initializeXml(self, xmlnode):
        super(BQValue, self).initializeXml(xmlnode)
        try:
            self.index = int(self.index)
        except Exception:
            self.index = None
        self.value = xmlnode.text

    def toetree(self, parent, baseuri):
        n = etree.SubElement(parent, 'value', )
        if self.type is not None: n.set('type', str(self.type))
        if self.index is not None: n.set('index', str(self.index))
        if self.value is not None: n.text = str(self.value)
        return n

    #def __call__(self):
    #    if len(self.values<=0): return ''
    #    elif len(self.values==1): return str(self.values[0])
    #    def str_join(x,y): return '%s,%s'%(x,y)
    #    return reduce(str_join, self.values)

class BQTag (BQResource):
    '''tag resource'''
    TAG = xmltag = "tag"
    xmlfields = ['name', 'type', 'uri', 'ts', 'value']
    xmlkids = ['tags', 'gobjects',  ] # handle values  specially

    #def __init__(self, name='', value=None, type=None):
    #    super(BQTag, self).__init__()
    #    self.name = name
    #    self.values = (value and [BQValue(value)]) or []
    #    if type is not None:
    #        self.type=type




################################################################################
# GObject
################################################################################

class BQVertex (BQNode):
    '''gobject vertex'''
    type = 'vertex'
    TAG = xmltag = "vertex"
    xmlfields = ['x', 'y', 'z', 't', 'c', 'index']

    #def __init__(self, **kw):
    #    self.fromObj(**kw)

    def __repr__(self):
        return 'vertex(x:%s,y:%s,z:%s,t:%s)'%(self.x, self.y, self.z, self.t)

    def set_parent(self, parent):
        parent.vertices.append(self)

    def toTuple(self):
        return (self.x, self.y, self.z, self.t)

    def fromTuple(self, v):
        x,y,z,t = v
        self.x=x; self.y=y; self.z=z; self.t=t

    def fromObj(self, **kw):
        for k,v in kw.items():
            if k in self.xmlfields:
                setattr(self,k,v)

class BQGObject(BQResource):
    '''Gobject resource: A grpahical annotation'''
    type = 'gobject'
    TAG = xmltag = "gobject"
    xmlfields = ['name', 'type', 'uri']
    xmlkids = ['tags', 'gobjects', 'vertices']

    #def __init__(self, name=None, type=None):
    #    super(BQGObject, self).__init__()
    #    self.vertices = []
    #    self.name=name
    #    self.type= type or self.xmltag

    def __str__(self):
        return '(type: %s, name: %s, %s)'%(self.type, self.name, self.vertices)

    def set_parent(self, parent):
        parent.gobjects.append(self)

    def verticesAsTuples(self):
        return [v.toTuple() for v in self.vertices ]

    def perimeter(self):
        return -1

    def area(self):
        return -1


class BQPoint (BQGObject):
    '''point gobject resource'''
    TAG = xmltag = "point"

class BQLabel (BQGObject):
    '''label gobject resource'''
    TAG = xmltag = "label"

class BQPolyline (BQGObject):
    '''polyline gobject resource'''
    TAG = xmltag = "polyline"
    def perimeter(self):
        vx = self.verticesAsTuples()
        d = 0
        for i in range(0, len(vx)-1):
            x1,y1,z1,t1 = vx[i]
            x2,y2,z2,t2 = vx[i+1]
            d += math.sqrt( math.pow(x2-x1,2.0) + math.pow(y2-y1,2.0) )
        return d


# only does 2D version right now, polygon area is flawed if the edges are intersecting
# implement better algorithm based on triangles
class BQPolygon (BQGObject):
    '''Polygon gobject resource'''
    TAG = xmltag = "polygon"
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
    TAG = xmltag = "circle"
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
    TAG = xmltag = "ellipse"
    type = 'ellipse'

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
    TAG = xmltag = "rectangle"
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
    TAG = xmltag = "square"


################################################################################
# Advanced Objects
################################################################################
class BQDataset(BQResource):
    TAG = xmltag = "dataset"
    #xmlfields = ['name', 'uri', 'ts']
    #xmlkids = ['kids', 'tags', 'gobjects']






class BQUser(BQResource):
    TAG = xmltag = "user"
    #xmlfields = ['name', 'uri', 'ts']
    #xmlkids = ['tags', 'gobjects']

class BQMex(BQResource):
    TAG = xmltag = "mex"
    #xmlfields = ['module', 'uri', 'ts', 'value']
    #xmlkids = ['tags', 'gobjects']



################################################################################
# Factory
################################################################################

class BQFactory (etree.PythonElementClassLookup):
    '''Factory for Bisque resources'''
    resources = dict([ (x[1].xmltag, x[1]) for x in inspect.getmembers(sys.modules[__name__]) if inspect.isclass(x[1]) and hasattr(x[1], 'xmltag') ])


    def __init__(self, session):
        self.session = session
        self.parser = etree.XMLParser()
        self.parser.set_element_class_lookup(self)

    def lookup (self, document, element):
        return self.find(element.tag, element.get ('type', ''))

    @classmethod
    def find(cls, xmltag, type_attr):
        if xmltag == "gobject" and type_attr in gobject_primitives:
            xmltag = type_attr
        c = cls.resources.get(xmltag, BQResource)
        return c

    @classmethod
    def make(cls, xmltag, type_attr):
        c = cls.find (xmltag, type_attr)
        return c()

    index_map = dict(vertex=('vertices',BQVertex), tag=('tags', BQTag))
    @classmethod
    def index(cls, xmltag, parent, indx):
        array, ctor = cls.index_map.get (xmltag, (None,None))
        if array:
            objarr =  getattr(parent, array)
            objarr.extend ([ ctor() for x in range(((indx+1)-len(objarr)))])
            v = objarr[indx]
            v.indx = indx;
            #log.debug ('fetching %s %s[%d]:%s' %(parent , array, indx, v))
            return v

    # Parsing
    def from_etree(self, node):
        """ Convert an etree to a python structure"""
        return node

    def from_string(self, xmlstring):
        return etree.XML(xmlstring, self.parser)

    # Generation
    @classmethod
    def to_string (self, nodes):
        return etree.tostring (nodes)

    @classmethod
    def to_etree(self, bqnode):
        """Convert BQNode  to elementTree"""
        return bqnode

    def string2etree(self, xmlstring):
        return etree.XML (xmlstring, self.parser)



################################################################################
# Generation
################################################################################

def toXml(dbo, parent=None, baseuri='', view=''):
    """Convert a BQObject to an etree object suitable for XML
    generation
    """
    node = dbo
    return node;


def create_element(dbo, parent, baseuri, **kw):
    """Create an etree element from BQ object
    """
    xtag = kw.pop('xtag', dbo.xmltag)
    if not kw:
        kw = model_fields (dbo, baseuri)
    if parent is not None:
        node =  etree.SubElement (parent, xtag, **kw)
    else:
        node =  etree.Element (xtag,  **kw)
    return node

def toxmlnode (dbo, parent, baseuri, view=None):
    if hasattr(dbo, 'toetree'):
        node = dbo.toetree(parent, baseuri)
    else:
        node = create_element (dbo, parent, baseuri)
        for kid_name in dbo.xmlkids:
            for x in getattr(dbo, kid_name, None):
                toxmlnode (x, node, baseuri, view)
    return node


def make_owner (dbo, fn, baseuri):
    return ('owner', baseuri + str(dbo.owner))

def make_uri(dbo, fn, baseuri):
    return ('uri', "%s%s" % (baseuri , str (dbo.uri)))

def get_email (dbo, fn, baseuri):
    return ('email', dbo.user.email_address)

mapping_fields = {
    'mex' : None,
    'acl' : None,
    # Auth
    'user_id' : get_email,
    'taggable_id': None,
    'permission': 'action',
    'resource': None,
    }

def model_fields(dbo, baseuri=None):
    """Extract known fields from a BQ object, while removing any known
    from C{excluded_fields}

    @rtype: dict
    @return fields to be rendered in XML
    """
    attrs = {}
    try:
        dbo_fields = dbo.xmlfields
    except AttributeError:
        # This occurs when the object is a fake DB objects
        # The dictionary is sufficient
        dbo_fields= dbo.__dict__
    for fn in dbo_fields:
        fn = mapping_fields.get(fn, fn)
        # Skip when map is None
        if fn is None:
            continue
        # Map is callable, then call
        if callable(fn):
            fn, attr_val = fn(dbo, fn, baseuri)
        else:
            attr_val = getattr(dbo, fn, None)

        # Put value in attribute dictionary
        if attr_val is not None and attr_val!='':
            if isinstance(attr_val, basestring):
               attrs[fn] = attr_val
            else:
               attrs[fn] = str(attr_val) #unicode(attr_val,'utf-8')
    return attrs
