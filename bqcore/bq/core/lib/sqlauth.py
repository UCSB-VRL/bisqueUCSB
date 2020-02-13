"""Example of a simplistic, importable authenticator plugin

Intended to work like a quick-started SQLAlchemy plugin"""
from repoze.who.plugins.sa import (
    SQLAlchemyAuthenticatorPlugin,
    SQLAlchemyUserMDPlugin,
)
from repoze.what.plugins.sql import configure_sql_adapters
from repoze.what.middleware import AuthorizationMetadata

from bq.core import model
auth_plugin = SQLAlchemyAuthenticatorPlugin(model.User, model.DBSession)
md_plugin = SQLAlchemyUserMDPlugin(model.User, model.DBSession )
_source_adapters = configure_sql_adapters(
    model.User,
    model.Group,
    model.Permission,
    model.DBSession,
)
md_group_plugin = AuthorizationMetadata(
    {'sqlauth': _source_adapters['group']},
    {'sqlauth': _source_adapters['permission']},
)

# THIS IS CRITICALLY IMPORTANT!  Without this your site will
# consider every repoze.what predicate True!
from repoze.what.plugins.pylonshq import booleanize_predicates
booleanize_predicates()
