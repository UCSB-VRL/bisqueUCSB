# -*- coding: utf-8 -*-
"""Unit and functional test suite for bqcore."""

from os import path
import sys

from tg import config
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from routes import url_for
from webtest import TestApp
from nose.tools import eq_
import transaction

from bq.core import model
from bq.core.model import DBSession

__all__ = ['setup_db', 'teardown_db', 'TestController', 'url_for']

def setup_db():
    """Method used to build a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.init_model(engine)
    model.metadata.create_all(engine)
    print "SETUP DB"

def teardown_db():
    """Method used to destroy a database"""
    DBSession.rollback()
    DBSession.remove()
    engine = config['pylons.app_globals'].sa_engine
    model.metadata.drop_all(engine)
    print "TEARDOWN DB"

    #transaction.doom()

def setup_app(section = 'main_without_authn'):
    conf_dir = 'config'  # config.here
    wsgiapp = loadapp('config:test.ini#%s' % section , relative_to=conf_dir)
    app = TestApp(wsgiapp)
    # Setting it up:
    test_file = path.join(conf_dir, 'test.ini')
    cmd = SetupCommand('setup-app')
    cmd.run([test_file])
    #transaction.commit()
    return app

def teardown_app ():
    teardown_db()

class TestController(object):
    """
    Base functional test case for the controllers.

    The bqcore application instance (``self.app``) set up in this test
    case (and descendants) has authentication disabled, so that developers can
    test the protected areas independently of the :mod:`repoze.who` plugins
    used initially. This way, authentication can be tested once and separately.

    Check bq.tests.functional.test_authentication for the repoze.who
    integration tests.

    This is the officially supported way to test protected areas with
    repoze.who-testutil (http://code.gustavonarea.net/repoze.who-testutil/).

    """

    application_under_test = 'main_without_authn'

    @classmethod
    def setup_class(cls):
        """Method called by nose before running each test"""
        print "TestController SETUP"
        # Loading the application:
        cls.app = setup_app()
        print "Setup COmplete"

    @classmethod
    def teardown_class(cls):
        """Method called by nose after running each test"""
        # Cleaning up the database:
        #DBSession.rollback()
        #DBSession.expunge_all()
        print "TestController TEARDOWN"
        teardown_db()

class DBTest(object):
    """Test that only uses datatbase resources
    """
    application_under_test = "main"

    def setUp(self):
        print "DBTest.setup"

    def tearDown(self):
        """Method called by nose after running each test"""
        # Cleaning up the database:
        #DBSession.rollback()
        #DBSession.expunge_all()
        print "DBTEST.teardown"
