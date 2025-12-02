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

import os
import sys
import math
import io
import inspect
import logging
import tempfile
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
from .xmldict import xml2nv


log = logging.getLogger('bqapi.class')

__all__ = [ 'BQFactory', 'BQNode', 'BQImage', 'BQResource', 'BQValue', 'BQTag', 'BQVertex', 'BQGObject',
            "BQDataset", "BQUser", "BQMex",
            'gobject_primitives',
            'BQPoint', 'BQLabel', 'BQPolyline', 'BQPolygon', 'BQCircle', 'BQEllipse', 'BQRectangle', 'BQSquare',] # 'toXml', 'fromXml' ]

gobject_primitives = set(['point', 'label', 'polyline', 'polygon', 'circle', 'ellipse', 'rectangle', 'square', 'line'])


################################################################################
# Base class for bisque resources
################################################################################

class BQNode (object):
    '''Base class for parsing Bisque XML'''
    xmltag = ''
    xmlfields = []
    xmlkids = []

    def __init__(self, *args, **kw):
        for k,v in zip(self.xmlfields, args):
            setattr(self, k, v)
        for k in self.xmlfields:
            if k in self.__dict__:
                continue
            setattr(self, k, kw.get(k, None))

    def initialize(self):
        'used for class post parsing initialization'
        pass

    def initializeXml(self, xmlnode):
        for x in self.xmlfields:
            setattr(self, x, xmlnode.get (x, None))

    def set_parent(self, parent):
        pass

    def __repr__(self):
        return '(%s:%s)' % (self.xmltag, id(self) )

    def __str__(self):
        return '(%s:%s)'%(self.xmltag,','.join (['%s=%s' % (f, getattr(self,f,'')) for f in self.xmlfields]))

    def toTuple (self):
        return tuple( [ x for x in self.xmlfields ] )

################################################################################
# Value
################################################################################

class BQValue (BQNode):
    '''tag value'''
    xmltag = "value"
    xmlfields = ['value', 'type', 'index']

    #def __init__(self,  **kw):
    #    super(BQValue, self).__init__(**kw)

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

################################################################################
# Base class for bisque resources
################################################################################

class BQResource (BQNode):
    '''Base class for Bisque resources'''
    xmltag = 'resource'
    xmlfields = ['name', 'type', 'uri', 'ts', 'resource_uniq']
    xmlkids = ['kids', 'tags', 'gobjects',] #  'values'] handled differently

    def __repr__(self):
        return '(%s:%s)'%(self.xmltag, self.uri) #pylint: disable=no-member

    def __init__(self, *args, **kw):
        self.tags = []
        self.gobjects = []
        self.kids = []
        self.values = []
        self.parent = None
        super(BQResource, self).__init__(*args, **kw)

    def toDict (self):
        objs = {}
        objs.update ( [ (f.name, f) for f in self.tags if f.name ] )
        objs.update ( [ (f.name, f) for f in self.gobjects if f.name ] )
        return objs

    def set_parent(self, parent):
        self.parent = parent
        parent.kids.append(self)

    def addTag(self, name=None, value=None, type = None, tag=None):
        if tag is None:
            tag = BQTag(name=name, value=value, type = type)
        tag.set_parent (self)
        return tag
    add_tag = addTag

    def addGObject(self, name=None, value=None, type = None, gob=None):
        if gob is None:
            gob = BQGObject(name=name, value=value, type = type)
        gob.set_parent(self)
    add_gob = addGObject


    def findall (self, name, limit=None):
        "find all name that match, options limit search tag, gobject or a kid"
        limit = limit or  ['tag', 'gobject', 'kid']
        results =[]
        if 'tag' in limit:
            for tg in self.tags:
                if tg.name == name:
                    results.append( tg )
        if 'gobject' in limit:
            for tg in self.gobjects:
                if tg.name == name:
                    results.append(  tg )
        if 'kid' in limit:
            for tg in self.kids:
                if tg.name == name:
                    results.append ( tg )
        return results

    def find(self, name, limit=None):
        "Find first element and return options limit search tag, gobject or a kid"
        limit = limit or  ['tag', 'gobject', 'kid']
        if 'tag' in limit:
            for tg in self.tags:
                if tg.name == name:
                    return tg
        if 'gobject' in limit:
            for tg in self.gobjects:
                if tg.name == name:
                    return tg
        if 'kid' in limit:
            for tg in self.kids:
                if tg.name == name:
                    return tg


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

    def get_value(self):
        if len(self.values)==0:
            return None
        if len(self.values)==1:
            return self.values[0].value
        return [ x.value for x in self.values ]

    def set_value(self, values):
        if not isinstance(values, list):
            values = [ values ]
        self.values = [ BQValue(*v) if isinstance(v, tuple) else BQValue(v) for v in values ]


    value = property(get_value, set_value)

    def toetree(self, parent, baseuri):
        xmlkids = list(self.xmlkids)
        if len(self.values)<=1:
            n = create_element(self, parent, baseuri)
        else:
            n = create_element(self, parent, baseuri)
            if 'value' in n.attrib:
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
    xmltag = "image"
    xmlfields = ['name', 'value', 'type', 'uri', 'ts', 'resource_uniq' ] #  "x", "y","z", "t", "ch"  ]
    xmlkids = ['tags', 'gobjects']

    def __init__(self, *args,  **kw):
        super(BQImage, self).__init__(*args, **kw)
        self._geometry = None
        self._meta = None
        self._info = {}

    # returns etree XML with image metadata
    def meta(self):
        'return image meta as xml'
        if self._meta is None:
            info = self.pixels().meta().fetch()
            self._meta = etree.XML(info)
            self._info = xml2nv(self._meta)
        return self._meta

    # returns dict with image metadata name:value
    def info(self):
        'return image meta as dict'
        if self._meta is None:
            self.meta()
        return self._info

    def geometry(self):
        'return x,y,z,t,ch of image'
        if self._geometry is None:
            info = self.meta()
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
        #return session.service_url('image_service',
        #                           % (self.image.resource_uniq, '&'.join(self.ops)))

    def fetch(self, path=None, stream=False):
        """resolve the current and fetch the pixel
        """
        url = self._construct_url()
        image_service = self.image.session.service ('image_service')
        if path is not None:
            stream = True

        response = image_service.fetch (url, stream=stream)
        if path is not None:
            with open (path, 'wb') as fb:
                for block in response.iter_content(chunk_size = 16 * 1024 * 1024): #16MB
                    fb.write(block)
                response.close()
        else:
            return response.content

    def command(self, operation, arguments=''):
        self.ops.append((operation, arguments))
        return self

    def slice(self, x='', y='',z='',t=''):
        """Slice the current image"""
        return self.command('slice', '%s,%s,%s,%s' % (x,y,z,t))

    def format(self, fmt):
        return self.command('format', fmt)

    def resize(self, w='',h='', interpolation=''):
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

    def savearray (self, fname, imdata=None, imshape=None, dtype=None, **kwargs):
        try:
            import tifffile
        except ImportError:
            log.error ("Please install Tifffile (Optional)")
            return None
        import_service = self.image.session.service ('import_service')
        imfile =  tempfile.mkstemp (suffix='.tiff')
        tifffile.imsave (imfile, imdata, imshape, dtype, **kwargs)
        import_service.transfer (fname, fileobj = open (imfile, 'rb'))
        os.remove (imfile)





################################################################################
# Tag
################################################################################

class BQTag (BQResource):
    '''tag resource'''
    xmltag = "tag"
    xmlfields = ['name',  'value', 'type', 'uri', 'ts']
    xmlkids = ['tags', 'gobjects', ] # handle values  specially

    def set_parent(self, parent):
        self.parent = parent
        parent.tags.append(self)

#     def get_value(self):
#         if len(self.values)==0:
#             return None
#         if len(self.values)==1:
#             return self.values[0].value
#         return [ x.value for x in self.values ]
#     def set_value(self, values):
#         if not isinstance(values, list):
#             self.values = [ BQValue(values)]
#         else:
#             self.values = [ BQValue(v) for v in values ]
#
#     value = property(get_value, set_value)
#
#     def toetree(self, parent, baseuri):
#         xmlkids = list(self.xmlkids)
#         if len(self.values)<=1:
#             n = create_element(self, parent, baseuri)
#         else:
#             n = create_element(self, parent, baseuri)
#             del n.attrib['value']
#             xmlkids.append('values')
#         for kid_name in xmlkids:
#             for x in getattr(self, kid_name, None):
#                 toxmlnode (x, n, baseuri)
#         return n




################################################################################
# GObject
################################################################################

class BQVertex (BQNode):
    '''gobject vertex'''
    type = 'vertex'
    xmltag = "vertex"
    xmlfields = ['x', 'y', 'z', 't', 'c', 'index']

    def __init__(self, **kw):
        self.fromObj(**kw)

    def __repr__(self):
        return 'vertex(x:%s,y:%s,z:%s,t:%s)'%(self.x, self.y, self.z, self.t)

    def set_parent(self, parent):
        self.parent = parent
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
    xmltag = "gobject"
    xmlfields = ['name', 'value', 'type', 'uri']
    xmlkids = ['tags', 'gobjects', 'vertices']

    def __init__(self, *args, **kw):
        super(BQGObject, self).__init__(*args, **kw)
        self.name = None
        self.vertices = []
        self.type= self.type or self.xmltag

    def __str__(self):
        return '(type: %s, name: %s, %s)'%(self.type, self.name, self.vertices)

    def set_parent(self, parent):
        self.parent = parent
        parent.gobjects.append(self)

    def verticesAsTuples(self):
        return [v.toTuple() for v in self.vertices ]

    def perimeter(self):
        return -1

    def area(self):
        return -1


class BQPoint (BQGObject):
    '''point gobject resource'''
    xmltag = "point"

class BQLabel (BQGObject):
    '''label gobject resource'''
    xmltag = "label"

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


################################################################################
# Advanced Objects
################################################################################
class BQDataset(BQResource):
    xmltag = "dataset"
    #xmlfields = ['name', 'uri', 'ts']
    #xmlkids = ['kids', 'tags', 'gobjects']

class BQUser(BQResource):
    xmltag = "user"
    #xmlfields = ['name', 'uri', 'ts']
    #xmlkids = ['tags', 'gobjects']

class BQMex(BQResource):
    xmltag = "mex"
    #xmlfields = ['module', 'uri', 'ts', 'value']
    #xmlkids = ['tags', 'gobjects']

################################################################################
# Factory
################################################################################

class BQFactory (object):
    '''Factory for Bisque resources'''
    resources = dict([ (x[1].xmltag, x[1]) for x in inspect.getmembers(sys.modules[__name__]) if inspect.isclass(x[1]) and hasattr(x[1], 'xmltag') ])

    def __init__(self, session):
        self.session = session

    @classmethod
    def make(cls, xmltag, type_attr):
        if xmltag == "gobject" and type_attr in gobject_primitives:
            xmltag = type_attr
        c = cls.resources.get(xmltag, BQResource)
        return c()

    index_map = dict(vertex=('vertices',BQVertex), tag=('tags', BQTag))
    @classmethod
    def index(cls, xmltag, parent, indx):
        array, ctor = cls.index_map.get (xmltag, (None,None))
        if array:
            objarr =  getattr(parent, array)
            objarr.extend ([ ctor() for x in range(((indx+1)-len(objarr)))])
            v = objarr[indx]
            v.indx = indx
            #log.debug ('fetching %s %s[%d]:%s' %(parent , array, indx, v))
            return v

    ################################################################################
    # Parsing
    ################################################################################

    def from_etree (self, xmlResource, resource=None, parent=None ):
        """ Convert an etree to a python structure"""
        stack = [];
        resources = [];
        #  Initialize stack with a tuple of
        #    1. The XML node being parsed
        #    2. The current resource being filled outs
        #    3. The parent resource if any
        stack.append ( (xmlResource, resource, parent ) )
        while stack:
            node, resource, parent = stack.pop(0);
            xmltag = node.tag;
            if resource is None:
                type_ = node.get( 'type', '')
                resource = self.make(xmltag, type_)

            resource.session = self.session
            resource.initializeXml(node)
            resources.append (resource)
            if parent:
                resource.set_parent(parent)
                #resource.doc = parent.doc;
            for k in node:
                stack.append( (k, None, resource) )

        resources[0].initialize()
        resources[0].xmltree = xmlResource
        return resources[0];
    def from_string (self, xmlstring):
        et = etree.XML (xmlstring)
        return self.from_etree(et)

    # Generation

    @classmethod
    def to_etree(self, dbo, parent=None, baseuri='', view=''):
        """Convert a BQObject to an etree object suitable for XML
        generation
        """
        node = toxmlnode(dbo, parent, baseuri, view)
        return node;
    @classmethod
    def to_string (self, node):
        if isinstance (node, BQNode):
            node = self.to_etree(node)
        return etree.tostring(node)

    @classmethod
    def string2etree(self, xmlstring):
        return etree.XML (xmlstring)


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
