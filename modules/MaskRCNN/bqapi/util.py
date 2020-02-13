

import os
import shutil
#import urllib
#import urlparse
#import time
import logging
from six.moves import urllib

#from lxml import etree as ET
#from lxml import etree
from .xmldict import xml2d, d2xml

log = logging.getLogger('bqapi.util')

#####################################################
# misc: unicode
#####################################################

def normalize_unicode(s):
    if isinstance(s, str):
        return s
    try:
        s = s.decode('utf8')
    except UnicodeEncodeError:
        s = s.encode('ascii', 'replace')
    return s

#####################################################
# misc: path manipulation
#####################################################

if os.name == 'nt':
    def url2localpath(url):
        path = urllib.parse.urlparse(url).path
        if len(path)>0 and path[0] == '/':
            path = path[1:]
        try:
            return urllib.parse.unquote(path).decode('utf-8')
        except UnicodeEncodeError:
            # dima: safeguard measure for old non-encoded unicode paths
            return urllib.parse.unquote(path)

    def localpath2url(path):
        path = path.replace('\\', '/')
        url = urllib.parse.quote(path.encode('utf-8'))
        if len(path)>3 and path[0] != '/' and path[1] == ':':
            # path starts with a drive letter: c:/
            url = 'file:///%s'%url
        else:
            # path is a relative path
            url = 'file://%s'%url
        return url

else:
    def url2localpath(url):
        url = url.encode('utf-8') # safegurd against un-encoded values in the DB
        path = urllib.parse.urlparse(url).path
        return urllib.parse.unquote(path)

    def localpath2url(path):
        url = urllib.parse.quote(path.encode('utf-8'))
        url = 'file://%s'%url
        return url

#####################################################


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        self[name] = value
        return value

    def __getstate__(self):
        return list(self.items())

    def __setstate__(self, items):
        for key, val in items:
            self[key] = val


def safecopy (*largs):
    largs = list (largs)
    d = largs.pop()

    for f in largs:
        try:
            dest = d
            if os.path.isdir (d):
                dest = os.path.join (d, os.path.basename(f))
            print ("linking %s to %s"%(f,dest))
            if os.path.exists(dest):
                print ("Found existing file %s: removing .." % dest)
                os.unlink (dest)
            os.link(f, dest)
        except (OSError, AttributeError) as e:
            print ("Problem in link %s .. trying copy" % e)
            shutil.copy2(f, dest)

def parse_qs(query):
    """
        parse a uri query string into a dict
    """
    pd = {}
    if '&' in query:
        for el in query.split('&'):
            nm, junk, vl = el.partition('=')
            pd.setdefault(nm, []).append(vl)
    return pd

def make_qs(pd):
    """
        convert back from dict to qs
    """
    query = []
    for k,vl in list(pd.items()):
        for v in vl:
            pair = v and "%s=%s" % (k,v) or k
            query.append(pair)
    return "&".join(query)


def save_blob(session,  localfile=None, resource=None):
    """
        put a local image on the server and return the URL
        to the METADATA XML record

        @param session: the local session
        @param image: an BQImage object
        @param localfile:  a file-like object or name of a localfile
        @return XML content  when upload ok

        @exceptions comm.BQCommError - if blob is failed to be posted
    """
    content = session.postblob(localfile, xml=resource)

    #content = ET.XML(content)
    content = session.factory.string2etree(content)
    if len(content)<1: #when would this happen
        return None
    return content[0]


def fetch_blob(session, uri, dest=None, uselocalpath=False):
    """
        fetch original image locally as tif
        @param session: the bqsession
        @param uri: resource image uri
        @param dest: a destination directory
        @param uselocalpath: true when routine is run on same host as server
    """
    image = session.load(uri)
    name = image.name or next_name("blob")

    query = None
    if uselocalpath:
        # Skip 'file:'
        path = image.value
        if path.startswith('file:'):
            path =  path[5:]
        return {uri: path}

    url = session.service_url('blob_service', path = image.resource_uniq)
    blobdata = session.c.fetch(url)
    if os.path.isdir(dest):
        outdest = os.path.join (dest, os.path.basename(name))
    else:
        outdest = os.path.join ('.', os.path.basename(name))
    f = open(outdest, 'wb')
    f.write(blobdata)
    f.close()
    return {uri: outdest}


def fetch_image_planes(session, uri, dest=None, uselocalpath=False):
    """
        fetch all the image planes of an image locally
        @param session: the bqsession
        @param uri: resource image uri
        @param dest: a destination directory
        @param uselocalpath: true when routine is run on same host as server

    """
    image = session.load (uri, view='full')
    #x,y,z,t,ch = image.geometry()
    meta = image.pixels().meta().fetch()
    #meta = ET.XML(meta)
    meta = session.factory.string2etree(meta)
    t  = meta.findall('.//tag[@name="image_num_t"]')
    t  = len(t) and t[0].get('value')
    z  = meta.findall('.//tag[@name="image_num_z"]')
    z  = len(z) and z[0].get('value')
    tplanes = int(t)
    zplanes = int(z)

    planes=[]
    for t in range(tplanes):
        for z in range(zplanes):
            ip = image.pixels().slice(z=z+1,t=t+1).format('tiff')
            if uselocalpath:
                ip = ip.localpath()
            planes.append (ip)

    files = []
    for i, p in enumerate(planes):
        slize = p.fetch()
        fname = os.path.join (dest, "%.5d.TIF" % i)
        if uselocalpath:
            #path = ET.XML(slize).xpath('/resource/@src')[0]
            resource = session.factory.string2etree(slize)
            path = resource.get ('value')
            # Strip file:/ from path
            if path.startswith ('file:/'):
                path = path[5:]
            if os.path.exists(path):
                safecopy (path, fname)
            else:
                log.error ("localpath did not return valid path: %s", path)
        else:
            f = open(fname, 'wb')
            f.write(slize)
            f.close()
        files.append(fname)

    return files


def next_name(name):
    count = 0
    while os.path.exists("%s-%.5d.TIF" % (name, count)):
        count = count + 1
    return "%s-%.5d.TIF" % (name, count)



def fetch_image_pixels(session, uri, dest, uselocalpath=False):
    """
        fetch original image locally as tif
        @param session: the bqsession
        @param uri: resource image uri
        @param dest: a destination directory
        @param uselocalpath: true when routine is run on same host as server
    """
    image = session.load(uri)
    name = image.name or next_name("image")
    ip = image.pixels().format('tiff')
    if uselocalpath:
        ip = ip.localpath()
    pixels = ip.fetch()
    if os.path.isdir(dest):
        dest = os.path.join(dest, os.path.basename(name))
    else:
        dest = os.path.join('.', os.path.basename(name))
    if not dest.lower().endswith ('.tif'):
        dest = "%s.tif" % dest


    if uselocalpath:
        #path = ET.XML(pixels).xpath('/resource/@src')[0]
        resource = session.factory.string2etree(pixels)
        path = resource.get ('value')
        #path = urllib.url2pathname(path[5:])
        if path.startswith('file:/'):
            path = path[5:]
            # Skip 'file:'
        if os.path.exists(path):
            safecopy(path, dest)
            return { uri : dest }
        else:
            log.error ("localpath did not return valid path: %s", path)

    f = open(dest, 'wb')
    f.write(pixels)
    f.close()
    return { uri : dest }


def fetch_dataset(session, uri, dest, uselocalpath=False):
    """
        fetch elemens of dataset locally as tif

        @param session: the bqsession
        @param uri: resource image uri
        @param dest: a destination directory
        @param uselocalpath: true when routine is run on same host as server

        @return:
    """
    dataset = session.fetchxml(uri, view='deep')
    members = dataset.findall('.//value[@type="object"]')

    results = {}
    for i, imgxml in enumerate(members):
        uri =  imgxml.text   #imgxml.get('uri')
        print ("FETCHING", uri)
        #fname = os.path.join (dest, "%.5d.tif" % i)
        x = fetch_image_pixels(session, uri, dest, uselocalpath=uselocalpath)
        results.update (x)
    return results


def fetchImage(session, uri, dest, uselocalpath=False):
    """
        @param: session -
        @param: url -
        @param: dest -
        @param: uselocalpath- (default: False)

        @return
    """
    image = session.load(uri).pixels().info()
    #fileName = ET.XML(image.fetch()).xpath('//tag[@name="filename"]/@value')[0]
    fileName = session.factory.string2etree(image.fetch()).findall('.//tag[@name="filename"]')[0]
    fileName = fileName.get ('value')

    ip = session.load(uri).pixels().format('tiff')

    if uselocalpath:
        ip = ip.localpath()

    pixels = ip.fetch()

    if os.path.isdir(dest):
        dest = os.path.join(dest, fileName)

    if uselocalpath:
        #path = ET.XML(pixels).xpath('/resource/@src')[0]
        resource = session.factory.string2etree(pixels)
        path = resource.get ('value')
        #path = urllib.url2pathname(path[5:])
        if path.startswith ('file:/'):
            # Skip 'file:'
            path = path[5:]
        if os.path.exists(path):
            safecopy(path, dest)
            return {uri: dest }
        else:
            log.error ("localpath did not return valid path: %s", path)

    f = open(dest, 'wb')
    f.write(pixels)
    f.close()
    return {uri :dest }


def fetchDataset(session, uri, dest, uselocalpath=False):
    dataset = session.fetchxml(uri, view='deep')
    members = dataset.findall('.//value[@type="object"]')
    results = {}

    for i, imgxml in enumerate(members):
        uri = imgxml.text
        print ("FETCHING: ", uri)
        #fname = os.path.join (dest, "%.5d.tif" % i)
        result = fetchImage(session, uri, dest, uselocalpath=uselocalpath)
        results[uri] = result[uri]
    return results


# Post fields and files to an http host as multipart/form-data.
# fields is a sequence of (name, value) elements for regular form
# fields.  files is a sequence of (name, filename, value) elements
# for data to be uploaded as files
# Return the tuple (rsponse headers, server's response page)

# example:
#   post_files ('http://..',
#   fields = {'file1': open('file.jpg','rb'), 'name':'file' })
#   post_files ('http://..', fields = [('file1', 'file.jpg', buffer), ('f1', 'v1' )] )

def save_image_pixels(session,  localfile, image_tags=None):
    """
        put a local image on the server and return the URL
        to the METADATA XML record

        @param: session - the local session
        @param: image - an BQImage object
        @param: localfile - a file-like object or name of a localfile

        @return: XML content when upload ok
    """
    xml = None
    if image_tags:
        #xml = ET.tostring(toXml(image_tags))
        xml = session.factory.to_string(image_tags)
    return session.postblob(localfile, xml=xml)



def as_flat_dict_tag_value(xmltree):
    def _xml2d(e, d, path=''):
        for child in e:
            name  = '%s%s'%(path, child.get('name', ''))
            value = child.get('value', None)
            if value is not None:
                if not name in d:
                    d[name] = value
                else:
                    if isinstance(d[name], list):
                        d[name].append(value)
                    else:
                        d[name] = [d[name], value]
            d = _xml2d(child, d, path='%s%s/'%(path, child.get('name', '')))
        return d

    return _xml2d(xmltree, {})

def as_flat_dicts_node(xmltree):
    def _xml2d(e, d, path=''):
        for child in e:
            name  = '%s%s'%(path, child.get('name', ''))
            #value = child.get('value', None)
            value = child
            #if value is not None:
            if not name in d:
                d[name] = value
            else:
                if isinstance(d[name], list):
                    d[name].append(value)
                else:
                    d[name] = [d[name], value]
            d = _xml2d(child, d, path='%s%s/'%(path, child.get('name', '')))
        return d

    return _xml2d(xmltree, {})
