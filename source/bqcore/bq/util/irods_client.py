import os
import re
import urlparse
import logging
import posixpath
import urllib


from bq.util.mkdir import _mkdir
from bq.util.paths import data_path
from bq.util.locks import Locks


log = logging.getLogger('bq.irods')

try:
    # pylint: disable=import-error
    from irods.exception import (DataObjectDoesNotExist,
                                 CollectionDoesNotExist,
                                 iRODSException)


    from irods.session import iRODSSession # pylint: disable=import-error
except ImportError:
    log.warn ("Irods not available: unable to import irods")

#IRODS_CACHE = data_path('irods_cache')

CONNECTION_POOL = {}


class IrodsError(Exception):
    pass

#log.setLevel (logging.DEBUG)

PARSE_NET = re.compile(r'^((?P<user>[^:]+):(?P<password>[\w.#^!;]+)?@)?(?P<host>[^:]+)(?P<port>:\d+)?')

class IrodsConnection(object):
    def __init__(self, url, user=None, host=None, port=None, password = None, zone=None):
        irods_url = urlparse.urlparse(url)
        assert irods_url.scheme == 'irods'
        env = PARSE_NET.match(irods_url.netloc).groupdict()
        args = dict(
            user = user or env['user'], #or irods_env.getRodsUserName()
            host  = 'data.cyverse.org' or env['host'], #or irods_env.getRodsHost()
            port  =  port or env['port'] or 1247, #or irods_env.getRodsPort() or 1247
            zone = zone or 'iplant',
            password = password or env['password'])

        log.debug ("irods_connection env %s ->%s" , env, args)

        path = ''
        zone = ''
        if irods_url.path:
            path = urllib.unquote(irods_url.path).split('/')
            if len(path):
                zone = path[1]
            path = '/'.join(path)

        self.irods_url = irods_url
        self.path = path
        self.zone = zone

        # Ensure all parameters are not None
        if not all (args.values()):
            raise IrodsError("missing parameter %s", ",".join ( k for k,v in args.items() if v is None))

        self.session = iRODSSession(**args)
        self.irods_url = urlparse.urlunparse(list(self.irods_url)[:2] + ['']*4)

    def open(self):
        pass
        #conn, err = irods.rcConnect(self.host, self.port, self.user, self.zone)
        #if conn is None:
        #    raise IrodsError("Can't create connection to %s " % self.host)
        #if self.password:
        #    irods.clientLoginWithPassword(conn, self.password)
        #else:
        #    irods.clientLogin(conn)

        #coll = self.session.collections.get (
        #nm = coll.getCollName()

        #self.irods_url = urlparse.urlunparse(list(self.irods_url)[:2] + ['']*4)
        #if self.path in ['', '/']:
        #    self.path = nm

        #self.conn = conn
        #self.base_dir = nm
        #return self

    def close(self):
        if self.session:
            self.session.cleanup()
        self.session = None

    def __enter__(self):
        if self.session is None:
            self.open()
        return self

    def __exit__(self, ty, val, tb):
        self.close()
        return False


BLOCK_SZ=512*1024
def copyfile(f1, *dest):
    'copy a file to multiple destinations'
    while True:
        buf = f1.read(BLOCK_SZ)
        if not buf:
            break
        for fw in dest:
            fw.write(buf)
        if len(buf) < BLOCK_SZ:
            break

def chk_cache(cache):
    if not os.path.exists(cache):
        _mkdir (cache)


#####################
# iRods CACHE
#def irods_cache_name(path):
#    cache_filename = os.path.join(IRODS_CACHE, path[1:])
#    return cache_filename
def irods_cache_fetch(path, cache):
    cache_filename = os.path.join(cache, path[1:])
    if os.path.exists(cache_filename):
        with Locks (cache_filename): # checks if currently writing
            return cache_filename
    return None

def irods_cache_save(f, path, cache, *dest):
    cache_filename = os.path.join(cache, path[1:])
    _mkdir(os.path.dirname(cache_filename))
    with Locks (None, cache_filename,  failonexist=True) as l:
        if l.locked:
            with open(cache_filename, 'wb') as fw:
                copyfile(f, fw, *dest)

    with Locks (cache_filename):
        return cache_filename

def irods_fetch_file(url, cache, **kw):
    chk_cache(cache)
    try:
        with IrodsConnection(url, **kw) as ic:
            log.debug( "irods_fetching %s -> %s" , url, ic.path)
            localname = irods_cache_fetch(ic.path, cache)
            if localname is None:
                obj = ic.session.data_objects.get (ic.path)
                with obj.open ('r') as f:
                    localname = irods_cache_save(f, ic.path, cache)
            return localname
    except Exception as e:
        log.exception ("fetch of %s", url)
        raise IrodsError("can't read irods url %s" % url)

def irods_mkdirs (session, dirpath):
    """irods_mkdir creates all directories on path

    This version works backwords from the fullpath as the underlying
    irods library always generates CollectionDoesNotExist even for access
    errors therefore we cannot know if we are failing because we need
    to create the directory or just skip over it.

    @param session: The current session
    @param dirpath: A string for the path to be created
    @return : the collection requested
    """
    dirpath  = dirpath.split ('/')
    newpath  = []
    while dirpath:
        try:
            collection = session.collections.get ("/".join (dirpath))
            break
        except CollectionDoesNotExist:
            pass
        newpath.append (dirpath.pop())
    while newpath:
        dirpath.append (newpath.pop())
        collection = session.collections.create ("/".join (dirpath))
    return collection

def irods_push_file(fileobj, url, cache, savelocal=True, **kw):
    chk_cache(cache)
    try:
        with IrodsConnection(url, **kw) as ic:
            # Hmm .. if an irodsEnv exists then it is used over our login name provided above,
            # meaning even though we have logged in as user X we may be the homedir of user Y (in .irodsEnv)
            # irods.mkCollR(conn, basedir, os.path.dirname(path))
            #retcode = irods.mkCollR(ic.conn, '/', os.path.dirname(ic.path))
            #ic.makedirs (os.path.dirname (ic.path))
            irods_mkdirs (ic.session, posixpath.dirname (ic.path))
            log.debug( "irods-path %s" ,  ic.path)
            obj = ic.session.data_objects.create (ic.path)
            with obj.open('w') as f:
                localname = irods_cache_save(fileobj, ic.path, cache, f )
            return localname
    except Exception, e:
        log.exception ("during push %s", url)
        raise IrodsError("can't write irods url %s" % url)

def irods_delete_file(url, cache, **kw):
    chk_cache(cache)
    try:
        with IrodsConnection(url, **kw) as ic:
            log.debug( "irods-path %s" ,  ic.path)
            localname = irods_cache_fetch(ic.path, cache=cache)
            if localname is not None:
                os.remove (localname)
            log.debug( "irods_delete %s -> %s" , url, ic.path)
            ic.session.data_objects.unlink (ic.path)
    except Exception, e:
        log.exception ("during delete %s", url)
        raise IrodsError("can't delete %s" % url)

def irods_isfile (url, **kw):
    try:
        with IrodsConnection(url, **kw) as ic:
            log.debug( "irods_isfile %s -> %s" , url, ic.path)
            obj = ic.session.data_objects.get (ic.path)
            return hasattr (obj, 'path')
    except DataObjectDoesNotExist:
        pass
    except Exception:
        log.exception ("isfile %s", url)
    return False

def irods_isdir (url, **kw):
    try:
        with IrodsConnection(url, **kw) as ic:
            ic.session.collections.get (ic.path)
            return True
    except CollectionDoesNotExist:
        pass
    except Exception:
        log.exception("isdir %s", url)
    return False


def irods_fetch_dir(url, **kw):
    try:
        result = []
        with IrodsConnection(url, **kw) as ic:
            dirpath = ic.path.rstrip ('/')
            log.debug ("listing %s", dirpath)
            coll = ic.session.collections.get (dirpath)
            for sc in coll.subcollections:
                result.append('/'.join([ic.irods_url, ic.path[1:], sc.name, '']))

            for resource in  coll.data_objects:
                result.append( '/'.join([ic.irods_url, ic.path[1:], resource.name]))
        return result
    except Exception:
        log.exception ('fetch_dir %s', url)
        return result
