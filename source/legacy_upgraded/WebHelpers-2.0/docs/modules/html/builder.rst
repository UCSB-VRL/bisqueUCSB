:mod:`webhelpers.html.builder`
================================================

.. automodule:: webhelpers.html.builder

.. currentmodule:: webhelpers.html.builder

Classes
-------

.. autoclass:: literal(s, encoding=None, errors=strict')
   :members:

   .. automethod:: escape

      Same as the ``escape`` function but return the proper subclass
      in subclasses.

   .. automethod:: unescape

   .. automethod:: striptags

.. class:: HTML

   Described above.

Functions
---------

.. autofunction:: lit_sub

.. function:: url_escape(s, safe='/')

    Urlencode the path portion of a URL. This is the same function as
    ``urllib.quote`` in the Python standard library. It's exported here
    with a name that's easier to remember.

The ``markupsafe`` package has a function ``soft_unicode`` which converts a
string to Unicode if it's not already. Unlike the Python builtin ``unicode()``,
it will not convert ``Markup`` (``literal``) to plain Unicode, to avoid
overescaping. This is not included in WebHelpers but you may find it useful.
