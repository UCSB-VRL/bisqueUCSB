Third-party helpers
===================

The following third-party Python packages are not included in WebHelpers due to
their size or dependencies, but are often used in WebHelpers applications.

`BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_

    A robust HTML/XML parser that can make sense of bad markup.

`HTMLTidy <http://tidy.sourceforge.net/>`_

    Clean up and pretty print HTML. This is a C library. There are several
    `Python bindings
    <http://pypi.python.org/pypi?%3Aaction=search&term=tidy&submit=search>`_ to
    it.

`Unidecode <http://pypi.python.org/pypi/Unidecode>`_

    Convert Unicode characters to ASCII equivalents. Accented letters and
    symbols are converted to a visual approximation, and non-Latin letters
    are converted to their standard Latin pronounciation.  Several of the
    ``convert_\*`` functions in ``webhelpers.text`` will use Unidecode if
    it's installed.

`Unipath <http://pypi.python.org/pypi/Unipath>`_

    An object-oriented alternative to the path functions in ``os``,
    ``os.path``, and ``shutil``.  Similar packages include
    `path.py <http://pypi.python.org/pypi/path.py>`_. 
