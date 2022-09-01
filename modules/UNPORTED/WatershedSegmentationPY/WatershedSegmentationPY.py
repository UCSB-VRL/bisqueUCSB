import logging
from lxml import etree
import base64
import scipy.ndimage
from bisquik.util.bisquik2db import known_gobjects, updateDB as parseXml
from  bisquik.util.http import request, post_files
from bisquik import identity
import base64

import cStringIO # *much* faster than StringIO
import StringIO # *much* faster than StringIO
#from struct import pack
from numpy import *
from PIL import Image, ImageOps
from scipy.ndimage.filters import sobel
from scipy.ndimage.measurements import label, watershed_ift
from scipy.ndimage.morphology import binary_erosion
from scipy import *

ch = logging.StreamHandler()
log = logging.getLogger("test")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(" %(message)s");
ch.setFormatter(formatter)
log.addHandler(ch)

class BQObject(object):
    def __init__(self, **kw):
        self.gobjects = []
        self.tags = []
        self.kids = []

class BQImage(BQObject):
    pass
class BQGObject(BQObject):
    def __init__(self):
        self.vertices = []
        
class BQTag(BQObject):
    pass
class BQVertex(object):
    pass
class BQValue(object):
    pass

nodemap = { 'resource' : BQObject,
    'image' : BQImage,
    'tag': BQTag,
}
    
    
class BQNodeFactory(object):
    @classmethod 
    def load_uri (cls, uri):
        return None
    @classmethod
    def new(cls, xmlnode, parent, uri=None, **kw):
        xmlname = xmlnode.tag
        if xmlname in known_gobjects:
            node = BQGObject()
            node.tag_type =  unicode(xmlname)
            if parent:
                parent.gobjects.append(node)
        elif xmlname == "tag":
            node = BQTag()
            #node.tag_type = "string"
            if parent:
                parent.tags.append(node)
        elif xmlname == "vertex":
            node = BQVertex()
            parent.vertices.append (node)
            node.indx = len(parent.vertices)-1 # Default value (maybe overridden)
        elif xmlname == "value":
            node = BQValue()
            parent.values.append(node)
            node.indx = len(parent.values)-1   # Default value (maybe overridden)
        elif xmlname== "request" or xmlname=="response":
            if parent:
                node = parent
            else:
                node = BQObject(xmlname)
        elif xmlname=="resource":
            xmlname = xmlnode.attrib['type']
            cls = nodemap.get (xmlname, BQObject) 
            log.debug ('CREATING %s -> %s' % (xmlname,  cls))
            node =  cls() #BQObject(xmlname)
            if parent:
                parent.kids.append(node)
        else:
            cls = nodemap.get (xmlname, BQObject) 
            log.debug ('CREATING %s -> %s' % (xmlname,  cls))
            node = cls()
            if parent:
                parent.kids.append(node)
        if uri:
            node.uri = uri
        return node

    index_map = dict(vertex=('vertices',BQVertex), tag=('tags', BQTag))
    @classmethod
    def index(cls, node, parent, indx):
        xmlname = node.tag
        #return cls.new(xmlname, parent)
        array, ctor = cls.index_map.get (xmlname, (None,None))
        if array:
            objarr =  getattr(parent, array)
            objarr.extend ([ ctor() for x in range(((indx+1)-len(objarr)))])
            v = objarr[indx]
            v.indx = indx;
            log.debug ('fetching %s %s[%d]' %(parent , array, indx)) 
            return v




class WatershedSegmentationPY:
    """Example Python module

    Simple Image Processing
    """
    def __init__(self):
        pass
        
    def loadImage(self, url):
        resp, content = request(url)
        log.debug ('WatershedSegmentationPY - response:  ' +  str(content)  + '||||||||||' +url)
        response = etree.XML(content)
        image = parseXml(root = response, factory = BQNodeFactory)
        log.debug("GOT " + str(image.uri))
        return image

    def processImage(self):        
        log.debug("IMAGE: " +  self.image.z + ',' + self.image.t + ',' + self.image.ch)
        print 'In process image'
        if int(self.image.z) == 1  and  int(self.image.t) == 1 and (int(self.image.ch) ==1 or int(self.image.ch) == 3):
            # read image from Bisque system
            resp, content = request(self.image.src + '?format=tiff', "GET", userpass = self.userpass )
            # convert stream into Image
            im = cStringIO.StringIO(content)            
            img = Image.open(im)
            log.debug("IMAGE: " +  str(img.format) + ',' + str(img.size) + ',' + str(img.mode))
            ''' IMAGE PROCESSING '''
            # convert color image into grayscale image
            grayimg = ImageOps.grayscale(img)
            # convert Image into numpy array
            in_im = asarray(grayimg)
            # normalize image
            norm_im = self.normalizeImage(in_im)
            # set the threshold value
            thNorm = double((double(self.thValue)/100.0))
            # threshold image with thNorm value
            th_im = norm_im < thNorm;
            # label image with 8conn
            structure = [[1,1,1], [1,1,1], [1,1,1]]
            th_im = binary_erosion(~th_im,structure)            
            label_tuple = label(th_im,structure) #(data, dtype, number of labels)
            label_im = label_tuple[0]-1
            # wathershed
            wh_im = watershed_ift(in_im, label_im)
            # convert numpy array into Image
            img_out = Image.fromarray(wh_im.astype('uint8'))
            ''' IMAGE PROCESSING '''
            # convert Image into stream
            buffer = StringIO.StringIO()
            img_out.save(buffer, 'TIFF')
            # upload image into Bisque system
            buffer.seek(0)
            buffer.name = 'file.tif'
            fields = { 'file' :  buffer }
            resp, content =  post_files (self.client_server + '/bisquik/upload_images', fields=fields, userpass = self.userpass,)
            log.debug("RESP: " +  str(content))
            self.image_out_url = str(content)

    def normalizeImage(self, im):
        im = array(im, copy=1, dtype=double)
        im =(im - min(im.flat))/(max(im.flat) - min(im.flat)) 
        return im

    def postTag(self,parent,tag):
        req = etree.Element ('request')
        etree.SubElement (req, 'tag',  name=str(tag.name), value=str(tag.value), type='string')
        log.debug("REQ: " + etree.tostring(req))
        resp, content = request(parent.uri, "POST", body = etree.tostring(req), headers={'content-type':'text/xml' }, userpass = self.userpass )
        log.debug("RESP: " + str(content))
        return resp

#   def main(self, client_server='http://bodzio.ece.ucsb.edu:8080', image_url='http://bodzio.ece.ucsb.edu:8080/ds/images/17131', ThresholdValue = 50, user='admin', password='admin'):
    def main(self, client_server, image_url, ThresholdValue, user=None, password=None):
     	
     	print'Running in main'
        self.userpass  = ( user, password )
        self.client_server = client_server
        self.image_url = image_url
        self.thValue = ThresholdValue
        

        self.image = self.loadImage(self.image_url)
        buffer = self.processImage()

        self.tag = BQTag
        self.tag.name = "Segmented Image"
        self.tag.value = self.image_out_url 
        resp = self.postTag(self.image, self.tag)

