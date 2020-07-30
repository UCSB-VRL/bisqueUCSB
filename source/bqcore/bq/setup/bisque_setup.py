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
Configure bisque

DESCRIPTION
===========



"""
from __future__ import print_function
from past.builtins import execfile
from future import standard_library
standard_library.install_aliases()
from builtins import next
from builtins import chr
from builtins import input
from builtins import str
from builtins import range
from past.builtins import basestring
from builtins import object

import datetime
import fnmatch
import getpass
import hashlib
import logging
import os
import platform
import posixpath
import pprint
import random
import re
import shutil
import socket
import stat
import string
import io
import subprocess
import sys
import tarfile
import textwrap
import time
import traceback
import urllib.parse
import uuid
import zipfile
from collections import OrderedDict

from dateutil.parser import parse
from dateutil import tz
import requests
import pkg_resources

try:
    from pip import main as pipmain
except:
    from pip._internal import main as pipmain


#from setuptools.command import easy_install

try:
    from marrow.mailer import  Mailer
    MAILER='marrow.mailer'
except ImportError:
    try:
        import turbomail as Mailer
        MAILER='turbomail'
    except ImportError:
        MAILER=None


#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('bisque-setup')
#log.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)

#formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
#formatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
# add formatter to ch
#ch.setFormatter(formatter)
#log.addHandler(ch)


## ENSURE setup.py has been run before..
capture = None
answer_file = None
save_answers = False
use_defaults = False

try:
    import sqlalchemy as sa
    from bq.util.configfile import ConfigFile
    #from bq.model import db_version
except ImportError as e:
    log.exception( "There was a problem with the bisque environment\n"
                   "Have you run %s setup.py yet?" , sys.executable)

    sys.exit(0)

try:
    import readline #pylint:disable=W0611
    #readline.parse_and_bind('tab: complete')
    #readline.parse_and_bind('set editing-mode emacs')
except ImportError as e:
    log.info( "No readline available" )

try:
    import pty
    has_script=True
except ImportError:
    has_script=False


class SetupError(Exception):
    'error in setup'

class InstallError(Exception):
    pass



#############################################
#  Setup some local constants
DIRS= dict (
    # These are by set by install
    share  =None,
    run    =None,
    virtualenv=None,
    # These are derived from those above
    bin    = None,
    config = None,
    default=None,
    depot  =None,
)
SITE_CFG = None
RUNTIME_CFG = None


PYTHON=sys.executable
EXT_SERVER = "http://biodev.ece.ucsb.edu/binaries/depot/" # EXTERNAL host server DIRS['depot']


#HOSTNAME = socket.getfqdn()
HOSTNAME = "0.0.0.0"


if os.name == 'nt':
    EXEC_EXTS = ['.com', '.exe', '.bat' ]
    SCRIPT_EXT = '.exe'
    ARCHIVE_EXT = '.zip'
else:
    SCRIPT_EXT = ''
    ARCHIVE_EXT = '.tar.gz'
    EXEC_EXTS = ['']



TRUE_RESPONSE = { 'true': 'Y', 'y': 'Y', 't' : 'Y', 'yes' : 'Y', '1' : 'Y'}

############################################
# HELPER FUNCTIONS
def to_sys_path( p ):
    ''' Converts POSIX style path into the system style path '''
    return p.replace('/', os.sep)

def to_posix_path( p ):
    ''' Converts system style path into POSIX style path '''
    return p.replace(os.sep, '/')

def defaults_path(*names):
    return to_sys_path(os.path.join(DIRS['default'],  *names))

def config_path(*names):
    return to_sys_path(os.path.join(DIRS['config'], *names))

def share_path(*names):
    return to_sys_path(os.path.join(DIRS['share'], *names))

def bin_path(*names):
    return to_sys_path(os.path.join(DIRS['bin'],  *names))

def run_path(*names):
    return to_sys_path(os.path.join(DIRS['run'],  *names))


QUOTED_CHARS="#"
def quoted(value):
    'quote a value if has special chars'
    return '\"%s\"' % value if any(c in value for c in QUOTED_CHARS ) else value



def which(command):
    """Emulate the Shell command which returning the path of the command
    base on the shell PATH variable
    """
    for dr in [ os.path.expanduser (x) for x in os.environ['PATH'].split (os.pathsep)]:
        for ext in EXEC_EXTS:
            path  = os.path.join(dr, "%s%s" % (command, ext) )
            if os.path.isfile (path):
                mode =  os.stat (path).st_mode
                if stat.S_IXUSR & mode:
                    return path
                return None

def check_exec(command):
    return which (command) != None


def copy_link (*largs):
    largs = list (largs)
    d = largs.pop()

    for f in largs:
        try:
            dest = d
            if os.path.isdir (d):
                dest = os.path.join (d, os.path.basename(f))
            log.info( "linking %s to %s", f, dest )
            if os.path.exists (dest):
                os.unlink(dest)
            os.link(f, dest)
        except Exception:
            if os.name != 'nt':
                log.exception( "Problem in link %s .. trying copy" , f)
            shutil.copyfile (f, dest)

def getanswer(question, default, help=None, envvar=None):
    global capture
    if "\n" in question:
        question = textwrap.dedent (question)
    while 1:
        if not save_answers and answer_file:
            ans = answer_file.readline().strip()
            if question.strip() != ans:
                raise SetupError( "Mismatch '%s' !=  '%s' " % (question, ans) )
            ans = answer_file.readline().strip()
            answer_file.readline()

        elif capture is not None:
            ans =  capture.logged_input ("%s [%s]? " % (question, default))
        else:
            if not use_defaults:
                ans =  input ("%s [%s]? " % (question, default))
            else:
                ans = default

        if ans=='?':
            if help is not None:
                print (textwrap.dedent(help))
            else:
                print ("Sorry no help available currently.")
            continue
        y_n = ('Y', 'y', 'N', 'n')
        if default in y_n and ans in y_n:
            ans = ans.upper()

        if ans == '': ans = default
        if save_answers and answer_file:
            answer_file.write(question)
            answer_file.write ('\n')
            answer_file.write (ans)
            answer_file.write ('\n\n')
        break
    return ans


def patch_file (path, mapping, destination=None, **kw):
    """Replace the file at path replacing the elements found in kw
    Keyword are signaled with '$' i.e.  $KEY is reaplced with 'something'
    if mapping has {'KEY' : 'something' }
    """
    with open(path) as f:
        contents = f.read()
    template = string.Template(contents).substitute(mapping, **kw)
    if destination is None:
        destination = path
    if os.path.isdir(destination):
        destination = os.path.join(destination, os.path.basename(path))
    with open(destination,'w') as f:
        f.write (template)


def sql(DBURI, statement, verbose = False):

    from sqlalchemy import create_engine, sql
    try:
        engine = create_engine(DBURI, echo= verbose)
        result = engine.execute(sql.text(statement))
        return 0, result.fetchall()
    except Exception:
        if verbose:
            log.exception('in sql %s' % statement)
        return 1, ''


    print ( "SQL: NOT IMPLEMEMENT %s" % statement )
    return 0, ''
    # OLD SHell out version
    # command = ["psql"]
    # if DBURI.username:
    #     command.extend (['-U', DBURI.username])
    # if DBURI.host:
    #     command.extend (['-h', DBURI.host])
    # if DBURI.port:
    #     command.extend (['-p', str(DBURI.port)])
    # stdin = None
    # if DBURI.password:
    #     stdin = StringIO.StringIO(DBURI.password)

    # p =subprocess.Popen(command + ['-d',str(DBURI.database), '-c', statement],
    #                     stdout=subprocess.PIPE,
    #                     stderr=subprocess.STDOUT)
    # out, err = p.communicate()
    # return p.returncode, out


class STemplate (string.Template):
    """ Like the standard template but allows '.' in names
    """
    idpattern = r'[_a-z][._a-z0-9]*'


def call(cmd, echo=False, capture=False, **kw):
    """Special version subprocess.call that write output
    """
    lines = []
    if echo:
        print( "Executing '%s'" % ' '.join (cmd))
    if 'stdout' not in kw:
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, **kw)
        while True:
            l = p.stdout.readline()
            if not l: break
            print (l, end='')
            lines .append(l)
            #p.wait()
    else:
        p = subprocess.Popen(cmd, **kw)

    p.wait()

    if capture:
        return p.returncode, "".join(lines)
    else:
        return p.returncode


def unpack_zip (zfile, dest, strip_root=None):
    z = zipfile.ZipFile (zfile, 'r')
    if strip_root is None:
        z.extractall(dest)
        names = z.namelist()
    else:
        top_dir = z.infolist()[0].filename.split('/',1)[0]+'/'
        names = []
        for info in z.infolist():
            new_path = info.filename.replace(top_dir, '')
            filename = os.path.join(dest, new_path)
            names.append(filename)
            if os.name == 'nt':
                filename = filename.replace('/', '\\')
            mypath = os.path.dirname(filename)
            if not os.path.exists(mypath):
                os.makedirs(mypath)
            # write the file, .extract would force the subpath and can't be used
            try:
                f = open(filename, 'wb')
                f.write(z.read(info))
                f.close()
            except IOError:
                pass
    z.close()
    return names

def newer_file (f1, f2):
    "check if f1 is newer than f2"
    if not os.path.exists(f1) or not os.path.exists(f2):
        return True
    return   os.path.getmtime(f1) > os.path.getmtime(f2)

def touch(fname, times=None):
    "emulate unix touch"
    # http://stackoverflow.com/questions/1158076/implement-touch-using-python
    fhandle = open(fname, 'a')
    try:
        os.utime(fname, times)
    finally:
        fhandle.close()

def find_path (name, places):
    """Look in PLACES for a file (or directory) named NAME
    """
    for dr in places:
        place = os.path.join (dr, name)
        if os.path.exists(place):
            return place
    return None

def check_env (section, key):
    """Check the variable

    A site.cfg variable such as bisque.a.b.c in section 'main'  will check the environment variable
    BISQUE_MAIN_BISQUE_A_B_C

    @param section: The site.cfg section name
    @param key: a site.cfg key
    """
    # Check environment variables
    section_name = '' if section == BQ_SECTION or section is None else section + "_"
    envkey = "BISQUE_" + section_name.upper() + key.upper().replace('.','_')
    #print "checking", envkey
    return os.environ.get (envkey)


# stolen form pylons
def asbool(obj):
    if isinstance(obj, basestring):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError("String is not true/false: %r" % obj)
    return bool(obj)

def remove_prefix(text, prefix):
    return re.sub(r'^{0}'.format(re.escape(prefix)), '', text)



#################################################
## Initial values
SITE_VARS = {
    'bisque.server' : 'http://%s:8080' % HOSTNAME,
    'bisque.organization': 'Your Organization',
    'bisque.title': 'Image Repository',
    'bisque.admin_email' : 'YourEmail@YourOrganization',
    'bisque.admin_id' : 'admin',
    'bisque.paths.root' : os.getcwd(),
    }

ENGINE_VARS  ={
    'bisque.engine': 'http://%s:27000'  % HOSTNAME,
    'bisque.paths.root' : os.getcwd(),
    # 'bisque.admin_email' : 'YourEmail@YourOrganization',
    }

# Add any variables to read from the site.cfg each time
# you run bisque-setup
initial_vars = {
    'bisque.paths.root' : os.getcwd(),
#    bisque.root overides use of request url in generating responses
#    'bisque.root' : 'http://0.0.0.0:8080',
    'bisque.organization': 'Your Organization',
    'bisque.title': 'Image Repository',
    'bisque.admin_email' : 'YourEmail@YourOrganization',
    'bisque.admin_id'    : 'admin',
    'sqlalchemy.url': 'sqlite:///bisque.db',
    'mail.on' : 'False',
    'mail.manager' : "immediate",
    'mail.transport' : "smtp",
    'mail.smtp.server' : 'localhost',
    'runtime.matlab_home' : '',
    'runtime.mode' : 'command',
    'runtime.staging_base' : '',
    'condor.submit_template': '',
    'condor.dag_template' : '',
    'condor.dag_config_template': '',
}

linked_vars = {
#    'h1.url' : '${bisque.server}',
#    'bisque.root' : '${bisque.server}',
    'registration.site_name' : '${bisque.title} (${bisque.server})',
    'registration.host' : '${bisque.server}',
    'registration.mail.smtp_server' : '${mail.smtp.server}',
    'registration.mail.admin_email' : '${bisque.admin_email}',
    'beaker.session.sa.url' : '${sqlalchemy.url}',
    # Paster error variables
    'error_email_from' : '${bisque.admin_email}',
    'email_to' : '${bisque.admin_email}',
    'smtp_server' : '${mail.smtp.server}',
}

SERVER_QUESTIONS=[
    ('backend' , 'The server agent for bisque', "Bisque can configured to be served by paster or uwsgi"),
    ('servers', "list of server entries to be configured", "Each server listed will be configured"),
]

PASTER_QUESTIONS=[
    ('url', 'the url of the server', 'The url including port of the internal server'),
    ('services_enabled', 'Services enabled', ''),
    ('services_disabled', 'Services disabled', ''),
]

UWSGI_QUESTIONS=[
    ('url', 'the url of the server', 'The url including port of the internal server'),
    ('services_enabled', 'Services enabled', ''),
    ('services_disabled', 'Services disabled', ''),
    ('uwsgi.socket', 'The socket to listen on', ''),
    ('bisque.static_files', 'enables serving static files', 'usually uwsgi is used behing another web servers, so leave disabled'),
    ]



SITE_QUESTIONS = [
('bisque.server' , 'Enter the root URL of the server ',
 """A complete URL where your application will be mounted i.e. http://someserver:8080/
 If you server will be mounted behind a proxy, please enter
 the proxy address and see AdvancedInstalls"""),
     ('bisque.admin_displayname', 'Your real name  administrator account', None),
     ('bisque.admin_id', 'A login ID for the administrator account', None),
     ('bisque.admin_email' , 'An email for the administrator', None),
     ('bisque.organization', 'A small organization title for the main page',
      "This will show up in the upper left of every page display"),
     ('bisque.title', 'The main title for the web page header',
      "The title of your collection, group or project" ),
     ('bisque.paths.root', 'Installation Directory',
      'Location of bisque installation.. used for find configuration and data')]


ENGINE_QUESTIONS=[
    #    ('bisque.root' , 'Enter the root URL of the BISQUE server ',
    #     "A URL of Bisque site where this engine will register modules"),
    ('bisque.engine', "Enter the URL of this bisque module engine",
     "A module engine offers services over an open URL like a web-server. Please make sure any firewall software allows access to the selected port"),
    ('bisque.paths.root', 'Installation Directory',
     'Location of bisque installation.. used for find configuration and data'),
]



DB_QUESTIONS = [('sqlalchemy.url', 'A database URI', """
                  A SQLAlchemy DBURI (see http://www.sqlalchemy.org/).
                  Examples of typical DB URI:
                      sqlite:///bisque.db
                      postgresql://localhost:5432/bisque
                      mysql://user:pass@localhost/bisque
                      mysql://user:pass@localhost/bisque?unix_socket=/bisque-data/mysql-db/mysql-socket.sock
                  """),
               ]

MATLAB_QUESTIONS=[
    ('runtime.matlab_home', "Enter toplevel matlab directory (under which is bin)",
     "matlab home is used by modules to setup the correct environment variables"),

    ]
RUNTIME_QUESTIONS=[
    ('runtime.platforms', "Enter a list (comma,seperated) of module platforms",
     'controls how  module are run locally or condor'),

    ('runtime.staging_base', "An temproary area that can be used to stage execution of modules",
    """
    Some modules are copied to a temporary directory with data so that they may run
    cleanly.  Condor often requires a staging area that is seen by all nodes that
    it can dispatch jobs to.  This area can be a local or condor shared filesystem
    """)
    ]


CONDOR_QUESTIONS =[
    ('condor.submit_template', "Path to condor submit script",
     """A script used to submit jobs to Condor"""),
    ('condor.dag_template', "A DAGMAN script", None),
    ('condor.dag_config_template', "A DAGMan Config", None)
    ]


DOCKER_QUESTIONS = [
    ('docker.hub', 'A docker image repository to store locally built images', 'biodev.ece.ucsb.edu:5000' ),
    ('docker.hub.user', 'A docker login', "a username or blank e.g. your images will be named hubaddr/username/imagename"),
    ('docker.hub.password', 'A docker login password', "Password on docker registry or blank if none"),
    ('docker.hub.email', 'A docker login email', None),

    ]
DOCKER_IMAGE_QUESTIONS = [
    ('docker.image.matlab_runtime', "matlab runtime image", "a docker image spec of the matlab runtime"),
    ('docker.image.cellprofiler', "cellprofiler runtime image", "a docker image spec of the cellprofiler runtime"),
    ('docker.image.dream3d', "dream3d runtime image", "a docker image spec of the dream3d runtime"),
    ]

TEST_QUESTIONS = [
    ('host.root', 'The root bisque server to test', ''),
    ('host.user', 'The testing user login ID', ''),
    ('host.password', 'Testing user password', ''),
    ]


LOGIN_QUESTIONS = [
    ('bisque.login.local.text', 'Displayed text for login  button', ''),
    ('bisque.login.password', "use hashed password (hashed, freetext)", ''),
    ]

#####################################################
# Installer routines
def unpack(seq, nfirst):
    """Unpack N elements of a tuple and return them with rest
    a = (1,2,3)
    unpack (a, 2)
    1,2, (3)
    """
    it = iter(seq)
    for x in range(nfirst):
        yield next(it, None)
    yield tuple(it)

def make_ntuple (tpl, n, default=None):
    "Force a tuple to be a certain length"
    return tuple (list(tpl) + [default]*(n-len(tpl)))

def ensure_default (qs):
    return [make_ntuple(x, 4, '') for x in qs]


def update_variables (qs, store):
    """Ask questions to update any global  variables"""
    values = {}
    values.update (store)

    # Set all values to empty or default values if provided
    for key, q, h, default  in ensure_default(qs):
        values.setdefault (key, default)

    # Ask the question in qs after substituting vars
    for key, question, help, _ in ensure_default(qs):
        values[key] = STemplate (values[key]).safe_substitute(values)
        values[key] = getanswer (question, values[key], help)

    # Based on the given answers, update the again values  (for mutual references)
    for key in list(values.keys()):
        if isinstance (values[key], basestring):
            values[key] = STemplate (values[key]).safe_substitute(values)

    return values

#######################################################
# config editing
BQ_SECTION="app:main"

def install_cfg (site_cfg, section, default_cfg):
    if not os.path.exists (site_cfg):
        shutil.copyfile(default_cfg, site_cfg)
    params = read_site_cfg(cfg=site_cfg, section=section)
    return params

def read_site_cfg(cfg , section):
    "Read the config and return a dict with elements found"
    bisque_vars = {}

    # first pull initial values from config files
    #iv = initial
    tc = ConfigFile()
    if os.path.exists (cfg):
        tc.read(open(cfg))
        bisque_vars.update(tc.get(section, asdict=True))

    #print "READING CFG", cfg, bisque_vars

    return bisque_vars


def visible(k,v):
    return not k.startswith('__')

def update_site_cfg (bisque_vars, section = BQ_SECTION, append=True, cfg=None, filterby = visible ):
    """Read the config file and update the variables in a section
    @param bisque_vars: dict of variables
    @param section: name of section to modify
    @param append:  bool append new variables
    @param cfg : the file to modify
    """
    if cfg is None:
        cfg = SITE_CFG

    c = ConfigFile()
    if os.path.exists (cfg):
        c.read(open(cfg))

    for k,v in list(bisque_vars.items()):
        if filterby is None or filterby(k, v):
            c.edit_config (section, k, '%s = %s' % (k,quoted(str(v))), {}, append)
        #print "edit %s %s" % (k,v)
    c.write (open (cfg, 'w'))
    return bisque_vars

Nonce = object()

def modify_site_cfg(qs, bisque_vars, section = BQ_SECTION, append=True, cfg=None):
    """Ask questions and modify a config file
    see update_site_cfg
    """
    if cfg is None:
        cfg = SITE_CFG

    if not os.path.exists (cfg):
        raise InstallError('missing %s' % cfg)

    # Check environment defaults
    for key, _ in [unpack(q, 1) for q in qs ]:
        # Check environment variables
        default = check_env(section, key) or bisque_vars.get (key, Nonce)
        if default is not Nonce:
            bisque_vars[key] = default

    bisque_vars =  update_variables(qs, bisque_vars )
    for k,v in list(linked_vars.items()):
        if k in bisque_vars:
            bisque_vars [k] = v
    bisque_vars =  update_variables([], bisque_vars )

    c = ConfigFile()
    c.read(open(cfg))
    for k,v in list(bisque_vars.items()):
        c.edit_config (section, k, '%s = %s' % (k,quoted(str(v))), {}, append)
        #print "edit %s %s" % (k,v)
    c.write (open (cfg, 'w'))
    return bisque_vars



############################################
# Database

DB_CREATE_ERROR = """
*** Database creation failed ***
Please check your db url to ensure that it is in the correct format.
Also please ensure that the user specified can actually create/access a database.
"""

def create_postgres_sa (dburl):
    "Check existance of database base and create new if needed"
    dbstr = str (dburl)
    template1 = posixpath.join (posixpath.dirname (dbstr), "template1")
    dbname    = posixpath.basename (dbstr)

    engine = sa.create_engine(template1)
    conn   = engine.connect()
    # End automatic Postgres  transaction with commit
    conn.execute("commit")
    # create new database
    conn.execute("create database %s" % dbname)
    conn.close()
    log.info ("Created postgresql database %s", dbname)
    return True


def create_postgres_psql (dburl):
    "Check existance of database base and create new if needed"

    command = ["psql"]
    if dburl.username:
        command.extend (['-U', dburl.username])
    if dburl.host:
        command.extend (['-h', dburl.host])
    if dburl.port:
        command.extend (['-p', str(dburl.port)])

    stdin = None
    if dburl.password:
        stdin = io.StringIO(dburl.password)
    if call (command + [ '-d', str(dburl.database), '-c', r'\q'], stdin = stdin ) == 0:
        print ("Database exists, not creating")
        return False
    # http://www.faqs.org/docs/ppbook/x17149.htm
    # psql needs a database to connect to even when creating.. use template1
    if dburl.password:
        stdin = io.StringIO(dburl.password)
    if call (command + ['-c', 'create database %s' % dburl.database, 'template1'], echo=True,
             stdin = stdin) != 0:
        print( DB_CREATE_ERROR)
        return False

    return True



###############
#

def create_mysql_sa(dburl):
    "Create a new mysql database "
    dbstr = str(dburl)
    connecturl = posixpath.dirname (dbstr)
    dbname     = posixpath.basename (dbstr)

    engine = sa.create_engine (connecturl)
    engine.execute ("CREATE DATABASE %s" % dbname)
    log.info ("Created mysql database %s", dbname)
    return True

def create_mysql_cmd(dburl):
    command = [ 'mysql' ]
    if 'unix_socket' in dburl.query:
        command.append ( '--socket=%s' % dburl.query['unix_socket'] )
    if dburl.username:
        command.append ('-u%s' % dburl.username)
    if dburl.password:
        command.append ('-p%s' % dburl.password)

    print( "PLEASE ignore 'ERROR (...)Unknown database ..' ")
    if call (command+[dburl.database, '-e', 'quit'], echo=True) == 0:
        print( "Database exists, not creating")
        return False

    if call (command+['-e', 'create database %s' % dburl.database], echo=True) != 0:
        print( DB_CREATE_ERROR )
        return False
    return True


###############
#
def create_sqlite (dburl):
    return True


known_db_types = {
    'sqlite'     : ('sqlite3', '',   create_sqlite ),
    'postgres'   : ('psycopg2',  'psycopg2', create_postgres_sa   ),
    'postgresql' : ('psycopg2',  'psycopg2',  create_postgres_sa  ),
    'mysql'      : ('_mysql',    'mysql-python', create_mysql_sa ),
    }

def install_driver(DBURL):
    """For known database types: check whether required driver is installed;
    install it if not installed.

    Argument: sqlalchemy.engine.url.URL object.

    Returns True if driver is available (so it makes sense to continue),
    False otherwise (database configuration should be cancelled).
    """
    py_drname, ei_drname, create = known_db_types.get(DBURL.drivername,
                                                      (None,None,None))
    if py_drname is None:
        return getanswer(
            """
            This database type is not known to Bisque.
            Make sure that you have installed appropriate driver
            so SQLAlchemy can use it to access your database.
            Continue?
            """,
            'N',
            """
            Bisque knows what driver is required for SQLite, PostreSQL, and MySQL
            and automatically installs it if needed.
            For other databases, you have to install driver manually.
            It is also recommended that you create empty database manually,
            as some databases may use proprietary syntax for database creation.
            """) == "Y"

    else:
        try:
            print( 'Trying to import driver %s...' % py_drname)
            __import__(py_drname)
            print( 'Driver successfully imported.')
            return True
        except ImportError:
            print ('\nImport failed, trying to install package %s...' % ei_drname)
            try:
                #easy_install.main(['-U',ei_drname])
                pipmain(['install', '-U', ei_drname]) #pylint: disable=no-member
                # The following line is needed to make installed module importable
                pkg_resources.require(ei_drname)
                print('Package %s successfully installed.' % ei_drname)
                return True
            except Exception:
                print( "ERROR: Could not easy install package")
                print ( "Usually this occurs if the development headers for a partcular driver")
                print( "are not available. Please check the Bisque Wiki")
                print( "http://biodev.ece.ucsb.edu/projects/bisquik/wiki/AdvancedInstalls")

                log.exception( 'Failed to install package %s.' , str( ei_drname ))
                return False



def test_db_existance(DBURL):
    """Test whether Bisque database exists and is accessible.
    Note that database may exist, but the user specified in DBURL has no
    rights to access it, etc.
    This function is able to catch only basic configuration errors
    (like Bisque database user was created, but no rigts were granted to it).
    Even if this function succeeds, later steps may fail due to misconfigured
    access rights.

    Argument: sqlalchemy.engine.url.URL object.

    Returns True if database exists and is accessible, False otherwise.
    """
    try:
        print( 'Checking whether database "%s" already exists...' % DBURL.database)
        d = sa.create_engine(DBURL)
        try:
            c = d.connect()
            c.close()
        finally:
            d.dispose()
        print( 'Yes, it exists.')
        return True
    except Exception:
        log.warn("Could not contact database %s. It may not exist yet", str(DBURL))
        return False

def get_dburi(params):

    if os.getenv('BISQUE_DBURL'):
        params['sqlalchemy.url'] = os.getenv('BISQUE_DBURL')
    if params['sqlalchemy.url'].startswith('sqlite:///bisque.db'):
        params['sqlalchemy.url'] = "sqlite:///%s/bisque.db" % (DIRS['run'])

    params = modify_site_cfg(DB_QUESTIONS, params)
    dburi = os.getenv('BISQUE_DBURL') or params.get('sqlalchemy.url', None)
    DBURL = sa.engine.url.make_url (dburi)
    return params, DBURL


def test_db_alembic (DBURL):
    r, out = sql(DBURL, 'select * from alembic_version')
    return r == 0

def test_db_sqlmigrate(DBURL):
    r, out = sql(DBURL, 'select * from migrate_version')
    return r == 0

def test_db_initialized(DBURL):
    r, out = sql(DBURL, 'select * from taggable limit 1')
    return r == 0


def install_database(params, runtime_params):
    """Main database configuration routine.
    To succeed, database server should run, be accessible using the specified
    dburi, and have the specified database.

    Note: this always is true for SQLite.

    Note: for all other database types, database should be created manually
    before running Bisque setup.
    """
    try:
        params, DBURL = get_dburi(params)
    except sa.exc.ArgumentError:
        log.exception( "Unable to understand DB url. Please see SqlAlchemy" )
        return params

    # 'dburi' is a string entered by the user
    # 'DBURL' is an object with attributes:
    #   drivername  -- string like 'sqlite', 'postgres', 'mysql'
    #   username    -- string
    #   password    -- string
    #   host        -- string
    #   port        -- string
    #   database    -- string
    #   query       -- map from query's names to values

    # Step 1: check whether database driver is available (install it if needed)
    if not install_driver(DBURL):
        print("""Database   driver was bit installed.  Missing packages?
Please resolve the problem(s) and re-run 'bisque-setup --database'.""")
        return params, runtime_params

    if getanswer("Create and initialize database", "Y", "Create, initialize or upgrade database") == "Y":
        params, runtime_params = setup_database (params, runtime_params)
    return params, runtime_params


def setup_database (params, runtime_params):
    try:
        params, DBURL = get_dburi(params)
    except sa.exc.ArgumentError:
        log.exception( "Unable to understand DB url. Please see SqlAlchemy" )
        return params, runtime_params
    # Step 2: check whether the database exists and is accessible
    if not create_database(DBURL):
        print( "database not created")
        return params, runtime_params
    # Step 3: find out whether the database needs initialization
    params = initialize_database(params, DBURL)
    # Step 4: migrate database (and project to latest version)"
    if not asbool(params['new_database']):
        migrate_database(DBURL)
    return params, runtime_params

def create_database(DBURL):
    "Create a database based on the DB URL"

    db_exists = test_db_existance(DBURL)
    if not db_exists:
        if getanswer ("Would you like to create the database",
                      "Y",
                      """
      Try to create the database using system level command.  This
      really is outside of the scope of the installer due to the complexity
      of user and rights management in database systems.   This command
      may succeed if you been able to create database previously at the
      command line
      """) == 'Y':
            py_drname, ei_drname, create_db = \
                       known_db_types.get(DBURL.drivername, (None,None,None))
            if callable(create_db):
                try:
                    db_exists = create_db (DBURL)
                except Exception:
                    log.exception('Could not create database')

    if not db_exists:
        print( """
        Database was NOT prepared -- either server has no database '%s'
        or user "%s" has no rights to access this database.
        Please fix the problem(s) and re-run 'bq-admin setup createdb'
        """ % (DBURL.database,DBURL.username) )
        return False
    return True




def setup_testing(params, runtime_params):
    "ensure test.ini is created and loaded"

    TEST_CFG = config_path ('test.ini')
    if not  os.path.exists(TEST_CFG):
        test_params = install_cfg(TEST_CFG, section='test', default_cfg=defaults_path('test.ini.default'))
    else:
        test_params = read_site_cfg(cfg=TEST_CFG, section = 'test')

    test_params = modify_site_cfg (TEST_QUESTIONS, test_params,section='test', cfg = TEST_CFG)


    return params




def initialize_database(params, DBURL=None):
    "Initialize the database with tables"

    if DBURL:
        db_initialized = test_db_initialized(DBURL)
    else:
        db_initialized = True

    params['new_database'] = 'false'
    alembic_params = {
        'script_location' : share_path ('migrations'),
        'sqlalchemy.url'  : params.get ('sqlalchemy.url'),
    }
    ALEMBIC_CFG  = config_path('alembic.ini')

    install_cfg(ALEMBIC_CFG, section="alembic", default_cfg=defaults_path('alembic.ini.default'))
    update_site_cfg(alembic_params, section='alembic', cfg = ALEMBIC_CFG, append=False)
    if not db_initialized and getanswer(
        "Intialize the new database",  "Y",
        """
        The database is freshly created and doesn't seem to have
        any tables yet.  Allow the system to create them..
        """) == "Y":
        if call ([bin_path('paster'),'setup-app', config_path('site.cfg')]) != 0:
            raise SetupError("There was a problem initializing the Database")
        params['new_database'] = 'true'
    return params


def migrate_database(DBURL=None):
    "Attempt to migrate existing database to latest version"

    #if DBURL and test_db_sqlmigrate(DBURL):
    #    print "Upgrading database version (sqlmigrate)"
    #    call ([PYTHON, to_sys_path ('bqcore/migration/manage.py'), 'upgrade'])

    #if not params['new_database'] : #and test_db_alembic(DBURL):
    print( "Upgrading database version (alembic)")
    if call ([bin_path("alembic"), '-c', config_path('alembic.ini'), 'upgrade', 'head']) != 0:
        raise SetupError("There was a problem initializing the Database")




#######################################################
# Matlab
def install_matlab(params, runtime_params, cfg = None):

    if cfg is None:
        cfg = RUNTIME_CFG
    #print params
    matlab_home = which('matlab')
    if matlab_home:
        runtime_params['runtime.matlab_home'] = os.path.abspath(os.path.join (matlab_home, '../..'))

    print ( "CONFIG", cfg )
    runtime_params = modify_site_cfg(MATLAB_QUESTIONS, runtime_params, section=None, cfg=cfg)
    if runtime_params.get ('runtime.matlab_launcher') == 'config-defaults/templates/matlab_launcher_SYS.tmpl':
        if os.name == 'nt':
            runtime_params['runtime.matlab_launcher'] = os.path.abspath(defaults_path ('templates/matlab_launcher_win.tmpl'))
        else:
            runtime_params['runtime.matlab_launcher'] = os.path.abspath(defaults_path ('templates/matlab_launcher.tmpl'))
    else:
        print( "using matlab_launcher ", runtime_params.get ('runtime.matlab_launcher'))

    if  not os.path.exists(runtime_params['runtime.matlab_home']):
        print ( "WARNING: Matlab is required for many modules" )
        runtime_params['matlab_installed'] = False

    #install_matlabwrap(runtime_params)
    return params, runtime_params


def install_matlabwrap(params):
    if  not params['runtime.matlab_home']:
        return

    if getanswer( "Install mlabwrap (need for some analysis)", 'Y',
                  "Install a compiled helper to run matlab scripts.  Matlab must be installed and visible!") != 'Y':
        return

    # Already installed for stats server
    #print "Installing mlabwrap dependencies"
    #retcode = call(['easy_install', 'numpy'])

    print( """untar'ing  mlabwrap from the external directory
    and running python setup.py.. Please watch for errors

    Please visit for more information:

    http://biodev.ece.ucsb.edu/projects/bisquik/wiki/RequiredAndSuggestedSoftware

    """)

    BUILD = to_sys_path("../build")
    if not os.path.exists (BUILD):
        os.mkdir (BUILD)

    tf = tarfile.open (to_sys_path("../external/mlabwrap-1.0.tar.gz"))
    tf.extractall(path = BUILD)
    cwd = os.getcwd()
    os.chdir(os.path.join(BUILD,"mlabwrap-1.0-bisquik"))
    call ([PYTHON, 'setup.py', 'install'])
    os.chdir (cwd)


def install_docker (params, runtime_params, cfg = None):
    """Setup docker runners for modules on system
    """
    if os.name == 'nt':
        return params, runtime_params
    if cfg is None:
        cfg = RUNTIME_CFG

    has_docker = which('docker')
    if getanswer( "Enable docker modules", 'Y' if has_docker else 'N',
                  "Use docker to build and run modules") != 'Y':
        return params, runtime_params


    docker_params = read_site_cfg (cfg, 'docker')
    docker_params  = update_environment (docker_params, prefix="RT__", section="docker", cfg=cfg)
    docker_params['docker.enabled'] = 'true'
    docker_params = modify_site_cfg(DOCKER_QUESTIONS, docker_params, section='docker', cfg=cfg)


    return params, runtime_params

def install_docker_base_images(params, runtime_params, cfg=None):
    if cfg is None:
        cfg = RUNTIME_CFG
    # Ensure base docker images are available
    docker_params = {}
    docker_params = modify_site_cfg(DOCKER_IMAGE_QUESTIONS, docker_params, section='docker', cfg=cfg,append=False)
    devnull = None
    if os.path.exists('/dev/null'):
        devnull = open ('/dev/null')

    for val, _, help in  DOCKER_IMAGE_QUESTIONS:
        image = docker_params.get (val)
        if image:
            retcode = call('docker pull %s' % image, shell=True, stdout=devnull, stderr=devnull)
            if retcode != 0:
                print( "Could not pull " , image)
                print("Please check contrib/docker-base-images", image)

    return params, runtime_params




#######################################################
# Modules

def setup_build_modules (params, runtime_params):
    "Build the local set of modules"
    ans =  getanswer( "Try to Build modules locally", 'Y',
                  "Run the installation scripts on the modules. Some of these require local compilations and have outside dependencies. Please monitor carefullly")
    if ans != 'Y':
        return params, runtime_params

    module_names = params.get ("setup.arguments", None)

    module_dirs = params.get ('bisque.paths.modules', "")
    module_dirs = [ x.strip() for x in module_dirs.split(",") ]
    # Walk any module trees installing modules found
    skipped =[]
    built   =[]
    failed  =[]
    for module_dir in module_dirs:
        if not os.path.exists(module_dir):
            os.makedirs (module_dir)
        sk,bt,fl = install_tree(module_dir, BisqueModule, params, runtime_params)
        skipped.extend(sk)
        built.extend(bt)
        failed.extend(fl)

    if failed:
        print( "Skipped {}: {}".format (len(skipped),",".join(skipped)))
        print ( "Built   {}: {}".format (len(built),  ",".join(built)))
        print ("Failed  {}: {}".format (len(failed), ",".join(failed)))
        params['error_code']=1

    return params, runtime_params


def install_modules(params, runtime_params):
    # Check each module for an install script and run it.
    ans =  getanswer( "Try to install precompiled modules", 'Y', "Setup docker to run precompiled modules")
    if ans != 'Y':
        return params, runtime_params
    fetch_repos (params, 'modules')
    return params, runtime_params

def install_plugins(params, runtime_params):
    # Check each module for an install script and run it.
    ans =  getanswer( "Try to install plugins", 'Y', "Install plugins")
    if ans != 'Y':
        return params, runtime_params
    fetch_repos (params, 'plugins')

    plugin_dirs = params.get ('bisque.paths.plugins', "")
    plugin_dirs = [ x.strip() for x in plugin_dirs.split(",") ]
    print ("INSTALL PLGINS ", plugin_dirs)

    skipped =[]
    built   =[]
    failed  =[]

    for plugin_dir in plugin_dirs:
        sk,bt,fl = install_tree(plugin_dir, BisquePlugin, params, runtime_params)
        skipped.extend(sk)
        built.extend(bt)
        failed.extend(fl)

    if failed:
        print("Skipped {}: {}".format (len(skipped),",".join(skipped)))
        print("Built   {}: {}".format (len(built),  ",".join(built)))
        print("Failed  {}: {}".format (len(failed), ",".join(failed)))
        params['error_code']=1

    return params, runtime_params


def fetch_git (module_url, module_dir):
    """GIT clone/pull repository to local dir
    """
    cmd = [ 'git' ]
    mdir = '.'
    module_branch=None
    if '#' in module_url:
        module_url, module_branch = module_url.split ('#')

    if not os.path.exists (module_dir):
        cmd.extend(['clone', module_url, module_dir])
    else:
        cmd.extend(['pull'])
        mdir = module_dir
    log.debug  ( "calling  %s in  %s", cmd, mdir)
    call (cmd, cwd=mdir)
    if module_branch:
        call (['git', 'checkout', module_branch], cwd=mdir, stdin = io.open(os.devnull))
    version_info = subprocess.check_output(['git', 'log', '--max-count=1'], cwd=mdir)

    return module_dir, version_info

def fetch_mercurial (module_url, module_dir):
    """Mercurial clone/pull repository to local dir
    """
    cmd = [ 'hg' ]
    mdir = '.'
    module_branch=''
    if '#' in module_url:
        module_url, module_branch = module_url.split ('#')
    if not os.path.exists (module_dir):
        cmd.extend ([ 'clone',  module_url, module_dir])
    else:
        cmd.extend (['pull', '-u'])
        mdir = module_dir
    log.debug ( "calling %s in   %s" , cmd, mdir)
    call (cmd, cwd=mdir, stdin = io.open(os.devnull))
    if module_branch:
        call (['hg', 'update', module_branch], cwd=module_dir)
    version_info = subprocess.check_output(['hg', 'tip'] , cwd=mdir)
    return module_dir, version_info

def fetch_tar (module_url, module_dir):
    return module_dir, ''
def fetch_zip (module_url, module_dir):
    return module_dir, ''
def fetch_dir (module_url, module_dir):
    if not os.path.exists (module_url):
        return None
    if os.path.abspath (module_url) != os.path.abspath (module_dir):
        if  os.path.exists (module_dir):
            shutil.rmtree (module_dir)
        shutil.copytree (module_url, module_dir)
    return module_dir, ''

def fetch_svn (module_url, module_dir):
    cmd = [ 'svn' ]
    mdir = '.'
    if '#' in module_url:
        module_url, module_branch = module_url.split ('#')
    if not os.path.exists (module_dir):
        cmd.extend(['checkout', module_url, module_dir])
    else:
        cmd.extend(['update', module_dir])
    log.debug ( "calling  %s in  %s" , cmd, mdir)
    call (cmd, cwd=mdir)
    version_info = subprocess.check_output(['svn', 'log', '--limit', '1' ] , cwd=mdir)
    return module_dir, version_info

REPO_FETCH = {
    'tar' : fetch_tar,
    'zip' : fetch_zip,
    'dir' : fetch_dir,
    }

def check_fetchers ():
    for cmd, fetch in [ ('hg', fetch_mercurial), ('git', fetch_git), ('svn', fetch_svn), ]:
        found = which (cmd)
        if found:
            REPO_FETCH[cmd] = fetch
        else:
            print( "INFO '%s'not found: cannot fetch source repositories with %s " % (cmd,cmd))

def fetch_repos(params, repotype):
    """Get and install modules from remote and local sources

    MOODULE/PLUGIN file syntax
    dir <dir> [ name  ] [ == version/tag/branch ]
    git url[#branch]   [ name ]
    hg  url[#tag or branch]   [ name ]
    tar url   [ name ]
    zip url   [ name ]

    @params params: dictionay of loaded parameters
    @return list of directories with modules
    """
    check_fetchers()

    #wanted_module_names = params.get ("setup.arguments", None)

    repolist = repotype.upper()

    if not os.path.exists(config_path (repolist)):
        shutil.copyfile(defaults_path(repolist), config_path(repolist))
    # Read list of modules trees from config/MODULES
    module_list = config_path(repolist)
    if module_list is None:
        print( "Can't find list of %s to install"  % repotype)
        return params
    module_locations = []
    lineno = 0
    with open(module_list) as repos_list:
        for line in repos_list:
            lineno += 1
            line = line.split ('#',1)[0].strip()
            if not line:
                continue
            module_locations.append( (line, lineno) )
    # Clone any remote repositories
    module_dirs = []
    for module_line, lineno in module_locations:
        module_type, module_url, name, _ = unpack ( [x.strip() for x in module_line.split ()], 3 )
        if module_type not in REPO_FETCH:
            print( "Illegal %s type %s at line %s" % (repotype, module_type, lineno))
            continue
        if not name:
            name = os.path.splitext(os.path.basename(module_url))[0]

        print( "Installing %s %s(s) from %s to %s" % (module_type, repotype, module_url, name))
        module_dir = os.path.join (DIRS[repotype], name)
        if module_dir in module_dirs:
            print( "Skipping duplicated", repotype, module_url)
            continue
        try:
            fetcher = REPO_FETCH.get (module_type)
            module_dir = fetcher (module_url, module_dir)
            if module_dir:
                module_dirs.append (module_dir)
        except Exception:
            log.exception("Problem fetching module")
    #params['bisque.engine_service.module_dirs'] = ", ".join(os.path.abspath (x) for x in module_dirs)
    params['bisque.paths.%s' % repotype ] = DIRS[repotype]
    return params




# def _fetch_update_module (module_type, module_url, name):
#     " Fetch or update module "
#     hg = which('hg')
#     git = which('git')
#     mdir = '.'
#     module_dir = None
#     if git and ( module_url.endswith ('.git') or 'git@' in module_url):
#         cmd =  [ git ]
#         module_dir = os.path.join (DIRS['modules'], os.path.splitext(os.path.basename(module_url))[0])
#         if not os.path.exists (module_dir):
#             cmd.extend(['clone', module_url, module_dir])
#         else:
#             cmd.extend(['pull'])
#             mdir = module_dir
#         print "calling  %s in  %s" % (cmd, mdir)
#         call (cmd, cwd=mdir)
#     elif hg and ( module_url.startswith ('https') or 'hg@' in module_url):
#         cmd = [hg]
#         module_dir = os.path.join (DIRS['modules'], os.path.basename(module_url))
#         if not os.path.exists (module_dir):
#             cmd.extend ([ 'clone', module_url, module_dir])
#         else:
#             cmd.extend (['pull', '-u'])
#             mdir = module_dir
#         print "calling %s in   %s" % (cmd, mdir)
#         call (cmd, cwd=mdir)
#     elif os.path.exists (module_url):
#         module_dir = module_url
#     else:
#         print "Could not determine fetch method for module %s " % module_url
#     return module_dir


def identify_repository_url(url):
    """Determine what sort of repository is at URL
    @param URL: a url string
    @return: 'git','hg', or None
    """
    hg = which('hg')
    git = which('git')
    r = call ([hg, 'identify', url])
    if r == 0:
        return 'hg'
    r = call([git, 'ls-remote', url])
    if r == 0:
        return 'git'
    return None

class BisqueModule (object):
    def __init__(self, module_dir):
        self.module_dir = module_dir
    def check_enabled(self):
        cfg = os.path.join(self.module_dir, 'runtime-module.cfg')
        if not os.path.exists(cfg):
            log.debug ("Skipping %s (%s) : no runtime-module.cfg" , self.module_dir, cfg)
            return False
        cfg = ConfigFile (cfg)
        mod_vars = cfg.get (None, asdict = True)
        log.debug ("module config = %s", mod_vars)
        enabled = mod_vars.get('module_enabled', 'true').lower() in [ "true", '1', 'yes', 'enabled' ]
        ### Check that there is a valid Module descriptor
        if not enabled:
            log.debug ("Skipping %s : disabled" , self.module_dir)
            return False
        return True

    def setup(self, environ):
        "Find and setup a single bisque module:"
        if not os.path.exists(os.path.join(self.module_dir, 'setup.py')):
            print( "setup.py not found in %s" % self.module_dir)
            return False
        cwd = os.getcwd()
        os.chdir (self.module_dir)
        print( "################################")
        print( "Running %s setup.py in %s" % (PYTHON, self.module_dir) )
        try:
            r = call ([PYTHON, '-u', 'setup.py'], env=environ)
            if r == 0:
                return True
            print( "setup in %s returned error %s " ,  self.module_dir, r)
        except Exception as e:
            log.exception ("An exception occured during the module setup: %s" , str(e))
        finally:
            os.chdir (cwd)
        return False

class BisquePlugin (object):
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir
    def check_enabled(self):
        # it's a plgin if ../plugin_name/plugin_name
        return os.path.isdir (os.path.join (self.plugin_dir, os.path.basename (self.plugin_dir)))

    def setup(self, environ):
        "Find and setup a single bisque module:"
        print ("PLUGIN SETUP", self.plugin_dir)
        copydir = True
        if  os.path.exists(os.path.join(self.plugin_dir, 'setup.py')):
            #print( "setup.py not found in %s" % self.plugin_dir)
            # Use standard copy
            copydir = self.call_setup (environ)
        if copydir:
            plugin_js_dir  =  os.path.join (DIRS['public'], 'core', 'plugins', os.path.basename(self.plugin_dir))
            if os.path.exists (plugin_js_dir):
                shutil.rmtree  (plugin_js_dir)
            #os.makedirs (plugin_js_dir)

            # Copydir is ../path/<plugname>/<plugname>
            src_plugin = os.path.join (self.plugin_dir, os.path.basename(self.plugin_dir))
            if not os.path.exists (src_plugin):
                print ("bad plugin structure.. missing ", src_plugin)
                return False
            print ("COPY ", src_plugin, " to ", plugin_js_dir)
            shutil.copytree (src_plugin, plugin_js_dir)
        else:
            print ("Skipped copying of ",  self.plugin_dir)
            return False

        return True


    def call_setup(self, environ):
        cwd = os.getcwd()
        os.chdir (self.plugin_dir)
        print( "################################")
        print( "Running %s setup.py in %s" % (PYTHON, self.plugin_dir) )
        try:
            r = call ([PYTHON, '-u', 'setup.py'], env=environ)
            if r == 0:
                return True
            print( "setup in %s returned error %s " ,  self.plugin_dir, r)
        except Exception as e:
            log.exception ("An exception occured during the module setup: %s" , str(e))
        finally:
            os.chdir (cwd)
        return False


def install_tree(module_root, install_class, params, runtime_params):
    """Find and install module based at MODULE_ROOT
    """
    environ = dict(os.environ)
    environ.pop ('DISPLAY', None) # Makes matlab hiccup
    environ['BISQUE_ROOT'] = os.getcwd()

    module_names = params.get ("setup.arguments", None)

    failed    = []
    completed = []
    skipped   = []
    print( "Checking %s for modules" % module_root)
    for root, dirs, files in os.walk(module_root):
        module_directory = root
        dirname = os.path.basename (module_directory)
        if module_names and dirname not in module_names:
            print( "Skipping {0}. Not in {1}".format (dirname, module_names))
            continue
        installer = install_class (module_directory)
        if installer.check_enabled ():
            if installer.setup(environ):
                completed.append (module_directory)
            else:
                failed.append (module_directory)
            continue
        skipped.append (module_directory)

        # for module_file in files:
        #     if module_file == 'runtime-module.cfg':
        #         module_directory = os.path.dirname (os.path.join (root, module_file))
        #         dirname = os.path.basename (module_directory)
        #         if module_names and dirname not in module_names:
        #             print( "Skipping {0}. Not in {1}".format (dirname, module_names))
        #             continue
        #         installer = install_class (module_directory)
        #         if installer.check_enabled ():
        #             if installer.setup(environ):
        #                 completed.append (module_directory)
        #             else:
        #                 failed.append (module_directory)
        #             continue
        #         skipped.append (module_directory)
    return skipped, completed, failed





#######################################################
# initial configuration files

def install_server_defaults(params, runtime_params):
    "Install initial configuration for a bisque server"
    print( "Server config")
    new_install = False

    if not os.path.exists(config_path('server.ini')):
        shutil.copyfile(defaults_path('server.ini.default'), config_path('server.ini'))

    if not os.path.exists(config_path('shell.ini')):
        shutil.copyfile(defaults_path('shell.ini.default'), config_path('shell.ini'))

    if not os.path.exists(config_path('who.ini')):
        shutil.copy(defaults_path('who.ini.default'), config_path('who.ini'))


    if not os.path.exists(config_path('registration.cfg')):
        shutil.copyfile(defaults_path('registration.cfg.default'), config_path('registration.cfg'))

    if not os.path.exists(SITE_CFG):
        params = install_cfg(SITE_CFG, section=BQ_SECTION, default_cfg=defaults_path('site.cfg.default') )
        params.update(SITE_VARS)
        new_install = True

        for k, v  in list(DIRS.items()):
            params["bisque.paths.%s" % k] = v

    params = update_environment (params, "BQ__")

    print( "Top level site variables are:")
    for k in sorted(SITE_VARS.keys()):
        if k not in params:
            params[k] = SITE_VARS[k]
        print( "  %s=%s" % (k,params[k]))

    if getanswer("Change a site variable", 'Y' if new_install else 'N') == 'Y':
        params = modify_site_cfg(SITE_QUESTIONS, params)

        path = urllib.parse.urlparse(params['bisque.server']).path
        params['bisque.root'] = path

    if new_install:
        # Update the installation directories
        for k, v  in list(DIRS.items()):
            params["bisque.paths.%s" % k] = v
        update_site_cfg(params, section=BQ_SECTION)

        #server_params = {'h1.url' : params['bisque.server']}
        #server_params = update_site_cfg(server_params, 'servers', append=False)

    if getanswer ('Do you want to create new server configuations', 'Y',
                  "Use an editor to edit the server section (see http://biodev.ece.ucsb.edu/projects/bisquik/wiki/Installation/ParsingSiteCfg )") == 'Y':
        setup_server_cfg(params, runtime_params)

    return params, runtime_params


def setup_server_cfg (params, runtime_params):
    'Edit the server section of the site.cfg'

    server_params = read_site_cfg (SITE_CFG, 'servers')
    pprint.pprint (server_params)
    previous_backend = server_params['backend']

    #status = 0
    #if getanswer ('Edit servers in site.cfg ', 'N',
    #              "Please edit only the server section ") != 'N':
    #    editor = os.environ.get ('EDITOR', which ('vi'))
    #    if editor is not None:
    #        status = subprocess.call ([editor, SITE_CFG])
    #    else:
    #        print "No editor found. Please set EDITOR"
    #        return

    #if status != 0:
    #    print "GOT status", status
    #    return params


    server_params = modify_site_cfg (SERVER_QUESTIONS,  server_params, section='servers', append=False)
    if server_params['backend'] == 'uwsgi':
        params, server_params = setup_uwsgi(params, server_params)
    if server_params['backend'] == 'paster':
        params, server_params = setup_paster(params, server_params)
    return params, runtime_params



def install_engine_defaults(params, runtime_params):
    "Install initial configuration for a bisque engine"
    print( "Engine config")
    new_install = False

    if not os.path.exists(config_path('server.ini')):
        shutil.copyfile(defaults_path('server.ini.default'), config_path('server.ini'))

    if not os.path.exists(config_path('shell.ini')):
        shutil.copyfile(defaults_path('shell.ini.default'), config_path('shell.ini'))

    if not os.path.exists(config_path('who.ini')):
        shutil.copy(defaults_path('who.engine.ini'), config_path('who.ini'))

    if not os.path.exists(SITE_CFG):
        params = install_cfg(SITE_CFG, section=BQ_SECTION, default_cfg=defaults_path('engine.cfg.default'))
        params.update(ENGINE_VARS)
        new_install = True

    if not os.path.exists(RUNTIME_CFG):
        runtime_params = install_cfg(RUNTIME_CFG, section=None, default_cfg=defaults_path('runtime-bisque.default'))

    print( "Top level site variables are:")
    for k in sorted(ENGINE_VARS.keys()):
        if k not in params:
            params[k] = ENGINE_VARS[k]
        print( "  %s=%s" % (k,params[k]))

    if getanswer("Change a site variable", 'N')=='Y':
        params = modify_site_cfg(ENGINE_QUESTIONS, params)

    server_params = {  'e1.url' : params['bisque.engine'], }
    server_params = update_site_cfg(server_params, 'servers', append=True )
    pprint.pprint (server_params)

    if getanswer("Update servers", 'Y' if new_install else 'N', 'Modify [server] section of site.cfg') == 'Y':
        params.update(server_params)
    else:
        print( "Warning: Please review the [server] section of site.cfg after modifying site variables")
    return params, runtime_params



def install_proxy(params, runtime_params):
    if getanswer('Configure bisque with proxy', 'N',
                 ("Multiple bisque servers can be configure behind a proxy "
                  "providing enhanced performance.  As this an advanced "
                  "configuration it is only suggested for experienced "
                  "system administrators")) == 'Y':
        print ("See site.cfg comments and contrib/apache/proxy-{http,ssl} "
               "for details. Also see the website "
               "http://biodev.ece.ucsb.edu/projects/bisquik/wiki/AdvancedInstalls")
    return params, runtime_params


def update_environment(params, prefix, section = BQ_SECTION, cfg=None):
    """Process the environments parameters listed by PREFIX i.e. BQ__, or RT__
    and update the params
    """
    # Process env
    newenv = {}
    for k,v in list(os.environ.items()):
        if k.startswith (prefix):
            k = remove_prefix(k, prefix).replace('__', '.').lower()
            print("env ",  k,v)
            newenv[k] = v
            params [k] = v
    if newenv:
        print( "ENV REPLACED", newenv)
        update_site_cfg(params, section=section, cfg=cfg)
    return params



#######################################################
#
def check_condor (params, runtime_params, cfg  = None):
    if cfg is None:
        cfg = RUNTIME_CFG
    try:

        if os.path.exists('/dev/null'):
            devnull = open ('/dev/null')
        else:
            import tempfile
            devnull = tempfile.TemporaryFile(mode='w')

        retcode = call ([ 'condor_status' ], stdout=devnull, stderr=devnull )
    except OSError:
        print( "No condor was found. See bisque website for details on using condor")
        return params, runtime_params
    print( "Condor job management software has been found on your system")
    print( "Bisque can use condor facilities for some module execution")

    # Check BISQUE_CONDOR_ENABLED
    dval = check_env (None, 'condor.enabled') or 'true'
    dval = TRUE_RESPONSE.get (dval.lower(), 'N')
    if getanswer("Configure modules for condor", dval,
                 "Configure condor shared directories for better performance")=="Y":
        if 'condor' not in runtime_params['runtime.platforms']:
            runtime_params['runtime.platforms'] = ','.join (['condor', runtime_params['runtime.platforms']])

        print( """
        NOTE: condor configuration is complex and must be tuned to
        every instance.  Bisque will try to use the condor facilities
        but please check that this is operating correctly for your
        installation

        Please check the wiki at biodev.ece.ucsb.edu/projects/bisquik/wiki/AdvancedInstalls#CondorConfiguration
        """)

        runtime_params = read_site_cfg(cfg=cfg, section='condor', )
        runtime_params['condor.enabled'] = "true"
        #print params
        if getanswer("Advanced Bisque-Condor configuration", "N",
                     "Change the condor templates used for submitting jobs")!='Y':
            for f in ['condor.dag_template', 'condor.submit_template', 'condor.dag_config_template']:
                if os.path.exists(runtime_params[f]):
                    runtime_params[f] = os.path.abspath(runtime_params[f])

            update_site_cfg(runtime_params, section="condor", cfg=cfg)
            return params, runtime_params

        runtime_params = modify_site_cfg(CONDOR_QUESTIONS, runtime_params, section='condor', cfg=cfg)
        for v, d, h in CONDOR_QUESTIONS:
            if runtime_params[v]:
                runtime_params[v] = os.path.abspath(os.path.expanduser(runtime_params[v]))
                print( "CONDOR", v, runtime_params[v])
        update_site_cfg(runtime_params, section="condor", cfg=cfg)

    return params, runtime_params



def install_runtime(params, runtime_params, cfg = None):
    """Check and install runtime control files"""

    if cfg is None:
        cfg = RUNTIME_CFG

    runtime_params['runtime.platforms'] = "command"
    check_condor(params, runtime_params, cfg=cfg)

    runtime_params['runtime.staging_base'] = run_path('staging')
    runtime_params = modify_site_cfg(RUNTIME_QUESTIONS, runtime_params, section=None, cfg=cfg)
    staging=runtime_params['runtime.staging_base'] = os.path.abspath(os.path.expanduser(runtime_params['runtime.staging_base']))

    update_site_cfg(runtime_params, section=None, cfg=cfg)

    # for bm in os.listdir (bisque_path('modules')):
    #     modpath = bisque_path('modules', bm)
    #     if os.path.isdir(modpath) and os.path.exists(os.path.join(modpath, "runtime-module.cfg")):
    #         cfg_path = os.path.join(modpath, 'runtime-bisque.cfg')
    #         copy_link(RUNTIME_CFG, cfg_path)
    try:
        if not os.path.exists(staging):
            os.makedirs(staging)
    except OSError as e:
        print( "%s does not exist and cannot create: %s" % (staging, e))

    return params, runtime_params


#######################################################
#
if MAILER=='marrow.mailer':
    MAIL_QUESTIONS = [
        ('mail.transport.use', "Enter mail transport", "Mail transport", "smtp"),
    ]
    SMTP_QS = [
        ('mail.transport.host', "Enter your smtp mail server",
         "The mail server that delivers mail.. often localhost"),
        ('mail.transport.username', "A login for authenticated smtp", "Usernmae"),
        ('mail.transport.password.', "A login password for authenticated smtp", "password"),
        ('mail.transport.tls', "Use TLS", "Use TLS", 'false'),
    ]
if MAILER=='turbomail':
    MAIL_QUESTIONS = [
        ('mail.smtp.server', "Enter mail transport", "Mail transport"),
    ]
    SMTP_QS = []

def install_mail(params, runtime_params):
    params['mail.smtp.server'] = os.getenv('MAIL_SERVER', params['mail.smtp.server'])


    if getanswer ("Enable mail delivery","Y",
                  """
                  The system requires mail delivery for a variety of operations
                  including user registration and sharing notifications.
                  This section allows you to configure the mail system""" )!="Y":
        params['mail.on'] =  'False'
        return params, runtime_params
    params['mail.on'] = 'True'
    params = modify_site_cfg (MAIL_QUESTIONS, params)
    if params.get ('mail.transport.use') == 'smtp':
        params = modify_site_cfg (SMTP_QS, params)

    print( "Please review/edit the mail.* settings in site.cfg for you site""")
    return params, runtime_params

#######################################################

def install_preferences(params, runtime_params):
    if asbool(params.get('new_database')): #already initialized
        return params, runtime_params

    if getanswer ("Initialize Preferences ","Y",
                  """Initialize system preferences.. new systems will requires this while, upgraded system may depending on changes""")!="Y":
        return params, runtime_params

    cmd = [bin_path('bq-admin'), 'preferences', 'init', ]
    if getanswer("Force initialization ", "N", "Replace any existing preferences with new ones") == "Y":
        cmd.append ('-f')
    r  = subprocess.call (cmd, stderr = None)
    if r!=0:
        print( "Problem initializing preferences.. please use bq-admin preferences")
    return params, runtime_params


#######################################################

def install_public_static(params, runtime_params):
    "Setup up public JS area with all static resources"

    if getanswer("Deploy all static resources to public directory", "Y",
                 "Usefull for integrating with frontend webserverv") == 'Y':
        cmd = [bin_path('bq-admin'), 'deploy', '--packagedir=%s'%DIRS['jslocation'],
               run_path ('public') ]
        r  = subprocess.call (cmd, stderr = None)
        if r!=0:
            print( 'Problem deploying static resources... run "bq-admin deploy public" manually')

    return params, runtime_params

#######################################################

def install_secrets(params, runtime_params):
    "Ensure cookies are unique across sites"

    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    secrets = os.getenv ("BISQUE_SECRET", None) or id_generator(8)
    secrets = getanswer("Encrypt cookies with secret phrase", secrets,
                        "Login informations if encoded with this secret")
    who_cfg = config_path ("who.ini")

    update_site_cfg(cfg=who_cfg, section='plugin:auth_tkt', bisque_vars= { 'secret' : secrets })
    # Update the beaker session secret also
    update_site_cfg(bisque_vars= { 'beaker.session.secret' : secrets }, append=False)
    params ['beaker.session.secret'] = secrets
    return params, runtime_params


#######################################################
#
def setup_uwsgi(params, server_params):
    if getanswer("Install (update) uwsgi config (application server and configs)", 'Y',
                 "Uwsgi can act as backend server when utilized with web-front end (Nginx)") != 'Y':
        return params
    if which ('uwsgi') is None:
        #easy_install.main(['-U','uwsgi'])
        pipmain (['install', '-U','uwsgi']) #pylint: disable=no-member

    from bq.util.dotnested import parse_nested, unparse_nested
    servers = [ x.strip() for x in server_params['servers'].split(',') ]
    for server in servers:
        server_params.setdefault(server + '.bisque.static_files', 'false')
        questions = [ (server+'.'+q[0], server+': '+q[1], q[2]) for q in UWSGI_QUESTIONS ]
        server_params = modify_site_cfg (questions, server_params, section="servers", append=False)
    servers =  parse_nested (server_params, servers)
    log.debug ( "AFTER Q %s", servers)
    for server, sv in list(servers.items()):
        cfg = config_path ("%s_uwsgi.cfg" % server)

        if os.path.exists (cfg) and os.path.exists(SITE_CFG):
            cfg_time  = os.stat(cfg).st_mtime
            site_time = os.stat (SITE_CFG).st_mtime
            if cfg_time - site_time > 60:
                if getanswer ("%s looks newer than %s.. modify" % (cfg, SITE_CFG), "N",
                              "%s may have special modifications" %cfg) == "N":
                    continue
        install_cfg (cfg, section="*", default_cfg=defaults_path ('uwsgi.cfg.default'))
        print( "Created uwsgi config: ", cfg)

        uwsgi_vars = sv.pop ('uwsgi', {})
        bisque_vars = sv.pop ('bisque', {})
        paster_vars = sv.pop ('paster', {})
        url = sv.pop ('url')

        if 'socket' in uwsgi_vars:
            uwsgi_vars['socket'] =  uwsgi_vars['socket'].replace('unix://','').strip()

        svars = { #'bisque.root' : sv['url'],
                  'bisque.server' : url,
                  'bisque.services_disabled' : sv.pop ('services_disabled', ''),
                  'bisque.services_enabled'  : sv.pop ('services_enabled', ''),
                }

        for k,v in unparse_nested (bisque_vars):
            svars["bisque.%s" % k] = v

        # put other vars backinto bisque area
        svars.update ( unparse_nested(sv) )

        uwsgi_vars ['virtualenv'] = DIRS['virtualenv']
        uwsgi_vars ['procname-prefix'] = "bisque_%s_" % server
        update_site_cfg(cfg=cfg, bisque_vars=svars)
        update_site_cfg(cfg=cfg, section='uwsgi',bisque_vars = uwsgi_vars )
        update_site_cfg(cfg=cfg, section='sa_auth',
                        bisque_vars = { 'cookie_secret' : uuid.uuid4()} )
    return params, server_params

#######################################################
#
def setup_paster(params, server_params):
    if getanswer("Install (update) paster configs (application server and configs)", 'Y',
                 "Paster is the default backend server") != 'Y':
        return params

    print("PARAMS",  server_params)

    from bq.util.dotnested import parse_nested, unparse_nested
    servers = [ x.strip() for x in server_params['servers'].split(',') ]
    for server in servers:
        server_params.setdefault(server + '.bisque.static_files', 'true')
        questions = [ (server+'.'+q[0], server+': '+q[1], q[2]) for q in PASTER_QUESTIONS ]
        server_params = modify_site_cfg (questions, server_params, section="servers", append=False)
    servers =  parse_nested (server_params, servers)
    #print "AFTER Q", servers

    for server, sv in list(servers.items()):

        cfg = config_path ("%s_paster.cfg" % server)
        if os.path.exists (cfg) and os.path.exists(SITE_CFG):
            cfg_time  = os.stat(cfg).st_mtime
            site_time = os.stat (SITE_CFG).st_mtime
            if cfg_time - site_time > 60:
                if getanswer ("%s looks newer than %s.. modify" % (cfg, SITE_CFG), "N",
                              "%s may have special modifications" %cfg) == "N":
                    continue
        install_cfg (cfg, section="*", default_cfg=defaults_path('server.ini.default'))
        print( "Created paster config: ", cfg)

        uwsgi_vars = sv.pop ('uwsgi', {})
        paster_vars = sv.pop ('paster', {})
        bisque_vars = sv.pop ('bisque', {})
        url = sv.pop ('url')

        svars = { #'bisque.root' : sv['url'],
                  'bisque.server' : url,
                  'bisque.services_disabled' : sv.pop ('services_disabled', ''),
                  'bisque.services_enabled'  : sv.pop ('services_enabled', ''),
                }

        for k,v in unparse_nested (bisque_vars):
            svars["bisque.%s" % k] = str(v)

        # put other vars backinto bisque area
        svars.update ( unparse_nested(sv) )

        log.debug ( "BVARS %s", bisque_vars)
        log.debug ( "SVARS %s", svars)

        #svars.update (bisque_vars)

        fullurl = urllib.parse.urlparse (url)
        if 'host' not in paster_vars:
            paster_vars['host'] = fullurl[1].split(':')[0]
        if 'port' not in paster_vars:
            paster_vars['port'] = str(fullurl.port)

        update_site_cfg(cfg=cfg, bisque_vars=svars)
        update_site_cfg(cfg=cfg, section='server:main',bisque_vars = paster_vars )
        update_site_cfg(cfg=cfg, section='sa_auth',
                        bisque_vars = { 'cookie_secret' : uuid.uuid4()} )


    return params, server_params
#######################################################
#

STORES_QUESTIONS=[
    ('bisque.blob_service.stores', 'Stores to be configured', 'A list of simple names of stores lile "images"')]


STORE_QUESTIONS=[
    ( 'mounturl', 'The location of the external store', 'file:// or irods:// or s3://'),
    ( 'readonly', 'The store is readonly', 'true or false', 'false'),
    ( 'paths',    'Paths are stored', 'true or false', 'true'),
    ]
DRIVER_QS =  {
    'file': [ ('top', 'top store if using macros',
               'i.e. top = file://$datadir/blobdir/ for file://$datadir/imagedir/$user/')],
    's3': [ ('credentials', '<AWS_KEY>:<AWS_SECRET>', ''),
            ('bucket_id', 'The bucket id', ''),
            ('location', 'a location string', 'us-west-1, us-west-2, sa-east-1, EU, ap-northeast-1, etc', 'us-west-2'),],
    'irods': [ ('credentials', ' <user>:<pass> pair', '')]
}


def setup_stores(params, runtime_params):
    """Stores """
    if getanswer("Install Stores", 'Y',
                 "Setup Stores use of external storage ") != 'Y':
        return params, runtime_params

    #print params

    params = modify_site_cfg (STORES_QUESTIONS, params,  append=False)
    from bq.util.dotnested import parse_nested, unparse_nested
    stores = [ x.strip() for x in params['bisque.blob_service.stores'].split(',') ]
    for store in stores:
        count = 0
        while count < 2:
            questions = [ ('bisque.stores.%s.%s' %(store,q[0]), store+': '+q[1], q[2],q[3])
                          for q in ensure_default(STORE_QUESTIONS) ]
            params = modify_site_cfg (questions, params,  append=False)
            scheme = urllib.parse.urlparse(params.get ('bisque.stores.%s.mounturl' %store)).scheme
            if scheme not in DRIVER_QS:
                print( "Invalide driver must be one of:", list(DRIVER_QS.keys()))
                count+=1
                if count == 2:
                    print( "Removing ", store, " from store list")
                    stores.remove (store)
                    params['bisque.blob_service.stores'] = ",".join (stores)
                continue
            questions = [ ('bisque.stores.%s.%s' %(store,q[0]), store+': '+q[1], q[2],q[3])
                          for q in ensure_default( DRIVER_QS[scheme])]
            params = modify_site_cfg (questions, params,  append=False)
            break

    #stores =  parse_nested (params, ['bisque.stores.%s' % store for store in stores])
    #print "AFTER Q", stores

    #for store, sv in stores.items():
    #    print store, sv

    return params, runtime_params



def setup_logins (params, runtime_params):
    if getanswer("Change login options", 'Y',
                 "Setup local login option  ") != 'Y':
        return params, runtime_params

    params = modify_site_cfg (LOGIN_QUESTIONS, params,  append=False)

    return params, runtime_params

#######################################################
#

def _sha1hash(data):
    return hashlib.sha1(data).hexdigest().upper()

def fileretrieve(fetch_url, dest, sha1=None):

    filehash = sha1 and hashlib.sha1()
    r = requests.get (fetch_url, stream=True)
    if r.status_code != 200:
        raise Exception ("Could not read file from %s", fetch_url)
    with open (dest, 'wb') as f:
        for chunk in r.iter_content(chunk_size=64*1024):
            if chunk:
                f.write(chunk)
                if sha1:
                    filehash.update (chunk)
        if sha1 and sha1 != filehash.hexdigest().upper():
            os.remove (dest)
            raise Exception('hash mismatch in %s' % dest)

    # Set the time to Server File  time.
    try:
        mtime = parse (r.headers['Last-Modified']).astimezone(tz.tzlocal())
        srv_lastmodified = time.mktime(mtime.timetuple())
        touch (dest, (srv_lastmodified, srv_lastmodified))
    except (KeyError, ValueError) as _:
        pass

    return dest


def install_external_binaries (params, runtime_params):
    """Read EXTERNAL_FILES for binary file names (with prepended hash)
    and download from external site.  Allows binary files to be distributed
    with source code

    Syntax
    """

    def fetch_file (hash_name, where, localname=None):
        sha1, name = hash_name.split ('-', 1)
        if localname is not None:
            name = localname
        if os.path.isdir (where):
            dest = os.path.join(where,name)
        else:
            dest = where
        if os.path.exists(dest):
            with  open(dest, 'rb') as f:
                shash = _sha1hash (f.read())
            if sha1 == shash:
                print( "%s found locally" % name)
                return

        fetch_url = urllib.parse.urljoin(EXT_SERVER,  hash_name)
        print( "Fetching %s" % fetch_url)
        fileretrieve (fetch_url, dest, sha1)


    if getanswer ("Fetch external binary files from Bisque development server",
                  "Y",
                  "This action is required only on first download") != 'Y':
        return params, runtime_params

    if not os.path.exists(DIRS['depot']):
        os.makedirs (DIRS['depot'])
    conf = ConfigFile(defaults_path('EXTERNAL_FILES'))
    external_files = conf.get ('common')
    #local_platform = platform.platform()
    local_platform = platform.platform().replace('-', '-%s-'%platform.architecture()[0], 1) # dima: added 64bit
    for section in conf.section_names():
        if fnmatch.fnmatch(local_platform, section):
            print( "Matched section %s" % section)
            external_files.extend (conf.get (section))
    for  line in [ f.strip().split('=') for f in external_files]:
        lname = None
        fname = line.pop(0)
        if len(line):
            lname =line.pop(0)
        if fname:
            try:
                fetch_file (fname, DIRS['depot'], lname)
            except Exception as e:
                log.exception ("Problem in fetch")
                print( "Failed to fetch '%s' with %s" % (fname,e))

    return params, runtime_params

#######################################################
#
def uncompress_dependencies (archive, filename_dest, filename_check, strip_root=None):
    """Install dependencies that aren't handled by setup.py"""

    if os.path.exists(filename_check) and os.path.getmtime(archive) < os.path.getmtime(filename_check):
        return

    print( "Unpacking %s into %s"  % (archive, filename_dest))
    if tarfile.is_tarfile(archive):
        return tarfile.open(archive).extractall (filename_dest)
    else:
        return unpack_zip(archive, filename_dest, strip_root)

def uncompress_extjs (extzip, public, extjs):
    """Install extjs"""

    if os.path.exists(extjs) and os.path.getmtime(extzip) < os.path.getmtime(extjs):
        return

    print( "Unpacking %s into %s"  % (extzip, public))

    names = unpack_zip(extzip, public)
    if os.path.exists(extjs):
        shutil.rmtree(extjs)
    # Move whatever dir name you found in the names to "public/extjs"
    topdir = names and names[0].split('/',1)[0] or "extjs-4.0.0"
    unpackdir = to_sys_path('%s/%s' % (public, topdir))
    while not os.path.exists(unpackdir):
        print( "Couldn't find top level dir of %s" % extzip)
        unpackdir = getanswer("Dirname in %s " % public,
                              unpackdir,
                              "Will rename whater top level dir to extjs")
    shutil.move (unpackdir, extjs)

def install_dependencies (params, runtime_params):
    """Install dependencies that aren't handled by setup.py"""

    # install ExtJS
    extzip = os.path.join(DIRS['depot'], 'extjs.zip')
    public = to_sys_path(os.path.join (DIRS['jslocation'], 'bq/core/public'))
    extjs =  os.path.join (public, "extjs")
    uncompress_extjs (extzip, public, extjs)
    for skip in ('docs', 'examples', 'builds', '.sencha', 'cmd', 'locale', 'packages', 'plugins', 'src', 'welcome'):
        if os.path.exists (os.path.join(extjs, skip)):
            shutil.rmtree (os.path.join(extjs, skip))


    install_imgcnv()
    install_imarisconvert()
    install_openslide()
    install_bioformats()

    return params, runtime_params


#######################################################
# Image Converters

def install_imgcnv ():
    """Install dependencies that aren't handled by setup.py"""

    filename_zip = os.path.join(DIRS['depot'], 'imgcnv.zip')
    imgcnv = which('imgcnv')
    if imgcnv :
        r, version = call ([ imgcnv, '-v'], capture = True)
        if r == 0:
            print( "Found imgcnv version %s" % version)
        if  not os.path.exists(filename_zip):
            print( "Imgcnv is installed and no-precompiled version exists. Using installed version")
            return

    if not os.path.exists(filename_zip):
        print ("""No pre-compiled version of imgcnv exists for your system
        Please visit biodev.ece.ucsb.edu/projects/imgcnv
        or visit our mailing list https://groups.google.com/forum/#!forum/bisque-bioimage
        for help""")
        return


    if getanswer ("Install Bio-Image Convert", "Y",
                  "imgcnv will allow image server to read pixel data") == "Y":

        filename_check = os.path.join(DIRS['bin'], 'imgcnv%s'% SCRIPT_EXT)
        uncompress_dependencies (filename_zip, DIRS['bin'], filename_check)

def install_openslide ():
    """Install dependencies that aren't handled by setup.py"""

    archive = os.path.join(DIRS['depot'], 'openslide-bisque%s' % ARCHIVE_EXT)
    if not os.path.exists(archive):
        print( "No pre-compiled version of openslide exists for your system")
        print( "Please visit our mailing list https://groups.google.com/forum/#!forum/bisque-bioimage for help")
        return
    if getanswer ("Install OpenSlide converter", "Y",
                  "OpenSlide will allow image server to read full slide pixel data") == "Y":
        uncompress_dependencies (archive, DIRS['bin'], '')


def install_bioformats():

    archive = os.path.join(DIRS['depot'], 'bioformats-pack.zip')
    filename_check = os.path.join(DIRS['bin'], 'bioformats_package.jar')

    if not newer_file(archive, filename_check):
        print( "Bioformats is up to date")
        return

    if getanswer ("Install bioformats", "Y",
                  "Bioformats can be used as a backup to read many image file types") == "Y":

        old_bf_files = [
            'bfconvert', 'bfconvert.bat', 'bfview', 'bfview.bat', 'bio-formats.jar',
            'domainlist', 'domainlist.bat', 'editor', 'editor.bat', 'formatlist',
            'formatlist.bat', 'ijview', 'ijview.bat', 'jai_imageio.jar', 'list.txt',
            'loci_plugins.jar', 'loci_tools.jar', 'loci-common.jar', 'loci-testing-framework.jar',
            'log4j.properties', 'lwf-stubs.jar', 'mdbtools-java.jar', 'metakit.jar', 'notes',
            'notes.bat', 'ome_plugins.jar', 'ome_tools.jar', 'ome-editor.jar', 'ome-io.jar',
            'omeul', 'omeul.bat', 'ome-xml.jar', 'poi-loci.jar', 'scifio.jar', 'showinf',
            'showinf.bat', 'tiffcomment', 'tiffcomment.bat', 'xmlindent', 'xmlindent.bat', 'xmlvalid', 'xmlvalid.bat'
        ]

        # first remove old files
        for f in old_bf_files:
            p = os.path.join(DIRS['bin'] ,f)
            if os.path.exists(p):
                os.remove(p)

        biozip = zipfile.ZipFile (archive)
        mask = stat.S_IXUSR|stat.S_IRUSR|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH
        for fname in  biozip.namelist():
            if fname[-1] == '/':  # skip dirs
                continue
            dest = os.path.join(DIRS['bin'], os.path.basename(fname))

            data = biozip.read(fname)
            fd = open(dest, 'wb')
            fd.write(data)
            if not fname.endswith ('jar'):
                os.chmod (dest, os.fstat(fd.fileno()).st_mode|mask)  # User exec
            fd.close()

        # python >2.6
        #biozip.extractall(os.path.join(BQENV, "bin"))
        biozip.close()

def install_imarisconvert ():
    """Install dependencies that aren't handled by setup.py"""

    archive = os.path.join(DIRS['depot'], 'ImarisConvert%s' % ARCHIVE_EXT)
    if not os.path.exists(archive):
        print( "No pre-compiled version of ImarisConvert exists for your system")
        print( "Please visit our mailing list https://groups.google.com/forum/#!forum/bisque-bioimage for help")
        return
    filename_check = which ("ImarisConvert")
    filename_check = filename_check or os.path.join (DIRS['bin'], 'ImarisConvert%s' % SCRIPT_EXT)
    if not newer_file(archive, filename_check) :
        print( "ImarisConvert is up to date")
        return
    if  getanswer ("Install ImarisConvert", "Y",
                      "ImarisConvert will allow image server to read many image formats") == "Y":
        uncompress_dependencies (archive, DIRS['bin'], filename_check)
        touch (filename_check)

############################
# Features server deps


def install_features (params, runtime_params):
    """Install dependencies that aren't handled by setup.py"""

    if getanswer ("Install feature extractors (Feature Server)", "Y",
                  "Feature extractors will enable many descriptors in the Feature Server that require binary code") == "Y":

        filename_zip = os.path.join(DIRS['depot'], 'feature_extractors.zip')
        filename_dest = to_sys_path(run_path('bqfeature', 'bq'))
        filename_check = ''
        uncompress_dependencies (filename_zip, filename_dest, filename_check)

        install_features_source()
        install_libtiff()
        install_opencv()

    return params, runtime_params


def install_features_source ():
    """Install dependencies that aren't handled by setup.py"""

    if getanswer ("Install source code for feature extractors", "N",
                  "Feature descriptors source code will allow recompiling external feature extractors on unsupported platforms") == "Y":

        filename_zip = os.path.join(DIRS['depot'], 'feature_extractors_source.zip')
        fileretrieve('https://bitbucket.org/CBIucsb/featureextractors/get/default.zip', filename_zip)
        filename_dest = to_sys_path('bqfeature/bq/src')
        filename_check = ''
        uncompress_dependencies (filename_zip, filename_dest, filename_check, strip_root=True)

        print( """Now you can recompile feature extractors. Follow instructions located in:
          bqserver/bq/features/src/extractors/build/Readme.txt
        """)

def install_libtiff():
    """
        Install dependencies that aren't handled by setup.py

        Downloads and installs libtiff-4.0.3 in sitepackages in bqenv/Scripts

        Only for Windows, for debian linux use apt-get
    """
    src = 'https://bitbucket.org/CBIucsb/pylibtiff/downloads/LibTiff-4.0.3-Windows-64bit.zip'
    filename_zip = os.path.join(DIRS['depot'], 'LibTiff-4.0.3-Windows-64bit.zip')
    #filename_dest = bisque_path(os.path.join('bqenv','Scripts'))
    filename_check = ''

    if sys.platform == 'win32':
        if getanswer ("Install libtiff-4.0.3", "Y",
                      "Enables reading OME-bigtiff for feature extraction") == "Y":
            print( 'Fetching from %s'%src)

            fileretrieve (src, filename_zip)
            uncompress_dependencies ( filename_zip, DIRS['bin'], filename_check, strip_root=True)
            print('Installed libtiff-4.0.3 in %s'% DIRS['bin'])
    else:
        print( """To enable the feature service to read OME-bigtiff for feature extraction install
        libtiff4
        For Debian use the command apt-get install libtiff5-dev
        """)

def install_opencv():
    """
        Install dependencies that aren't handled by setup.py

        Downloads and installs opencv in sitepackages in bqenv
    """

    def extract_archive_dir(zip_file,zip_dir,destination,verbose = True):
        """
            unzips files in dir in the zipfile
            warning: can not extract a dir in that dir
            @zip_file - name of the zip file
            @zip_dir - path to the dir in the zip file from the root file in the zip
            @destination - dir were the extracted files will be placed
            @verbose

            @output - none
        """

        #with zipfile.ZipFile(zip_file, 'r') as z:  # KGK Not available in 2.6
        z =  zipfile.ZipFile(zip_file, 'r')
        for f in z.namelist():
            if os.path.normpath(f).startswith(zip_dir) and not os.path.normpath(f) == zip_dir:
                with open(os.path.join(destination,os.path.relpath(f, zip_dir)), 'wb') as fout:
                    fout.write(z.read(f))
                    if verbose:
                        print( 'Extracted %s -> %s'%(f,os.path.join(destination,os.path.relpath(f, zip_dir))))


    if getanswer ("Install OpenCV-2.4.6", "Y",
                  "Enables descriptors in the Feature Server that use OpenCV-2.4.6") == "Y":

        filename_check = ''
        python_version = sys.version_info[:2]
        if not (python_version==(2,6) or python_version==(2,7)):
            print('Failed to install opencv. Requires python 2.6 or 2.7.')
            return
        filename_zip = os.path.join(DIRS['depot'], 'opencv-2.4.6.zip')
        if sys.platform.startswith ('win'): #windows
            extract_archive_dir(filename_zip,os.path.join('opencv-2.4.6','static_libs',''), DIRS['packages'])
        elif sys.platform.startswith('linux'):
            pass
        else:
            print('Failed to install opencv. System type is neither linux or windows')
            return

        #unpackes opencv cv2.so/.dll and cv.py in to bqenv site-packages
        extract_archive_dir(filename_zip,os.path.join('opencv-2.4.6','python%s.%s'%python_version,''), DIRS['packages'])





#######################################################
#
def setup_admin(params, runtime_params):
    try:
        params, DBURL = get_dburi(params)
    except sa.exc.ArgumentError:
        log.exception( "Unable to understand DB url. Please see SqlAlchemy" )
        return

    # Not sure why, but needs to separate script
    r = call ([PYTHON, 'scripts/create_admin.py'])
    #r, admin_pass = sql("select password from tg_user where user_name='admin';")
    # Returns "[(pass, )]"
    if r!= 0:
        print("There was a problem fetching the initial admin password")
        return params, runtime_params

    #admin_pass = eval(admin_pass)[0][0]
    new_pass = getpass.getpass ("Please set the bisque admin password >")

    #sql(DBURL, "update tg_user set password='%s' where user_name='admin';" % (new_pass))
    print("Set new admin password")
    return params, runtime_params


############################################
# Upgrade scripts
def kill_server(params, runtime_params):
    "Attempt to kill the server"

    if getanswer ("Stop server for upgrade", "Y",
                  "Server must be restarted during an upgrade operation") == "Y":
        r = call([bin_path('bq-admin'), 'server', 'stop'])
        print("Server is *not* automatically restarted")
    else:
        print("Proceeding with upgrade with (possibly) running server (dangerous)")

    return params, runtime_params



def fetch_stable (params, runtime_params):
    hg = which ('hg')
    r = call ([hg, 'pull', '-u'])
    if r!= 0:
        print("There was a problem fetching new version")
        return
    return params, runtime_params

def setup_migrate(params, runtime_params):
    "migrate db, site.cfg, and preferences "

    # Step 1: migrate db
    migrate_database()

    #Step 2: migrate site.cfg
    print("NO automatic way to upgrade site.cfg.. please check site.cfg.default")

    #Step 3: migrate preferences
    print("No Automatic way to migrate system preferences.. please check config/preferences.xml.default")

    return params, runtime_params




def cleanup(params):
    "clean up caches and prepare for restart"

    from bq.util.paths import data_path

    # support function: check and remove data tree
    def cleandata (path):
        rpath = os.path.realpath(data_path (path))
        if os.path.exists (rpath):
            shutil.rmtree(rpath)

    if getanswer("Purge cache", "Y", "cleaning cache is recommended on upgrades") == "Y":
        cleandata ('server_cache')

    if getanswer("Purge image workdir", "N", "cleaning workdir not is recommended unless noted in release") == "Y":
        cleandata ('workdir')

    # Kill the bisque.js minified file
    b_js = os.path.realpath('public/js/b.js')
    if os.path.exists (b_js):
        os.remove (b_js)

    return params

def setup_upgrade (params, runtime_params):
    #'upgrade' : [ kill_server, fetch_stable, install_external_binaries, install_dependencies, setup_migrate,
    #             cleanup ],
    return params , runtime_params


#######################################################
#  Send the installation report
# http://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python
unprintable = "".join(set(chr(x) for x in range(0,255)) - set(string.printable))
control_char_re = re.compile('[%s]' % re.escape(unprintable))
def remove_control_chars(s):
    return control_char_re.sub('', s)

def send_installation_report(params):
    if getanswer("Send Installation/Registration report", "Y",
                  """This helps the developers understand what issues
                  come up with installation.  This information is never
                  shared with others.""") != "Y":
        return

    BISQUE_REPORT="""
    Host: %(host)s
    Platform : %(platform)s
    Python : %(python_version)s
    Admin: %(admin)s
    Time: %(installtime)s
    Duration: %(duration)s

    """
    sender_email = params.get ('bisque.admin_email', 'YOUR EMAIL')

    sender_email = getanswer ("Enter the site administrator's email",
                              sender_email,
                              """This will us to contact you (very rarely) with updates""")

    config  = { k:v for k,v in list(params.items()) if k.startswith('mail.') }
    config['mail.on'] = True
    mailer = Mailer (config)
    mailer.start()


    parts = []
    text = textwrap.dedent(BISQUE_REPORT) % dict (host = socket.getfqdn(),
              admin = sender_email,
              #platform = platform.platform(),
              platform = platform.platform().replace('-', '-%s-'%platform.architecture()[0], 1), # dima: added 64bit
              python_version = platform.python_version(),
              installtime = params['install_started'],
              duration = params['duration'],
                                                  )
    parts.append(text)
    parts.append(str(params))
    if os.path.exists('bisque-install.log'):
        parts.append (remove_control_chars (open('bisque-install.log','r').read()))

    try:
        msg = mailer.Message(sender_email, "bisque-install@biodev.ece.ucsb.edu", "Installation report")

        msg.plain = "\n-----------\n".join (parts)
        msg.send()
    except Exception as e:
        print("Mail not sent.. problem sending the email %s" % str(e))
        print("----------------------------------------")
        print(text)
        print("----------------------------------------")
        print("Please send your installation log to the bisque-help@biodev.ece.ucsb.edu")


    print("""Please join the bisque mailing list at:
    User Group:    http://groups.google.com/group/bisque-bioimage
    Developer :    http://biodev.ece.ucsb.edu/cgi-bin/mailman/listinfo/bisque-dev
    """)




#######################################################
#

start_msg = """
Initialize your database with:
   $$ bq-admin setup createdb

You can start bisque with:
   $$ bq-admin server start
then point your browser to:
    ${bisque.server}
If you need to shutdown the servers, then use:
   $$ bq-admin server stop
You can login as admin and change the default password.
"""

engine_msg="""
You can start a bisque module engine with
   $$ bq-admin server start
which will register any module with
    ${bisque.engine}
"""


########################################################
# User visible command line packages to be run in order i.e. during a
# default steps for a server install
INSTALL_STEPS = OrderedDict([
    ('binaries', [ install_external_binaries, install_dependencies ]),
    ('features' , [ install_features ]),
    ('plugins' , [ install_plugins]),
    ('statics' , [ install_public_static]),
])

CONFIGURATION_STEPS= OrderedDict ([
    ('server_cfg', [ install_server_defaults]),
    ('mail', [ install_mail ]),
    ('secrets', [ install_secrets ]),
])


DATABASE_STEPS = OrderedDict([
    ('database' , [ install_database ]),
    ('preferences' , [ install_preferences ]),
])

#SERVER_STEPS = OrderedDict (INSTALL_STEPS)
#SERVER_STEPS.update(CONFIGURATION_STEPS)
#SERVER_STEPS.update(DATABASE_STEPS)


# default steps for an engine install
CONFIG_ENGINE_STEPS= OrderedDict ([
    ('engine_cfg' , [install_engine_defaults]),
    ('docker', [ install_docker] ),
    ('matlab', [ install_matlab ]),  # needde for Matlab ENV
    ('runtime', [ install_runtime]),
#    ('runtime' , [ install_runtime ]),
#    ('fetch-modules' , [ fetch_modules ]) ,

    ])

MODULE_INSTALL_STEPS = OrderedDict ([
    ('modules' , [ install_modules ]),
    ])

DEVELOPER_STEPS = OrderedDict ([
    ('matlab' , [ install_matlab ]),
    ])

#FULL_STEPS = OrderedDict (server_steps)
#FULL_STEPs.update ( engine_steps)
#FULL_STEPS.remove ('engine_cfg')

# other unrelated admin actions
OTHER_STEPS = {
    'admin' : [  setup_admin ],
    'upgrade' : [setup_upgrade ],
    "webservers" : [ setup_server_cfg ],
    "createdb" : [ setup_database ],
    "stores": [ setup_stores ],
    "testing" : [ setup_testing ],
    "logins"  : [ setup_logins ],
    "testing" : [ setup_testing ],
    'docker'  : [ install_docker ],
    'runtime' : [ install_runtime ] ,
    'build-modules'   : [ install_modules, install_matlab, setup_build_modules ] ,
}

def merge_lists (*dicts ):
    return [ x  for d in dicts for l in list(d.values()) for x in l ]

server_steps = merge_lists (INSTALL_STEPS, CONFIGURATION_STEPS, DATABASE_STEPS)
full_steps = merge_lists (INSTALL_STEPS, CONFIGURATION_STEPS, DATABASE_STEPS)
developer_steps = merge_lists (INSTALL_STEPS, CONFIGURATION_STEPS, DATABASE_STEPS,
                               MODULE_INSTALL_STEPS, CONFIG_ENGINE_STEPS)

COMMAND_STEPS = OrderedDict ([
    ("install",  merge_lists (INSTALL_STEPS)),
    ('module-install', merge_lists(MODULE_INSTALL_STEPS)),
    ('plugin-install', [ install_plugins]),
    ('configure' , merge_lists (CONFIGURATION_STEPS , DATABASE_STEPS)),
    ('fullconfig', merge_lists (CONFIGURATION_STEPS , DATABASE_STEPS, CONFIG_ENGINE_STEPS)),
    ('developer', developer_steps),
# Backward compatible
    ('bisque' , server_steps),
    ('developer' , server_steps),
    ('server', server_steps),
    ('full' , full_steps),
    ('engine' , merge_lists (CONFIG_ENGINE_STEPS)),
])
COMMAND_STEPS.update (INSTALL_STEPS)
COMMAND_STEPS.update (CONFIGURATION_STEPS)
COMMAND_STEPS.update (DATABASE_STEPS)
COMMAND_STEPS.update (DATABASE_STEPS)
COMMAND_STEPS.update (OTHER_STEPS)




######################################################################
# List of user visible commands and their corresponding internal actions
SETUP_COMMANDS = set ([
    'server_cfg',
    'engine_cfg' ,
    'binaries',
    'features' ,
    'database' ,
    'mail'
    'preferences' ,
    'statics'  ,
    'secrets'  ,
    'upgrade' ,
    "webservers",
    "createdb" ,
    "stores",
    "modules" ,
    "testing" ,
    "logins"  ,
])

# Special procedures that modify runtime-bisque.cfg (for the engine)
RUNTIME_COMMANDS = set ([
    'engine_runtime_cfg' ,
    'matlab'
    'runtime'
    'docker'
    'modules'
    'fetch-modules'
    'build-modules'
])



ALL_OPTIONS =   list(COMMAND_STEPS.keys())
USAGE = " usage: bq-admin setup [%s] " % ' '.join(ALL_OPTIONS)


def bisque_installer(options, args):
    #cwd = to_posix_path(os.getcwd())
    #if not os.path.exists ('bqcore'):
    #    print "ERROR: This script must be bisque installation directory"
    #    sys.exit()

    if not os.path.exists(defaults_path()):
        print("Cannot find config-defaults.. please run bq-admin setup from bisque root directory")
        sys.exit(1)

    print( """This is the main installer for Bisque

    The system will initialize and be ready for use after a succesfull
    setup has completed.

    Several questions must be answered to complete the install.  Each
    question is presented with default in brackets [].  Pressing
    <enter> means that you are accepting the default value. You may
    request more information by responding with single '?' and then <enter>.

    For example:
    What is postal abbreviation of Alaska [AK]?

    The default answer is AK and is chosen by simply entering <enter>

    """)
    system_type = ['bisque', 'engine']
    install_steps = []
    if len(args) == 0: # Default install is 'full' both bisque and engine
        args = [ 'server' ]

    # Read group of steps or just execute steps on command line
    install_steps = COMMAND_STEPS.get (args[0])

    if install_steps is None:
        print(USAGE)
        return

    print("Beginning install of %s with %s " % (system_type, args))

    runtime_params =  {}
    #if not os.path.exists (DIRS['config']):
    #    os.makedirs (DIRS['config'])
    params = initial_vars.copy()

    if 'bisque' in system_type and  os.path.exists (SITE_CFG):
        params = read_site_cfg(cfg = SITE_CFG, section=BQ_SECTION)
    if 'engine' in system_type and  os.path.exists(RUNTIME_CFG):
        runtime_params = read_site_cfg(cfg=RUNTIME_CFG, section = None)

    params['setup.arguments']  =  args[1:]
    params['bisque.installed'] = "inprogress"

    #print "STEPS", install_steps
    for step in install_steps:
        # Normal commands that modify site.cfg
        print("CALLING ", step)
        params, runtime_params = step (params, runtime_params)
        #flist  =  SETUP_COMMANDS.get(step, [])
        #for step_f in flist:
        #    params = step_f(params)
        ## Special commands that modify runtime-bisque.cfg
        #flist  =  RUNTIME_COMMANDS.get(step, [])
        #for step_f in flist:
        #    runtime_params = step_f(runtime_params)

    params['bisque.installed'] = "finished"
    params['new_database'] = 'false'
    params = modify_site_cfg([], params,)

    if args[0]  in ('server', 'bisque'):
        print(STemplate(start_msg).substitute(params))
    if args[0] == 'engine':
        print(STemplate(engine_msg).substitute(params))
    return params.get ('error_code', 0)


class CaptureIO(object):
    def __init__(self, logfile):
        self.o = sys.stdout
        self.f = open(logfile,'w')

    def close(self):
        self.f.close()
        sys.stdout = self.o

    def __del__(self):
        if 'CaptureIO' in locals() and isinstance(sys.stdout, CaptureIO):
            self.close()

    def write(self,s):
        self.o.write(s)
        self.f.write(s); self.f.flush()
    def logged_input(self,prompt):
        response = input(prompt)
        self.f.write (response)
        self.f.write ('\n')
        return response

#capture = CaptureIO('bisque-install.log')
#sys.stdout = capture


def typescript(command, filename="typescript"):
#    import sys, os, time
#    import pty
    mode = 'wb'
    script = open(filename, mode)
    def read(fd):
        data = os.read(fd, 1024)
        script.write(data)
        return data

    script.write(('Script started on %s\n' % time.asctime()).encode())
    pty.spawn(command, read)
    script.write(('Script done on %s\n' % time.asctime()).encode())
    script.close()
    with open(filename) as install:
        if 'Cancel' in install.read():
            return 128
    return 0


def find_virtualenv ():
    "Find the system virtualenv"

    virtenv = os.environ.get ('VIRTUAL_ENV', None)
    if virtenv is None:
        # argv should be the bq-admin command path
        activate_this = os.path.join (os.path.dirname (os.path.realpath(sys.argv[0])),
                                      'activate_this.py')
        if os.path.exists (activate_this):
            execfile (activate_this, dict (__file__ = activate_this))
        virtenv = os.path.dirname (os.path.dirname (activate_this))
    if virtenv is None:
        print("Cannot determine your python virtual environment")
        print("This make installation much simpler.  Please activate or prepare the environment given by the web instructions")
        if getanswer ("Continue without virtualenv", "N", "Try installation without python virtualenv") == 'N':
            sys.exit(0)
    return virtenv

def update_globals (options, args):
    """Update the global directories and files locations based on the type
    of install we are doing.. developer, system, or engine
    """

    global SITE_CFG # The site.cfg in configuration
    global RUNTIME_CFG

    python_version = sys.version_info[:2]

    DIRS['config'] = options.config
    DIRS['virtualenv'] = find_virtualenv()
    DIRS['default'] = find_path ('config-defaults', ['.', '/etc/bisque', '/usr/share/bisque'])
    if os.name == "nt":
        DIRS['bin'] = os.path.join(DIRS['virtualenv'], 'Scripts') # windows local
        DIRS['packages'] =  os.path.join(DIRS['virtualenv'], 'Lib', 'site-packages')
    else:
        DIRS['bin'] = os.path.join(DIRS['virtualenv'], 'bin') # Our local bin
        DIRS['packages'] = os.path.join(DIRS['virtualenv'], 'lib','python%s.%s'%python_version,'site-packages')

    # Figure out installation type
    #
    install_type = None # unknown
    if os.path.exists ('./config-defaults'):
        install_type = 'developer'
    else:
        install_type = 'system'

    if install_type is 'system':
        print("Package installation")
        # This is a system install
        DIRS['share']   = "/usr/share/bisque"
        # Was /var/run/bisque but /var/run -> symlinked /run hiccuped in imgsrv ../../../var/run/bisque
        DIRS['run']     = '/run/bisque'
        DIRS['config']  = DIRS['config'] or "/etc/bisque"
        log.warn ("Will install new python packages into %s", DIRS['packages'])
        DIRS['jslocation'] = DIRS['packages']
    else:
        print("Developer installation")
        DIRS['share']  = '.'  # Our top installation path
        DIRS['run']    = DIRS['share'] #'.'
        DIRS['config'] = DIRS['config'] or os.path.join(DIRS['share'], "config")
        DIRS['jslocation'] = "bqcore"

    DIRS['data']   = os.path.join(DIRS['run'], 'data')
    DIRS['depot']  = os.path.join(DIRS['run'], "external") # Local directory for externals
    DIRS['public'] = os.path.join(DIRS['run'], 'public')
    DIRS['modules'] = os.path.join(DIRS['share'], 'modules')
    DIRS['plugins'] = os.path.join(DIRS['share'], 'plugins')
    print("DIRS: ", DIRS)
    # Ensure dirs are available
    for key, folder in list(DIRS.items()):
        if not os.path.exists (folder):
            os.makedirs (folder)

    SITE_CFG     = config_path('site.cfg')
    RUNTIME_CFG  = config_path('runtime-bisque.cfg')

    SITE_VARS['bisque.server'] = 'http://0.0.0.0:8080'
    SITE_VARS['bisque.paths.root'] = DIRS['share']

def setup(options, args):

    cancelled = False
    global answer_file, save_answers
    global use_defaults


    update_globals (options, args)

    begin_install = datetime.datetime.now()
    if options.debug:
        chout = logging.StreamHandler(sys.stdout)
        root = logging.getLogger()
        #root.addHandler(chout)
        root.setLevel (logging.DEBUG)
        log.debug ("TESTING")

    if options.read:
        print("Reading answers from %s" % options.read)
        answer_file = open (options.read)
    elif options.write:
        print("Saving answers to %s" % options.write)
        answer_file = open (options.write, "wb")
        save_answers = True
    elif options.yes:
        use_defaults = True
    elif has_script and not options.inscript and not options.debug:
        script = ['bq-admin', 'setup', '--inscript']
        script.extend (args)
        r = typescript(script, 'bisque-install.log')
        #print "RETURN is ", r
        if not cancelled and r != 128:
            end_install = datetime.datetime.now()
            params = read_site_cfg(cfg= SITE_CFG, section=BQ_SECTION)
            params['install_started'] = begin_install
            params['duration'] = str(end_install-begin_install)
            try:
                send_installation_report(params)
            except KeyboardInterrupt:
                print("Cancelled")
        sys.exit(r)
    try:
        r  = bisque_installer(options, args)
        return r
    except InstallError as e:
        cancelled = True
    except KeyboardInterrupt:
        print("Interupted")
        print("Cancelling Installation")
        sys.exit (128)
    except Exception as e :
        print("An Unknown exception occured %s" % e)
        excType, excVal, excTrace  = sys.exc_info()
        msg = ["During setup:", "Exception:"]
        msg.extend (traceback.format_exception(excType,excVal, excTrace))
        msg = "\n".join(msg)

        print(msg)

    # indicate an issue
    return 2

#    finally:
#        capture.close();
#        capture = None
#
#        if not cancelled:
#            end_install = datetime.datetime.now()
#            send_installation_report(params)
