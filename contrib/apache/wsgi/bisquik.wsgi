import sys

APPDIR= "/usr/local/turbogears/bisquik"
APPNAME="bisquik"
sys.path.append(APPDIR)
sys.stdout = sys.stderr

import os
#os.environ['PYTHON_EGG_CACHE'] = APP


import atexit
import cherrypy
import cherrypy._cpwsgi
import turbogears

turbogears.update_config(configfile=APPDIR, modulename="%s.config" % (APPNAME))
turbogears.config.update({'global': {'server.environment': 'production'}})
turbogears.config.update({'global': {'autoreload.on': False}})
turbogears.config.update({'global': {'server.log_to_screen': False}})

#For non root mounted app:
#turbogears.config.update({'global': {'server.webpath': '/myfirstapp'}})

import bisquik.controllers

cherrypy.root = bisquik.controllers.Root()

if cherrypy.server.state == 0:
    atexit.register(cherrypy.server.stop)
    cherrypy.server.start(init_only=True, server_class=None)

For root mounted app
application = cherrypy._cpwsgi.wsgiAppi

#For none-root mounted app
#def application(environ, start_response):
#    environ['SCRIPT_NAME'] = ''
#    return cherrypy._cpwsgi.wsgiApp(environ, start_response)