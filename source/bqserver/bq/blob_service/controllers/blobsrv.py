###############################################################################
##  Bisque                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009,2010,2011,2012                           ##
##     by the Regents of the University of California                        ##
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
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ''AS IS'' AND ANY         ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE         ##
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR        ##
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR           ##
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,     ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ##
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## The views and conclusions contained in the software and documentation     ##
## are those of the authors and should not be interpreted as representing    ##
## official policies, either expressed or implied, of <copyright holder>.    ##
###############################################################################
"""
SYNOPSIS
========
blob_service


DESCRIPTION
===========
Micro webservice to store and retrieve blobs(untyped binary storage) on a variety
of storage platforms: local, irods, s3
"""
# pylint: disable=import-error,no-self-use

import os
import logging

from datetime import datetime
from datetime import timedelta
from lxml import etree
from sqlalchemy.exc import IntegrityError

#import smokesignal

import tg
from tg import expose, config, require, abort
from tg.controllers import RestController, TGController
#from paste.fileapp import FileApp
from bq.util.fileapp import BQFileApp
from pylons.controllers.util import forward
from paste.deploy.converters import asbool
#from paste.deploy.converters import asbool
from repoze.what import predicates

#from sqlalchemy.exc import IntegrityError

from bq.core import  identity
#from bq.core.identity import set_admin_mode
from bq.core.service import ServiceMixin
#from bq.core.service import ServiceController
from bq.exceptions import IllegalOperation
from bq.util.timer import Timer
from bq.util.sizeoffmt import sizeof_fmt
from bq.util.hash import is_uniq_code
from bq.util.contextfuns import optional_cm
from bq import data_service
from bq.data_service.model import Taggable, DBSession
#from bq import image_service
from bq import export_service

#from . import blob_drivers
from . import mount_service
from .blob_drivers import split_subpath
from .blob_plugins import ResourcePluginManager

SIG_NEWBLOB  = "new_blob"

log = logging.getLogger('bq.blobs')

#########################################################
# Utility functions
########################################################

def transfer_msg(flocal, transfer_t):
    'return a human string for transfer time and size'
    if flocal is None or not os.path.exists(flocal):
        return "NO FILE to measure %s" % flocal
    fsize = os.path.getsize (flocal)
    name  = os.path.basename(flocal)
    if isinstance(name, unicode):
        name  = name.encode('utf-8')
    if transfer_t == 0:
        return "transferred %s in 0 sec!" % fsize
    return "{name} transferred {size} in {time} ({speed}/sec)".format(
        name=name, size=sizeof_fmt(fsize),
        time=timedelta(seconds=transfer_t),
        speed = sizeof_fmt(fsize/transfer_t))


#pylint: disable=too-few-public-methods
class TransferTimer(Timer):
    def __init__(self, path=''):
        super(TransferTimer, self).__init__()
        self.path = path
    def __exit__(self, *args):
        Timer.__exit__(self, *args)
        if self.path and log.isEnabledFor(logging.INFO):
            log.info (transfer_msg (self.path, self.interval))



######################################################
# Store manageer

###########################################################################
# BlobServer
###########################################################################

class PathService (TGController):
    """Manipulate paths in the database

    Service to be used by filesystem agents to move references to files
    """
    def __init__(self, blobsrv):
        super (PathService, self).__init__()
        self.blobsrv = blobsrv
        self.mounts  = None

    @expose(content_type='text/xml')
    def index(self):
        "Path service initial page"
        resource = etree.Element ('resource')
        etree.SubElement (resource,'method', name='list?path=store_url', value="List resources at the path")
        etree.SubElement (resource,'method', name='insert?path=store_url', value="Insert resources at the path")
        etree.SubElement (resource,'method', name='move?path=store_url&destination=store_url', value="Move a resources at the path to a new path")
        etree.SubElement (resource,'method', name='delete?path=store_url', value="Delete resources at the path")
        return etree.tostring (resource)

    @expose(content_type='text/xml')
    @require(predicates.not_anonymous())
    def list(self, path=None, *args,  **kwargs):
        'Find a resource identified by a path'
        log.info("list( %s )" ,  path)
        resource = data_service.query('image|file', resource_value = path, wpublic='1', cache=False)
        return etree.tostring(resource)

    @expose(content_type='text/xml')
    @require(predicates.not_anonymous())
    def insert(self, path=None, user=None, **kwargs):
        """ Move a resource identified by path
        """
        if user is not None and identity.is_admin():
            identity.current.set_current_user( user )

        resource = self._check_post_body()

        if  resource is None:
            resource = etree.Element('resource', value = path)
        else:
            path = resource.get('value')

        log.info("insert_path() %s %s %s" , tg.request.method, path, kwargs)

        store,driver = self.mounts.valid_store_ref (resource)
        if store is None:
            abort (400, "%s is not a valid store " % path)

        if resource.get ('name') is None:
            resource.set ('name',  path.replace(driver.mount_url, ''))
        log.debug ("insert %s %s %s", path, driver.mount_url, etree.tostring (resource))

        resource = self.blobsrv.store_blob(resource)
        return etree.tostring(resource)

    @expose(content_type='text/xml')
    @require(predicates.not_anonymous())
    def move(self, path, destination, user=None,  **kw):
        ' Move a resource identified by path  '
        log.info("move(%s,%s) %s %s" , path, destination, tg.request.method, kw )
        if user is not None and identity.is_admin():
            identity.current.set_current_user( user )

        # sanity check
        resource = etree.Element('resource', value = destination)
        store,driver = self.mounts.valid_store_ref (resource)
        if store is None:
            abort (400, "%s is not a valid store " % destination)

        resource = data_service.query("file|image", resource_value = path, wpublic='1', cache=False)
        for child in resource:
            old_store,old_driver = self.mounts.valid_store_ref (child)
            if old_store is None:
                abort (400, "%s is not a valid store " % destination)
            # Remove links in directory hierarchy
            self.mounts.delete_links (child)
            # Change the location
            child.set('value',  destination)
            child.set('name', os.path.basename (destination))
            resource = data_service.update(child)
            # Update the tag
            q1 = data_service.query ('tag', parent = resource, name='filename')
            if len(q1):
                q1[0].set ('value', os.path.basename (destination))
                data_service.update(q1[0])
            # update the links
            partial_path = destination.replace(driver.mount_url,'')
            self.mounts.insert_mount_path(store, partial_path, resource)

        return etree.tostring(resource)

    @expose(content_type='text/xml')
    @require(predicates.not_anonymous())
    def remove(self, path,  delete_blob=True, user=None, **kwargs):
        ' Delete a resource identified by path  '
        log.info("delete() called %s" , path)
        if user is not None and identity.is_admin():
            identity.current.set_current_user( user )

        #convert delete_blob to a bool
        if delete_blob.lower() in ["false", "f"]:
            delete_blob = False

        resource = data_service.query("file|image", resource_value = path, wpublic='1', cache=False)
        for child in resource:
            data_service.del_resource (child, delete_blob=delete_blob)
        return etree.tostring(resource)


    def _check_post_body (self):
        "read a resource from post body if avaibable"
        request = tg.request
        if request.method.lower() in ("post", "put"):
            try:
                clen = int(request.headers.get('Content-Length', 0))
                content = request.headers.get('Content-Type')
                if content.startswith('text/xml') or  content.startswith('application/xml'):
                    data = request.body_file.read(clen)
                    resource = etree.XML (data)
                    log.debug ("POST BODY %s", etree.tostring (resource))
                    return resource
            except etree.XMLSyntaxError:
                log.exception ("Bad XML syntax in %s", data [:100])
                abort (400, "Bad XML syntax in POST: %s" % data)




###########################################################################
# BlobServer
###########################################################################

class BlobServer(RestController, ServiceMixin):
    '''Manage a set of blob files'''
    service_type = "blob_service"

    # do this on init
    #store = store_resource.StoreServer ()

    def __init__(self, url ):
        ServiceMixin.__init__(self, url)
        #self.drive_man = DriverManager()
        #self.__class__.store = store_resource.StoreServer(self.drive_man.drivers)
        paths = self.__class__.paths  = PathService(self)
        mounts = self.__class__.mounts = mount_service.MountServer(url)
        self.__class__.store = mounts
        paths.mounts = mounts

        self.subtransactions = asbool(config.get ('bisque.blob_service.subtransaction', True))

        path_root = config.get('bisque.paths.public', '')
        path_plugins = os.path.join(path_root, 'core', 'plugins')
        self.plugin_manager = ResourcePluginManager(path_plugins)


    def guess_type(self, filename):
        from bq import image_service
        filename = filename.strip()
        if image_service.is_image_type (filename):
            return 'image'
        return self.plugin_manager.guess_type(filename) or 'file'

    def guess_mime(self, filename):
        from bq import image_service
        filename = filename.strip()
        if image_service.is_image_type (filename):
            try:
                return 'image/%s'%os.path.splitext(filename.strip())[1][1:].lower()
            except Exception:
                pass
        return self.plugin_manager.guess_mime(filename) or 'application/octet-stream'

    def get_import_plugins(self):
        return self.plugin_manager.get_import_plugins()

#################################
# service  functions
################################
    def check_access(self, ident, action):
        from bq.data_service.controllers.resource_query import resource_permission
        query = DBSession.query(Taggable).filter_by (resource_uniq = ident)
        resource = resource_permission (query, action=action).first()
        if resource is None:
            if identity.not_anonymous():
                abort(403)
            else:
                abort(401)
        return resource

    #@expose()
    #def store(self, *path, **kw):
    #    log.debug ("STORE: Got %s and %s" ,  path, kw)





    @expose()
    def get_all(self):
        return "Method Not supported"

    @expose()
    def get_one(self, ident, **kw):
        "Fetch a blob based on uniq ID"
        log.info("get_one(%s) %s" , ident, kw)
        try:
            if not is_uniq_code (ident):
                abort (404, "Must be resource unique code")

            resource = data_service.resource_load(uniq=ident)
            if resource is None:
                abort (403, "resource does not exist or permission denied")
            filename,_ = split_subpath(resource.get('name', str(ident)))
            blb = self.localpath(ident)
            if blb.files and len(blb.files) > 1:
                return export_service.export(files=[resource.get('uri')], filename=filename)

            localpath = os.path.normpath(blb.path)
            if 'localpath' in kw:
                tg.response.headers['Content-Type']  = 'text/xml'
                resource = etree.Element ('resource', name=filename, value=localpath)
                return etree.tostring (resource)

            disposition = '' if 'noattach' in kw else 'attachment; '
            try:
                disposition = '%sfilename="%s"'%(disposition, filename.encode('ascii'))
            except UnicodeEncodeError:
                disposition = '%sfilename="%s"; filename*="%s"'%(disposition, filename.encode('utf8'), filename.encode('utf8'))

            content_type = self.guess_mime(filename)
            return forward(BQFileApp(localpath,
                                     content_type=content_type,
                                     content_disposition=disposition,).cache_control(max_age=60*60*24*7*6)) # 6 weeks
        except IllegalOperation:
            abort(404, "Error occurent fetching blob")

    @expose(content_type='text/xml')
    @require(predicates.not_anonymous())
    def post(self, **transfers):
        "Create a blob based on unique ID"
        log.info("post() called %s" , transfers)
        #log.info("post() body %s" % tg.request.body_file.read())

        def find_upload_resource(transfers, pname):
            log.debug ("transfers %s " , transfers)

            resource = transfers.pop(pname+'_resource', None) #or transfers.pop(pname+'_tags', None)
            log.debug ("found %s _resource/_tags %s " , pname, resource)
            if resource is not None:
                if hasattr(resource, 'file'):
                    log.warn("XML Resource has file tag")
                    resource = resource.file.read()
                if isinstance(resource, basestring):
                    log.debug ("reading XML %s" , resource)
                    try:
                        resource = etree.fromstring(resource)
                    except etree.XMLSyntaxError:
                        log.exception ("while parsing %s" , str(resource))
                        resource = None
            return resource

        for k,f in dict(transfers).items():
            if k.endswith ('_resource') or k.endswith('_tags'): continue
            if hasattr(f, 'file'):
                resource = find_upload_resource(transfers, k)
                resource = self.store_blob(resource = resource, fileobj = f.file)

        return resource


    @expose()
    @require(predicates.not_anonymous())
    def delete(self, ident, **kwargs):
        ' Delete the resource  '
        log.info("delete() called %s" , ident)
        from bq.data_service.controllers.resource_query import resource_delete
        from bq.data_service.controllers.resource_query import resource_permission
        from bq.data_service.controllers.resource_query import RESOURCE_READ, RESOURCE_EDIT
        query = DBSession.query(Taggable).filter_by (resource_uniq=ident,resource_parent=None)
        resource = resource_permission(query, RESOURCE_EDIT).first()
        if resource:
            resource_delete(resource)
        return ""



########################################
# API functions
#######################################
    def _create_resource(self, resource ):
        'create a resource from a blob and return new resource'
        # hashed filename + stuff

        perm     = resource.get('permission', 'private')
        filename = resource.get('name')
        if resource.tag == 'resource': # requires type guessing
            resource.set('resource_type', resource.get('resource_type') or self.guess_type(filename))
        if resource.get('resource_uniq') is None:
            resource.set('resource_uniq', data_service.resource_uniq() )
        else:
            pass
        ts = resource.get('ts') or datetime.now().isoformat(' ')

        # KGK
        # These are redundant (filename is the attribute name name upload is the ts
        # dima: today needed for organizer to work
        resource.insert(0, etree.Element('tag', name="filename", value=filename, permission=perm))
        resource.insert(1, etree.Element('tag',
                                         name="upload_datetime",
                                         value=ts,
                                         type='datetime',
                                         permission=perm,))

        if resource.get('resource_uniq') is None:
            resource.set('resource_uniq', data_service.resource_uniq() )
        log.info ("INSERTING NEW RESOURCE <= %s" , etree.tostring(resource))
        new_resource = data_service.new_resource(resource = resource, flush=False)
        return new_resource
        #if asbool(config.get ('bisque.blob_service.store_paths', True)):
            # dima: insert_blob_path should probably be renamed to insert_blob
            # it should probably receive a resource and make decisions on what and how to store in the file tree
            #try:
        #    self.store.insert_blob_path( path=resource.get('value') or resource.xpath('value')[0].text,
        #                                 resource_name = resource.get('name'),
        #                                 resource_uniq = resource.get ('resource_uniq'))
            #except IntegrityError:
            #    # dima: we get this here if the path already exists in the sqlite
            #    log.error('store_multi_blob: could not store path into the tree store')
    def create_resource(self, resource ):
        if resource.get('resource_uniq') is None:
            resource.set('resource_uniq', data_service.resource_uniq() )

        subtrans = None
        if self.subtransactions:
            #pylint: disable=no-member
            subtrans = DBSession.begin_nested
            log.debug ("USING NESTED transaction")
        for x in range (3):
            try:
                new_resource = None
                with optional_cm (subtrans):
                    new_resource = self._create_resource(resource)
                break
            except IntegrityError:
                log.exception ("Issue creating resource")
                resource.set ('resource_uniq', data_service.resource_uniq() )
        return new_resource


    def store_blob(self, resource, fileobj = None, rooturl = None):
        """Store a resource in the DB must be a valid resource

        @param fileobj: an open file i.e. recieved in a POST
        @param rooturl: a multi-blob resource will have urls as values rooted at rooturl
        @return: a resource
        """
        if log.isEnabledFor (logging.DEBUG):
            log.debug(' => store_blob: %s, %s -> %s', fileobj, rooturl, etree.tostring(resource))

        store_url, store, store_path, lpath = self.mounts.store_blob(resource, rooturl=rooturl, fileobj=fileobj)
        if store_url is  None:
            log.error ("Could not store FILEOBJ of resource")
            # TODO: Clean up created resource
            return None

        resource = self.create_resource (resource)
        if resource is None:
            log.error("Resource creation failed=> %s", etree.tostring (resource))
            return None

        store_opts =  self.mounts.get_store_opts(store)
        if asbool(store_opts.get ('paths', True)):
            self.mounts.insert_mount_path (store, store_path, resource)
        else:
            log.debug ("path store disabled %s", store_path)

        if log.isEnabledFor (logging.DEBUG):
            log.debug("store_blob stored: %s %s -> %s", store_url, lpath, etree.tostring (resource))
        return resource


    def localpath (self, uniq_ident, resource=None, blocking=True):
        "Find  local path for the identified blob, using workdir for local copy if needed"
        if resource is None:
            resource = data_service.resource_load (uniq=uniq_ident, view='full')
        #try:
        #    resource = data_service.query(resource_uniq=uniq_ident, wpublic=1, view='full')[0]
        #except IndexError:
        if resource is None:
            log.warn ('requested resource %s was not available/found' , uniq_ident)
            return None
        return self.mounts.fetch_blob(resource, blocking=blocking)

    def delete_blob(self, uniq_ident):
        """Delete the  blob reference defined by this resource
           Does not delete the resource itself nor does it check that you have rights
        """
        resource = data_service.resource_load(uniq=uniq_ident)
        self.mounts.delete_blob (resource)

    def originalFileName(self, ident):
        log.debug ('originalFileName: deprecated %s', ident)
        resource = data_service.resource_load(uniq=ident)
        if resource is None:
            log.warn ('requested resource %s was not available/found' , ident)
            return str(ident)

        fname,_ = split_subpath(resource.get('name', str (ident)))
        log.debug('Blobsrv - original name %s->%s ' , ident, fname)
        return fname

    def move_resource_store(self, srcstore, dststore):
        """Find all resource on srcstore and move to dststore

        @param srcstore: Source store  ID
        @param dststore: Destination store ID
        """

    """COMMENTED OUT
        src_store = self.drive_man.get(srcstore)
        dst_store = self.drive_man.get(dststore)
        if src_store is None or dst_store is None:
            raise IllegalOperation("cannot access store %s, %s" % (srcstore, dststore))
        if src_store == dst_store:
            raise IllegalOperation("cannot move onto same store %s, %s" % (srcstore, dststore))

        for resource in DBSession.query(Taggable).filter_by(Taggable.resource_value.like (src_store.top)):
            b = self.localpath(resource.resource_uniq)
            localpath = b.path

            filename = resource.resource_name
            user_name = resource.owner.resource_name
            try:
                with open(localpath) as f:
                    blob_id, flocal = dst_store.write(f, filename, user_name = user_name)
            except Exception:
                log.error("move failed for resource_uniq %s" , resource.resource_uniq)
                continue
            old_blob_id = resource.resource_value
            resource.resource_value = blob_id
    """

    def geturi(self, ident):
        return self.url + '/' + str(ident)


def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize %s" , uri)
    service =  BlobServer(uri)
    #directory.register_service ('image_service', service)

    return service

#def get_static_dirs():
#    """Return the static directories for this server"""
#    package = pkg_resources.Requirement.parse ("bqserver")
#    package_path = pkg_resources.resource_filename(package,'bq')
#    return [(package_path, os.path.join(package_path, 'image_service', 'public'))]

#def get_model():
#    from bq.image_service import model
#    return model

__controller__ =  BlobServer
