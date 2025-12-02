.. -*-rst-*-

NOTICE
======

This software is not actively maintained. Simple bugfixes and other patches
will be accepted, and released.

Introduction
============

WebError provides WSGI middleware for the debugging and handling of errors
inside of WSGI applications.

Usage
=====

There are two primary WSGI middleware components:

weberror.errormiddleware.make_error_middleware 
----------------------------------------------

This middleware should be used for production deployed applications and is used
to track extra information regarding errors that occur. These error entries can
additionally be emailed to a given email address using the *error_email*
option. Example usage::

  from weberror.errormiddleware import make_error_middleware
  app = make_error_middleware(app, global_conf)


weberror.evalexception.make_eval_exception
------------------------------------------

This middleware is used to help debug errors in wsgi applications during
development and should not be used in production. Example usage::

  from weberror.evalexception import make_eval_exception
  app = make_eval_exception(app, global_conf)
