# -*- coding: utf-8 -*-
"""WSGI middleware initialization for the bqcore application."""
import os
import sys
import logging
import pkg_resources
#from webtest import TestApp

#from paste.cascade import Cascade
from paste.registry import RegistryManager

from bq.config.app_cfg import base_config
from bq.config.environment import load_environment
from bq.core.controllers import root
from bq.util.paths import site_cfg_path
from bq.util.proxy import Proxy
from tg.configuration import config
from .direct_cascade import DirectCascade

__all__ = ['make_app', 'bisque_app']

log = logging.getLogger("bq.config.middleware")

bisque_app = None

def add_profiler(app):
    if config.get('bisque.profiler.enable', None) == 'true': #inialize profiler app
        from bq.util.LinesmanProfiler import BQProfilingMiddleware
        app = BQProfilingMiddleware(app, config.get('sqlalchemy.url', None), config.get('bisque.profiler.path', '__profiler__'))
        log.info("HOOKING profiler app")
    return app #pass through

base_config.register_hook('before_config', add_profiler)

def save_bisque_app(app):
    global bisque_app
    bisque_app = app # RegistryManager(app, streaming = True)
    log.info ("HOOKING App %s", str(app))
    return app

base_config.register_hook('before_config', save_bisque_app)

# Use base_config to setup the necessary PasteDeploy application factory.
# make_base_app will wrap the TG2 app with all the middleware it needs.
make_base_app = base_config.setup_tg_wsgi_app(load_environment)



class LogWSGIErrors(object):
    def __init__(self, app, logger, level):
        self.app = app
        self.logger = logger
        self.level = level

    def __call__(self, environ, start_response):
        environ['wsgi.errors' ] = self
        return self.app(environ, start_response)

    def write(self, message):
        if message != '\n':
            self.logger.log(self.level, message)

class ProxyApp(object):
    def __init__(self, app):
        self.oldapp = app

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith('/proxy/'):
            log.debug('ProxyApp activated')
            command = environ['PATH_INFO'].split('/', 3)
            #log.debug('ProxyApp command: %s', command)
            address = 'http://%s'%command[2]
            path = '/%s'%command[3]
            environ['PATH_INFO'] = path
            proxy = Proxy(address)
            return proxy(environ, start_response)
        return self.oldapp(environ, start_response)


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set bqcore up with the settings found in the PasteDeploy configuration
    file used.

    :param global_conf: The global settings for bqcore (those
        defined under the ``[DEFAULT]`` section).
    :type global_conf: dict
    :param full_stack: Should the whole TG2 stack be set up?
    :type full_stack: str or bool
    :return: The bqcore application with all the relevant middleware
        loaded.

    This is the PasteDeploy factory for the bqcore application.

    ``app_conf`` contains all the application-specific settings (those defined
    under ``[app:main]``.


    """
    site_cfg = site_cfg_path()
    logging.config.fileConfig(site_cfg)
    global bisque_app

    app = make_base_app(global_conf, full_stack=True, **app_conf)

    #from repoze.profile.profiler import AccumulatingProfileMiddleware

    # Wrap your base TurboGears 2 application with custom middleware here
    #app = AccumulatingProfileMiddleware(
    #    app,
    #    log_filename='/tmp/proj.log',
    #    cachegrind_filename='/tmp/cachegrind.out.bar',
    #    discard_first_request=True,
    #    flush_at_shutdown=True,
    #    path='/__profile__'
    #    )

    # Wrap your base TurboGears 2 application with custom middleware here
    #from tg import config

    app = ProxyApp(app)
    bisque_app = app
    app = LogWSGIErrors(app, logging.getLogger('bq.middleware'), logging.ERROR)

    # Call the loader in the root controller
    log.info ("wsgi - Application : complete")
    root.startup()
    log.info ("Root-Controller: startup complete")

    return app



class AddValue(object):
    def __init__(self, app, key, value):
        self.app = app
        self.key = key
        self.value = value

    def __call__(self, environ, start_response):
        environ = dict(environ)
        environ[self.key] = self.value
        return self.app(environ, start_response)

def add_global(global_conf, **app_conf):
    def filter(app):
        return AddValue(app, 'global_app', app)
            #app_conf.get('key', 'default'),
            #app_conf.get('value', 'defaultvalue'))
    return filter
