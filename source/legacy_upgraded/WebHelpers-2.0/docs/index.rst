WebHelpers
%%%%%%%%%%
:Version: 1.3, released 2011-03-23
:PyPI: http://pypi.python.org/pypi/WebHelpers
:Docs: http://sluggo.scrapping.cc/python/WebHelpers/index.html
:Source: https://bitbucket.org/bbangert/webhelpers (Mercurial)

.. image:: _static/webhelpers-logo.png
   :width: 100px
   :height: 100px
   :alt: WebHelpers Logo
   :align: right

WebHelpers is a wide variety of utility functions for web applications and
other applications. It can be used with any web framework.  See 
`What's New`_ for a list of changes and upgrading hints.

Version 1.3 improves Pyramid support in Paginate via URL generator classes.
(Note: 1.3b1 had a performance regression in Paginate. This is fixed in 1.3
final.)

WebHelpers includes the widely-used HTML tag builder with smart escaping and
convenience functions for common tags such as form fields. The common builder
ensures the tags are syntactically correct and prevent cross-site scripting
attacks and double-escaping. 

Other helpers perform text processing, split a large number of records into
pages, generate Atom/RSS feeds with geographical (GIS) data, handle MIME types,
calculate numerica statistics, and more.  There are also high-level container
types, including a value counter and accumulator.  There are lists of country
names, country codes, US states, Canadian provinces, and UK counties.

WebHelpers itself depends only on MarkupSafe_, which has an optional C
speedup for HTML escaping. However, a few individual helpers depend on 
Routes_, Unidecode_, WebOb_, or Pylons_
as noted in their documentation.  WebHelpers requires Python 2.4 or higher,
and has not yet been tested with Python 3. An extensive test suite for doctest
and Nose is included.

For support/questions/patches, please use the pylons-discuss_ mailing list.

.. toctree::
   :maxdepth: 2

   contents

.. toctree::
   :maxdepth: 1

   whats_new
   changelog
   third_party
   todo
   development
   todo

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _What's New: whats_new.html
.. _MarkupSafe: http://pypi.python.org/pypi/MarkupSafe
.. _Routes: http://routes.groovie.org/
.. _Unidecode: http://pypi.python.org/pypi/Unidecode/
.. _WebOb: http://pythonpaste.org/webob/
.. _Pylons: http://pylonshq.com/
.. _pylons-discuss: http://groups.google.com/group/pylons-discuss
