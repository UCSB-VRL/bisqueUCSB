# -*- coding: utf-8 -*-
"""Sample controller with all its actions protected."""
from tg import expose, flash
from repoze.what.predicates import has_permission
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider

from bq.core.lib.base import BaseController
#from bq.model import DBSession, metadata

__all__ = ['SecureController']


class SecureController(BaseController):
    """Sample controller-wide authorization"""

    # The predicate that must be met for all the actions in this controller:
    allow_only = has_permission('manage',
                                msg='Only for people with the "manage" permission')

    @expose('bq.core.templates.index')
    def index(self):
        """Let the user know that's visiting a protected controller."""
        flash("Secure Controller here")
        return dict(page='index')

    @expose('bq.core.templates.index')
    def some_where(self):
        """Let the user know that this action is protected too."""
        return dict(page='some_where')
