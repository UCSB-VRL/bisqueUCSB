import sys
import os
import subprocess
import re
import pkg_resources
import optparse
import errno
import logging
import shutil

from paste.deploy.converters import asbool

from bq.release import __VERSION__
from bq.util.io_misc import remove_safe
from bq.util.paths import site_cfg_path, data_path, config_path, defaults_path



logging.basicConfig(level=logging.INFO, formatter="%(name)s:%(levelname)s:%(message)s")
#logging.basicConfig(level=logging.DEBUG)

def load_config(filename):
    from paste.deploy import appconfig
    from bq.config.environment import load_environment
    conf = appconfig('config:' + os.path.abspath(filename))
    load_environment(conf.global_conf, conf.local_conf)


def load_bisque_services():
    from tg import config
    from bq.util.fakerequestenv import create_fake_env
    from bq.core.controllers.root import RootController

    root = config.get ('bisque.root', '/')
    create_fake_env()
    enabled = [ 'blob_service', 'data_service', 'mnt' ]
    disabled= []
    RootController.mount_local_services(root, enabled, disabled)


def main():
    """Main entrypoint for bq-admin commands"""
    commands = {}
    for entrypoint in pkg_resources.iter_entry_points("bq.commands"):
        command = entrypoint.load()
        commands[entrypoint.name] = (command.desc, entrypoint)

    def _help():
        "Custom help text for bq-admin."

        print """
Bisque %s command line interface

Usage: %s [options] <command>

options: -d, --debug : print debug

Commands:""" % (__VERSION__, sys.argv[0])

        longest = max([len(key) for key in commands.keys()])
        format = "%" + str(longest) + "s  %s"
        commandlist = commands.keys()
        commandlist.sort()
        for key in commandlist:
            print format % (key, commands[key][0])


    parser = optparse.OptionParser()
    parser.allow_interspersed_args = False
    #parser.add_option("-c", "--config", dest="config")
    #parser.add_option("-e", "--egg", dest="egg")
    parser.add_option("-d", "--debug", action="store_true", default=False)
    parser.print_help = _help
    (options, args) = parser.parse_args(sys.argv[1:])
    if not args or not commands.has_key(args[0]):
        _help()
        sys.exit()

    if options.debug:
        logging.info ("setting debug")
        logging.getLogger().setLevel(logging.DEBUG)

    commandname = args[0]

    # strip command and any global options from the sys.argv
    sys.argv = [sys.argv[0],] + args[1:]
    command = commands[commandname][1]
    command = command.load()
    command = command(__VERSION__)
    command.run()

class server(object):
    desc = "Start or stop a bisque server"

    def __init__(self, version):
        parser = optparse.OptionParser(usage="%prog servers [options] start|stop|restart",
                                       version="%prog " + version)
        parser.add_option("--reload", action="store_true", help="autoreload for development" )
        parser.add_option("-n", "--dryrun", action="store_true", help="Dry run and show commands")
        parser.add_option("-v", "--verbose", action="store_true", help="show commands as run" )
        parser.add_option("-w", "--wait", action="store_true", help="wait for children" )
        parser.add_option("-s", "--site", help="specify location of site.cfg" )
        parser.add_option("-f", "--force", action="store_true", default=False, help="try force start or stop: ignore old pid files etc." )

        options, args = parser.parse_args()
        self.command = self.options = None
        if len(args) < 1 or args[0] not in ['start', 'stop', 'restart', 'echo', 'list' ]:
            parser.print_help()
            return

        if options.dryrun:
            options.verbose = True

        self.options = options
        self.command = args[0]
        self.args = args[1:]

    def run(self):
        #Check for self.command in init..
        from . import server_ops
        if self.command:
            server_ops.operation(self.command, self.options, *self.args)

class cache(object):
    desc = "delete the cache"

    def run(self):
        #Check for self.command in init..
        for p in (data_path('.server_cache'), data_path('.client_cache')):
            if os.path.exists (p):
                shutil.rmtree (p)
                os.makedirs(p)

class database(object):
    desc = 'Execute a database command'
    def __init__(self, version):
        parser = optparse.OptionParser(usage="%prog database [admin]",
                                       version="%prog " + version)


        parser.add_option('-c','--config', default=site_cfg_path(), help="Path to config file: %default")
        parser.add_option('-n','--dryrun', action="store_true", default=False)
        options, args = parser.parse_args()

        self.args = args
        self.options = options
        if len(args) == 0:
            parser.error('argument must be clean')

        options, args = parser.parse_args()
        self.command = args[0]
        self.args = args[1:]


    def run(self):
        load_config(self.options.config)
        from . import cleandb
        cleandb.clean_images(self.options)



class setup(object):
    desc = 'Setup or update a bisque server'
    def __init__(self, version):
        from bq.setup.bisque_setup import USAGE, ALL_OPTIONS
        parser = optparse.OptionParser(usage=USAGE, version="%prog " + version)
        parser.add_option("--inscript", action="store_true", help="we are running under typescript" )
        parser.add_option("-r", "--read", action="store", help="Read answers from given file" )
        parser.add_option("-w", "--write", action="store", help="Write answers from given file" )
        parser.add_option("-y", "--yes", action="store_true", help="Use default answers for all questions" )
        parser.add_option("-c", "--config",  help="Set config directory locations"  )
        parser.add_option("-d", "--debug", action="store_true", default=False)
        options, args = parser.parse_args()
        if args and args[0] not in ALL_OPTIONS:
            parser.error('argument %s must be install option %s' % (args[0], ALL_OPTIONS))

        self.args = args
        self.options = options


    def run(self):
        ''
        from bq.setup import bisque_setup
        r = bisque_setup.setup( self.options, self.args )
        sys.exit(r)

class deploy(object):
    desc = 'Advanced deployment options: public'
    def __init__(self, version):
        from bq.util.copylink import copy_symlink, copy_link
        parser = optparse.OptionParser(usage="%prog deploy [public]", version="%prog " + version)
        parser.add_option("--packagedir",  help="Root package of install", default='bqcore' )
        parser.add_option("--symlinks", default=True, help='use symlinks instead of copying' )
        options, args = parser.parse_args()
        self.args = args
        self.options = options
        self.copy = copy_symlink if asbool(options.symlinks) else copy_link

    def run(self):
        #if 'public' in self.args:
        self.public_dir = self.args.pop(0) if len(self.args)>0 else 'public'
        self.packagedir = self.options.packagedir
        self.deploy_public()



    def deploy_public(self):
        ''

        # dima: deploy fails under windows with access denied, need to clean dir first
        if os.name == 'nt':
            try:
                print "Cleaning up %s" % self.public_dir
                shutil.rmtree(self.public_dir, ignore_errors=True)
            except OSError, e:
                pass

        try:
            print "Creating %s" % self.public_dir
            os.makedirs (self.public_dir)
        except OSError, e:
            pass

        rootdir = os.getcwd()

        # update public
        #os.chdir(self.public_dir)
        #currdir = os.getcwd()

        for x in pkg_resources.iter_entry_points ("bisque.services"):
            try:
                #print ('found static service: ' + str(x))
                try:
                    service = x.load()
                except Exception, e:
                    print "Problem loading %s: %s" % (x, e)
                    continue
                if not hasattr(service, 'get_static_dirs'):
                    continue
                staticdirs  = service.get_static_dirs()
                for d,r in staticdirs:

                    # Copy all elements r into public_dir
                    #shutil.copytree (r, os.path.join (self.public_dir, x.name))
                    dest = os.path.join (self.public_dir, x.name)
                    if not os.path.exists (dest):
                        os.makedirs (dest)
                        print "Making ", dest
                    names = os.listdir (r)
                    for name in names:
                        src = os.path.join (r, name)
                        dst = os.path.join (dest, name)
                        if os.path.isdir (dst) and not os.path.islink (dst):
                            shutil.rmtree(dst)
                        if os.path.exists (dst):
                            os.unlink(dst)
                        self.copy (src, dst)
                        #print "%s->%s" % (src, dst)

            except Exception, e:
                logging.exception ("in copy")
                #print "Exception: ", e
                pass

        # # Link all core dirs
        # os.chdir(self.public_dir)
        # currdir = os.getcwd()
        # coredir = 'core' #os.path.join(self.public_dir, 'core').replace('/', os.sep)
        # print "COREDIR", coredir
        # import glob
        # for l in os.listdir(coredir):
        #     src =  os.path.join(coredir, l)
        #     dest = os.path.join(currdir, l)
        #     if os.path.exists (dest):
        #         os.unlink (dest)
        #     if os.path.isdir (dest):
        #         shutil.rmtree(dest)
        #     print "CORE", src, dest
        #     copy_symlink (src, dest)
        # os.chdir (rootdir)

        # regenerate all_js and all_css
        print '\nGenerating packaged JS and CSS files\n'
        from bq.core.lib.js_includes import generate_css_files, generate_js_files
        rootdir = os.path.join(self.packagedir, '').replace(os.sep, '/')
        publicdir = os.path.join(self.public_dir, '').replace(os.sep, '/')

        #all_css_combined = os.path.join(publicdir, 'core/css/all_css.css')
        all_css_public = os.path.join(publicdir, 'core/css/all_css.css')
        #all_js_combined = os.path.join(publicdir, 'core/js/all_js.js')
        all_js_public = os.path.join(publicdir, 'core/js/all_js.js')

        if os.name != 'nt': # under windows the whole public is removed at the beginning
            remove_safe(all_css_public)
            remove_safe(all_js_public)

        import pylons
        pylons.config["cache_enabled"] = "False"

        generate_css_files(root=rootdir, public=publicdir)
        generate_js_files(root=rootdir, public=publicdir)

        #if not os.path.exists (all_css_public):
        #    copy_symlink (all_css_combined, all_css_public)
        #if not os.path.exists (all_js_public):
        #    copy_symlink (all_js_combined, all_js_public)


class preferences (object):
    desc = "read and/or update preferences"
    def __init__(self, version):
        parser = optparse.OptionParser(usage="%prog preferences [init (db)|read (from db)|save (to db)]",
                                       version="%prog " + version)
        parser.add_option('-c','--config', default=site_cfg_path(), help="Path to config file: %default")
        parser.add_option('-f','--force', action="store_true", help="Force action if able")
        options, args = parser.parse_args()

        self.args = args
        self.options = options
        if len(args) == 0:
            parser.error('argument must be init, read, save')

    def run(self):

        load_config(self.options.config)
        from lxml import etree
        from tg import config, session, request
        from bq import data_service
        from bq.core.identity import set_admin_mode
        import transaction
        load_bisque_services()

        prefs = config_path('preferences.xml')

        set_admin_mode(True)
        if self.args[0].startswith('init'):
            x = data_service.query('system')
            if len(x):
                if self.options.force:
                    print ("deleting current system object")
                    data_service.del_resource(x[0])
                else:
                    print ("NO ACTION: System object initialized at %s " % etree.tostring(x[0]))
                    sys.exit (1)

            if os.path.exists(prefs):
                if self.options.force:
                    print ("deleting %s" % prefs)
                    os.remove (prefs)
                else:
                    print ('NO ACTION: %s exists.. cannot init' % prefs)
                    sys.exit(1)

            system = etree.parse(defaults_path ('preferences.xml.default')).getroot()
            for el in system.getiterator(tag=etree.Element):
                el.set ('permission', 'published')
            system = data_service.new_resource(system, view='deep')
        elif self.args[0].startswith('read'):
            system = data_service.query('system', view='deep')
            if len(system):
                system = system[0]
            else:
                system = None
        else:
            if not os.path.exists(prefs):
                print "Need %s" % prefs
                return
            system = etree.parse(prefs).getroot()
            # Esnure all elements are published
            for el in system.getiterator(tag=etree.Element):
                el.set ('permission', 'published')
            # Read system object
            uri = system.get('uri')
            print  'system = %s' % etree.tostring(system)

            system = data_service.update_resource(new_resource=system, resource=uri,  view='deep')
            print etree.tostring (system)
        transaction.commit()
        if system is not None:
            with open(prefs,'w') as f:
                f.write(etree.tostring(system, pretty_print=True))
                print "Wrote %s" % prefs


class sql(object):
    desc = 'Run a sql command (disabled)'
    def __init__(self, version):
        parser = optparse.OptionParser(usage="%prog sql <sql>",
                                       version="%prog " + version)
        parser.add_option('-c','--config', default=site_cfg_path(), help="Path to config file: %default")
        options, args = parser.parse_args()

        self.args = args
        self.options = options

    def run(self):
        ''

        from tg import config
        from sqlalchemy import create_engine
        from sqlalchemy.sql import text
        from ConfigParser import ConfigParser
        load_config(self.options.config)

        engine = config['pylons.app_globals'].sa_engine

        print engine


class group(object):
    'do a group command'
    def __init__(self, version):
        parser = optparse.OptionParser(usage="%prog sql <sql>",
                                       version="%prog " + version)
        parser.add_option('-c','--config', default=site_cfg_path(), help="Path to config file: %default")
        options, args = parser.parse_args()

        self.args = args
        self.options = options

    def run(self):
        ''

        from tg import config
        from sqlalchemy import create_engine
        from sqlalchemy.sql import text
        from ConfigParser import ConfigParser
        load_config(self.options.config)

        engine = config['pylons.app_globals'].sa_engine

        print engine



class stores(object):
    desc = 'Generate stores resource by visiting image/file resouces'

    def __init__(self, version):
        parser = optparse.OptionParser(usage="%prog stores  [list|create [name]]|fill[name]|update[name]",
                                       version="%prog " + version)
        parser.add_option('-c','--config', default=site_cfg_path(), help="Path to config file: %default")
        options, args = parser.parse_args()
        if len(args) < 1 or args[0] not in ('list', 'init', 'fill', 'update', 'move'):
            parser.error("No command given")
        self.command  = args.pop(0)
        self.args = args
        self.options = options

    def run(self):
        ''
        #engine = config['pylons.app_globals'].sa_engine
        #print engine
        #from bq.util.fakerequestenv import create_fake_env
        #session, request = create_fake_env()
        load_config(self.options.config)
        load_bisque_services()

        from .stores import init_stores, list_stores, fill_stores, update_stores, move_stores
        import transaction


        command = self.command.lower()
        username = None

        if command == 'move':
            from_store = self.args.pop(0)
            to_store   = self.args.pop(0)
        if len(self.args):
            username = self.args.pop(0)

        if command == 'list':
            list_stores(username)
        elif command == 'init':
            print "initializing stores"
            init_stores(username)
        elif command == 'fill':
            print "attempting to fill stores with data"
            fill_stores(username)
        elif command == 'update':
            print "attempting to update stores based on config/site.cfg settings"
            update_stores(username)
        elif command == 'move':
            print "attempting to update stores based on config/site.cfg settings"
            move_stores(from_store, to_store, username)

        transaction.commit()

class password(object):
    desc = 'Password utilities for manipulating passwords'

    def __init__(self, version):
        parser = optparse.OptionParser(
            usage="%prog password [convert: freetext to hashed][list: users and password][set: username password] ",
            version="%prog " + version)
        parser.add_option('-c','--config', default=site_cfg_path(), help="Path to config file: %default")
        parser.add_option('-f','--force', action="store_true", default=False)
        options, args = parser.parse_args()

        if len(args) > 0:
            self.command = args.pop(0)
        else:
            parser.error("Need at least one command")

        self.args = args
        self.options = options
        if self.command not in ('convert', 'set', 'list'):
            parser.error("illegal command")

    def run(self):
        import transaction
        load_config(self.options.config)

        from tg import config
        print "password mechanism:", config.get ('bisque.login.password', 'freetext')


        if self.command == 'set':
            user_name, password = self.args
            self.set_password (user_name, password)
        elif self.command == 'list':
            from bq.core.model.auth import User, DBSession
            for user in DBSession.query(User):
                print user.user_name, user.password
        elif self.command == 'convert':
            from bq.core.model.auth import User, DBSession
            for user in DBSession.query(User):
                if len(user.password)==80 and not self.options.force:
                    print "Skipping user %s already  converted" % user.user_name
                    continue
                self.set_password (user.user_name, user.password)
        transaction.commit()

    def set_password(self, user_name, password):
        from bq.core.model.auth import User, DBSession
        user = DBSession.query(User).filter_by(user_name = user_name).first()
        if user:
            print "setting %s" % user.user_name
            user.password = password
        else:
            print "cannot find user %s" % user_name





class hosturl(object):
    desc = 'Find and replace host settings in bisuqe db:'

    def __init__(self, version):
        self.parser = optparse.OptionParser(
            usage="%prog update old-host-url full-host-url] ",
            version="%prog " + version)
        self.parser.add_option('-c','--config', default=site_cfg_path(), help="Path to config file: %default")
        self.parser.add_option('-f','--force', action="store_true", default=False)
        self.parser.add_option('--dburl', default  = None, help='Override dburl from site.cfg')
        options, args = self.parser.parse_args()

        if len (args) > 0:
            self.command = args.pop(0)
        else:
            self.parser.error("Need at least one command")

        self.args = args
        self.options = options
        if self.command not in ('update'):
            self.parser.error("illegal command")

    def run(self):
        from tg import config
        from sqlalchemy import create_engine
        from sqlalchemy.sql import func, update
        import transaction

        if self.options.dburl is  None:
            load_config(self.options.config)
            engine = config['pylons.app_globals'].sa_engine
        else:
            engine = create_engine (self.options.dburl)

        print "updating ", engine

        if self.command == 'update':
            oldurl , newurl = self.args

            if not (oldurl.endswith ('/') and newurl.endswith('/')):
                self.parser.error ("Please end URLs with '/' for proper matching")
            from bq.data_service.model.tag_model import taggable, values
            #taggable.bind = engine

            # pylint: disable=no-value-for-parameter
            stmt = taggable.update ()\
                   .values (resource_value = func.replace (taggable.c.resource_value, oldurl, newurl))\
                   .where(taggable.c.resource_value.like (oldurl + '%'))
            print stmt
            engine.execute (stmt)
            stmt = values.update() \
                     .values (valstr = func.replace (values.c.valstr, oldurl, newurl))\
                     .where(values.c.valstr.like (oldurl + '%'))
            print stmt
            engine.execute (stmt)

            # Find all values
            transaction.commit()
