# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
# !!! modern approach
import pytest

from bq.core import model

class ModelTest:
    klass = None
    attrs = {}

    @pytest.fixture(autouse=True)
    def setup_model(self, dbsession):
        """Set up and tear down the object."""
        try:
            combined_attrs = dict(self.attrs)
            combined_attrs.update(self.do_get_dependencies())
            self.obj = self.klass(**combined_attrs)
            dbsession.add(self.obj)
            dbsession.flush()
        except Exception:
            dbsession.rollback()
            raise
        yield
        dbsession.rollback()

    def do_get_dependencies(self):
        return {}

    def test_create_obj(self):
        assert self.obj is not None

    def test_query_obj(self, dbsession):
        result = dbsession.query(self.klass).one()
        for key, val in self.attrs.items():
            assert getattr(result, key) == val

class TestGroup(ModelTest):
    """Unit test case for the ``Group`` model."""
    klass = model.Group
    attrs = dict(
        group_name = "test_group",
        display_name = "Test Group"
        )


class TestUser(ModelTest):
    klass = model.User
    attrs = {
        "user_name": "ignucius",
        "email_address": "ignucius@example.org",
    }

    def test_obj_creation_username(self):
        assert self.obj.user_name == "ignucius"

    def test_obj_creation_email(self):
        assert self.obj.email_address == "ignucius@example.org"

    def test_no_permissions_by_default(self):
        assert len(self.obj.permissions) == 0

    def test_getting_by_email(self, dbsession):
        user = model.User.by_email_address("ignucius@example.org")
        assert user == self.obj

class TestPermission(ModelTest):
    klass = model.Permission
    attrs = {
        "permission_name": "test_permission",
        "description": "This is a test Description"
    }

# !!! old approach
# from nose.tools import eq_

# from bq.core import model
# from bq.core.tests.models import ModelTest

# class TestGroup(ModelTest):
#     """Unit test case for the ``Group`` model."""
#     klass = model.Group
#     attrs = dict(
#         group_name = "test_group",
#         display_name = "Test Group"
#         )


# class TestUser(ModelTest):
#     """Unit test case for the ``User`` model."""

#     klass = model.User
#     attrs = dict(
#         user_name = "ignucius",
#         email_address = "ignucius@example.org"
#         )

#     def test_obj_creation_username(self):
#         """The obj constructor must set the user name right"""
#         eq_(self.obj.user_name, "ignucius")

#     def test_obj_creation_email(self):
#         """The obj constructor must set the email right"""
#         eq_(self.obj.email_address, "ignucius@example.org")

#     def test_no_permissions_by_default(self):
#         """User objects should have no permission by default."""
#         eq_(len(self.obj.permissions), 0)

#     def test_getting_by_email(self):
#         """Users should be fetcheable by their email addresses"""
#         him = model.User.by_email_address("ignucius@example.org")
#         eq_(him, self.obj)


# class TestPermission(ModelTest):
#     """Unit test case for the ``Permission`` model."""

#     klass = model.Permission
#     attrs = dict(
#         permission_name = "test_permission",
#         description = "This is a test Description"
#         )
