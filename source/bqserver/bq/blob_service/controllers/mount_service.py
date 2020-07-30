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
Store resource all special clients to simulate a filesystem view of resources.
"""


#pylint: disable=import-error

#import sys
import os
import logging
import string
import urllib
import posixpath

from lxml import etree
from sqlalchemy.exc import IntegrityError
from paste.deploy.converters import asbool

import tg
from tg import expose, config,  abort
from tg.controllers import TGController
#from repoze.what import predicates

from bq.core import  identity
from bq.core.model import DBSession
#from bq.core.service import ServiceMixin
#from bq.core.service import ServiceController
from bq.exceptions import IllegalOperation
#from bq.util.paths import data_path
from bq.util.compat import OrderedDict
from bq.util.bisquik2db import  load_uri  # needed for identity stuff
from bq.util.urlpaths import url2unicode,data_url_path,config2url,url2localpath
from bq.util.io_misc import   tounicode
from bq.util.contextfuns import optional_cm

from bq import data_service

from . import blob_drivers
from .blob_drivers import split_subpath, join_subpath

log = logging.getLogger('bq.blobs.mounts')


#################################################
#  Define helper functions for NT vs Unix/Mac
#

def get_tag(elem, tag_name):
    els = elem.xpath ('./tag[@name="%s"]' % tag_name)
    if len(els) == 0:
        return None
    return els



#  Load store parameters
OLDPARMS = dict (date='',
                 dirhash='',
                 filehash='',
                 filename='',
                 filebase='',
                 fileext='')
def load_default_drivers():
    stores = OrderedDict()
    store_list = [ x.strip() for x in config.get('bisque.blob_service.stores','').split(',') ]
    log.debug ('requested stores = %s' , store_list)
    for store in store_list:
        # pull out store related params from config
        params = dict ( (x[0].replace('bisque.stores.%s.' % store, ''), x[1])
                        for x in  config.items() if x[0].startswith('bisque.stores.%s.' % store))
        if 'mounturl' not in params:
            if 'path' in params:
                path = params.pop ('path')
                params['mounturl'] = string.Template(path).safe_substitute(OLDPARMS)
                log.warn ("Use of deprecated path (%s) in  %s driver . Please change to mounturl and remove any from %s", path, store, OLDPARMS.keys())
                log.info ("using mounturl = %s", params['mounturl'])
            else:
                log.error ('cannot configure %s without the mounturl parameter' , store)
                continue
        #if 'top' not in params:
        #    params['top'] = params['mounturl'].split ('$user')[0]
        #    log.warn ("top for %s was not set.  Using %s", params['mounturl'], params['top'])
        log.debug("params = %s" , params)
        #driver = make_storage_driver(params.pop('path'), **params)
        #if driver is None:
        #    log.error ("failed to configure %s.  Please check log for errors " , str(store))
        #    continue
        stores[store] = params
    return stores


def list_wings (lst, els = 5):
    """Give a summary for long lists"""
    if len(lst) <= 2*els:
        return lst, None
    return lst[:els], lst[-els:]
def list_summary(lst, els=5):
    """Give a summary for long lists"""
    if len(lst) <= 2*els:
        return str(lst)
    return  "[%s..%s]" % (",".join(str (x) for x in lst[:els]), ",".join(str (x) for x in lst[-els:]))


###########################################################################


class MountServer(TGController):
    """ Manipulate
    """
    def __init__(self, url):
        super(MountServer, self).__init__()
        self.drivers = load_default_drivers()
        log.info ("Loaded drivers %s", self.drivers)
        self.subtransactions = asbool(config.get ('bisque.blob_service.subtransaction', True))
        # Sanity check
        if config.get('sqlalchemy.url').startswith ('sqlite://'):
            self.subtransactions = False
            log.warn ("SQLITE does not support subtransactions: some mount service operations will fail")
        self.store_paths = asbool(config.get ('bisque.blob_service.store_paths', True))


    #############################################################
    # Web funs
    #
    @expose(content_type='text/xml')
    #@require(predicates.not_anonymous())
    def _default(self, *path, **kw):
        """ Dispatch based on request method GET, ...
        """

        # Ignore silently anonymous requests (no looking at files when not logged in)
        if identity.anonymous():
            return "<resource/>"

        # hmm some path elements arrive %encoded and utf8..  convert back to simple unicode
        path = [ url2unicode(x) for x in path ]
        method = tg.request.method
        if  method == 'GET':
            return self._get(list(path), **kw)
        elif method in ( 'POST', 'PUT'):
            return self._post(list(path), **kw)
        elif method == 'DELETE':
            return self._delete(list(path), **kw)
        abort(400)

    @expose(content_type='text/xml')
    #@require(predicates.not_anonymous())
    def index(self):
        #stores = etree.Element ('resource', resource_type='stores')
        #for k,v in self.drivers.items():
        #    etree.SubElement(stores, 'store', name = k, resource_unid=k, value=v.top)


        if identity.anonymous():
            return "<resource/>"

        root = self._create_root_mount()
        return etree.tostring(root)


    def _get(self, path, **kw):
        """ GET from a path /store_name/d1/d2/
        """
        log.info ("GET %s with %s" ,  path, kw)
        origview = kw.pop('view', 'short')
        value = None
        # Some crazy hanlding when de-referencing
        if len(path) and path[-1] == 'value':
            value = path.pop()
            #view = 'query'
            view = 'full'
            origkw = kw
            kw = {}
        else:
            view = 'full'
        # woops just want a list of stores.. index does that
        if len(path)==0:
            return self.index()
        store_name = path.pop(0)

        q = self._load_mount_path(store_name=store_name, path = path, view=view, **kw)
        if q is None:
            log.warn ("could not load store/path %s/%s", store_name, path)
            #abort (404, "bad store path %s" % path)
            return '<resource/>'
        # crazy value handling (emulate limit and offset)
        if value is not None:
            limit = origkw.pop('limit', None)
            offset = int(origkw.pop('offset', 0))
            resp = etree.Element('resource')
            for el in q[offset: limit and (int(limit) + offset)]:
                if el.tag == 'link':
                    r = data_service.get_resource (el.get ('value'), view=origview, **origkw)
                    if r is not None:
                        resp.append(r)
                    else:
                        log.warn ('element %s was not fetched', etree.tostring(el))
                else:
                    resp.append(el)
            # recipe for sorting trees from http://stackoverflow.com/questions/8385358/lxml-sorting-tag-order
            for parent in resp.xpath('//*[./*]'): # Search for parent elements
                parent[:] = sorted(parent,key=lambda x: x.get('name', None) or '')
            #resp.sort (key = lambda x: x.get ('name'))
            q = resp

        fullpath = ['', 'blob_service', 'store', store_name]
        fullpath.extend (path)
        self.mapuris (q, top="/".join (fullpath))

        return etree.tostring(q)

    def _post(self, path, **kw):
        log.info ("POST/PUT %s with %s" ,  path, kw)
        if len(path)==0:
            return self.index()
        store_name = path.pop(0)
        if len(path) == 0:
            store = self._validate_store_update (store_name, tg.request.body)
            if store is None:
                abort("Unable to update store")
            return etree.tostring(store)
        q = self.add_mount_path (store_name, path, **kw)
        return etree.tostring(q)

    def _delete(self, path, **kw):
        log.info ("DELETE %s with %s" ,  path, kw)
        if len(path)==0:
            return self.index()
        store_name = path.pop(0)
        if self.delete_mount_path(store_name, path, **kw):
            return "<response/>"


    def _refresh (self, path, **kw):
        "Refresh the store from a given path"
        if len(path)==0:
            return self.index()
        store_name = path.pop(0)



    ######################
    # Core
    def _create_root_mount(self):
        'create/find hidden root store for each user'

        root = data_service.query('store', resource_unid='(root)', view='full')
        #root = data_service.query('store', resource_unid='(root)', view='short')
        if len(root) == 0:
            found_root=  self._create_default_mounts()
        if len(root) == 1:
            found_root =  self._create_default_mounts(root[0])
        elif len(root) > 1:
            log.error("Root store created more than once: %s ", etree.tostring(root))
            return None

        self.mapuris(found_root)
        return found_root

    def mapuris (self, store_resource, top="/blob_service/store"):
        log.debug ("STORE RESOURCE -> %s", etree.tostring (store_resource))
        store_resource.set ('uri', top)
        resource_iter  = store_resource.iter()
        next (resource_iter)
        for el in resource_iter:
            if el.tag in ('link', 'dir'):
                el.set ('uri', (el.getparent() and el.getparent().get('uri', 'ROOT') or '') + '/' + el.get ('resource_unid', 'UNID'))



    def _create_default_mounts(self, root=None):
        'translate system stores into mount (store) resources'

        #for x in range(subtrans_attempts):
        #    with optional_cm(subtrans):
        update = False
        user_name  = identity.current.user_name
        if root is None:
            update  = True
            root = etree.Element('store', name="(root)", resource_unid="(root)")
            etree.SubElement(root, 'tag', name='order', value = ','.join (self.drivers.keys()))
            for store_name,driver in self.drivers.items():
                mount_path = string.Template(driver['mounturl']).safe_substitute(datadir = data_url_path(), user = user_name)
                etree.SubElement(root, 'store', name = store_name, resource_unid=store_name, value=config2url(mount_path))
        else:
            storeorder = get_tag(root, 'order')
            if storeorder is None:
                log.warn ("order tag missing from root store adding")
                storeorder = etree.SubElement(root, 'tag', name='order', value = ','.join (self.drivers.keys()))
                update = True
            elif len(storeorder) == 1:
                storeorder = storeorder[0]
            else:
                log.warn("Multible order tags on root store")

            # Check for store not already initialized
            user_stores   = dict ((x.get ('name'), x)  for x in root.xpath('store'))
            for store_name, driver in self.drivers.items():
                if store_name not in user_stores:
                    store = etree.SubElement (root, 'store', name = store_name, resource_unid = store_name)
                    # If there is a new store defined, better just to reset it to the default

                    #ordervalue = [ x.strip() for x in storeorder.get ('value', '').split(',') ]
                    #if store_name not in ordervalue:
                    #    ordervalue.append(store_name)
                    #    storeorder.set ('value', ','.join(ordervalue))
                    storeorder.set ('value', ','.join (self.drivers.keys()))
                else:
                    store = user_stores[store_name]
                if store.get ('value') is None:
                    mounturl = driver.get ('mounturl')
                    mounturl = string.Template(mounturl).safe_substitute(datadir = data_url_path(), user = user_name)
                    # ensure no $ are left
                    mounturl = mounturl.split('$', 1)[0]
                    store.set ('value', config2url(mounturl))
                    log.debug ("setting store %s value to %s", store_name, mounturl)
                    update = True

        if update:
            log.debug ("updating %s", etree.tostring(root))
            return data_service.update(root, new_resource=root, replace=False, view='full')
        return root


    def _create_user_mount (self, root_mount, mount_name, mount_url):
        'create a new user mount given a url'
        store = etree.Element('store', name = mount_name, resource_unid=mount_name, value=mount_url)
        data_service.new_resource(store, parent = root_mount)


    def _validate_store_update(self,storename, storexml):
        "Allow only the credential tag to be modified on store"
        try:
            storeel = etree.XML(storexml)
        except etree.ParseError:
            log.error ("bad storexml for update %s", storexml)
            return
        store = self._load_store(storename)
        # What constitutes a valid update?
        # 1.  Only admins can create new top level stores and they
        #  should be user specific (this is done using the site.cfg
        #  currently)
        if store is None:
            log.warn ("attempting modify non-existent store %s.. please add new store templates to site.cfg", storename)
            return None
        # 2. User can edit substores but may not change any attributes (only tags)
        if storeel.tag != 'tag' or storeel.get('name') != 'credentials':  # could be posting a tag
            log.warn("invalid store resource (use tag[credentials]) %s", storexml)
            return None
        store = data_service.get_resource(store, view="full")
        credtag = get_tag(store, 'credentials')
        if credtag is None:
            store.append (storeel)
        else:
            credtag[0].set('value', storeel.get ('value'))

        return data_service.update_resource(store, new_resource=store, replace=False, view='full')


    ###############################################
    # Store operators
    # A store path is the user friendly list of names

    def _load_root_mount(self):
        "fetch the root mount and submounts"
        #root = data_service.query('store', resource_unid='(root)', view='full', cache=False)
        root = data_service.query('store', resource_unid='(root)', view='full')
        #root = data_service.query('store', resource_unid='(root)', view='short', cache=False)
        if len(root) == 1:
            return self._create_default_mounts(root[0])
        elif len(root) == 0:
            raise IllegalOperation ("No root store not valid %s", etree.tostring (root))
        return root[0]

    def _load_store(self, store_name):
        'Simply load the store named by parameter.. will return short version'
        #root = self._create_root_mount()
        root = self._load_root_mount()
        storelist = root.xpath("store[@name='%s']" % store_name)
        if len(storelist) == 0:
            log.warn('No store named %s' , store_name)
        elif len(storelist) != 1:
            log.error ('Multiple named stores')
        else:
            return storelist[0]
        return None

    def _load_mount_path (self, store_name, path, **kw ):
        """load a store resource from store
        """
        log.debug ("load_mount_path : %s %s", store_name, path)
        path = list(path)   # make a copy to leave argument alone
        view = kw.pop('view', 'full')
        q = self._load_store(store_name)  # This load is not a full load but may be a short load
        #log.debug ('ZOOM %s', q.get ('uri'))
        while q is not None and path:
            el= path.pop(0)
            el = urllib.unquote (el)
            #q = data_service.query(parent=q, resource_unid=el, view='full', )
            q = data_service.query(parent=q, resource_unid=el, view='short', )
            if len(q) != 1:
                log.error ('multiple names (%s) in store level %s', el, q.get('uri'))
                return None
            q = q[0]
        if q is not None and (kw or len(q)) == 0:
            # might be limitin result
            log.debug ("loading with %s view=%s and %s", q, view, kw)
            q = data_service.get_resource(q, view=view, **kw)
        return q

    def add_mount_path(self, store_name, path, resource_uniq=None, resource_name=None, **kw):
        """Insert a URL path
        """
        store = self._load_store(store_name)
        if store is None:
            store = store_name
        return self._create_full_path(store, path, resource_uniq, resource_name, **kw)

    def delete_mount_path (self, store_name, path, delete_resource=True, **kw):
        """ Delete an store element and all below it

        :param path: A string (url) of the path
        :type  path: str
        """

        value = None
        if len(path) and path[-1] == 'value':
            value = path.pop()
        if len(path)==0:
            return False
        q = self._load_mount_path (store_name, path)
        if q is None:
            log.debug ("Cannot find %s in %s", path, store_name)
            return False
        log.debug ("delete from %s of %s = %s", store_name, path, etree.tostring(q))
        #if  q.tag != 'link':
        #    return False
        data_service.del_resource(q, check_acl=False, check_blob=False, check_references=False)
        if delete_resource and value is not None:
            data_service.del_resource(q.get ('value'))
        return True


    # def _walk_path (self, root):
    #     """Emulate OS walk on a store
    #     usage : for dird, sibdird, links in mount_service.walk_path ('/store/dir')
    #                print ("in dir ",  dird)
    #                for fname in links:
    #                   pass
    #     """
    #     value = None
    #     if len(path) and path[-1] == 'value':
    #         value = path.pop()
    #     if len(path)==0:
    #         return False
    #     q = self._load_mount_path (store_name, path)
    #     if q is None:
    #         log.debug ("Cannot find %s in %s", path, store_name)
    #         return False
    #     log.debug ("delete from %s of %s = %s", store_name, path, etree.tostring(q))




    #################################
    # blobsrv API
    def valid_store_ref(self, resource):
        """Test whether the resource  is on a store can be read by the user

        @param resource: a binary resource
        @return : a store resource
        """
        stores = self._get_stores()

        storeurls =  resource.get ('value')
        if storeurls is not None:
            storeurls = [storeurls]
        else:
            storeurls = [x.text for x in resource.xpath('value')]

        if len(storeurls) < 1:
            log.warn ("No value in resource trying name")
            return None,None

        for store_name, store in stores.items():
            prefix = store.get ('value')
            log.debug ("checking %s and %s" ,  prefix, storeurls[0])
            # KGK: TEMPORARY .. this should check readability by the driver
            try:
                driver = self._get_driver(store)
                if driver is None:
                    continue
            except IllegalOperation:
                log.warn ("Skipping store %s", store_name)
                continue
            if  driver.valid (storeurls[0]):
                # All *must* be valid for the same store
                for storeurl in storeurls[1:]:
                    if not driver.valid (storeurl):
                        raise IllegalOperation('resource %s spread across different stores %s', resource.get('resource_uniq'), storeurls)
                log.debug ("matched %s %s", store_name, driver.mount_url)
                return store, driver
        return None, None

    def store_blob(self, resource, fileobj = None, rooturl=None):
        """store a blob to a mount

        A resource contains:

          1.  A reference to a previously stored file with its
              storeurl i.e. irods://host/path/file.ext in resource.value

          2.  A relative location i.e. dir1/dir2/file.ext in the
              resource name which can be stored in the 1st store available
              by the users ordering on the root store

          3.  a fixed store location i.e. /irods_home/dir1/dir2/file.ext which must match a store name

        """
        stores = self._get_stores()
        log.debug ("Available stores: %s", stores.keys())
        # Strip off an subpaths from storepath (at this point.. not suported by drivers)
        storepath, _ = split_subpath (resource.get ('name'))
        if storepath[0]=='/':
            # This is a fixed store name i.e. /local or /irods and must be stored on the specific mount
            _, store_name, storepath = storepath.split ('/', 2)
            if store_name not in stores:
                raise IllegalOperation("Illegal store name %s", store_name)
            stores = dict([ (store_name, stores[store_name]) ])
        else:
            # A relative name.. could be a reference store only
            if fileobj is None:
                store, _ = self.valid_store_ref (resource)
                if store is not None:
                    stores = { store.get ('name') :  store}

        storeurl = lpath = None
        log.debug ("Trying mounts %s", stores.keys())
        for store_name, store in stores.items():
            try:
                storeurl, storepath, lpath = self._save_store (store, storepath, resource, fileobj, rooturl)
                break
            except IllegalOperation, e:
                log.debug ("failed %s store on %s with %s", storepath, store_name, e )
                storeurl = lpath = None
            except Exception:
                log.exception ("failed %s store on %s", storepath, store_name )
                storeurl = lpath = None
        log.debug('store_blob: %s at %s (%s)', storeurl, lpath, etree.tostring(resource))
        if storeurl is None:
            log.error ('storing %s failed (%s)', storepath, storeurl)

        return storeurl, store, storepath, lpath

    def _save_store(self, store, storepath, resource, fileobj=None, rooturl=None):
        'store the file to the named store'

        resource_name, sub  = split_subpath (resource.get ('name'))
        # Force a move into the store
        if fileobj:
            with  self._get_driver(store) as driver:
                if driver.readonly:
                    raise IllegalOperation('readonly store')

                storeurl = posixpath.join (driver.mount_url, storepath)
                log.debug('_save_store: %s from %s %s', storeurl, driver.mount_url, storepath)
                storeurl, localpath = driver.push (fileobj, storeurl, resource.get('resource_uniq'))

                # Store URL may be changed during driver push by disambiguation code.
                # revert change from changeset:2297 to always use storeurl
                #name = os.path.basename(resource_name) or tounicode(url2localpath(os.path.basename(storeurl)))
                name = tounicode(url2localpath(os.path.basename(storeurl)))
                resource.set('name', join_subpath(name, sub))
                resource.set('value', join_subpath(storeurl, sub))
                log.debug('_save_store: %s', etree.tostring(resource))
        else:
            # Try to reference the data in place (if on safe store)
            storeurl, localpath = self._save_storerefs (store, storepath, resource, rooturl)
            #Store  url may have changed due to conflict
            if resource.get ('value') is None: # This is multifile
                name = os.path.basename(resource_name)
            else:
                name = tounicode(url2localpath(os.path.basename(storeurl)))
            resource.set('name', join_subpath(name, sub))

        # Update the store path reference to similar to the storeurl
        storepath = storepath.split ('/')
        storepath[-1] = os.path.basename(storeurl)
        log.debug('_save_store: %s %s %s', storeurl, localpath, etree.tostring(resource))
        return storeurl, storepath, localpath

    def _save_storerefs(self, store, storepath, resource, rooturl):
        """store a resource with storeurls already in place.. these may be on a true store or simply reside locally
        due to local unpacking.

        @param store: a store resource
        @param storepath: a path on store where to put the resource
        @param resource: a resource with storeurls
        @param rooturl: the root of the storeurls
        """
        log.debug("_save_storerefs: %s, %s,  %s" , store, storepath,  rooturl)

        def setval(n, v):
            n.set('value', v)
        def settext(n, v):
            n.text = v

        with  self._get_driver(store) as driver:

            refs = resource.get ('value')
            if refs is not None:   # Single entity
                refs = [ (resource, setval, split_subpath(refs), storepath) ]
                rootpath = os.path.dirname(storepath) # dima: fix for stripping multi-file paths
            else:  # Multi-entity
                refs = [ (x, settext, split_subpath(x.text), None) for x in resource.xpath ('value') ]
                rootpath = storepath # dima: fix for stripping multi-file paths
            log.debug ("_save_storerefs refs: %s", list_summary(refs))

            #rootpath = os.path.dirname(storepath) # dima: fix for stripping multi-file paths

            # Determine a list of URL that need to be moved to a store (these were unpacked locally)
            # Assume the first URL is special and the others are related which can be used
            # to calculate storepath

            first = (None,None)
            movingrefs = []
            fixedrefs  = []
            for node, setter, (storeurl, subpath), storepath in refs:
                # dima: storeurl may be a relative url path
                if storeurl.startswith (driver.mount_url) or driver.valid(storeurl): # dima: if relative paths are stored
                    # Already valid on store (no move)
                    fixedrefs.append ( (node, setter, (storeurl, subpath), storepath))
                    continue
                # we deal with unpacked files below
                localpath = self._force_storeurl_local(storeurl)
                if os.path.isdir(localpath):
                    # Add a directory:
                    # dima: we should probably list and store all files but there might be overlaps with individual refs
                    movingrefs.extend ( (etree.SubElement(resource, 'value'), settext, (fpath, subpath), fpath[len(localpath):]) for fpath in blob_drivers.walk_deep(localpath))
                    #log.debug ("_save_storerefs if os.path.isdir(localpath): %s", movingrefs)
                elif os.path.exists(localpath):
                    if storepath is None:
                        storepath = posixpath.join(rootpath, storeurl[len(rooturl):])
                    movingrefs.append ( (node, setter, (localpath, subpath), storepath) )
                    #log.debug ("_save_storerefs elif os.path.exists(localpath): %s", movingrefs)
                else:
                    log.error ("_save_storerefs: Cannot access %s as %s of %s ", storeurl, localpath, etree.tostring(node))

            log.debug ("_save_storerefs movingrefs: %s", list_summary(movingrefs))
            log.debug ("_save_storerefs fixedrefs: %s", list_summary(fixedrefs))

            # I don't a single resource will have in places references and references that need to move
            if len(fixedrefs) and len(movingrefs):
                log.warn ("While storing refs: found inplace refs and moving refs in same resource %s", etree.tostring(resource))

            if len(fixedrefs):
                # retrieve storeurl, and  storepath yet
                first = (fixedrefs[0][2][0], fixedrefs[0][3])
                log.debug ("_save_storerefs fixed : %s", list_summary(fixedrefs))

            # References to a readonly store may be registered if no actual data movement takes place.
            if movingrefs and driver.readonly:
                raise IllegalOperation('readonly store')

            for node, setter, (localpath, subpath), storepath in movingrefs:
                with open (localpath, 'rb') as fobj:
                    storeurl = posixpath.join (driver.mount_url, storepath)
                    log.debug ("_save_store_refs: push %s", storeurl)
                    storeurl, localpath = driver.push (fobj, storeurl, resource.get ('resource_uniq'))
                    if first[0] is None:
                        first = (storeurl, localpath)
                    setter(node, join_subpath (storeurl, subpath))
            return first



    def _force_storeurl_local(self, storeurl):
        """User available drivers to fetch a local copy of the storeurl and return path
        @param storeurl: a valid storeurl
        @return : (A local fileyststem path, rootportion)  or None
        """
        # KGK: temporary simplification
        if storeurl.startswith ('file://'):
            return url2localpath(storeurl)
        return None

    def fetch_blob(self, resource, blocking):
        'return a (set) path(s) for a resource'
        log.debug ("fetch_blob %s", resource.get ('resource_uniq'))

        store,driver = self._find_store (resource)
        if  store is None:
            log.error ('Not a valid store ref in  %s' , etree.tostring (resource))
            return None

        with driver as driver:
            uniq     = resource.get('resource_uniq')
            bloburls = resource.get('value')
            if bloburls is not None:
                bloburls = [ bloburls ]
            else:
                bloburls  = [ x.text for x in resource.xpath('value') ]

            log.debug ("fetch_blob %s -> %s", resource.get ('resource_uniq'), bloburls)

            files = []
            sub = ''
            for storeurl in bloburls:
                localblob = driver.pull (storeurl, blocking=blocking)
                if localblob is None:
                    log.error ("Failed to fetch blob for %s of %s during pull %s", uniq, bloburls, storeurl)
                    return None
                sub = sub or localblob.sub
                if localblob.files:
                    files.extend(localblob.files)
                else:
                    files.append(localblob.path)
            if len(files) == 0:
                log.error ('fetch_blob: no files fetched for %s ', uniq)
                return None
            log.debug('fetch_blob for %s url=%s localpath=%s sub=%s', uniq, bloburls[0], files[0], sub)
            log.debug('fetch_blob %s', zip (bloburls, files))
            return blob_drivers.Blobs(files[0], sub, files)


    def delete_links(self, resource):
        'Delete link nodes   for a resource'
        log.debug ("delete_links %s", resource.get ('resource_uniq'))
        # Delete the reference in the store
        links = data_service.query ('link', parent=False, value = resource.get ('resource_uniq'), cache=False)
        for link in links:
            log.debug ("delete_blob: delete link %s", link.get('uri'))
            data_service.del_resource(link, check_acl=False, check_blob=False, check_references=False)


    def delete_blob(self, resource):
        'Delete elements  for a resource'
        log.debug ("delete_blob %s", resource.get ('resource_uniq'))

        self.delete_links(resource)

        store, driver = self._find_store (resource)
        if  store is None:
            log.warn ('Not a valid store ref in  %s' , etree.tostring (resource))
            return None

        if driver.readonly:
            log.warn ("Delete blob on readonly store.. skipping")
            return None

        with driver as driver:
            uniq     = resource.get('resource_uniq')
            bloburls = resource.get('value')
            if bloburls is None:
                bloburls  = [ x.text for x in resource.xpath('value') ]
            elif bloburls:
                bloburls = [ bloburls ]
            else:
                bloburls = []

            log.debug ("fetch_blob %s -> %s", resource.get ('resource_uniq'), bloburls)

            # If image has subimages then check for other subimage otherwise for image  itself.
            file_query, sub = split_subpath (bloburls[0])
            #if len(sub)>0:
            file_query = '%s*'%file_query

            # sanity check . ensure exactly one reference to store url before delete
            # Since storeurl can contain '#' marks for series files
            # What about directory URL.. this may match too many
            blobrefs = data_service.query(parent=False, value=file_query, cache=False)

            if len(blobrefs) < 2:
                for storeurl in bloburls:
                    driver.delete (storeurl)
            else:
                log.warn ("blob delete skipped >2 refs %s", str(blobrefs))


    def _find_store(self, resource):
        """return a store(mount)  by the resource

        case 1: Anonymous user:  resource must be published
        case 2: User == resource owner : should be one of the users stores
        case 3: User != resource owner : user has read permission

        We has N store prefix and we want to find the longest match for the target string (searchurl)
        """
        #  This should have been checked before we ever get here:
        #  Currently all service check accessibility before arriving here.
        #  so we can simply find the store using the resource's owner.

        # identity functions need to either accept URI we should move to using UNIQ codes for all embedded URI
        # i.e. <image uniq="00-AAA" owner="00-CCC" ../>
        owner_uri = resource.get('owner')
        owner = load_uri (owner_uri)

        # Is this enough context? Should the whole operation be carried out as the user or just the store lookup?
        with identity.as_user(owner):
            store, driver = self.valid_store_ref (resource)
        return store, driver

    def _get_stores(self):
        "Return an OrderedDict of store resources in the users ordering"

        #root = self._create_root_mount()
        root = self._load_root_mount()
        store_order = get_tag (root, 'order')
        if store_order is None:
            store_order = config.get('bisque.blob_service.stores','')
        else:
            store_order = store_order[0].get ('value')

        log.debug ("using store order %s", store_order)
        stores = OrderedDict()
        for store_name in (x.strip() for x in store_order.split(',')):
            store_el = root.xpath('./store[@name="%s"]' % store_name)
            if not store_el or len(store_el) > 1:
                log.warn ("store %s does not exist in %s", store_name, etree.tostring(root))
                continue
            store = store_el[0]
            stores[store_name] = store
            log.debug ("adding store '%s' at %s", store_name, len(stores))
        return stores

    def get_store_opts(self, store):
        "Create a  driver  for the user store"
        store_name = store.get ('name')
        if store_name not in self.drivers:
            raise IllegalOperation ('invalid store %s:  not in available stores %s' % (store_name , self.drivers.keys()))

        driver_opts = dict(self.drivers.get (store_name))

        # Replace any default driver opts with tags
        storetags = store.xpath('tag')
        driver_opts.update ( (x.get ('name'), x.get ('value')) for x in storetags )

        log.debug ("after store tags %s" , driver_opts)
        if not driver_opts.get ('credentials'):
            driver_opts['credentials']=''

        driver_opts['path'] = mount_path = store.get ('value')
        driver_opts['mount_url' ] = mount_path
        return driver_opts

    def _get_driver(self, store):
        store_name = store.get ('name')
        driver_opts = self.get_store_opts(store)
        mount_path = driver_opts['path']
        if mount_path is None:
            raise IllegalOperation ("BAD STORE FOUND %s %s" % ( store_name, driver_opts))


        # get a driver to use
        #KGK : maybe use a timeout cache here so the connection can be reused?
        log.debug ('making store driver %s: %s', store_name, driver_opts)
        try:
            driver = blob_drivers.make_storage_driver(**driver_opts)
            return driver
        except Exception:
            log.exception ("While creating driver %s", driver_opts)
        return None


    ##############################
    # services for mounts

    def _create_full_path(self, store, path, resource_uniq=None, resource_name=None, count=1, **kw):
        """Create the full path relative to store
        @param store: a string name or etreeElement
        @param path: a path relative to the store
        @param resource_uniq: optional resource to be placed
        @param resource_name: options name of resource
        """

        if isinstance (path, basestring):
            path = path.split ('/')
        path = list (path)
        root = None
        log.debug ("CREATE_PATH %s %s", store, path)
        if isinstance(store, basestring):
            resource = root = etree.Element ('store', name = store, resource_unid = store)
            store = self._load_root_mount()

        # Scan path for all existing directories and possible existing filelink
        parent = store
        while parent is not None and path:
            el = path.pop(0)
            if not el:
                continue
            #q  = data_service.query(parent=parent, resource_unid=el, view='full', cache=False)
            q  = data_service.query(parent=parent, resource_unid=el, view='short', cache=False)
            if len(q) == 0:
                # no element we are done
                path.insert(0, el)
                break
            if len(q) > 1:
                log.error ('multiple names (%s) in store level %s', el, q.get('uri'))
                #path.insert(0, el)
                parent = q[0]
                return None
                #break # return Fail?
            # len(q) == 1 .. we have a result .. just keep searching down the path
            parent2 = parent
            parent = q[0]
        # directories do not exists len(path) > 1
        # directories exist but filelink does not len(path) == 1
        # directories and filelink exists len(path) == 0

        log.debug ("create: at %s rest %s", (parent is not None) and parent.get ('uri'), path)
        while len(path)>1:
            # any left over path needs to be created
            nm = path.pop(0)
            if root is None:
                resource = root = etree.Element ('dir', name=nm, resource_unid = nm)
            else:
                resource = etree.SubElement (resource, 'dir', name=nm, resource_unid=nm)
        # The last element might be dir or a link
        if len(path)==1:
            nm = resource_name or path.pop(0)
            #nm = path.pop(0)
            if root is None:
                resource = root = etree.Element ('link' if resource_uniq else 'dir', name=nm, resource_unid = nm)
            else:
                resource = etree.SubElement (resource, 'link' if resource_uniq else 'dir', name=nm, resource_unid=nm)

            if resource_uniq:
                resource.set ('value', resource_uniq)
            # create the new resource
            log.debug ("New resource %s at %s " , etree.tostring(root), (parent is not None) and parent.get ('uri'))
            q = data_service.new_resource(resource=root, parent=parent, flush=False)
        elif len(path) == 0:
            log.warn ("NAME conflict? %s %s", resource_name, count)
            # Conflict in link name?  Possible when mutltfile name has not be disambiguated by underlying filesystem
            nm = "%s-%s" % (resource_name, count)
            if root is None:
                resource = root = etree.Element ('link' if resource_uniq else 'dir', name=nm, resource_unid = nm)
            else:
                resource = etree.SubElement (resource, 'link' if resource_uniq else 'dir', name=nm, resource_unid=nm)
            if resource_uniq:
                resource.set ('value', resource_uniq)
            q = data_service.new_resource(resource=root, parent=parent2, flush=False)

        return q



    def _insert_mount_path(self, store, mount_path, resource, count, **kw):
        """ insert a store path into the store resource

        This will create a store element if does not exist
        :param path: a blob path for the store
        """
        log.info("Insert_mount_path %s(%s) create %s path %s ", resource.get('name'), resource.get('uniq'), str(store), str(mount_path))

        return self._create_full_path(store, mount_path, resource.get ('resource_uniq'), resource.get('name'), count, **kw)


    def insert_mount_path(self, store, mount_path, resource, **kw):
        subtrans = None
        repeats = 2
        if self.subtransactions:
            repeats = 8
            #pylint: disable=no-member
            subtrans = DBSession.begin_nested
        for x in range(1, repeats+1):
            try:
                with optional_cm(subtrans):
                    value =  self._insert_mount_path (store, mount_path, resource, count=x, **kw)
                log.debug ("Inserted path %s -> %s", mount_path, value)
                return value
            except IntegrityError:
                log.exception ('Integrity Error caught on attempt %s.. retrying %s', x, mount_path)

        log.error('StoreError: tried too many attempts %s.. not inserting %s', x, mount_path)
        return None
