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
SYNOPSIS
========


DESCRIPTION
===========

  Interface to an image server for other bisquik components.
  Abstract access to local, remote and multiple actual images servers

"""
import logging
import urlparse
import functools
from tg import config

#from bq.util.http import *
from controllers.service import ImageServiceController as LocalImageServer
from bq.core import identity
from bq.exceptions import RequestError

log = logging.getLogger('bq.image_service')

_preferred = None
servers   = {}


log.debug ("image_service loaded")

class RenamableFile (object):
    def __init__(self, filename, params):
        fd = open (filename, params)
        object.__setattr__(self, '_file', fd)

    def get_name(self):
        return self.filename
    def set_name(self, vl):
        self.filename = vl

    name = property(get_name, set_name)

    def __getattr__(self, name):
        return getattr(self._file, name)


class proxy_dispatch (object):
    class dispatch_for(object):
        def __init__(self, parent):
            self.stack   = []
            self.path    = parent.baseurl
            self.proxy   = parent
        def __getattr__(self, method):
            log.debug ("proxy url %s" % method)
            if method in self.proxy.server.srv.services:
                return functools.partial(self.push_method, method)
            raise AttributeError, method

        def get(self):
            fullurl = self.create_url()
            return self.proxy.dispatch (fullurl)
        def post(self, body):
            fullurl = self.create_url()
            return self.proxy.dispatch (fullurl, body=body)


        def push_method (self, method, *largs, **kw):
            #print "url push %s %s " % (method, largs)
            self.stack.append ( (method, ",".join([str(x) for x in largs]), kw) )
            return self

        def create_url(self):
            url = self.path
            if self.stack:
                args = []
                for m,a,k in self.stack:
                    if a:
                        args.append ('%s=%s' % (m,a))
                    else:
                        args.append (m)

                args = "&".join (args)
                url  =  "%s?%s" % (url, args)
            return url

        def image(self, path):
            self.path = path
            return self
        def __str__(self):
            return self.create_url()

    def __init__(self):
        self.baseurl = None
        self.server = None

    def add_server(self, rooturl, image_server):
        self.baseurl  = rooturl
        self.server   = image_server

    def __getattr__ (self, name):
        'construct a URL dispatcher and pass the inital request to it'
        d =  proxy_dispatch.dispatch_for(self)
        return getattr(d, name)



    def dispatch(self, fullurl, body=None):
        if fullurl.startswith (self.baseurl):
            return self.local_dispatch(fullurl, body)
        return self.remote_dispatch(fullurl)

    def local_dispatch(self, fullurl, body=None):
        path, params = urlparse.urlsplit (fullurl)[2:4]
        userId  = identity.get_username()

        try:
            id = int(path.split('/')[-1])
        except ValueError:
            id = None
        request = "%s?%s" % (path, params)
        data_token = self.server.srv.process(request, id, userId )
        if data_token.isHttpError():
            log.debug('Response Code: ' +str(data_token.httpResponseCode) )
            raise RequestError(data_token.httpResponseCode)

        #second check if the output is TEXT/HTML/XML
        if data_token.isText():
            return data_token.data

        if data_token.isFile():
            fpath = data_token.data.split('/')
            fname = fpath[len(fpath)-1]

            if data_token.hasFileName():
                fname = data_token.outFileName
                print "has ", fname

            #Content-Disposition: attachment; filename=genome.jpeg;
            #if data_token.isImage():
            #    disposition = 'filename="%s"'%(fname)
            #else:
            #    disposition = 'attachment; filename="%s"'%(fname)
            #cherrypy.response.headers["Content-Disposition"] = disposition
            # this header is cleared when the streaming is used
            #cherrypy.response.headers["Content-Length"] = 10*1024*1024

            ofs = RenamableFile(data_token.data,'rb')
            ofs.name = fname
            return ofs
            log.debug('Returning file: ' + str(fname) )

    #def remote_dispatch (self, fullurl):
    #    header, content  = http_client.request (fullurl)
    #    # Process content is similar way to local dispatch based on returned headers
    #    return content


class ImageService(proxy_dispatch):

    def initialize(self, uri):
        local_image_server = LocalImageServer(server_url = uri)

        self.add_server (uri, local_image_server)
        return local_image_server

    def new_file(self, src=None, name=None, **kw):
        ''' Find the preferred image server and store the file there
        '''
        return self.server.new_file(src=src, name=name, **kw)

    def new_image(self,name, src = None, **kw):
        ''' Find the preferred image server and store the image there
        '''
        return self.server.new_image(src, name, **kw)

    def files_exist(self,hashes, **kw):
        ''' Return a list of hashes found in the blob server'''

        return self.server.files_exist(hashes, **kw)

    def find_uris(self,hsh, **kw):
        ''' Return a list of uris found in the blob server for a particular hash'''
        return self.server.find_uris(hsh, **kw)

    def image_path(self,imgsrc, **kw):
            ''' Return meta data of image from image_server
            '''
            return self.server.local_path (imgsrc, **kw)

    def set_file_info(self,image_uri, **kw):
        ''' Set file info in blob server'''
        return self.server.set_file_info(image_uri, **kw)

    def set_file_credentials(self,image_uri, owner_name, permission):
        ''' Set file credentials in blob server'''
        return self.server.set_file_credentials(image_uri, owner_name, permission)

    def set_file_acl(self, image_uri, owner_name, permission):
        return self.server.set_file_acl(image_uri, owner_name, permission)

    def info (self, uniq):
        return self.server.info (uniq)

    def meta(self, uniq):
        return self.server.meta(uniq)

    def getFileName(self, imgsrc):
        return self.server.get_filename(imgsrc)

    def getImageID(self, imgsrc):
        return self.server.get_image_id(imgsrc)

from bq.core.service import service_registry

def find_server(url=None):
    return service_registry.find_service ('image_service')


#def store_blob (src, name):
#    server = find_server()
#    if server:
#        return server.store_blob(src=src, name=name)
#    else:
#        log.debug ("PREFERED IS NONE: no image server is available")
#        # Find a remote image server that is writable and send image there
#        pass

def is_image_type(filename):
    server = find_server()
    return server.is_image_type(filename)

def proprietary_series_extensions ():
    server = find_server()
    return server.proprietary_series_extensions()

def proprietary_series_headers():
    server = find_server()
    return server.proprietary_series_headers()

def non_image_extensions ():
    server = find_server()
    return server.non_image_extensions()

def get_info(filename):
    server = find_server()
    return server.get_info(filename)

# we use URL here in order to give access to derived computed results as local files
def local_file(url):
    ''' Return local path for a given image URL with processing'''
    server = find_server()
    return server.local_file(url)

def meta(uniq):
    ''' Return metadata XML for a given image ID'''
    server = find_server()
    return server.meta(uniq)

def info(uniq):
    ''' Return image info dictionary for a given image ID'''
    server = find_server()
    return server.info(uniq)

#def new_file(src=None, name=None, **kw):
#    ''' Find the preferred image server and store the file there
#    '''
#    server = find_server(src)
#    if server:
#        return server.new_file(src=src, name=name, **kw)
#    else:
#        log.debug ("PREFERED IS NONE: no image server is available")
#        # Find a remote image server that is writable and send image there
#        pass
#
#def new_image(name, src = None, **kw):
#    ''' Find the preferred image server and store the image there
#    '''
#    log.debug("new %s %s" % (name, src))
#    server = find_server(src)
#    if server:
#        log.debug ("PREFERED : %s" % str(server))
#        return server.new_image(src, name, **kw)
#    else:
#        log.debug ("PREFERED IS NONE: no image server is available")
#        # Find a remote image server that is writable and send image there
#        pass

def files_exist(hashes, **kw):
    ''' Return a list of hashes found in the blob server'''
    server = find_server()
    if server:
        return server.files_exist(hashes, **kw)
    else:
        # Find a remote image server to query
        pass

def find_uris(hsh, **kw):
    ''' Return a list of uris found in the blob server for a particular hash'''
    server = find_server()
    if server:
        return server.find_uris(hsh, **kw)
    else:
        # Find a remote image server to query
        pass

def image_path(imgsrc, **kw):
        ''' Return meta data of image from image_server
        '''
        server = find_server(imgsrc)
        if server:
            return server.local_path (imgsrc, **kw)

def getFileName(imgsrc):
    server = find_server(imgsrc)
    if server:
        return server.get_filename(imgsrc)

def getImageID(imgsrc):
    server = find_server(imgsrc)
    if server:
        return server.get_image_id(imgsrc)

def set_file_info(image_uri, **kw):
    ''' Set file info in blob server'''
    server = find_server('')
    if server:
        return server.set_file_info(image_uri, **kw)
    else:
        pass

def set_file_credentials(image_uri, owner_name, permission):
    ''' Set file credentials in blob server'''
    server = find_server(image_uri)
    if server:
        return server.set_file_credentials(image_uri, owner_name, permission)
    else:
        pass

def set_file_acl(image_uri, owner_name, permission):
    server = find_server(image_uri)
    return server.set_file_acl(image_uri, owner_name, permission)

def uri(image_uri):
    server = find_server(image_uri)
    return server.uri(image_uri)
