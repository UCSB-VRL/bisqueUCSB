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

    RESTful resource with caching

"""
from __future__ import with_statement
import os
import re
#import md5
import hashlib
import logging
import tempfile

from urlparse import urlparse
from datetime import datetime
from time import gmtime, strptime

from pylons.controllers.util import abort

import tg
from tg import  expose
from tg.util import Bunch
from tg.configuration import  config
#from tg.controllers import CUSTOM_CONTENT_TYPE

from bq.core import identity
from bq.core.service import ServiceController
#from bq.exceptions import RequestError
from bq.util.paths import data_path
from bq.util.converters import asbool
#from bq.util.copylink import copy_link
from bq.util.io_misc import dolink
#from bq.util.xmldict import d2xml
from .formats import find_inputer, find_formatter

log = logging.getLogger("bq.data_service.resource")

CACHING  = asbool(config.get ('bisque.data_service.caching', True))
ETAGS    = asbool(config.get ('bisque.data_service.etags', True))
#SERVER_CACHE = asbool(config.get('bisque.data_service.server_cache', True))
CACHEDIR = config.get ('bisque.data_service.server_cache', data_path('server_cache'))

URI = re.compile(r"^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?")

def parse_uri(uri):
    """Parses a URI using the regex given in Appendix B of RFC 3986.

        (scheme, authority, path, query, fragment) = parse_uri(uri)
    """
    groups = URI.match(uri).groups()
    return (groups[1], groups[3], groups[4], groups[6], groups[8])

def urlnorm(uri):

    (scheme, authority, path, params, query, fragment) = urlparse(uri)
    #(scheme, authority, path, query, fragment) = parse_uri(uri)
    #if not scheme or not authority:
    #    raise RequestError("Only absolute URIs are allowed. uri = %s" % uri)
    authority = authority and authority.lower() or ""
    scheme = scheme and scheme.lower() or ""
    path = path or "/"

    # Put special queries first for invalidations"
    ql = query.split('&')
    for qi in ql:
        for qn in [ 'tag_values', 'tag_query', 'tag_names', 'gob_types']:
            if qi.startswith(qn):
                # move it to the front
                ql.insert(0, ql.pop(ql.index(qi)))
                break
    query = "&".join(ql)

    # Could do syntax based normalization of the URI before
    # computing the digest. See Section 6.2.2 of Std 66.
    request_uri = query and "?".join([path, query]) or path
    #request_uri = path
    scheme = scheme.lower()
    #defrag_uri = scheme + "://" + authority + request_uri
    defrag_uri = request_uri
    return scheme, authority, request_uri, defrag_uri


# Cache filename construction (original borrowed from Venus http://intertwingly.net/code/venus/)
re_url_scheme    = re.compile(r'^\w+://')
#re_slash         = re.compile(r'[?/:|]+')
re_slash         = re.compile(r'[/\:|]+')
re_reserved      = re.compile(r'[<>"*]+')

def safename(filename, user):
    """Return a filename suitable for the cache.

    Strips dangerous and common characters to create a filename we
    can use to store the cache in.
    """

    try:
        if re_url_scheme.match(filename):
            if isinstance(filename,str):
                filename = filename.decode('utf-8')
                filename = filename.encode('ascii', 'xmlcharrefreplace')
            else:
                filename = filename.encode('ascii', 'xmlcharrefreplace')
    except UnicodeError:
        pass
    if isinstance(filename,unicode):
        filename=filename.encode('utf-8')
    #filemd5 = md5.new(filename).hexdigest()
    filename = re_url_scheme.sub("", filename)
    filename = re_slash.sub(",", filename)
    filename = re_reserved.sub('-', filename)
    # This one is special to create cachenames that args can be seperate from requested path
    filename = filename.replace('?', '#')

    # limit length of filename
    if len(filename)>200:
        filename=filename[:200]
    if user is None: user = 0
    #return ",".join((str(user), filename, filemd5))
    return ",".join((str(user), filename))



def force_load(resource):
    "Force the loading the of resource from the database"

    from sqlalchemy.orm import Query
    from bq.data_service.model import Taggable
    if isinstance(resource, tuple):
        parent = getattr(tg.request.bisque,'parent', None)
        #log.debug ("invalidate: tuple using %s", parent) #provokes logging error
        if parent:
            resource = parent
            #log.debug ("CACHE parent %s", parent)
        else:
            # The a pure form i.e. /data_service/[image] with a POST
            if resource[0] == 'resource':
                # special case for POST to /data_service.. resource type is unknown so remove all
                resource = ('', resource[1])
            resource = Bunch(resource_uniq = None, resource_type = resource [0], permission="published")
    if isinstance(resource, Query):
        resource = resource.first() #pylint: disable=no-member
    if isinstance(resource, Taggable):
        resource = resource.document #pylint: disable=no-member
    return resource

def modified_resource(resource):
    #cachename = os.path.join(self.cachepath, self._cache_name(url, user))

    log.debug ("modified %s" ,  str(resource))
    resource = force_load(resource)
    if hasattr(resource, 'ts'):
        return resource.ts # pylint: disable=no-member
    return None

def etag_resource(resource):
    mtime =  modified_resource(resource)
    log.debug ('etag_resource %s', mtime)
    if mtime:
        # pylint: disable=E1103
        return hashlib.md5 (str(mtime)).hexdigest()
        # pylint: enable=E1103
    return None



class BaseCache(object):
    def fetch(self, url, user):
        return None, None
    def save(self, url, header, value, user):
        pass
    def invalidate(self, url, user, files=None):
        pass
    def invalidate_resource(self, resource, user):
        pass
    def modified(self, url, user):
        return None
    def etag (self, url, user):
        return None
    def modified_resource(self, resource):
        return getattr (resource, 'ts', None)
    def etag_resource (self, resource):
        return getattr (resource, 'ts', None)


class ResponseCache(BaseCache):
    known_headers = [ 'Content-Length', 'Content-Type' ]

    def __init__(self, cachepath):
        "create the local cache"
        self.cachepath  = cachepath
    def _setup (self):
        if not os.path.exists(self.cachepath):
            os.makedirs (self.cachepath)
        return self

    def _cache_name (self, url, user):
        scheme, authority, request_uri, defrag_uri = urlnorm(url)
        return safename ( defrag_uri, user ).replace(',data_service','').replace(',,',',').replace(',#','#')

    def _resource_cache_names(self, resource, user):
        names = [ "%s,%s" % (user if user else '',  resource.resource_uniq if resource else '') ]
        if resource and resource.permission == 'published':
            names.append ( '0,%s' % resource.resource_uniq if resource else '' )
        return names
    def _resource_query_names(self, resource, user, *args):
        resource_type = getattr(resource, 'resource_type', None) or (isinstance (resource, basestring) and resource) or ''
        base = "%s,%s" % (user if user else '', resource_type)
        top = "%s#" % (user if user else 0)
        return [ top, base ] + [ "#".join ([base, arg]) for arg in args ]

    def save(self, url, headers, value, user):
        cachename = os.path.join(self.cachepath, self._cache_name(url, user))
	if ",value" in cachename:
	    log.debug (u'NO NO NOcache write %s to %s', url, cachename)
	    return
        headers = dict ([ (k,v) for k,v in headers.items() if k in self.known_headers])
        log.debug (u'cache write %s to %s', url, cachename )
        clen = headers.get ('Content-Length', None)
        if not clen or clen=='0':
            headers['Content-Length'] = str (len (value))
        try:
            with tempfile.NamedTemporaryFile (dir=os.path.dirname(cachename), delete=False) as f:
                f.write (str (headers))
                f.write ('\n\n')
                f.write (value)
                #copy_link (f.name, cachename)
                if os.name == 'nt':
                    os.remove (cachename)
                os.rename (f.name, cachename)
                #dolink (f.name, cachename)

        except (OSError, IOError) as e:
            if os.name == 'nt':
                log.debug ("problem in cache save of %s", cachename)
            else:
                log.exception ("problem in cache save of %s", cachename)

    def fetch(self, url,user):
        #log.debug ('cache fetch %s' % url)
        try:
            cachename = os.path.join(self.cachepath, self._cache_name(url, user))
            log.debug (u'cache check %s', cachename)
            if os.path.exists (cachename):
                with open(cachename) as f:
                    headers, cached = f.read().split ('\n\n', 1)
                    log.debug (u'cache fetch serviced %s', url)
                    headers = eval (headers)
                    return headers, cached
        except ValueError,e:
            pass
        except IOError, e:
            pass
        return None, None

    def invalidate(self, url, user, files = None, exact=False):
        if not files:
            files = os.listdir(self.cachepath)
        # Skip parameters in invalidate
        if '?' in url:
            url = url.split('?',1)[0]
        cachename = self._cache_name(url, user)
        log.debug ('cache invalidate ( %s )' , cachename )
        if exact:
            # current cache names file-system safe versions of urls
            # /data_service/images/1?view=deep
            #   =>  ,data_service/images,1#view=deep
            # ',' can be troublesome at ends so we remove them
            #     ,data_service/images,1#view=deep == ,data_service/images,1,#view=deep
            try:
                cachename = cachename.split('#',1)[0].split(',',1)[1].strip(',')
                tfiles = [ (fn.split('#',1)[0].split(',',1)[1].strip(','), fn) for fn in files ]
            except Exception:
                log.exception ("while generating %s in with %s", cachename, files)
                return

            for mn, cf in tfiles:
                #log.debug('exact %s <> %s' % (cachename, mn))

                if mn == cachename:
                    try:
                        os.unlink (os.path.join(self.cachepath, cf))
                    except OSError:
                        # File was removed by other process
                        pass
                    files.remove (cf)
                    log.debug ('cache exact remove %s' % cf)
            return
        for cf in files[:]:
            #log.debug ("checking %s" % cf)
            try:
                #
                if (cachename.startswith('*') and cf.split(',',1)[-1].startswith(cachename.split(',',1)[-1]))\
                    or cf.startswith (cachename):
                    try:
                        os.unlink (os.path.join(self.cachepath, cf))
                    except OSError:
                        # File was removed by other process
                        pass
                    files.remove (cf)
                    log.debug ('cache remove %s' % cf)
            except Exception, e:
                log.exception ("while removing %s from %s", cf, files)

    def modified(self, url, user):
        cachename = os.path.join(self.cachepath, self._cache_name(url, user))
        if os.path.exists(cachename):
            return datetime.utcfromtimestamp(os.stat(cachename).st_mtime)
        return None

    def etag (self, url, user):
        mtime =  self.modified(url, user)
        if mtime:
            cachename = os.path.join(self.cachepath, self._cache_name(url, user))
            # pylint: disable=E1103
            return hashlib.md5 (str(mtime) + cachename).hexdigest()
            # pylint: enable=E1103
        return None

    def modified_resource(self, resource):
        return modified_resource (resource)
    def etag_resource (self, resource):
        return etag_resource (resource)



class HierarchicalCache(ResponseCache):
    """Specialized Cache that auto-invalidates parent elements of URL
    """
    def invalidate(self, url, user, files=None):
        """Invalidate the URL element and all above it until you hit a collection
        for example:
           invalidate /ds/images/1/gobjects/2  will invalidate both
           /ds/images/1/gobjects/2 and /ds/images/1/gobjects

           This is overkill as we do not need to invalidate
             /ds/images/1/gobjects/3
        """
        log.debug ("CACHE invalidate %s for %s " ,url , user)
        files = os.listdir(self.cachepath)
        (scheme, authority, path, query, fragment) = parse_uri(url)
        splitpath = path.split('/')
        # Delete the special queries that may change at any time
        # Will not work for public images used by other users
        # Should probably delete all users cached values but seems
        # like overkill
        scheme = scheme or 'http'
        authority = authority or 'localhost'
        for special in ('tag_names', 'tag_values'):
            super(HierarchicalCache, self).invalidate(''.join([scheme, "://",
                                                               authority,
                                                               '/data_service/image/',
                                                               special]),
                                         '*',files)
        object_found = False
        #  Delete all cached for the URL
        #  Delete exact matches if URL url is
        #
        path = '/'.join(splitpath[:4])
        request_uri = query and "?".join([path, query]) or path
        super(HierarchicalCache, self).invalidate (
            ''.join([scheme, "://" , authority , request_uri]),
            '*', files,exact= False )

        # Delete all top level caches without regard to parameter
        # but not recursively (would be alot )
        path = '/'.join(splitpath[:3])
        request_uri = query and "?".join([path, query]) or path
        super(HierarchicalCache, self).invalidate (
            ''.join([scheme, "://" , authority , request_uri]),
            '*', files,exact=True )
        # while splitpath:
        #     path = '/'.join(splitpath)
        #     request_uri = query and "?".join([path, query]) or path
        #     super(HierarchicalCache, self).invalidate (''.join([scheme, "://" , authority , request_uri]),
        #                                                user, files)
        #     pid = splitpath.pop()
        #     # Specifically for /ds/dataset/XX/tag/XX/values that apear
        #     # to act like full queries..
        #     if pid == 'values': continue
        #     # Not an integer token..so stop
        #     # Has the effect of stopping on the next highest container.
        #     #if pid and pid[0] in string.ascii_letters:
        #     #    break
        #     # The above was had error when modifing tags or gobjects
        #     # and then fetching a view deep on a top level object i.e
        #     # POST /data_service/images/2/gobjects/
        #     # then GET /data_service/images/2?view=deep
        #     # we are seeing a container
        #     # if numeric then break
        #     if pid and pid[0] not in string.ascii_letters:
        #         break
        #     # Current code just deletes all up until the top level object.
        #     # Could be made better by deletes all view=deeps ?
        #     #if len(splitpath) <=3:
        #     #    break


    def invalidate_resource(self, resource, user):
        """ Invalidate cached files and queries for a resource

        A resource can sqlalchemy query, Taggable, or a resource_type tuple


        # a simple resource invalidates:
           1.  The resource document and any subdocuments
                  USER,00-UNIQ....
           2.  Any query associated with  resource_type
                  USER, TYPE#....
           3.  Queries accross multiple resource types
                  USER,*#
           if published then delete all public queries
        """
        resource = force_load(resource)
        while  resource and not hasattr (resource, 'resource_uniq'):
            log.warn ("invalidate: Cannot determine resource %s",  resource)
            resource = resource.parent
            #return
        #pylint: disable=no-member
        log.debug ("CACHE invalidate: resource %s user %s", resource and resource.resource_uniq, user)

        files = os.listdir(self.cachepath)
        cache_names = self._resource_cache_names(resource, user)
        query_names = self._resource_query_names(resource, user, 'tag_values', 'tag_query', 'tag_names', 'gob_types')
        # Datasets are in the form USER,UNIQ#extract so build a special list
        # invalidate cached resource varients
        def delete_matches (files, names, mangle = lambda x:x):
            for f in list(files):
                #cf = f.split(',',1)[-1] if user is None else f
                cf = mangle (f)
                if any ( cf.startswith(mangle (qn)) for qn in names ):
                    try:
                        os.unlink (os.path.join(self.cachepath, f))
                    except OSError:
                        # File was removed by other process
                        pass
                    files.remove (f)
                    log.debug ('cache  remove %s' ,  f)

        names  = list( cache_names )
        names.extend (query_names)
        #names.extend (dataset_names)
        log.debug ("CACHE invalidate %s for %s %s" , resource and resource.resource_uniq , user, names)
        # Delete user matches
        try:
            log.debug ('cache delete for user')
            #delete_matches ( files, names)  Since True below will catch all these just skip this step.
            # Split off user and remove global queries
            # NOTE: we may only need to do this when resource invalidated was "published"
            # # value queries of shared datasets are a problem
            if True: # resource.permission == 'published':
                log.debug ('cache delete for all')
                #names = [ qnames.split(',',1)[-1] for qnames in names]
                delete_matches (files, names, lambda x: x.split(',', 1)[-1])
                log.debug ("cache delete extract ", )
                delete_matches (files, [ "#extract" ], lambda x: x.split ('#', 1)[-1])
        except Exception:
            log.exception ("Problem while deleting files")



def parse_http_date(timestamp_string):

    if timestamp_string is None: return None
    timestamp_string = timestamp_string.split(';')[0]    # http://stackoverflow.com/questions/12626699/if-modified-since-http-header-passed-by-ie9-includes-length
    test = timestamp_string[3]
    if test == ',':
        format = "%a, %d %b %Y %H:%M:%S %Z"
    elif test == ' ':
        format = "%a %d %b %H:%M:%S %Y"
    else:
        format = "%A, %d-%b-%y %H:%M:%S %Z"
    return datetime(*strptime(timestamp_string, format)[:6])


class Resource(ServiceController):
    '''
    Base class to create a REST like resource for turbogears:

    Addresses are of the form::

      /Resource
      /Resource/#ID
      /Resource/#ID[/ChildResource/#ID]*

    Operations::

      Target    METHOD: Descritption  method on resource object
      ../Resource : Collection
                GET   : list elements -> dir
                POST  : add an element to resource -> new(factory, doc)
                PUT   : replace all elements given -> replace_all(resource, doc)
                DELETE: delete all elements denoted -> delete_all(resource)

      Examples::
             /ds/images
                  GET : list all element of images
                  POST: create a new image
                        <request>
                          <image x='100' y='100' />
                          ...
             /ds/images/1/tags
                  PUT : replace tag collection of image 1 with
                        <request>
                           <tag name="param" />
                           ...
                  DELETE : delete collection of tags

      ../Resource/#ID : Element ::
                GET   : get value     -> get (resource)
                POST  : add element to resource -> append(resource, doc)
                /ds/images/1
                       <request>
                          <tag name = "" />
                          ...
                      or update the image element permission attribute
                       <request >
                         <image uri="/ds/images/1" perm="0" />

                PUT   : modify value  -> modify (resource, doc)
                DELETE: delete resource -> delete(resource)

      kw['xml_body'] will have the xml_body if available.

    '''
    service_type = "resource"
    cache = False
    children = {}
    # class level so are shared by all instances
    server_cache = BaseCache()
    hier_cache   = HierarchicalCache(CACHEDIR)

    def __init__(self, cache=True, **kw):
        super(Resource,self).__init__(**kw)

#         error_function = getattr(self.__class__, 'error', None)
#         if error_function is not None:
#             #If this class defines an error handling method (self.error),
#             #then we should decorate our methods with the TG error_handler.
#             self.get = error_handler(error_function)(self.get)
        log.debug ("Resource()")
        if cache and self.cache == True:
            log.debug ("using CACHE")
            self.server_cache = self.hier_cache._setup()

#             self.modify = error_handler(error_function)(self.modify)
#             self.new = error_handler(error_function)(self.new)
#             self.append = error_handler(error_function)(self.append)
#             self.delete = error_handler(error_function)(self.delete)

    @classmethod
    def get_child_resource(cls, token):
        return cls.children.get(token, None)


    def check_cache_header(self, method, resource):
        #if not CACHING: return

        if ETAGS:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-None-Match
            # GET/HEAD check if client-side stale resource has changed.
            # PUT : only with * -> only if entity does not exist
            #if 'If-None-Match' in tg.request.headers:
            htag = tg.request.headers.get('If-None-Match', None)
            if htag is not None and method in ('get', 'head'):
                etag = self.get_entity_tag(resource)
                if etag is not None and etag == htag:
                    abort(304)
                return

            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/If-Match
            # GET, HEAD return resource  if etag  is still valid
            # Others: apply operation only if matches
            #if 'If-Match' in tg.request.headers:
            htag = tg.request.headers.get('If-Match', None)
            if htag is not None:
                etag = self.get_entity_tag(resource)
                log.debug ("IFMATCH %s = %s", htag, etag)
                if etag is not None and etag != htag:
                    abort(412) # precondtion failed
                return

        # Https://Developer.Mozilla.Org/en-US/docs/Web/HTTP/Headers/If-Modified-Since
        # GET,HEAD only
        #if 'If-Modified-Since' in tg.request.headers:
        modified_check = tg.request.headers.get('If-Modified-Since', None)
        if modified_check is not None and method in ('get', 'head'):
            modified_check = parse_http_date(modified_check)
            last_modified = self.get_last_modified_date(resource)
            if last_modified is not None:
                if last_modified <= modified_check:
                    log.debug('Document still valid')
                    abort(304)

    def add_cache_header(self, resource):
        #if not CACHING: return

        if ETAGS:
            etag = self.get_entity_tag(resource)
            if etag:
                tg.response.headers['ETag'] = etag
            return

        last_modified = self.get_last_modified_date(resource)
        #logger.debug('response: ' + str(last_modified))
        #if last_modified is  None:
            #tg.response.headers['Cache-Control'] = 'public, max-age=1'
            #last_modified = datetime(*gmtime()[:6])
        if last_modified is not None:
            tg.response.headers['Last-Modified'] = (
                datetime.strftime(last_modified, "%a, %d %b %Y %H:%M:%S GMT"))

    def invalidate(self, url):
        self.server_cache.invalidate(url, user=identity.get_user_id())

    def invalidate_resource(self, resource):
        self.server_cache.invalidate_resource(resource, user=identity.get_user_id())


    @expose()
    def _default(self, *path, **kw):
        request = tg.request
        response = tg.response
        path = list(path)
        resource = None
        if not hasattr(request, 'bisque'):
            bisque = Bunch()
            request.bisque = bisque
        bisque = request.bisque
        user_id  = identity.get_user_id()
        usecache = asbool(kw.pop('cache', True))
        http_method = request.method.lower()
        log.debug ('Request "%s" with %s?%s' , http_method, request.path,str(kw))
        #log.debug ('Request "%s" ', path)

        #check the http method is supported.
        try:
            method_name = dict(get='get', head='check', post='append',
                               put='modify', delete='delete')[http_method]
        except KeyError:
            abort(501)


        if not path: #If the request path is to a collection.
            #self.check_cache_header(http_method, resource)
            if http_method == 'post':
                #If the method is a post, we call self.create which returns
                #a class which is passed into the self.new method.
                resource = self.create(**kw)
                assert resource is not None
                method_name = 'new'
            elif http_method == 'get':

                resource = getattr(request.bisque,'parent', None)
                method_name = 'dir'
                # if parent:
                #     self.check_cache_header (http_method, parent)

                # #If the method is a get, call the self.index method, which
                # #should list the contents of the collection.
                # accept_header = headers = value = None
                # if usecache:
                #     headers, value = self.server_cache.fetch(request.url, user=user_id)
                #     if headers:
                #         _, accept_header = find_formatter (accept_header=request.headers.get ('accept'))
                #         content_type  = headers.get ('Content-Type')

                # if value and accept_header == content_type:
                #     response.headers.update(headers) # cherrypy.response.headers.update (headers)
                # else:
                #     #self.add_cache_header(None)
                #     value =  self.dir(**kw)
                #     self.server_cache.save (request.url,
                #                             response.headers,
                #                             value, user=user_id)
                # #self.add_cache_header(resource)
                # return value
            elif http_method == 'put':
                resource = getattr(bisque,'parent', None)
                method_name = 'replace_all'
            elif http_method == 'delete':
                resource = getattr(bisque,'parent', None)
                method_name = 'delete_all'
            elif http_method == 'head':
                # Determine whether the collection has changed
                resource = getattr(bisque,'parent', None)
                method_name = "check"
            else:
                #Any other methods get rejected.
                abort(501)

        if resource is None and method_name != 'dir':
            #if we don't have a resource by now, (it wasn't created)
            #then try and load one.
            if path:
                token = path.pop(0)
                resource = self.load(token)
            if resource is None:
                #No resource found?
                if user_id is None:
                    abort(401)
                abort(404)

        #if we have a path, check if the first token matches this
        #classes children.
        if path:
            token = path.pop(0)
            log.debug('Token: ' + str(token))
            child = self.get_child_resource(token)
            if child is not None:
                bisque.parent = resource
                log.debug ("parent = %s" , str(resource))
                #call down into the child resource.
                return child._default(*path, **kw)

#        if http_method == 'get':
#            #if this resource has children, make sure it has a '/'
#            #on the end of the URL
#            if getattr(self, 'children', None) is not None:
#                if request.path[-1:] != '/':
#                    redirect(request.path + "/")



        #resource = self.server_cache.force_load(resource)
        self.check_cache_header(http_method, resource)
        method = getattr(self, method_name)
        #pylons.response.headers['Content-Type'] = 'text/xml'
        log.debug ("Dispatch for %s", method_name)
        try:
            if http_method in ('post', 'put'):
                clen = int(request.headers.get('Content-Length', 0))
                content_type = request.headers.get('Content-Type')

                inputer = find_inputer (content_type)
                if not inputer:
                    log.debug ("Bad media type in post/put:%s" ,  content_type)
                    abort(415, "Bad media type in post/put:%s" % content_type )

                # xml arg is for backward compat
                value = method (resource, xml=inputer(request.body_file, clen), **kw)

                # if content.startswith('text/xml') or \
                #        content.startswith('application/xml'):
                #     data = request.body_file.read(clen)
                #     #log.debug('POST '+ data)
                #     #kw['xml_text'] = data
                #     value = method(resource, xml=data, **kw)
                # elif content.startswith("application/json"):
                #     try:
                #         #data = request.body_file.read(clen)
                #         data = d2xml (json.load (request.body_file))
                #         value = method(resource, xml=data, **kw)
                #     except Exception as e:
                #         log.exception ("while reading json content")
                #         abort(415, "Bad media type in post/put:%s" % content )
                # else:
                #     #response = method(resource, doc = None, **kw)
                #     # Raise illegal operation (you should provide XML)
                #     log.debug ("Bad media type in post/put:%s" ,  content)
                #     abort(415, "Bad media type in post/put:%s" % content )
                # #self.server_cache.invalidate(request.url, user=user_id)
                self.server_cache.invalidate_resource(resource, user=user_id)
            elif http_method == 'delete':
                self.server_cache.invalidate_resource(resource, user=user_id)
                value = method(resource, **kw)
                #self.server_cache.invalidate(request.url, user=user_id)
            elif  http_method == 'get':
                accept_header = headers = value = None
                if usecache:
                    headers, value = self.server_cache.fetch(request.url, user=user_id)
                    if headers:
                        content_type  = headers.get ('Content-Type')
                        _, accept_header = find_formatter (accept_header=request.headers.get ('accept'))
                if value and accept_header == content_type:
                    response.headers.update (headers)
                    return value
                else:
                    #run the requested method, passing it the resource
                    value = method(resource, **kw)
                    # SET content length?
                    self.server_cache.save (request.url,
                                            response.headers,
                                            value, user=user_id)
                    self.add_cache_header(resource)
            else: # http_method == HEAD
                value = method(resource, **kw)

            #set the last modified date header for the response
            return value

        except identity.BQIdentityException:
            response.status_int = 401
            return "<response>FAIL</response>"


    def get_entity_tag(self, resource):
        """
        returns the Etag for the collection (resource=None) or the resource
        """
        #log.debug ("ETAG: %s " %tg.request.url)
        if self.cache:
            etag =  self.server_cache.etag_resource (resource)
            #etag =  self.server_cache.etag (tg.request.url, identity.get_user_id())
            return etag
        return etag_resource (resource)
        #return None
    def get_last_modified_date(self, resource):
        """
        returns the last modified date of the resource.
        """
        #log.debug ("CHECK MODFIED: %s " %tg.request.url)

        if self.cache:
            #return self.server_cache.modified (tg.request.url, identity.get_user_id())
            return self.server_cache.modified_resource (resource)
        return modified_resource (resource)
        #return None

    def dir(self, resource, **kw):
        """
        returns the representation of a collection of resources.
        """
        raise abort(403)

    def load(self, token):
        """
        loads and returns a resource identified by the token.
        """
        return None

    def create(self, **kw):
        """
        returns a class or function which will be passed into the self.new
        method.
        """
        raise abort(501)

    def new(self, resource_factory, xml, **kw):
        """
        uses resources factory to create a resource, commit it to the
        database.
        """
        raise abort(501)

    def modify(self, resource, xml, **kw):
        """
        Modify the resource in place replace the value
        uses kw to modifiy the resource.
        """
        raise abort(501)

    def get(self, resource, **kw):
        """
        fetches the resource, and returns a representation of the resource.
        """
        raise abort(501)
    def append(self, resource, xml, **kw):
        """
        Append value to resource
        """
        raise abort(501)
    def delete(self, resource,  **kw):
        """
        Delete the resource from the database
        """
        raise abort(501)

    def check(self, resource,  **kw):
        """
        Check that you can read the object
        """
        abort(501)
