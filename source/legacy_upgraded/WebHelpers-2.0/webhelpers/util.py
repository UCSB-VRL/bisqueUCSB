"""Utility functions used by various web helpers.

This module contains support functions used by other helpers, and functions for
URL manipulation. Most of these helpers predate the 0.6 reorganization; they
would have been put in other subpackages if they have been created later.
"""
import cgi
import copy
import sys
import urllib.request, urllib.parse, urllib.error
import urllib.parse
# from UserDict import DictMixin # Python 2
from collections import UserDict # !!! Python 3
from xml.sax.saxutils import XMLGenerator

try:
    from urllib.parse import parse_qs
except ImportError:   # Python < 2.6
    from cgi import parse_qs


def update_params(_url, _debug=False, **params):
    """Update query parameters in a URL.

    ``_url`` is any URL, with or without a query string.

    ``\*\*params`` are query parameters to add or replace. Each value may be a
    string, a list of strings, or None. Passing a list generates multiple
    values for the same parameter. Passing None deletes the corresponding
    parameter if present.

    Return the new URL.

    *Debug mode:* if a pseudo-parameter ``_debug=True`` is passed,
    return a tuple: ``[0]`` is the URL without query string or fragment,
    ``[1]`` is the final query parameters as a dict, and ``[2]`` is the
    fragment part of the original URL or the empty string.

    Usage:

    >>> update_params("foo", new1="NEW1")
    'foo?new1=NEW1'
    >>> update_params("foo?p=1", p="2")
    'foo?p=2'
    >>> update_params("foo?p=1", p=None)
    'foo'
    >>> update_params("http://example.com/foo?new1=OLD1#myfrag", new1="NEW1")
    'http://example.com/foo?new1=NEW1#myfrag'
    >>> update_params("http://example.com/foo?new1=OLD1#myfrag", new1="NEW1", _debug=True)
    ('http://example.com/foo', {'new1': 'NEW1'}, 'myfrag')
    >>> update_params("http://www.mau.de?foo=2", brrr=3)
    'http://www.mau.de?foo=2&brrr=3'
    >>> update_params("http://www.mau.de?foo=A&foo=B", foo=["C", "D"])
    'http://www.mau.de?foo=C&foo=D'

    """
    url, fragment = urllib.parse.urldefrag(_url)
    if "?" in url:
        url, qs = url.split("?", 1)
        query = parse_qs(qs)
    else:
        query = {}
    for key, value in params.items():
        if value is not None:
            query[key] = value
        elif key in query:
            del query[key]
    if _debug:
        return url, query, fragment
    qs = urllib.parse.urlencode(query, True)
    if qs:
        qs = "?" + qs
    if fragment:
        fragment = "#" + fragment
    return "%s%s%s" % (url, qs, fragment)

def cgi_escape(s, quote=False):
    """Replace special characters '&', '<' and '>' by SGML entities.

    This is a slightly more efficient version of the cgi.escape by
    using 'in' membership to test if the replace is needed.

    This function returns a plain string. Programs using the HTML builder
    should call ``webhelpers.html.builder.escape()`` instead of this to prevent
    double-escaping.

    Changed in WebHelpers 1.2: escape single-quote as well as double-quote.

    """
    if '&' in s:
        s = s.replace("&", "&amp;") # Must be done first!
    if '<' in s:
        s = s.replace("<", "&lt;")
    if '>' in s:
        s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
        s = s.replace("'", "&apos;")
    return s

def html_escape(s):
    """HTML-escape a string or object.
    
    This converts any non-string objects passed into it to strings
    (actually, using ``unicode()``).  All values returned are
    non-unicode strings (using ``&#num;`` entities for all non-ASCII
    characters).
    
    None is treated specially, and returns the empty string.
    
    This function returns a plain string. Programs using the HTML builder
    should wrap the result in ``literal()`` to prevent double-escaping.

    """
    if s is None:
        return ''
    if not isinstance(s, str):
        if hasattr(s, '__unicode__'):
            s = str(s)
        else:
            s = str(s)
    s = cgi_escape(s, True)
    if isinstance(s, str):
        s = s.encode('ascii', 'xmlcharrefreplace')
    return s


def iri_to_uri(iri):
    """
    Convert an IRI portion to a URI portion suitable for inclusion in a URL.

    (An IRI is an Internationalized Resource Identifier.)

    This is the algorithm from section 3.1 of RFC 3987.  However, since 
    we are assuming input is either UTF-8 or unicode already, we can 
    simplify things a little from the full method.

    Returns an ASCII string containing the encoded result.

    """
    # Called by webhelpers.feedgenerator
    #
    # The list of safe characters here is constructed from the printable ASCII
    # characters that are not explicitly excluded by the list at the end of
    # section 3.1 of RFC 3987.
    if iri is None:
        return iri
    return urllib.parse.quote(iri, safe='/#%[]=:;$&()+,!?')


class Partial(object):
    
    """
    A partial function object.

    Equivalent to functools.partial, which was introduced in Python 2.5.

    """
    
    def __init__(*args, **kw):
        self = args[0]
        self.fn, self.args, self.kw = (args[1], args[2:], kw)
    
    def __call__(self, *args, **kw):
        if kw and self.kw:
            d = self.kw.copy()
            d.update(kw)
        else:
            d = kw or self.kw
        return self.fn(*(self.args + args), **d)

class SimplerXMLGenerator(XMLGenerator):
    """A subclass of Python's SAX XMLGenerator."""

    # Used by webhelpers.feedgenerator

    def addQuickElement(self, name, contents=None, attrs=None):
        """Add an element with no children."""
        if attrs is None:
            attrs = {}
        self.startElement(name, attrs)
        if contents is not None:
            self.characters(contents)
        self.endElement(name)

class UnicodeMultiDict(UserDict):
    """
    A MultiDict wrapper that decodes returned values to unicode on the fly. 
    
    Decoding is not applied to assigned values.
    """

    def __init__(self, multi=None, encoding=None, errors='strict', decode_keys=False):
        # MultiDict-like storage
        self.multi = multi or {}
        if encoding is None:
            encoding = sys.getdefaultencoding()
        self.encoding = encoding
        self.errors = errors
        self.decode_keys = decode_keys

    def _decode_key(self, key):
        if self.decode_keys:
            key = key.decode(self.encoding, self.errors) if isinstance(key, bytes) else key
        return key

    def _decode_value(self, value):
        """
        Decode the specified (``str`` or `FieldStorage``) value to unicode. 
        
        ``FieldStorage`` objects are specially handled.
        
        """
        if isinstance(value, dict):  # Handle FieldStorage-like behavior (use dict as a substitute)
            value = copy.copy(value)
            if self.decode_keys:
                value['name'] = value['name'].decode(self.encoding, self.errors) if isinstance(value.get('name'), bytes) else value.get('name')
            value['filename'] = value['filename'].decode(self.encoding, self.errors) if isinstance(value.get('filename'), bytes) else value.get('filename')
        else:
            try:
                value = value.decode(self.encoding, self.errors) if isinstance(value, bytes) else value
            except AttributeError:
                pass
        return value

    def __getitem__(self, key):
        return self._decode_value(self.multi[key])

    def __setitem__(self, key, value):
        self.multi[key] = value

    def add(self, key, value):
        """Add the key and value, not overwriting any previous value."""
        if key not in self.multi:
            self.multi[key] = value
        else:
            if isinstance(self.multi[key], list):
                self.multi[key].append(value)
            else:
                self.multi[key] = [self.multi[key], value]

    def getall(self, key):
        """Return list of all values matching the key (may be an empty list)."""
        return [self._decode_value(v) for v in self.multi.get(key, [])]

    def getone(self, key):
        """Return one value matching key. Raise KeyError if multiple matches."""
        value = self.multi.get(key)
        if isinstance(value, list):
            if len(value) == 1:
                return self._decode_value(value[0])
            raise KeyError(f"Multiple values found for key {key}")
        return self._decode_value(value)

    def mixed(self):
        """Return dict where values are single values or a list of values."""
        unicode_mixed = {}
        for key, value in self.multi.items():
            if isinstance(value, list):
                value = [self._decode_value(v) for v in value]
            else:
                value = self._decode_value(value)
            unicode_mixed[self._decode_key(key)] = value
        return unicode_mixed

    def dict_of_lists(self):
        """Return dict where each key is associated with a list of values."""
        unicode_dict = {}
        for key, value in self.multi.items():
            value = [self._decode_value(v) for v in value]
            unicode_dict[self._decode_key(key)] = value
        return unicode_dict

    def __delitem__(self, key):
        del self.multi[key]

    def __contains__(self, key):
        return key in self.multi

    has_key = __contains__  # Deprecated in Python 3, but kept for compatibility

    def clear(self):
        self.multi.clear()

    def copy(self):
        return UnicodeMultiDict(self.multi.copy(), self.encoding, self.errors)

    def setdefault(self, key, default=None):
        return self._decode_value(self.multi.setdefault(key, default))

    def pop(self, key, *args):
        return self._decode_value(self.multi.pop(key, *args))

    def popitem(self):
        key, value = self.multi.popitem()
        return (self._decode_key(key), self._decode_value(value))

    def __repr__(self):
        items = ', '.join(['(%r, %r)' % v for v in list(self.items())])
        return '%s([%s])' % (self.__class__.__name__, items)

    def __len__(self):
        return len(self.multi)

    ##
    ## All the iteration:
    ##

    def keys(self):
        return [self._decode_key(k) for k in self.multi.keys()]

    def iterkeys(self):
        for k in self.multi.keys():
            yield self._decode_key(k)

    __iter__ = iterkeys

    def items(self):
        return [(self._decode_key(k), self._decode_value(v)) for k, v in self.multi.items()]

    def iteritems(self):
        for k, v in self.multi.items():
            yield (self._decode_key(k), self._decode_value(v))

    def values(self):
        return [self._decode_value(v) for v in self.multi.values()]

    def itervalues(self):
        for v in self.multi.values():
            yield self._decode_value(v)