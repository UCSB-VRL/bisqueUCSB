:mod:`webhelpers.feedgenerator`
================================================

This is a port of Django's feeed generator for creating RSS and Atom feeds.
The Geo classes for publishing geographical (GIS) data are also ported.

.. automodule:: webhelpers.feedgenerator

.. currentmodule:: webhelpers.feedgenerator

Classes
-------

.. autoclass:: SyndicationFeed
    :members:
    :undoc-members:

.. autoclass:: Enclosure
    :members:
    :undoc-members:

.. autoclass:: RssFeed
    :members:
    :undoc-members:

.. autoclass:: RssUserland091Feed
    :members:
    :undoc-members:

.. autoclass:: Rss201rev2Feed
    :members:
    :undoc-members:

.. autoclass:: Atom1Feed
    :members:
    :undoc-members:

``DefaultFeed`` is an alias for ``Rss201rev2Feed``.

Functions
---------

.. autofunction:: rfc2822_date
.. autofunction:: rfc3339_date
.. autofunction:: get_tag_uri

GIS subclasses
--------------

These classes allow you to include geometries (e.g., latitude/longitude) in
your feed. The implementation is in a mixin class:

.. autoclass:: GeoFeedMixin
   :members:

   Methods:

Two concrete subclasses are provided:

.. autoclass:: GeoAtom1Feed
   :members:

.. autoclass:: W3CGeoFeed
   :members:

A minimal geometry class is included:

.. autoclass:: Geometry
   :members:

