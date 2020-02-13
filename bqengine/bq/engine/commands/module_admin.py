###############################################################################
##  Bisque                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009,2010,2011                                ##
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

import optparse
import os
import posixpath
import sys
import logging
#import urlparse
#import urllib
import datetime
from lxml import etree
from paste.deploy import appconfig
from tg import config

from six.moves import urllib

#from bq.config.environment import load_environment
from ConfigParser import ConfigParser
#from bq.util import http
from bq.util.configfile import ConfigFile
from bq.util.paths import config_path
from bq.util.commands import find_site_cfg
from bq.util.urlnorm import norm
from bqapi import *

logging.basicConfig(level = logging.WARN)


log = logging.getLogger('bq.engine.command.module_admin')

usage = """
%prog module [register|unregister/list-engine/list-server] [-u user:pass] [-r bisque_root_url]  [-p] [-a] http://myengnine.org/engine_service/[MyModule]
  Version 2

  Register or unregister and bisque analysis (Engine) on a bisque server.

  The module engine uri must be specified
  Optionaly include the the module_uri on the server to disambiguate

"""

def error (msg):
    print >>sys.stderr, msg


class module_admin(object):
    desc = 'module options'
    def __init__(self, version):
        parser = optparse.OptionParser(usage=usage, version="%prog " + version)
        parser.add_option('-u', '--user', default=None, help='Login as user <user>:<pass>')
        parser.add_option('-a', '--all', action='store_true', help='Register/Unregister all modules at engine',
                          default=False)
        parser.add_option('-r', '--root', help='Bisque server root url')
        parser.add_option('-p', '--published', help='Make published module', default=False, action='store_true')
        parser.add_option('--cas', help='login with CAS', default=False, action='store_true')

        options, args = parser.parse_args()
        self.args = args
        self.options = options
        self.command = None
        if len(self.args):
            self.command = getattr(self, self.args.pop(0).replace('-', '_'), None)
        if not self.command:
            parser.error("no valid command given")

        self.credentials = None
        if self.options.user:
            self.credentials = tuple(self.options.user.split(':'))


        self.module_uri = None
        if len(self.args):
            self.engine_path = self.args.pop(0)
            if not self.engine_path.endswith('/'):
                self.engine_path += '/'

            if len(self.args):
                self.module_uri = self.args.pop(0)


    def run(self):
        if self.options.root:
            self.root = self.options.root
        else:
            site_cfg = find_site_cfg('site.cfg')
            cfile = ConfigFile (site_cfg)
            self.root = posixpath.join (cfile.get ('app:main', 'bisque.root'), '')

        if not self.root:
            print ("need a bisque server to contact.. please specify with -r ")

        self.session = BQSession()
        if self.credentials:
            if self.options.cas:
                self.session.init_cas (self.credentials[0], self.credentials[1], bisque_root = self.root, create_mex=False)
            else:
                self.session.init_local (self.credentials[0], self.credentials[1], bisque_root = self.root, create_mex=False)
        self.command()


    def get_xml(self, url):
        print "loading ", url
        xml = self.session.fetchxml (url)
        return xml

    def get_modules(self, engine_path):
        'list module urls  at engine given path path'
        engine_path = norm(engine_path + '/')
        modules = self.get_xml( url = urllib.parse.urljoin(engine_path, '_services'))
        if modules is None:
            return error ('Cannot read modules from engine: %s' % engine_path)
        return  [ m.get('value') for m in modules ]

    def register_one(self, module_path):
        bisque_root = self.root
        module_path = norm(module_path + '/')
        module_register = norm (urllib.parse.urljoin(bisque_root, "module_service/register_engine") + '/')
        module_xml = self.get_xml( url = urllib.parse.urljoin(module_path, 'definition'))
        if module_xml is None:
            error ("cannot read definition from %s!  Is engine address correct?")
        name = module_xml.get('name')
        if module_xml is not None:
            log.info ("POSTING %s to %s" % (name, module_register))
            #engine = etree.Element ('engine', uri = module_path)
            #engine.append(module_xml)
            #xml =  etree.tostring (engine)
            #print xml
            module_xml.set('ts', datetime.datetime.now().isoformat())
            if self.options.published:
                for el in module_xml.getiterator(tag=etree.Element):
                    el.set ('permission', 'published')
            xml = etree.tostring(module_xml)
            params = [ ('engine_uri', module_path) ]
            if self.module_uri:
                params.append ( ('module_uri', self.module_uri) )
            url = "%s?%s" % (module_register, urllib.parse.urlencode(params))
            self.session.postxml (url, xml = xml)
            print "Registered"

    def register (self):
        if self.options.all:
            module_paths = self.get_modules(self.engine_path)
        else:
            module_paths = [ self.engine_path ]
        for m in module_paths:
            print "registering %s" % m
            self.register_one(m)


    def unregister(self):
        if self.options.all:
            module_paths = self.get_modules(self.engine_path)
        else:
            module_paths = [ self.engine_path ]
        for m in module_paths:
            print "unregistering %s" % m
            self.unregister_one(m)


    def unregister_one(self, module_path):
        bisque_root = self.root
        module_path = norm(module_path + '/')
        module_unregister = norm (urllib.parse.urljoin(bisque_root, "module_service/unregister_engine") + '/')

        module_name = module_path.split('/')[-2]
        params = [ ('engine_uri', module_path) ]
        if self.module_uri:
            params.append ( ('module_uri', self.module_uri) )

        self.session.fetchxml (module_unregister, ** dict (params))

        print "UnRegistered"

    def list_engine(self):
        module_paths = self.get_modules(self.engine_path)
        if module_paths is None:
            module_paths = self.get_modules(self.engine_path + '/engine_service/')
        for module in module_paths or []:
            print module


    def list_server(self):
        from collections import namedtuple
        Row = namedtuple ('Row', ('name', 'engine', 'module'))
        server_modules = self.get_xml( url = urllib.parse.urljoin(self.root, 'module_service'))
        if server_modules is None:
            error ("No modules registered at %s. Is this a bisque server?" % self.root)

        rows = [ Row(name=module.get('name'), engine=module.get('value'), module=module.get ('uri'))
                 for module in server_modules ]
        pprinttable ( rows)


#taken from
#http://stackoverflow.com/questions/5909873/python-pretty-printing-ascii-tables
def pprinttable(rows):
  if len(rows) > 1:
    headers = rows[0]._fields
    lens = []
    for i in range(len(rows[0])):
      lens.append(len(max([x[i] for x in rows] + [headers[i]],key=lambda x:len(str(x)))))
    formats = []
    hformats = []
    for i in range(len(rows[0])):
      if isinstance(rows[0][i], int):
        formats.append("%%%dd" % lens[i])
      else:
        formats.append("%%-%ds" % lens[i])
      hformats.append("%%-%ds" % lens[i])
    pattern = " | ".join(formats)
    hpattern = " | ".join(hformats)
    separator = "-+-".join(['-' * n for n in lens])
    print hpattern % tuple(headers)
    print separator
    for line in rows:
      print pattern % tuple(line)
  elif len(rows) == 1:
    row = rows[0]
    hwidth = len(max(row._fields,key=lambda x: len(x)))
    for i in range(len(row)):
      print "%*s = %s" % (hwidth,row._fields[i],row[i])
