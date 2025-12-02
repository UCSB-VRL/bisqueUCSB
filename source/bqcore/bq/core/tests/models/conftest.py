# tests/models/conftest.py or directly in test_auth.py
import pytest
from bq.core.model import DBSession
from bq.core.tests import setup_db, teardown_db


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
