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


DESCRIPTION
===========

"""
import os
import logging
import urlparse
import urllib
import string
import shutil
import collections
import posixpath
import socket
import tempfile

from tg import config
from paste.deploy.converters import asbool

from bq.exceptions import ConfigurationError, IllegalOperation, DuplicateFile

from bq.util.paths import data_path
from bq.util.mkdir import _mkdir
from bq.util.compat import OrderedDict
from bq.util.urlpaths import move_file, localpath2url, url2localpath, data_url_path, force_filesys
from bq.util.hash import make_uniq_code, is_uniq_code

from bq.util.io_misc import blocked_alpha_num_sort, tounicode

log = logging.getLogger('bq.blobs.drivers')

__all__ = [ 'make_storage_driver' ]

supported_storage_schemes = [ '', 'file' ]

#try:
#    from bq.util import irods_icmd as irods
#    supported_storage_schemes.append('irods')
#except ImportError:
#    pass

try:
    # pylint: disable=import-error
    from bq.util import irods_client as irods
    supported_storage_schemes.append('irods')
except ImportError:
    log.warn ("Can't import irods: irods storage not supported")


try:
    import boto
    from bq.util import s3_handler
    from boto.s3.connection import S3Connection, Location
    supported_storage_schemes.append('s3')
except ImportError:
    log.warn ("Can't import boto:  S3  Storage not supported")
    pass


try:
    import smb   # neeed for exceptions
    from smb.SMBConnection import SMBConnection
    supported_storage_schemes.append('smb')
except ImportError:
    pass



#################################################
#  misc
#################################################
# Blobs class
class Blobs(collections.namedtuple("Blobs", ["path", "sub", "files"])):
    "A tuple of main file, , suburl , and list of files associated with a blobid(storeurl)"


def split_subpath(path):
    """Splits sub path that follows # sign if present
    """
    spot = path.rfind ('#')
    if spot < 0:
        return path,''
    return path[:spot], path[spot+1:]

def join_subpath(path, sub):
    return "%s#%s" % (path, sub) if sub else path

def walk_deep(path):
    """Splits sub path that follows # sign if present
    """
    for root, _, filenames in os.walk(path):
        for f in filenames:
            yield os.path.join(root, f).replace('\\', '/')


if os.name == 'nt':
    def store_compare(store_url, mount_url):
        return store_url.lower().startswith (mount_url.lower())
else:
    def store_compare(store_url, mount_url):
        return store_url.startswith (mount_url)


##############################################
#  Load store parameters
def load_storage_drivers():
    stores = OrderedDict()
    store_list = [ x.strip() for x in config.get('bisque.blob_service.stores','').split(',') ]
    log.debug ('requested stores = %s' , store_list)
    for store in store_list:
        # pull out store related params from config
        params = dict ( (x[0].replace('bisque.stores.%s.' % store, ''), x[1])
                        for x in  config.items() if x[0].startswith('bisque.stores.%s.' % store))
        if 'path' not in params:
            log.error ('cannot configure %s without the path parameter' , store)
            continue
        log.debug("params = %s" ,  str(params))
        driver = make_storage_driver(params.pop('path'), **params)
        if driver is None:
            log.error ("failed to configure %s.  Please check log for errors " , str(store))
            continue
        stores[store] = driver
    return stores



class StorageDriver(object):
    scheme   = "scheme"   # The URL scheme id
    readonly = False      # store is readonly or r/w
    mount_url = "unmounted"

#     def __init__(self, mount_url=None, **kw):
#         """ initializae a storage driver
#         @param mount_url: optional full storeurl to mount
#         """

    # New interface
    def __enter__(self):
        self.mount()
        return self

    def __exit__(self,  type, value, traceback):
        self.unmount()

    def mount(self):
        """Mount the driver"""
    def unmount (self):
        """Unmount the driver """
    def mount_status(self):
        """return the status of the mount: mounted, error, unmounted
        """
    # File interface
    def valid (self, storurl):
        "Return validity of storeurl"
    def push(self, fp, storeurl, uniq=None):
        "Push a local file (file pointer)  to the store"
    def pull (self, storeurl, localpath=None, blocking=True):
        "Pull a store file to a local location"
    def chmod(self, storeurl, permission):
        """Change permission of """
    def delete(self, ident):
        'delete an entry on the store'
    def isdir (self, storeurl):
        "Check if a url is a container/directory"
    def status(self, storeurl):
        "return status of url: dir/file, readable, etc"
    def list(self, storeurl):
        "list contents of store url"
    def __str__(self):
        return self.mount_url

    # dima: possible additions ???, should modify walk to take ident ???
#     def is_directory(self, ident):
#         'check if the ident points to a directory'
#     def walk(self, ident):
#         'walk a specific directory in the store'



class LocalDriver (StorageDriver):
    """Local filesystem driver"""

    def __init__(self, mount_url=None, top = None,  readonly=False, **kw):
        """Create a local storage driver:

        :param path: format_path for how to store files
        :param  top: allow old style (relatave path file paths)
        :param readonly: set repo readonly
        """
        # posixpath.join '' force ending with /
        self.mount_url = posixpath.join(mount_url,'')
        self.mount_path = posixpath.join (url2localpath (self.mount_url),'')
        datadir = data_url_path()
        for key, value in kw.items():
            setattr(self, key, string.Template(value).safe_substitute(datadir=datadir))
        #self.top = posixpath.join(top or self.mount_url, '')
        self.readonly = asbool(readonly)
        if top:
            self.top = posixpath.join(string.Template(top).safe_substitute(datadir=datadir), '')
            self.top_path = posixpath.join(url2localpath(self.top), '')
        else:
            self.top = None
            self.top_path = ''


        self.options = kw


    def valid(self, storeurl):
        #log.debug('valid ident %s top %s', ident, self.top)
        #log.debug('valid local ident %s local top %s', url2localpath(ident), url2localpath(self.top))

        if store_compare(storeurl, self.mount_url):
            return storeurl

        # It might be a shorted
        storeurl,_ = split_subpath(storeurl)
        scheme = urlparse.urlparse(storeurl).scheme

        if not scheme and storeurl[0] != '/':
            storeurl = urlparse.urljoin (self.top, storeurl)
            # OLD STYLE : may have written %encoded values to file system
            path = posixpath.normpath(urlparse.urlparse(storeurl).path)
            path = force_filesys (path)
            log.debug ("checking unquoted %s", tounicode(path))
            if os.path.exists (path):
                return path  # not returning an actual URL ..
        elif storeurl.startswith('file:///'):
            #should have matched earlier
            return None
        elif storeurl.startswith('file://'):
            storeurl = urlparse.urljoin(self.top, storeurl[7:])
        else:
            return None
        localpath = url2localpath (storeurl)
        log.debug ("checking %s", tounicode(localpath))
        return os.path.exists(localpath) and localpath2url(localpath)

    def relative(self, storeurl):
        path = url2localpath (self.valid (storeurl))
        log.debug ("MOUNT %s PATH %s",self.mount_path,  path)
        return  path.replace (self.mount_path, '')

    # New interface
    def push(self, fp, storeurl, uniq=None):
        "Push a local file (file pointer)  to the store"

        log.debug('local.push: url=%s', storeurl)
        origpath = localpath = url2localpath(storeurl)
        fpath,ext = os.path.splitext(origpath)
        _mkdir (os.path.dirname(localpath))
        uniq = uniq or make_uniq_code()
        for x in xrange(len(uniq)-7):
        #for x in range(100):
            if not os.path.exists (localpath):
                log.debug('local.write: %s -> %s' , tounicode(storeurl), tounicode(localpath))
                #patch for no copy file uploads - check for regular file or file like object
                try:
                    move_file (fp, localpath)
                except OSError as e:
                    if not os.path.exists (localpath):
                        log.exception ("Problem moving file to%s ", localpath)
                    else:
                        log.error ("Problem moving file, but it seems to be there.. check permissions on store")

                #log.debug ("local.push: top = %s  path= %s",self.top_path, localpath )
                ident = localpath[len(self.top_path):]
                #if ident[0] == '/':
                #    ident = ident[1:]
                ident = localpath2url(ident)
                log.info('local push  blob_id: %s -> %s',  tounicode(ident), tounicode(localpath))
                return ident, localpath
            localpath = "%s-%s%s" % (fpath , uniq[3:7+x] , ext)
            #localpath = "%s-%04d%s" % (fpath , x , ext)
            log.warn ("local.write: File exists... trying %s", tounicode(localpath))
        raise DuplicateFile(localpath)

    def pull (self, storeurl, localpath=None, blocking=True):
        "Pull a store file to a local location"
        #log.debug('local_store localpath: %s', path)
        path,sub = split_subpath(storeurl)
        if not path.startswith('file:///'):
            if path.startswith('file://'):
                path = os.path.join(self.top, path.replace('file://', ''))
            else:
                path = os.path.join(self.top, path)

        path = url2localpath(path.replace('\\', '/'))

        #log.debug('local_store localpath path: %s', path)

        # if path is a directory, list contents
        files = None
        if os.path.isdir(path):
            files = walk_deep(path)
            files = sorted(files, key=blocked_alpha_num_sort) # use alpha-numeric block sort
        elif not os.path.exists(path):
            # No file at location .. fail
            return None
        # local storage can't extract sub paths, pass it along
        return Blobs(path=path, sub=sub, files=files)


    def list(self, storeurl, view=None, limit=None, offset=None):
        "list contents of store url"
        path, _sub = self._local (storeurl)

        return  [ "%s%s" % (posixpath.join (storeurl, f),
                            '' if os.path.isfile (os.path.join(path, f)) else '/')
                  for f in  os.listdir (path) ]

    def delete(self, storeurl):
        #ident,_ = split_subpath(ident) # reference counting required?
        path,_sub = split_subpath(storeurl)
        if not path.startswith('file:///'):
            if path.startswith('file://'):
                path = os.path.join(self.top, path.replace('file://', ''))
            else:
                path = os.path.join(self.top, path)

        path = url2localpath(path.replace('\\', '/'))
        log.info("local deleting %s", path)
        if os.path.isfile (path):
            try:
                os.remove (path)
            except OSError:
                log.exception("Could not delete %s", path)


    def _local(self, storeurl):
        "Make local path (converting local relative to full path)"
        path,sub = split_subpath(storeurl)
        if not path.startswith('file:///'):
            if path.startswith('file://'):
                path = os.path.join(self.top, path.replace('file://', ''))
            else:
                path = os.path.join(self.top, path)

        path = url2localpath(path.replace('\\', '/'))
        return path, sub

    def __str__(self):
        return "localstore[%s, %s]" % (self.mount_url, self.top)

###############################################
# Irods

class IrodsDriver(StorageDriver):
    """New Irods driver :

    MAYBE TO BE REDONE to reuse connection.
    """

    def __init__(self, mount_url, readonly=False, credentials=None, cache = None, **kw):
        """Create a iRods storage driver:

        :param path: irods:// url format_path for where to store files
        :param  user: the irods users
        :param  password: the irods password
        :param readonly: set repo readonly
        """
        self.mount_url = posixpath.join (mount_url, '')
        datadir = data_url_path()
        for key, value in kw.items():
            setattr(self, key, string.Template(value).safe_substitute(datadir=datadir))
        if credentials:
            try:
                self.user, self.password = [ x.strip('"\'') for x in credentials.split(':') ]
            except ValueError:
                log.exception ('bad credentials for irods %s', credentials)

        #self.user = kw.pop('credentials.user',None) or kw.pop('user',None)
        #self.password = kw.pop('credentials.password', None) or kw.pop('password', None)
        self.readonly = asbool(readonly)
        self.options = kw
        self.user  = self.user.strip ('"\'')
        self.password  = self.password.strip ('"\'')
        cache = cache or data_path ('irods_cache')
        self.cache = string.Template(cache).safe_substitute(datadir=data_url_path())
        log.debug('irods.user: %s irods.password: %s' , self.user, self.password)
        # Get the constant portion of the path
        log.debug("created irods store %s " , self.mount_url)

    def valid(self, storeurl):
        return storeurl.startswith(self.mount_url) and storeurl

    # New interface
    def push(self, fp, storeurl, uniq = None):
        "Push a local file (file pointer)  to the store"
        log.info('irods.push: %s' , storeurl)
        fpath,ext = os.path.splitext(storeurl)
        uniq = uniq or make_uniq_code()
        try:
            for x in xrange(len(uniq)-7):
                if not irods.irods_isfile (storeurl, user=self.user, password = self.password):
                    break
                storeurl = "%s-%s%s" % (fpath , uniq[3:7+x] , ext)
            flocal = irods.irods_push_file(fp, storeurl, user=self.user, password=self.password, cache=self.cache)
            flocal = force_filesys (flocal)
        except irods.IrodsError:
            log.exception ("During Irods Push")
            raise IllegalOperation ("irods push failed")
        return storeurl, flocal

    def pull (self, storeurl, localpath=None, blocking=True):
        "Pull a store file to a local location"
        # dima: path can be a directory, needs listing and fetching all enclosed files
        log.info('irods.pull: %s' , storeurl)
        try:
            # if irods will provide extraction of sub files from compressed (zip, tar, ...) ask for it and return sub as None
            irods_ident,sub = split_subpath(storeurl)
            path = irods.irods_fetch_file(storeurl, user=self.user, password=self.password, cache=self.cache)
            # dima: if path is a directory, list contents
            path = force_filesys (path)
            return Blobs(path=path, sub=sub, files=None)
        except irods.IrodsError:
            log.exception ("Error fetching %s ", irods_ident)
        return None

    def list(self, storeurl):
        "list contents of store url"
        return irods.irods_fetch_dir (storeurl, user=self.user, password=self.password)

    def delete(self, irods_ident):
        log.info('irods.delete: %s' , irods_ident)
        try:
            irods.irods_delete_file(irods_ident, user=self.user, password=self.password, cache=self.cache)
        except irods.IrodsError, e:
            log.exception ("Error deleteing %s :%s", irods_ident, e)
        return None

###############################################
# S3
class S3Driver(StorageDriver):
    'blobs on s3'

    scheme = 's3'

    def __init__(self, mount_url=None, credentials = None,
                 bucket_id=None, location=None,
                 readonly = False, cache=None, **kw):
        """Create a iRods storage driver:

        :param path: s3:// url format_path for where to store files
        :param  credentials : access_key, secret_key
        :param  bucket_id: A unique bucket ID to store file
        :param location: The S3 location identifier (default is USWest)
        :param readonly: set repo readonly
        """

        self.mount_url = posixpath.join (mount_url, '')
        if credentials:
            access_key,  secret_key = credentials.split(':')
            self.creds = { 'aws_access_key_id': access_key,
                           'aws_secret_access_key' : secret_key,
        }
        else:
            log.error ('need credentials for S3 store')

        self.location = location or Location.USWest
        self.bucket_id = bucket_id #config.get('bisque.blob_service.s3.bucket_id')
        #self.bucket = None
        self.conn = None
        self.readonly = asbool(readonly)
        self.top = mount_url.split('$')[0]
        self.options = kw
        #self.mount ()
        cache = cache or data_path ('s3_cache')
        self.cache = string.Template(cache).safe_substitute(datadir=data_url_path())



    def mount(self):
        if self.conn is not None:
            return

        # if self.access_key is None or self.secret_key is None or self.bucket_id is None:
        #     raise ConfigurationError('bisque.blob_service.s3 incomplete config')

        # try:
        #     self.conn = S3Connection(self.access_key, self.secret_key)
        # except boto.exception.S3ResponseError:
        #     log.error ("S3 Connection failed")
        #     raise IllegalOperation ("S3 connection Failed")

        # try:
        #     self.bucket = self.conn.get_bucket(self.bucket_id)
        # except boto.exception.S3ResponseError:
        #     try:
        #         self.bucket = self.conn.create_bucket(self.bucket_id, location=self.location)
        #     except boto.exception.S3CreateError:
        #         raise ConfigurationError('bisque.blob_service.s3.bucket_id already owned by someone else. Please use a different bucket_id')

        # log.info("mounted S3 store %s (%s)" , self.mount_url, self.top)

    def unmount (self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def valid(self, storeurl):
        return storeurl.startswith(self.mount_url) and storeurl

    def push(self, fp, storeurl, uniq=None):
        'write a file to s3'
        s3_ident,sub = split_subpath(storeurl)
        s3_base,ext = os.path.splitext(s3_ident)
        log.info('s3.write: %s -> %s' , storeurl, s3_ident)
        uniq = uniq or make_uniq_code()
        for x in xrange(len(uniq)-7):
            s3_key = s3_ident.replace("s3://","")
            if not s3_handler.s3_isfile (self.bucket_id, s3_key, self.creds):
                break
            s3_ident = "%s-%s%s" % (s3_base , uniq[3:7+x] , ext)

        flocal = s3_handler.s3_push_file(fp, self.bucket_id , s3_key, self.cache, self.creds)
        flocal = force_filesys (flocal)
        return s3_ident, flocal

    def pull(self, storeurl, locapath=None, blocking=True):
        'return path to local copy of the s3 resource'
        # dima: path can be a directory, needs listing and fetching all enclosed files

        # if s3 will provide extraction of sub files from compressed (zip, tar, ...) ask for it and return sub as None
        log.info('s3.pull: %s ' , storeurl)
        storeurl,sub = split_subpath(storeurl)
        s3_key = storeurl.replace("s3://","")
        try:
            path = s3_handler.s3_fetch_file(self.bucket_id, s3_key, self.cache, self.creds, blocking=blocking)
            # dima: if path is a directory, list contents
            path = force_filesys (path)
            return Blobs(path=path, sub=sub, files=None)
        except boto.exception.S3ResponseError:
            log.exception ("During s3 pull")
            return None

    def delete(self, storeurl):
        log.info('s3.delete: %s ' , storeurl)
        s3_key = storeurl.replace("s3://","")
        s3_handler.s3_delete_file(self.bucket_id, s3_key, self.cache, self.creds)
    def isdir (self, storeurl):
        "Check if a url is a container/directory"
    def status(self, storeurl):
        "return status of url: dir/file, readable, etc"
    def list(self, storeurl):
        "list contents of store url"
        s3_key = posixpath.join(storeurl.replace("s3://",""), "")
        for obj in s3_handler.s3_list (bucket=self.bucket_id, key=s3_key, creds=self.creds):
            yield "s3://%s" % obj.key


###############################################
# HTTP(S)
class HttpDriver(StorageDriver):
    """HTTP storage driver  """
    scheme = 'http'

    def __init__(self, mount_url=None, credentials=None, readonly=True, **kw):
        """Create a HTTP storage driver:

        :param path: http:// url format_path for where to read/store files
        :param  user: the irods users
        :param  password: the irods password
        :param readonly: set repo readonly
        """
        self.mount_url = posixpath.join (mount_url, '')
        # DECODE Credential string
        if credentials:
            self.auth_scheme = credentials.split(':', 1)
            if self.auth_scheme.lower() == 'basic':
                _, self.user, self.password = [ x.strip('"\'') for x in credentials.split(':')]
        # basic auth
        log.debug('http.user: %s http.password: %s' , self.user, self.password)
        self.readonly = asbool(readonly)
        self.options = kw
        self.top = mount_url.split('$')[0]
        if mount_url:
            self.mount(mount_url, **kw)

    def mount(self):
        # Get the constant portion of the path
        log.debug("created http store %s " , self.mount_url)

    def valid(self, http_ident):
        return  http_ident.startswith(self.mount_url) and http_ident

    def push(self, fp, filename, uniq=None):
        raise IllegalOperation('HTTP(S) write is not implemented')

    def pull(self, http_ident,  localpath=None, blocking=True):
        # dima: path can be a directory, needs listing and fetching all enclosed files
        raise IllegalOperation('HTTP(S) localpath is not implemented')

class HttpsDriver (HttpDriver):
    "HTTPS storage"
    scheme = 'https'



class SMBNetDriver(StorageDriver):
    "Implement a SMB driver "
    scheme   = "smb"
    #https://pythonhosted.org/pysmb/api/smb_SMBConnection.html

    def __init__(self, mount_url=None, credentials = None, readonly = False, **kw):
        """ initializae a storage driver
        @param mount_url: optional full storeurl to mount
        """
        self.conn = None
        self.mount_url = posixpath.join(mount_url, '')
        self.readonly = readonly
        if credentials is None:
            log.warn ("SMBMount Cannot proceed without credentials")
            return
        self.user, self.password = credentials.split (':')
        self.localhost = socket.gethostname()
        urlcomp = urlparse.urlparse (self.mount_url)
        self.serverhost = urlcomp.netloc
        self.server_ip = socket.gethostbyname(self.serverhost)



    # New interface
    def mount(self):
        """Mount the driver
        @param mount_url: an smb prefix to be used to mount  smb://smbhostserver/sharename/d1/d2/"
        @param credentials: a string containing user:password for smb connection
        """

        # I don't this this is the SMB hostname but am not sure
        if self.conn is not None:
            return

        self.conn = SMBConnection (self.user, self.password, self.localhost, self.serverhost)
        if not self.conn.connect(self.server_ip, 139):
            self.conn = None

        #except smb.base.NotReadyError:
        #    log.warn("NotReady")
        #except smb.base.NotConnectedError:
        #    log.warn("NotReady")
        #except smb.base.SMBTimeout:
        #    log.warn("SMBTimeout")

    def unmount (self):
        """Unmount the driver """
        if self.conn:
            self.conn.close()
            self.conn=None

    def mount_status(self):
        """return the status of the mount: mounted, error, unmounted
        """

    @classmethod
    def split_smb(cls,storeurl):
        "return a pair sharename, path suitable for operations"
        smbcomp = urlparse.urlparse (storeurl)
        # smb://host    smbcomp.path = /sharenmae/path
        _, sharename, path = smbcomp.path.split ('/', 2)

        return sharename, '/' + path

    # File interface
    def valid (self, storeurl):
        "Return validity of storeurl"
        return storeurl.startswith (self.mount_url) and storeurl

    def push(self, fp, storeurl, uniq=None):
        "Push a local file (file pointer)  to the store"
        sharename, path = self.split_smb(storeurl)
        uniq = uniq or make_uniq_code()
        base,ext = os.path.splitext(path)
        for x in xrange(len(uniq)-7):
            try:
                if not self.conn.getAttributes (sharename, path):
                    break
            except smb.OperationError:
                path = "%s-%s%s" % (base , uniq[3:7+x] , ext)

        written = self.conn.storeFile (sharename, path, fp)
        log.debug ("smb wrote %s bytes", written)
        return "smb://%s/%s" % (sharename, path), None

    def pull (self, storeurl, localpath=None, blocking=True):
        "Pull a store file to a local location"
        sharename, path = self.split_smb(storeurl)
        if self.conn:
            if localpath:
                file_obj = open (localpath, 'wb')
            else:
                file_obj = tempfile.NamedTemporaryFile()
            file_attributes, filesize = self.conn.retrieveFile(sharename, path, file_obj)
            log.debug ("smb fetch of %s got %s bytes", storeurl, filesize)

    def chmod(self, storeurl, permission):
        """Change permission of """

    def delete(self, storeurl):
        'delete an entry on the store'
        sharename, path = self.split_smb(storeurl)
        if self.conn:
            self.conn.deleteFiles(sharename, path)

    def isdir (self, storeurl):
        "Check if a url is a container/directory"
    def status(self, storeurl):
        "return status of url: dir/file, readable, etc"
    def list(self, storeurl):
        "list contents of store url"






###############################################
# Construct a driver

def make_storage_driver(mount_url, **kw):
    """construct a driver using the URL path

    :param path: URL of storage path
    :param kw:   arguments to passed to storage constructor
    """

    storage_drivers = {
        #'file' : LocalStorage,
        #''     : LocalStorage,
        'file'  : LocalDriver,
        ''      : LocalDriver,
        'irods' : IrodsDriver,
        's3'    : S3Driver,
        'http'  : HttpDriver,
        'https' : HttpsDriver,
        'smb'   : SMBNetDriver,
        }

    scheme = urlparse.urlparse(mount_url).scheme.lower()
    if scheme in supported_storage_schemes:
        store = storage_drivers.get(scheme)
        log.debug ("creating %s driver with %s " , scheme, mount_url)
        return store(mount_url=mount_url, **kw)
    log.error ('request storage scheme %s unavailable' , scheme)
    return None
