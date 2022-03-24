import os
import re
import urlparse
import shutil
import atexit
import logging
import subprocess
import urllib

from bq.util.mkdir import _mkdir
from bq.util.paths import data_path
IRODS_CACHE = data_path('irods_cache')


# If you truly want to be the user when making interacting with iRODS, you can do the following as long as you can authenticate as that user with 'iinit'. Just use environment variables instead of .irodsEnv. You just need to make sure that each user has their own auth file  (.irodsA).  Here's an example.

# irodsHost=data.iplantc.org irodsPort=1247 irodsZone=iplant irodsUserName=tedgin irodsAuthFileName='/home/bisque/.irods/tedgin-auth iput file
# The above statement uploads a file, authenticated as me.
# irodsHost=data.iplantc.org irodsPort=1247 irodsZone=iplant irodsUserName=tedgin irodsAuthFileName='/home/bisque/.irods/tedgin-auth iinit <(echo password)
# The above statement creates a session authenticated as me.
# Here's a list of all the environment variables that can control the icommands environment.  https://wiki.irods.org/index.php/User_Environment_Variables

try:
    FNULL = open(os.devnull, 'w')
    subprocess.check_call (['ienv', '-h'], stdout=FNULL, stderr=FNULL)
except:
    raise ImportError ("Cannot initialize icommands for irods")


log = logging.getLogger('bq.irods')
log.setLevel (logging.DEBUG)

PARSE_NET = re.compile('^((?P<user>[^:]+):(?P<password>[\w.#^!;]+)?@)?(?P<host>[^:]+)(?P<port>:\d+)?')

class IrodsError(Exception):
    pass


class IrodsConnection(object):
    connections = {}


    def __init__(self, url, user=None, host=None, port=None, password = None, zone=None):
        irods_url = urlparse.urlparse(url)
        assert irods_url.scheme == 'irods'
        env = PARSE_NET.match(irods_url.netloc).groupdict()

        self.env = dict(
            irodsUserName = user or env['user'] or '', #or irods_env.getRodsUserName()
            irodsHost  = host or env['host'], #or irods_env.getRodsHost()
            irodsPort  = str (port or env['port'] or '1247'), #or irods_env.getRodsPort() or 1247
            irodsZone = zone or 'iplant',
            )
        self.password = password


        path = ''
        zone = ''
        if irods_url.path:
            path = urllib.unquote(irods_url.path).split('/')
            if len(path):
                zone = path[1]
            path = '/'.join(path)
        self.path = path
        self.auth_file = irods_cache_name ('/auth/%s-%s-%s-%s' % (self.env['irodsHost'],
                                                                 self.env['irodsPort'],
                                                                 self.env['irodsZone'],
                                                                 self.env['irodsUserName']))
        self.env ['irodsAuthFileName'] = self.auth_file
        self.irods_url = urlparse.urlunparse(list(irods_url)[:2] + ['']*4)


    def open(self):
        if  os.path.exists (self.auth_file):
            log.debug ("re-using auth file %s", self.auth_file)
            return self

        log.debug ("initializing auth file %s", self.auth_file)
        p = self.popen (['iinit'] ,  stdin=subprocess.PIPE)
        p.communicate (input = self.password)
        p.wait()
        return self

    def close(self):
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, ty, val, tb):
        self.close()
        return False

    def check_cmd(self, args, **kw):
        r = self.cmd (args, **kw)
        if r != 0:
            raise IrodsError ("command %s returned %s"% ( args, r))

    def cmd(self, args, **kw):
        env = dict (os.environ)
        env.update (self.env)
        if 'env'  in kw:
            env.update (kw.pop('env'))
        log.debug ("calling %s ", args)
        retcode = subprocess.call(args=args, env=env, **kw)
        return retcode

    def check_output(self, args, **kw):
        env = dict (os.environ)
        env.update (self.env)
        if 'env'  in kw:
            env.update (kw.pop('env'))
        log.debug ("calling %s with %s", args, env)
        return subprocess.check_output(args=args, env=env, **kw)




    def popen(self, args, **kw):
        env = dict (os.environ)
        env.update (self.env)
        if 'env'  in kw:
            env.update (kw.pop('env'))
        log.debug ("Popen with %s and %s %s", args, env, self.env)
        p = subprocess.Popen(args=args, env=env, **kw)
        return p



#####################
# iRods CACHE
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
def irods_cache_name(path):
    cache_filename = os.path.join(IRODS_CACHE, path[1:])
    _mkdir(os.path.dirname(cache_filename))
    return cache_filename

def irods_cache_fetch(path):
    cache_filename = os.path.join(IRODS_CACHE, path[1:])
    if os.path.exists(cache_filename):
        return cache_filename
    return None

def irods_cache_save(f, path, *dest):
    cache_filename = os.path.join(IRODS_CACHE, path[1:])
    _mkdir(os.path.dirname(cache_filename))
    with open(cache_filename, 'wb') as fw:
        copyfile(f, fw, *dest)

    return cache_filename


def irods_fetch_file(url, **kw):
    with IrodsConnection(url, **kw) as ic:
        log.debug( "irods_fetch iget %s -> %s" , url, ic.path)
        localname = irods_cache_fetch(ic.path)
        if localname is None:
            localname = irods_cache_name (ic.path)
            ic.check_cmd (["iget", ic.path, localname])
        return localname

def irods_push_file(fileobj, url, savelocal=True, **kw):
    with IrodsConnection(url, **kw) as ic:
        log.debug( "irods_push iput %s -> %s" , url, ic.path)
        localname = irods_cache_save(fileobj, ic.path)
        ic.check_cmd (['imkdir', '-p', os.path.dirname (ic.path)])
        ic.check_cmd (['iput', localname, ic.path])
        return localname

def irods_delete_file(url, **kw):
    with IrodsConnection(url, **kw) as ic:
        log.debug( "irods_delete irm  %s" ,  ic.path)
        localname = irods_cache_fetch(ic.path)
        if localname is not None:
            os.remove (localname)
        log.debug( "irods_delete %s -> %s" ,url, ic.path)
        ic.check_cmd  (['irm', ic.path])

def irods_isfile (url, **kw):
    with IrodsConnection(url, **kw) as ic:
        r = ic.cmd (["ils", ic.path])
        if r == 0:
            return True
    return False

def irods_isdir (url, **kw):
    with IrodsConnection(url, **kw) as ic:
        r = ic.cmd (["icd", ic.path])
        if r == 0:
            return True
    return False

def irods_fetch_dir(url, **kw):
    try:
        results = []
        with IrodsConnection(url, **kw) as ic:
            output = ic.check_output (["ils", ic.path]).strip().split ("\n")

            log.debug ("GOT : %s", output)
            # Skip the first line as it's the directory
            for line in output[1:]:
                line = line.split()[-1]
                results.append (  '/'.join([ic.irods_url, ic.path[1:], line.strip()]))
        return results
    except subprocess.CalledProcessError:
        log.exception ("problem while listing %s", ic.path)
        #raise IrodsError ("bad listing")
        return results
