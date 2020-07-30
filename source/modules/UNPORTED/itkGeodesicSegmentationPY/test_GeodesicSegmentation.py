import logging
from lxml import etree
import base64
from bisquik.util.bisquik2db import known_gobjects, updateDB as parseXml
from  bisquik.util.http import request, post_files
from bisquik import identity
import base64
import sys
import cStringIO 

import itk
import GeodesicSegmentation as seg

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
            
    
class itkGeodesicSegmentationPY:
    """ITK Geodeisic Active Contours Segmentation Module
    """
    def __init__(self):
        pass
        
    def loadImage(self, url):
        resp, content = request(url, userpass = self.userpass)
        log.debug ('itkGeodesicSegmentationPY - response:  ' +  str(content)  + '||||||||||' +url)
        response = etree.XML(content)
        image = parseXml(root = response, factory = BQNodeFactory)
        log.debug("GOT " + str(image.uri))
        return image

    def processImage(self):        
        log.debug("IMAGE: " +  self.image.z + ',' + self.image.t + ',' + self.image.ch)
        print 'In process image'
        if int(self.image.z) == 1  and  int(self.image.t) == 1 and (int(self.image.ch) ==1 or int(self.image.ch) == 3):
			# read image from Bisque system
			resp, content = request(self.image.src + '?format=png', "GET", userpass = self.userpass )

			print str(resp)
			print len(content)

			tempinfile = 'ac_in.png' 
			tempoutfile = 'ac_out.png'

			f = open(tempinfile,'w')
			f.write(content)
			f.close()
			print 'Done writing the file'

			InitialDistance = 5.0

			seg.doSegment(tempinfile,tempoutfile, self.seedX, self.seedY, InitialDistance, self.Sigma, self.SigmoidAlpha, self.SigmoidBeta,self.PropagationScaling)
			print 'Segmentation done!'

			buffer = open(tempoutfile,'r')

			print ' posting the output to the server ..'
			file = [('upload', tempoutfile, buffer.read())] 
			resp, content =  post_files (self.client_server + '/bisquik/upload_raw_image', file,  [], userpass = self.userpass,)
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
   
    def main(self, client_server, image_url,user='admin',password='admin'):
		print'Running in main'
		self.userpass  = ( user, password )
		self.client_server = client_server
		self.image_url = image_url
		#81 114 5 1 -0.5 3 2
		self.image = self.loadImage(self.image_url)
		self.seedX = int(81)
		self.seedY = int(114) 
		self.Sigma = float(1)
		self.SigmoidAlpha = float(-0.5)
		self.SigmoidBeta = float(3)
		self.PropagationScaling = float(2)

		self.processImage()
		self.tag = BQTag
		if self.seedX in range(78,83):
			self.tag.name = "AC_Left_Ventricle Segmented Image"
		elif self.seedX in range(97,101):
			self.tag.name = "AC_Right_Ventricle Segmented Image"
		elif self.seedX in range(54,58):
			self.tag.name = "AC_White_Matter Segmented Image"
		elif self.seedX in range(38,42):
			self.tag.name = "AC_Grey_Matter Segmented Image"
		else:
			self.tag.name = "AC_Unknown_Region Segmented Image"

		self.tag.value = self.image_out_url 
		resp = self.postTag(self.image, self.tag)
     	
if __name__ == "__main__":
	m = itkGeodesicSegmentationPY()
        m.main(sys.argv[1],sys.argv[2])
