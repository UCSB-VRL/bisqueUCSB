import os
import logging
from paste.fileapp import FileApp
from paste.httpheaders import ETAG #pylint: disable=no-name-in-module
from paste.httpexceptions import HTTPNotFound




log = logging.getLogger("bq.core.statics")

class BQStaticURLParser (object):
    def __init__(self):
        self.files = {}

    def add_path(self, top, local, prefix=None):
        """add a set of files to static file server

        @param top: a portion of the filepath to be removed from the web path
        @param local: the  directory path to be served
        @param prefix:
        """
        log.info('static path %s -> %s' % (local, top))
        for root, dirs, files in os.walk(local, followlinks=True):
            for f in files:
                pathname = os.path.join(root,f)
                partpath = pathname[len(local):]
                if prefix:
                    #print "PREFIX: ", prefix
                    partpath  = os.path.join(prefix, partpath[1:])

                partpath = partpath.replace('\\', '/')
                if partpath in self.files:
                    log.error("static files : %s will overwrite previous %s "
                              % (pathname, self.files[partpath]))
                    continue
                #log.debug(  "ADDING %s -> %s " % (partpath, pathname) )
                self.files[partpath] = (pathname, None)
        #log.debug ("Added statics %s", self.files.keys())


    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']
        #log.debug ('static search for %s' % path_info)
        if path_info in self.files:
            path, app = self.files.get(path_info)
            if not app:
                app = FileApp (path).cache_control (max_age=60*60*24*7*6) #6 weeks
                self.files[path_info] = (path, app)
            log.info ( "STATIC REQ %s" %  path_info)
            if_none_match = environ.get('HTTP_IF_NONE_MATCH')
            if if_none_match:
                mytime = os.stat(path).st_mtime
                if str(mytime) == if_none_match:
                    headers = []
                    ETAG.update(headers, mytime)
                    start_response('304 Not Modified', headers)
                    return [''] # empty body
        else:
            app = HTTPNotFound(comment=path_info)
        return app(environ, start_response)


        #return StaticURLParser.__call__(self, environ, start_response)
