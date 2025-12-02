WebHelpers
++++++++++++

WebHelpers provides functions useful in web applications: generating HTML tags,
showing results a pageful at a time, etc.  It may be used with any web
framework or template engine.  A brief outline is below, but see the
documentation and module docstrings for a more complete list.

``constants``
    Country codes, states and provinces.

``containers``
    High-level container objects and dict/list helpers.

``date``
    Date/time helpers.  These currently format strings based on dates.

``feedgenerator``
    A syndication feed library, used for generating RSS, Atom, etc.
    Ported from Django.

``html``
    A package of HTML-related helpers.

    ``html.builder``
        A library for generating HTML tags with smart escaping.  All
        public symbols are imported into ``webhelpers.html``.

    ``converters``
        Text-to-HTML converters.

    ``tags``
        High-level HTML tags, including form tags, hyperlinks, and 
        Javascript/CSS links.  The ``ModelTags`` class builds input
        tags from database records (for any kind of database).

    ``tools``
        Helpers producing chunks of HTML.

``markdown``
    A text to HTML converter.  Normally invoked via
    ``webhelpers.tools.markdown()``.  (If you use this library directly, you
    may have to wrap the results in ``literal()`` to prevent double escaping.)

``media``
    Helpers for images, PDFs, etc.

``misc``
    Miscellaneous helpers that are neither text, numeric, container, or date.

``number``
    Numeric helpers and number formatters.

``paginate``
    A tool for letting you view a large sequence a screenful at a time,
    with previous/next links.

``pylonslib``
    Helpers for the Pylons framework.  These depend on Pylons context variables
    (request, response, session, etc) or other aspects of Pylons and its
    dependencies.  Most can be ported to other frameworks with little effort.
    
``tags``
    Helpers producing simple HTML tags.

``text``
    Helpers producing string output, suitable for both HTML and non-HTML
    applications.

``textile``
    Another text to HTML converter.  Normally invoked via
    ``webhelpers.tools.textilize()``.  (If you use this library directly, you
    may have to wrap the results in ``literal()`` to prevent double escaping.)

``util``
    Miscellaneous functions.

WebHelpers is package aimed at providing helper functions for use within web
applications.

These functions are intended to ease web development with template languages by
removing common view logic and encapsulating it in re-usable modules as well as
occasionally providing objects for use within controllers to assist with common
web development paradigms.

For support/question/patches, please use the `Pylons mailing list
<http://groups.google.com/group/pylons-discuss>`_.

Requirements
------------

WebHelpers does not have any install dependencies, but some functions depend
on third-party libraries (Routes_, Pylons_, WebOb_, unidecode_) as specified in
their documentation.


.. _Routes:  http://routes.groovie.org/
.. _Pylons:  http://pylonshq.com/
.. _WebOb:   http://pythonpaste.org/WebOb
.. _unidecode:  http://python.org/pypi/Unidecode/
