# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in bqcore.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::

    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))

"""
import os
import sys
import tg
import logging
import transaction
import pkg_resources

from paste.deploy.converters import asbool
from pylons.middleware import StatusCodeRedirect
from pylons.util import call_wsgi_application

from tg.configuration import AppConfig, config
from tg.util import  Bunch
from tg.error import ErrorHandler
#import tgscheduler
#from repoze.who.config import make_middleware_with_config
from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.plugins.testutil import AuthenticationForgerMiddleware
from repoze.who.config import WhoConfig

import bq
from bq.core import model
from bq.core.lib import app_globals, helpers
from bq.core.lib.statics import BQStaticURLParser
from bq.util.etreerender import render_etree
from .direct_cascade import DirectCascade
from paste.urlparser import StaticURLParser

log = logging.getLogger("bq.config")

# Needed for engine statics
public_file_filter = BQStaticURLParser()
LOG_LEVELS = {'debug': logging.DEBUG,
                       'info': logging.INFO,
                       'warning': logging.WARNING,
                       'error': logging.ERROR,
                       }
LOG_STREAMS = dict (stdout = sys.stdout, stderr = sys.stderr)



def transaction_retry_wrapper(app_config, controller):
    def wrapped_controller(*args, **kw):
        for attempt in transaction.attempts(3):
            with attempt:
                return controller(*args, **kw)
    return wrapped_controller


class BisqueErrorFilter(object):

    def __init__(self, app, codes = []):
        self.app = app
        self.codes = tuple ([ str(x) for x in codes ] )

    def __call__(self, environ, start_response):
        # Check the request to determine if we need
        # to respond with an error message or just the code.

        status, headers, app_iter, exc_info = call_wsgi_application(
            self.app, environ, catch_exc_info=True)
        #log.debug ("ENV=%s" % environ)
        if status[:3] in self.codes and environ.has_key('HTTP_USER_AGENT') and \
                environ['HTTP_USER_AGENT'].startswith('Python'):
            environ['pylons.status_code_redirect'] = True
            log.info ('ERROR: disabled status_code_redirect')
        start_response(status, headers, exc_info)
        return app_iter

class BisqueAppConfig(AppConfig):
    def add_error_middleware(self, global_conf, app):
        """Add middleware which handles errors and exceptions."""
        app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

        # Display error documents for self.handle_status_codes status codes (and
        # 500 when debug is disabled)

        #if asbool(config['debug']):
        #    app = StatusCodeRedirect(app, self.handle_status_codes)
        #else:
        #    app = StatusCodeRedirect(app, self.handle_status_codes + [500])
        #app = BisqueErrorFilter (app, [401, 403,500])
        return app

    def setup_sqlalchemy(self):
        #from tg import config
        sqlalchemy_url = os.getenv('BISQUE_DBURL', None) or config.get ('sqlalchemy.url')
        has_database = asbool(config.get ('bisque.has_database', True))
        if not has_database or not sqlalchemy_url:
            config['use_transaction_manager'] = False
            config['has_database'] = False
            log.info ("NO DATABASE is configured")
            return
        log.info ("DATABASE %s", sqlalchemy_url)
        config['bisque.has_database'] = True
        self.has_database = True
        if not sqlalchemy_url.startswith('sqlite://'):
            return super(BisqueAppConfig, self).setup_sqlalchemy()
        log.info ("SQLLite special handling NullPool timoout")
        from sqlalchemy.pool import NullPool
        from sqlalchemy import engine_from_config
        engine = engine_from_config(config, 'sqlalchemy.',
                                    poolclass=NullPool,
                                    connect_args = { 'timeout' : 30000 } ,
                                )
        config['pylons.app_globals'].sa_engine = engine
        # Pass the engine to initmodel, to be able to introspect tables
        self.package.model.init_model(engine)
        self.register_hook('controller_wrapper', transaction_retry_wrapper)

    def after_init_config(self):
        "after config"
        config['pylons.response_options']['headers'].pop('Cache-Control', None)
        config['pylons.response_options']['headers'].pop('Pragma', None)
        ##print "DATA", config.get('use_sqlalchemy'), config.get('bisque.use_database')

    def add_static_file_middleware(self, app):
        #from tg import config
        log.info ("ADDING STATIC MIDDLEWARE")
        global public_file_filter
        static_app = public_file_filter
        app = DirectCascade([static_app, app])

        if asbool(config.get ('bisque.static_files', True)):
            # used by engine to add module specific static files
            # Add services static files
            log.info( "LOADING STATICS")
            #static_app.add_path (config['pylons.paths']['static_files'],
            #                     config['pylons.paths']['static_files']
            #                     )

            if config.get('bisque.js_environment', 'production') == 'production':
                static_app.add_path ('', config.get ('bisque.paths.public', './public'))
            else:
                ###staticfilters = []
                for x in pkg_resources.iter_entry_points ("bisque.services"):
                    try:
                        log.info ('found static service: ' + str(x))
                        service = x.load()
                        if not hasattr(service, 'get_static_dirs'):
                            continue
                        staticdirs  = service.get_static_dirs()
                        for d,r in staticdirs:
                            log.debug( "adding static: %s %s" % ( d,r ))
                            static_app.add_path(d,r, "/%s" %x.name)
                    except Exception:
                        log.exception ("Couldn't load bisque service %s" % x)
                        continue
                    #    static_app = BQStaticURLParser(d)
                    #    staticfilters.append (static_app)
            #cascade = staticfilters + [app]
            #print ("CASCADE", cascade)
            log.info( "END STATICS: discovered %s static files " % len(static_app.files.keys()))
        else:
            log.info( "NO STATICS")
        return app


    def add_auth_middleware(self, app, skip_authentication):
        """
        """
        log_stream = config.get ('who.log_stream', 'stdout')
        log_stream = LOG_STREAMS.get (log_stream, log_stream)
        if isinstance(log_stream, basestring ):
            log_stream  = logging.getLogger (log_stream)
        log_level = LOG_LEVELS.get (config['who.log_level'], logging.ERROR)
        log.debug ("LOG_STREAM %s LOG_LEVEL %s" , str(log_stream), str(log_level))

        if 'who.config_file' in config and asbool(config.get('bisque.has_database')):
            parser = WhoConfig(config['here'])
            parser.parse(open(config['who.config_file']))

            if not asbool (skip_authentication):
                app =  PluggableAuthenticationMiddleware(
                           app,
                           parser.identifiers,
                           parser.authenticators,
                           parser.challengers,
                           parser.mdproviders,
                           parser.request_classifier,
                           parser.challenge_decider,
                           log_stream = log_stream,
                           log_level = log_level,
                           remote_user_key=parser.remote_user_key,
                           )
            else:
                app = AuthenticationForgerMiddleware(
                           app,
                           parser.identifiers,
                           parser.authenticators,
                           parser.challengers,
                           parser.mdproviders,
                           parser.request_classifier,
                           parser.challenge_decider,
                           log_stream = log_stream,
                           log_level = log_level,
                           remote_user_key=parser.remote_user_key,
                           )
        else:
            log.info ("MEX auth only")
            # Add mex only authentication
            from repoze.who.plugins.basicauth import BasicAuthPlugin
            from bq.core.lib.mex_auth import make_plugin
            from repoze.who.classifiers import default_request_classifier
            from repoze.who.classifiers import default_challenge_decider
            basicauth = BasicAuthPlugin('repoze.who')
            mexauth   = make_plugin ()

            identifiers = [('mexauth', mexauth)]
            authenticators = [('mexauth', mexauth)]
            challengers = []
            mdproviders = []
            app = PluggableAuthenticationMiddleware(app,
                                                    identifiers,
                                                    authenticators,
                                                    challengers,
                                                    mdproviders,
                                                    default_request_classifier,
                                                    default_challenge_decider,
                                                    log_stream = log_stream,
                                                    log_level = log_level,
                                                    )
        return app





base_config = BisqueAppConfig()



#base_config = AppConfig()
#### Probably won't work for egg
#### Couldn't use pkg_resources ('bq') as it was picking up plugins dir
root=os.path.abspath(__file__ + "/../../core/")
base_config.paths = Bunch(root=root,
                          controllers=os.path.join(root, 'controllers'),
                          static_files=os.path.join(root, 'public'),
                          templates=[os.path.join(root, 'templates')])


#base_config.call_on_startup = [ tgscheduler.start_scheduler ]
base_config.renderers = []
base_config.package = bq.core

#Enable json in expose
base_config.renderers.append('json')
#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
base_config.render_functions.etree = render_etree
base_config.disable_request_extensions=True

# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#  add a set of variable to the template
base_config.variable_provider = helpers.add_global_tmpl_vars


#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True

base_config.model = bq.core.model
base_config.DBSession = bq.core.model.DBSession

# from repoze.who.plugins import basicauth
# from bq.core.lib.mex_auth import MexAuthenticatePlugin
# # Configure the authentication backend
# # Undocumented TG2.1 way of adding identifiers
# # http://docs.repoze.org/who/2.0/configuration.html#module-repoze.who.middleware
# # http://turbogears.org/2.1/docs/main/Config/Authorization.html
# base_config.sa_auth.identifiers = [
#     ('mexuath',  MexAuthenticatePlugin() ),
#     ('basicauth', basicauth.make_plugin() )
#     ]

# try:
#      #from repoze.who.plugins.ldap import LDAPAuthenticatorPlugin, LDAPAttributesPlugin
#     from bq.core.lib.auth import LDAPAuthenticatorPluginExt, LDAPAttributesPluginExt
#     ldap_host='ldap://directory.ucsb.edu'
#     ldap_basedn ='o=ucsb'

#     base_config.sa_auth.authenticators = [
#         ('mexuath',  MexAuthenticatePlugin() ),
#         #('ldap', LDAPAuthenticatorPlugin(ldap_host, ldap_basedn)),
#         ('ldap', LDAPAuthenticatorPluginExt(ldap_host, ldap_basedn)),
#         ]

#     base_config.sa_auth.mdproviders = [
#         #('ldap_attributes', LDAPAttributesPlugin (ldap_host, ['cn', 'sn', 'email']))
#         #('ldap_attributes', LDAPAttributesPluginExt (ldap_host, None))
#         ]
# except ImportError, e:
#     pass


# YOU MUST CHANGE THIS VALUE IN PRODUCTION TO SECURE YOUR APP
#base_config.sa_auth.cookie_secret = "images"
#base_config.sa_auth.cookie_timeout = 60
#base_config.sa_auth.cookie_reissue_time = 50

base_config.auth_backend = 'bisque' # dummy name we setup in who.ini
base_config.sa_auth.dbsession = model.DBSession
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User
# what is the class you want to use to search for groups in the database
base_config.sa_auth.group_class = model.Group
# what is the class you want to use to search for permissions in the database
base_config.sa_auth.permission_class = model.Permission

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
#base_config.sa_auth.form_plugin = None

# override this if you are using a different charset for the login form
#base_config.sa_auth.charset = 'utf-8'

# You may optionally define a page where you want users to be redirected to
# on login:
#base_config.sa_auth.post_login_url = '/auth_service/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
#base_config.sa_auth.post_logout_url = '/auth_service/post_logout'
#base_config.sa_auth.login_url = "/auth_service/login"
