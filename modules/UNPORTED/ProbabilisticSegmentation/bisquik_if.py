from lxml import etree
import httplib2
import base64


class BQInterface:


    def __init__(self):
        self.name = 'me'
        self.http = httplib2.Http('.cache')
    
    def getImage(self, url):
        #print self.http.credentials
        #print base64.encodestring("admin" + ":" + "admin").strip()
        resp, txt = self.http.request(url, 'GET', 
                            headers = { 
            'authorization' : 'Basic ' + base64.encodestring("admin" + ":" + "admin").strip()} )
        image = etree.XML(txt)[0]
        d = {}
        
        for (name, value) in image.attrib.items():
            d[name] = value
        
        return d
    
    def getImagePixels(self, url, format):
        fetchurl = url + "?format=" + format
        resp, txt = self.http.request(url, 'GET', 
                            headers = { 
            'authorization' : 'Basic ' + base64.encodestring("admin" + ":" + "admin").strip()} )
        return txt
    
    def getImageTags(self, url, extended=False):
        fetchurl = url + "/tags"
        resp, txt = self.http.request(fetchurl, 'GET', 
                            headers = { 
            'authorization' : 'Basic ' + base64.encodestring("admin" + ":" + "admin").strip()} )
        response = etree.XML(txt)
        d = []
        for i in response.findall('tag'):
            if (extended==False):
                d.append((i.attrib['name'], i.attrib['value']))
            else:
                d.append((i.attrib['name'], i.attrib['value'], i.attrib['index'], i.attrib['uri']))
        return d
    
    def getGObjects(self, url, gtype=""):
        fetchurl = url + "/gobjects"
        resp, txt = self.http.request(fetchurl, 'GET', 
                            headers = { 
            'authorization' : 'Basic ' + base64.encodestring("admin" + ":" + "admin").strip()} )
        response = etree.XML(txt)
        gobs = []
        
        for i in response:
            
            if (not gtype or i.attrib['type'] == gtype):
                gobs.append(i)
            
        return gobs
            
    def getGObjectName(gob)
        d = [];
        for i in gob:
            d.append(i.attrib['name'])
        return d
        
    
    def getGObjectType(gob)
        d = [];
        for i in gob:
            d.append(i.attrib['type'])
        return d
        
    def getGObjectURI(gob)
        d = [];
        for i in gob:
            d.append(i.attrib['uri'])
        return d
        
    #def getGObjectKids(gob)
        #d = [];
        #for i in gob:
            #d.append(i.attrib['name'])
        #return d
        
    def getGObjectVertices(gob)
        d = [];
        for i in gob:
            d.append((i.attrib)
        return d
        
    #def getGObjectTags(gob)\
        #d = [];
        #for i in gob:
            #d.append(i.attrib['name'])
        #return d
    
            
            
    
    def findImageAttribute(ImageData, Attribute):
        root = ImageData.children
        if (root.name == 'response'):
            child = root.children
        else:
            child = root
        while child is not None:
            if child.name == "image":
                return child.prop(Attribute)
            else:
                child = child.next
        
    def findGObjectAttribute(GObjectData, Attribute):
        root = GObjectData.children
        if (root.name == 'response'):
            child = root.children
        else:
            child = root
        while child is not None:
            if child.prop(Attribute):
                return child.prop(Attribute)
            else:
                child = child.next
    
    
    def postImage(url, Image, ImageType):
        CRLF = '\r\n'
        boundary = 'THIS_IS_A_TEMP_BOUNDARY'
        headers = { 'Content-Type' : 'multipart/form-data; boundary=' + boundary} 
        data = ""
        data = writeFormData(boundary, 'userfilecount', '1', 'text', '')
        data = data + writeFormData(boundary, 'img0tagcount', '0', 'text', '')
        data = data + writeFormData(boundary, 'userfile0', Image, ImageType, 'MatlabGeneratedImage')
        data = data + '--' + boundary + '--' + CRLF
        request = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(request)
        return response
    
    def writeFormData(boundary, name, value, datatype, filename):
        CRLF = '\r\n'
        
        data = ""
        data = data + '--' + boundary + CRLF
        data = data + 'Content-Disposition: form-data;  name="' + name + '"'
        
        if (datatype == 'text'):
            data = data + CRLF
            data = data + 'Content-Type: text/plain' + CRLF
            data = data + CRLF + value
        else:
            data = data + '; filename="' + filename + '"' + CRLF
            data = data + 'Content-Type: image/' + datatype + CRLF
            data = data + 'Content-Transfer-Encoding: binary' + CRLF + CRLF
            data = data + value.read()
        
        data = data + CRLF
        return data
    
    def addTag(TagName, TagValue, existingTags):
        if (~existingTags):
            docNode = libxml2.parseDoc('<request></request>')
        else:
            docNode = existingTags
            
        tag = docNode.children.newChild(None, 'tag', '')
        tag.newProp('name', TagName)
        tag.newProp('value', str(TagValue))
        tag.newProp('type', str(type(TagValue)))
        return docNode
        
