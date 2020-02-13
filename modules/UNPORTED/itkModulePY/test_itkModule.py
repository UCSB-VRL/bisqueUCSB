import logging
from lxml import etree
import base64
from bisquik.util.bisquik2db import known_gobjects, updateDB as parseXml
from  bisquik.util.http import request, post_files, xmlrequest
from bisquik import identity
import base64
import sys
import StringIO 
import time

import itk
#import FastMarchingSegmentation as seg

from lxml import etree

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
            
    
class itkModulePY:
    """test integration Module
    """
    def __init__(self):
        pass
        
    def loadImage(self, url):
        resp, content = request(url)
        log.debug ('itkModulePY - response:  ' +  str(content)  + '||||||||||' +url)
        response = etree.XML(content)
        image = parseXml(root = response, factory = BQNodeFactory)
        log.debug("GOT " + str(image.uri))
        return image

    def postTag(self,parent,tag):
        req = etree.Element ('request')
        etree.SubElement (req, 'tag',  name=str(tag.name), value=str(tag.value), type='string')
        log.debug("REQ: " + etree.tostring(req))
        resp, content = request(parent.uri, "POST", body = etree.tostring(req), headers={'content-type':'text/xml' }, userpass = self.userpass )
        log.debug("RESP: " + str(content))
        print etree.tostring(response)
        return resp

    def createXML(self,client_server,image_url,seedX, seedY, Sigma, SigmoidAlpha, SigmoidBeta):
		request = etree.Element('request')
		mex = etree.SubElement(request,'mex',  module = "http://bodzio.ece.ucsb.edu:8080/ds/modules/21534" )
		etree.SubElement(mex,'tag', name="client_server", value=str(client_server), index="0")
		etree.SubElement(mex,'tag', name="image_url", value=str(image_url), index="1")
		etree.SubElement(mex,'tag', name="seedX", value=str(seedX), index="2")    	
		etree.SubElement(mex,'tag', name="seedY", value=str(seedY), index="3")
		etree.SubElement(mex,'tag', name="Sigma", value=str(Sigma), index="4")
		etree.SubElement(mex,'tag', name="TSigmoidAlpha", value=str(SigmoidAlpha), index="5")
		etree.SubElement(mex,'tag', name="TSigmoidBeta", value=str(SigmoidBeta), index="6")
		etree.SubElement(mex,'tag', name="resources", value="")
		#xml = etree.XML(etree.tostring(request))
		temp = etree.parse(StringIO.StringIO(etree.tostring(request)))
		#print 'REQUEST =',str(request)
		#print 'tree = ',temp
		#print 'xml = ',xml
		return request

    def createXML2(self,client_server,image_url,tagname):
		request = etree.Element('request')
		mex = etree.SubElement(request,'mex',  module = "http://bodzio.ece.ucsb.edu:8080/ds/modules/22005" )
		etree.SubElement(mex,'tag', name="client_server", value=str(client_server), index="0")
		etree.SubElement(mex,'tag', name="image_url", value=str(image_url), index="1")
		etree.SubElement(mex,'tag', name="tagname", value=str(tagname), index="2")
		return request    	
    	   
    def main(self):
		print'Running in main'
		
		client_server = sys.argv[1]
		image_url = sys.argv[2]
		user = 'admin'
		password = 'admin'
		self.userpass  = ( user, password )

		seedX = [81,99 ,56,40]
		seedY = [114 ,114 ,92, 90] 
		Sigma = [1.0,1.0,1.0,1.0]
		SigmoidAlpha = [-0.5,-0.5,-0.3,-0.3]
		SigmoidBeta = [3.0,3.0,2.0,2.0]
		
		requesturl = client_server + '/ms/'
		
		#run all the four segmentation processes sequentially
		for i in range(0,len(seedX)):
			# Initiate the mex
			response = self.createXML(client_server,image_url,seedX[i], seedY[i], Sigma[i], SigmoidAlpha[i], SigmoidBeta[i])	
		
			resp, content = xmlrequest(requesturl , method="POST", body=etree.tostring(response), userpass=self.userpass )
			#print 'RESPONSE = ', str(resp)
			#print 'CONTENT = ',str(content)
			#print 'CONTENT LENGTH = ',len(content)

			# Check mex status 
			#mex = etree.parse(content)
			#print '\n\n parsing \n\n'
			mex = etree.parse(StringIO.StringIO(content))
			uri = mex.getroot().get('uri') 
			#print '\nURI = ' ,str(uri)
		    
			while 1:
				resp,content = request(uri, userpass=self.userpass)
				#print "###CONTENT = ",str(content)
				mex = etree.parse(StringIO.StringIO(content))
				if mex.getroot()[0].get('status') == 'FINISHED':
					print 'Finished'
					break
				elif mex.getroot()[0].get('status') =='FAILURE':
					print 'Failure'
					break
				#else:
				#	print '### Waiting..'   

# START COMMENT
		# decide on the tag name to search
		#if seedX in range(78,83):
		#	tagName= "Left_Ventricle_Mask"
		#elif seedX in range(97,101):
		#	tagName = "Right_Ventricle_Mask"
		#elif seedX in range(54,58):
		#	tagName = "White_Matter_Mask"
		#elif seedX in range(38,42):
		#		tagName = "Grey_Matter_Mask"
		#else:
		#	tagName = "Unknown_Region_Mask"
				
		# Now the tag is created- search for the tag in the image url-tag
		#resp, content = request(image_url, userpass=self.userpass)
		#print 'image url CONTENT = ',str(content)
		#tag = etree.parse(StringIO.StringIO(content))
		#tag_url = tag.getroot()[0][0].get('uri')
		
		#request for the tag values again
		#resp, content = request(tag_url , userpass=self.userpass)
		#print 'image url CONTENT = ',str(content)
		
		#tag = etree.parse(StringIO.StringIO(content))
		#tag_root = tag.getroot()
		#now parse the xml
		#i = 0;
		#while tag_root[i] !=  None:
		#	name = tag_root[i].get('name')
		#	if(name == tagName):
		#		break
		#	else:
		#		i = i+1

		#mask_url = tag_root[i].get('value')
		#if mask_url=='':
		#	print '\nERROR: mask_url not found'
		
		
		#print '\n\n', mask_url
		#time.sleep(5)
#END COMMENT
		
		tagName = ['Left_Ventricle_Mask','Right_Ventricle_Mask','White_Matter_Mask','Grey_Matter_Mask']

		requesturl = client_server + '/ms/'
		#Start processing for program 2
		for i in range(0,len(tagName)):
			response = self.createXML2(client_server,image_url,tagName[i])

			resp, content = xmlrequest(requesturl , method="POST", body=etree.tostring(response), userpass=self.userpass )
			#print 'RESPONSE = ', str(resp)
			#print 'CONTENT = ',str(content)
			#print 'CONTENT LENGTH = ',len(content)
		
			mex = etree.parse(StringIO.StringIO(content))
			uri = mex.getroot().get('uri') 
			#print '\nURI = ' ,str(uri)
			
			condCount = 0
			while 1:
				resp,content = request(uri, userpass=self.userpass)
				mex = etree.parse(StringIO.StringIO(content))
				if mex.getroot()[0].get('status') == 'FINISHED':
					print ' Finished module 2'
					break
				elif mex.getroot()[0].get('status') =='FAILURE':
					if condCount < 3:
						print 'Failure module 2 == Retrying for a free engine',condCount
						print 'Sleeping for 5 seconds'
						time.sleep(5)
						resp, content = xmlrequest(requesturl , method="POST", body=etree.tostring(response), userpass=self.userpass )
						mex = etree.parse(StringIO.StringIO(content))
						uri = mex.getroot().get('uri')
						condCount+=1
						
					else:
						print 'Failure module 2'
						break
				#else:
					#print '### Waiting..'   
		
		
		#self.processImage()
		#self.tag = BQTag
		

		#self.tag.value = self.image_out_url 
		#resp = self.postTag(self.image, self.tag)
    	
if __name__ == "__main__":
	m = itkModulePY()
        m.main()
