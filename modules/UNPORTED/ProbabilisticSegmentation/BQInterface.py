from lxml import etree
import httplib2
import base64
from PIL import Image


class BQInterface:


    def __init__(self):
        self.name = 'me'
        self.http = httplib2.Http('.cache')
    
    def getImage(self, url, user=None, password=None):
        #print self.http.credentials
        #print base64.encodestring("admin" + ":" + "admin").strip()
        resp, txt = self.http.request(url, 'GET', 
                            headers = { 
            'authorization' : 'Basic ' + base64.encodestring(user + ":" + password).strip()} )
        image = etree.XML(txt)[0]
        d = {}
        
        for (name, value) in image.attrib.items():
            d[name] = value
        
        return d
    
    def getImagePixels(self, url, format, user=None, password=None):
        if format is not None:
            fetchurl = url + "?format=" + format + ",stream"
        else:
            fetchurl = url
        #print fetchurl
        resp, txt = self.http.request(fetchurl, 'GET', 
                            headers = { 
            'authorization' : 'Basic ' + base64.encodestring(user + ":" + password).strip()} )
        
        return txt
    
    def getImageTags(self, url, extended=False, user=None, password=None):
        fetchurl = url + "/tags"
        resp, txt = self.http.request(fetchurl, 'GET', 
                            headers = { 
            'authorization' : 'Basic ' + base64.encodestring(user + ":" + password).strip()} )
        response = etree.XML(txt)
        d = []
        for i in response.findall('tag'):
            if (extended==False):
                d.append((i.attrib['name'], i.attrib['value']))
            else:
                d.append((i.attrib['name'], i.attrib['value'], i.attrib['index'], i.attrib['uri']))
        return d
    
    def getGObjects(self, url, gtype="", user=None, password=None):
        fetchurl = url + "/gobjects"
        resp, txt = self.http.request(fetchurl, 'GET', 
                            headers = { 
            'authorization' : 'Basic ' + base64.encodestring(user + ":" + password).strip()} )
        response = etree.XML(txt)
        gobs = []
        
        for i in response:
            
            if (not gtype or i.attrib['type'] == gtype):
                gobs.append(i)
            
        return gobs
            
    def getGObjectName(gob):
        d = [];
        for i in gob:
            d.append(i.attrib['name'])
        return d
        
    
    def getGObjectType(gob):
        d = [];
        for i in gob:
            d.append(i.attrib['type'])
        return d
        
    def getGObjectURI(gob):
        d = [];
        for i in gob:
            d.append(i.attrib['uri'])
        return d
        
    #def getGObjectKids(gob)
        #d = [];
        #for i in gob:
            #d.append(i.attrib['name'])
        #return d
        
    def getGObjectVertices(self, gob):
        d = [];
        for i in gob:
            d.append(i.attrib)
        return d
        
    #def getGObjectTags(gob)\
        #d = [];
        #for i in gob:
            #d.append(i.attrib['name'])
        #return d
    

    
    
    def newImageFile(self, url, ImagePath, ImageType, user=None, password=None):

        
        tsize = "1"
        channels = '1'
        depth = '8'
        types = 'uint8'
        endian = 'little'
        format = ImageType

        im = Image.open(ImagePath)
        width, height = im.size        
        try:
            while 1:
                im.seek(im.tell()+1)
        except EOFError:
            pass # end of sequence
        zsize = str(im.tell()+1)
        im = open(ImagePath, 'r')
        
        
        #urlQuery = "?width="+str(width)+"&height="+str(height)+"&zsize="+zsize+"&tsize="+tsize + "&channels="+channels+"&depth="+depth+"&type="+types+"&endian="+endian+"&format=raw"
        ulurl = url + "/bisquik/upload_handler" #+ urlQuery
                
        CRLF = '\r\n'
        boundary = 'THIS_IS_A_TEMP_BOUNDARY'
        headers = { 'Content-Type' : 'multipart/form-data; boundary=' + boundary, 'authorization' : 'Basic ' + base64.encodestring(user +':'+password)}
                    
        data = ""
        data = data + self.writeFormData(boundary, 'userfilecount', '1', 'text', '')
        data = data + self.writeFormData(boundary, 'img0tagcount', '0', 'text', '')
        data = data + self.writeFormData(boundary, 'xml', '1', 'text', '')
        data = data + self.writeFormData(boundary, 'userfile0', im, ImageType, 'ProbailisticSegmentation.tif')
        data = data + '--' + boundary + '--' + CRLF
	#t = open('packet.out', 'w')
	#t.write(data)
	#t.close()
        resp, txt = self.http.request(ulurl, 'POST', body = data, headers=headers);
        #print txt
        im.close()
        
        return txt
   
    
    def writeFormData(self, boundary, name, value, datatype, filename):
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
    
    def addTag(self, TagName, TagValue, TagType, existingTags = None):
        
        if (existingTags == None):
            docNode = etree.Element('request')
        else:
            docNode = existingTags
        
        etree.SubElement (docNode, 'tag',
                          name=str(TagName), value=str(TagValue), type=str(TagType))
        return docNode
    
    def postTag(self, url, tag, user=None, password=None):
        xml=etree.tostring(tag);
        
        if user is None:
            resp, txt = self.http.request(url, 'POST', body = xml,
                            headers = {
                'content-type'  : 'text/xml',
                'authorization' : 'Basic ' + base64.encodestring("%s:%s" % self.http.credentials[0]).strip()  
                } )
        else:
            resp, txt = self.http.request(url, 'POST', body = xml,
                            headers = {
                'content-type'  : 'text/xml',
                'authorization' : 'Basic ' + base64.encodestring(user +':'+password)  
                } )
        return txt














