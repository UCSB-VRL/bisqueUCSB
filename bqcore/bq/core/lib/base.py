# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context
from tg.controllers import RestController
from tg.render import render
from tg import request
from pylons.i18n import ugettext as _, ungettext, N_
#from  bq.core.model import  *

#from bq.data_service.model import *
#from bq.model_service.model import *


__all__ = ['BaseController']


#class BaseController(RestController):
class BaseController(TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity', {})
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)
        #return RestController.__call__(self, environ, start_response)
