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

   Digital notebook service.

"""
import pkg_resources
import os
import logging
import shutil
import tg
from pylons.controllers.util import abort
from tg import expose, redirect, response
from tg import config
from lxml import etree
from urllib import urlencode
from repoze.what import predicates
from repoze.what.predicates import not_anonymous
#from paste.debug.profile import profile_decorator


from bq.core.identity import get_username, anonymous
from bq.core.service import ServiceController, service_registry
from bq.util.bix2db import BIXImporter
from bq.util.mkdir import _mkdir
from bq.util.paths import data_path
from bq import image_service
from bq import blob_service

#from turbogears import controllers, expose, redirect, paginate
#from turbogears import identity, visit, config, validate, error_handler



log = logging.getLogger('bq.notebook')

class DNServer(ServiceController):
    service_type = "notebook_service"


    #subcontroller = ...
    #def __init__(self, uri):
    #    self.baseuri = uri

    def imagelink(self, resource):
        base = self.baseuri
        base = base.replace( '/notebook_service', '/client_service')
        return base + "/view?" + urlencode ({'resource': resource})

    @expose()
    def index(self):
        return redirect (self.baseuri + '/config')

    @expose(content_type="text/xml")
    def config(self, **kw):
        response = etree.Element('response')

        etree.SubElement (response, 'config',
                          notify   =  self.baseuri + '/notify',
                          transfer = self.baseuri + '/savefile',
                          #user = get_user_id()
                          #password = get_user_pass()
                          )

        # Try the current server without any ports
#        ftpurl = urlparse.urlsplit (self.baseuri)[1].split(':')[0]
#
#        etree.SubElement (response, 'ftp',
#                          host = ftpurl,
#                          #user = 'bisque',
#                          #password = 'ucsb2004',
#                          path  = '/home/bisque/incoming'
#                          )

        return etree.tostring(response)


    @expose(content_type="text/xml")
    #@require(predicates.not_anonymous())
    #@profile_decorator(logfile="/home/kage/dn_savefile.profile")
    def savefile (self, **kw):
        log.info ("savefile request " + str (tg.request))
        username = get_username()
        # check the user identity here and return 401 if fails
        if anonymous():
            response.status_int = 401
            log.debug( 'Access denied' )
            return 'Access denied'

        # if requested test for uploaded
        hashes_str = kw.pop('hashes', None)
        if hashes_str != None:
            all_hashes = [ fhash.strip() for fhash in hashes_str.split(',') ]
            #for fhash in hashes_str.split(','):
            #    all_hashes.append( fhash )
            #found_hashes = blob_service.files_exist(all_hashes) TODO
            found_hashes = []
            found_html = ",".join([str(h) for h in found_hashes])
            return "Found: "+found_html

        # here user is authenticated - upload
        if not 'upload' in kw:
            response.status_int = 501
            return "No file to be uploaded..."
        upload = kw['upload']
        uploadroot = config.get('bisque.image_service.upload_dir', data_path('uploads'))
        upload_dir = uploadroot+'/'+ str(username)
        _mkdir (upload_dir)
        if not upload.filename:
            return 'No file sent...'
        #patch for no copy file uploads - check for regular file or file like object
        uploadpath = upload_dir+'/'+upload.filename
        #KGK: note upload.file.name is not available for some uploads (attached files)
        #abs_path_src = os.path.abspath(upload.file.name)
        #if os.path.isfile(abs_path_src):
        #    shutil.move(abs_path_src, uploadpath)
        #else:
        with open(uploadpath, 'wb') as trg:
            shutil.copyfileobj(upload.file, trg)

        return 'Upload done for: ' + upload.filename


    @expose()
    def notify(self, **kw):
        ''' DN upload request using HTTP uploads
            this function is only created temporaly to provide backward compatibility
            for DN provide http uploads, where directory is not specified by DN
            but is known by the server and thus should be ignored here
        '''
        username = get_username()
        #log.debug( 'notify - username: ' + str(userpwd) )
        if username is None:
            log.debug( 'notify needs credentialed user' )
            abort(401)

        log.debug( 'notify - args: ' + str(kw) )

        bixfiles   = kw.pop('bixfiles', [])
        imagefiles = kw.pop('imagefiles', [])
        upload_dir = kw.pop('uploaddir', None)
        if (upload_dir == None):
            uploadroot = config.get('bisque.image_service.upload_dir', data_path('uploads'))
            upload_dir = os.path.join(uploadroot,username)
            #upload_dir = uploadroot+'/'+ str(identity.current.user_name)

        remove_uploads = config.get('bisque.image_service.remove_uploads', False)
        #identity.set_current_identity(ident)
        importer = BIXImporter(upload_dir)
        images = []
        for bix in bixfiles.split(':'):
            if bix!=None and bix!='':
                try:
                    name, uri = importer.process_bix(bix)
                except Exception:
                    name = '%s [error importing]'%(bix)
                    uri = '#'
                if name != '' and uri != '':
                    images.append ( (name, uri ) )
                    if remove_uploads:
                        try:
                            os.unlink (os.path.join (upload_dir, bix))
                            os.unlink (os.path.join (upload_dir, name))
                        except Exception:
                            log.debug( 'Error removing temp BIX and/or Image files' )

        imageshtml = "<table>"
        imageshtml += "".join(['<tr><td><a href="%s">%s</a></td></tr>' %(self.imagelink (u), n)
                          for n,u in images])
        imageshtml += '</table>'

        if len(bixfiles) < len(imagefiles):
            inputimages = imagefiles.split(':')
            for n,u in images:
                inputimages.remove(n)
            if remove_uploads:
                for name in inputimages:
                    os.unlink (os.path.join (upload_dir, name))

            imageshtml += '<h2>Uploaded but not included as images %d (no meta-data file):</h2>'%(len(inputimages))
            imageshtml += "<table>".join(['<tr><td>%s</td></tr>' %(n) for n in inputimages])
            imageshtml += '</table>'

        return '<h2>Uploaded %d images:</h2>'%(len(images)) + imageshtml


#     @expose()
#     def notify(self, **kw):
#         ''' DN upload request using HTTP uploads
#             this function is only created temporaly to provide backward compatibility
#             for DN provide http uploads, where directory is not specified by DN
#             but is known by the server and thus should be ignored here
#         '''

#         # check the user identity here and return 401 if fails

#         userpwd = get_user_pass()
#         log.debug( 'notify - username: ' + str(userpwd[0]) )
#         if userpwd[0] == None or not not_anonymous():
#             response.status_int = 401
#             log.debug( 'Access denied' )
#             return "Access denied"

#         log.debug( 'notify - args: ' + str(kw) )

#         username   = str(userpwd[0])
#         password   = str(userpwd[1])
#         bixfiles   = kw.pop('bixfiles', [])
#         imagefiles = kw.pop('imagefiles', [])
#         upload_dir = kw.pop('uploaddir', None)
#         if (upload_dir == None):
#             uploadroot = config.get('bisquik.image_service.upload_dir', './uploads')
#             upload_dir = uploadroot+'/'+ str(userpwd[0])

#         #ident = identity.current_provider.validate_identity(username, password,
#         # visit.current().key)
#         remove_uploads = config.get('bisquik.image_service.remove_uploads', False)
#         #identity.set_current_identity(ident)
#         importer = BIXImporter(upload_dir)
#         images = []
#         for bix in bixfiles.split(':'):
#             if bix!=None and bix!='':
#                 try:
#                     name, uri = importer.process_bix(bix)
#                 except Exception:
#                     name = '%s [error importing]'%(bix)
#                     uri = '#';
#                 if name != '' and uri != '':
#                     images.append ( (name, uri ) )
#                     if remove_uploads:
#                         try:
#                             os.unlink (os.path.join (upload_dir, bix))
#                             os.unlink (os.path.join (upload_dir, name))
#                         except Exception:
#                             log.debug( 'Error removing temp BIX and/or Image files' )

#         imageshtml = "<table>"
#         imageshtml += "".join(['<tr><td><a href="%s">%s</a></td></tr>' %(self.imagelink (u), n) for n,u in images])
#         imageshtml += '</table>'

#         if len(bixfiles) < len(imagefiles):
#             inputimages = imagefiles.split(':')
#             for n,u in images:
#                 inputimages.remove(n)
#             if remove_uploads:
#                 for name in inputimages:
#                     os.unlink (os.path.join (upload_dir, name))
#             imageshtml += '<h2>Uploaded but not included as images %d (no meta-data file):</h2>'%(len(inputimages))
#             imageshtml += "<table>".join(['<tr><td>%s</td></tr>' %(n) for n in inputimages])
#             imageshtml += '</table>'

#             return '<h2>Uploaded %d images:</h2>'%(len(images)) + imageshtml
#         else:
#             response.status_int = 401
#             return "login unsuccessful"

    @expose()
    def test_uploaded(self, **kw):
        ''' XDMA upload request using HTTP uploads
            this function is only created temporaly to provide backward compatibility
            for DN provide http uploads, where directory is not specified by DN
            but is known by the server and thus should be ignored here
        '''
        #log.debug( 'dn_test_uploaded - username ' + str(identity.current.user_name) )

        # check the user identity here and return 401 if fails
        if not not_anonymous():
            response.status_int = 401
            return "Access denied"

        log.debug( 'dn_test_uploaded ' + str(kw) )

        hashes_str = kw.pop('hashes', [])

        all_hashes = []
        for fhash in hashes_str.split(','):
            all_hashes.append( fhash )
        found_hashes = image_service.files_exist(all_hashes)
        found_html = ",".join([str(h) for h in found_hashes])
        return "Found: "+found_html

dn_server = None
#def uri():
#    return client_server.baseuri

def savefile (upload, **kw):
    ''' Use preferred dn server '''
    if dn_server:
        return dn_server.savefile(upload, **kw)
    else:
        pass

def notify (**kw):
    ''' Use preferred dn server '''
    if dn_server:
        return dn_server.notify(**kw)
    else:
        pass

def test_uploaded (**kw):
    ''' Use preferred dn server '''
    if dn_server:
        return dn_server.test_uploaded(**kw)
    else:
        pass

service_class = DNServer
service_type  = service_class.service_type
#test = N_('hello')



def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    dn_server = service_class(uri)
    return dn_server


__controller__ = DNServer
__staticdir__ = None
__model__ = None
