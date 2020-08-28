# -*- coding: utf-8 -*-
"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.

It's perfectly fine to re-use this definition in the bqcore application,
though.

"""
import logging
from tg import config

import os
from datetime import datetime
import sys

try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: No module named hashlib\n'
             'If you are on python2.4 this library is not part of python. '
             'Please install it. Example: easy_install hashlib')

import sqlalchemy as sa
from sqlalchemy import Table, ForeignKey, Column, select
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation, synonym#, validates
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.hybrid import hybrid_property
from bq.core.model import DeclarativeBase, metadata, DBSession

log = logging.getLogger('bq.core.model.auth')

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if config.get('sqlalchemy.url', '').startswith ("sqlite://"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        log.debug ("SQLITE: enabling foriegn keys")

@event.listens_for(Engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    if config.get('sqlalchemy.url', '').startswith ("sqlite://"):
        dbapi_connection.isolation_level = None
        log.debug ("SQLITE: Disable automatic transactions")

@event.listens_for(Engine, "begin")
def do_begin(conn):
    # emit our own BEGIN
    if config.get('sqlalchemy.url', '').startswith ("sqlite://"):
        #http://docs.sqlalchemy.org/en/rel_1_0/dialects/sqlite.html#transaction-isolation-level
        #conn.execute("BEGIN EXCLUSIVE")
        conn.execute("BEGIN ")
        log.debug ("SQLITE: Begin Transaction")

# http://docs.sqlalchemy.org/en/latest/core/pooling.html#pool-disconnects-pessimistic
# http://docs.sqlalchemy.org/en/latest/core/pooling.html#disconnect-handling-pessimistic
#@event.listens_for(Engine, "engine_connect")
# def ping_connection(connection, branch):
#     if branch:
#         # "branch" refers to a sub-connection of a connection,
#         # we don't want to bother pinging on these.
#         return
#     # turn off "close with result".  This flag is only used with
#     # "connectionless" execution, otherwise will be False in any case
#     save_should_close_with_result = connection.should_close_with_result
#     connection.should_close_with_result = False
#     try:
#         # run a SELECT 1.   use a core select() so that
#         # the SELECT of a scalar value without a table is
#         # appropriately formatted for the backend
#         connection.scalar(select([1]))
#     except sa.exc.DBAPIError as err:
#         # catch SQLAlchemy's DBAPIError, which is a wrapper
#         # for the DBAPI's exception.  It includes a .connection_invalidated
#         # attribute which specifies if this connection is a "disconnect"
#         # condition, which is based on inspection of the original exception
#         # by the dialect in use.
#         if err.connection_invalidated:
#             # run the same SELECT again - the connection will re-validate
#             # itself and establish a new connection.  The disconnect detection
#             # here also causes the whole connection pool to be invalidated
#             # so that all stale connections are discarded.
#             connection.scalar(select([1]))
#         else:
#             raise
#     finally:
#         # restore "close with result"
#         connection.should_close_with_result = save_should_close_with_result

__all__ = ['User', 'Group', 'Permission', 'HashPassword', 'FreeTextPassword']



from sqlalchemy.engine import Engine

# THIS APPEARS TO BE A DUPLICATE (bad merge) of the above..
#@event.listens_for(Engine, "connect")
#def set_sqlite_pragma(dbapi_connection, connection_record):
#    if config.get('sqlalchemy.url', '').startswith ("sqlite://"):
#        cursor = dbapi_connection.cursor()
#        cursor.execute("PRAGMA foreign_keys=ON")
#        cursor.close()


#{ Association tables


# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
#group_permission_table = Table('tg_group_permission', metadata,
group_permission_table = Table('group_permission', metadata,
    Column('group_id', Integer, ForeignKey('tg_group.group_id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
#    Column('permission_id', Integer, ForeignKey('tg_permission.permission_id',
    Column('permission_id', Integer, ForeignKey('permission.permission_id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
#user_group_table = Table('tg_user_group', metadata,
user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.user_id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('tg_group.group_id',
        onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
)

class HashPassword():
    @staticmethod
    def create_password(password):
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()
        return hashed_password

    @staticmethod
    def check_password(passval, password):
        hash = sha1()
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        hash.update(password + str(passval[:40]))
        return passval[40:] == hash.hexdigest()

class FreeTextPassword ():
    @staticmethod
    def create_password(password):
        return password
    @staticmethod
    def check_password(passval, password):
        return passval == password


password_map = {
    'hashed' : HashPassword,
    'freetext' : FreeTextPassword,
    }



#{ The auth* model itself


class Group(DeclarativeBase):
    """
    Group definition for :mod:`repoze.what`.

    Only the ``group_name`` column is required by :mod:`repoze.what`.

    """

    __tablename__ = 'tg_group'

    #{ Columns

    group_id = Column(Integer, autoincrement=True, primary_key=True)
    group_name = Column(Unicode(16), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)

    #{ Relations

    users = relation('User', secondary=user_group_table, backref='groups')

    #{ Special methods

    def __repr__(self):
        return ('<Group: name=%s>' % self.group_name).encode('utf-8')

    def __unicode__(self):
        return self.group_name

    #}


# The 'info' argument we're passing to the email_address and password columns
# contain metadata that Rum (http://python-rum.org/) can use generate an
# admin interface for your models.
class User(DeclarativeBase):
    """
    User definition.

    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.

    """
    __tablename__ = 'tg_user'
    callbacks = []

    #{ Columns

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    user_name = Column(Unicode(255), unique=True, nullable=False)
    _email_address = Column('email_address', Unicode(255), unique=True, nullable=False,
                           info={'rum': {'field':'Email'}})
    display_name = Column(Unicode(255))
    _password = Column('password', Unicode(80),
                       info={'rum': {'field':'Password'}})
    created = Column(DateTime, default=datetime.now)

    #{ Special methods
    def __init__(self, **kw):
        super(User, self).__init__(**kw)
        if 'password' in kw:
            self.password = kw['password'] # Force hashing if needed

        self.on_create()

    def __repr__(self):
        return ('<User: name=%r, email=%r, display=%r>' % (
                self.user_name, self.email_address, self.display_name)).encode('utf-8')

    def __unicode__(self):
        return self.display_name or self.user_name

    #{ Getters and setters

    @property
    def permissions(self):
        """Return a set with all permissions granted to the user."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    @classmethod
    def by_email_address(cls, email):
        """Return the user object whose email address is ``email``."""
        return DBSession.query(cls).filter_by(email_address=email).first()

    @classmethod
    def by_user_name(cls, username):
        """Return the user object whose user name is ``username``."""
        return DBSession.query(cls).filter_by(user_name=username).first()

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""

        password_type = config.get ('bisque.login.password', 'freetext')
        password_cls  = password_map.get(password_type, FreeTextPassword)

        password = password_cls.create_password (password)
        # Make sure the hashed password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # columns
        log.debug ("Setting %s password", password_type)

        if not isinstance(password, unicode):
            password = password.decode('utf-8')
        self._password = password
        self.on_update()

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym('_password', descriptor=property(_get_password,
                                                        _set_password))

    #}

    def validate_password(self, password):
        """
        Check the password against existing credentials.

        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool

        """

        password_type = config.get ('bisque.login.password', 'freetext')
        password_cls  = password_map.get(password_type, FreeTextPassword)

        if isinstance(password, unicode):
            password = password.encode('utf-8')

        return password_cls.check_password(self.password, password)

    #@hybrid_property
    def _get_email(self):
        return self._email_address

    #@email_address.setter
    def _set_email(self, email):
        self._email_address = email
        self.on_update()

    email_address = synonym('_email_address', descriptor=property(_get_email,
                                                                  _set_email))



    def on_create(self):
        for cb in User.callbacks:
            cb(tg_user = self, operation = 'create')
    def on_update(self):
        # never run update on new objects
        if self.user_id is None:
            return
        for cb in User.callbacks:
            cb(tg_user = self, operation = 'update')


# Newer sqlalchemy does not allow modification of session ..
#def create_user(mapper, connection, target, ):
#    for cb in User.callbacks:
#        cb(tg_user = target, operation = 'create')
#def update_user(mapper, connection, target, ):
#    for cb in User.callbacks:
#        cb(tg_user = target, operation = 'update')
#event.listen(User, 'after_update', update_user )
#event.listen(User, 'after_insert', create_user )



class Permission(DeclarativeBase):
    """
    Permission definition for :mod:`repoze.what`.

    Only the ``permission_name`` column is required by :mod:`repoze.what`.

    """

#    __tablename__ = 'tg_permission'
    __tablename__ = 'permission'

    #{ Columns

    permission_id = Column(Integer, autoincrement=True, primary_key=True)
    permission_name = Column(Unicode(63), unique=True, nullable=False)
    description = Column(Unicode(255))

    #{ Relations

    groups = relation(Group, secondary=group_permission_table,
                      backref='permissions')

    #{ Special methods

    def __repr__(self):
        return ('<Permission: name=%r>' % self.permission_name).encode('utf-8')

    def __unicode__(self):
        return self.permission_name

    #}


#}
