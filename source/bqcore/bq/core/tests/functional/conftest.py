"""Pytest fixtures and setup for bqcore tests."""

import pytest
from os import path
from tg import config
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from webtest import TestApp

from bq.core.model import DBSession
from bq.core.tests import setup_db, teardown_db


@pytest.fixture(scope="session")
def app():
    """Returns a functional test app with authentication enabled."""
    conf_dir = "config"
    section = "main_with_auth"  # Use config section with authentication enabled
    wsgiapp = loadapp(f"config:test.ini#{section}", relative_to=conf_dir)
    test_file = path.join(conf_dir, "test.ini")
    SetupCommand("setup-app").run([test_file])
    app = TestApp(wsgiapp)
    return app



@pytest.fixture(scope="module", autouse=True)
def init_database():
    """Setup and teardown the database once per module."""
    setup_db()
    yield
    teardown_db()


@pytest.fixture
def dbsession():
    """Provide a clean DBSession per test."""
    try:
        yield DBSession
        DBSession.flush()
    except Exception:
        DBSession.rollback()
        raise
    finally:
        DBSession.rollback()