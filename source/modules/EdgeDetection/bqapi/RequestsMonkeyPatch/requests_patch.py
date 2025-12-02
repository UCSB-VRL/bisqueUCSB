"""
    A patch to format_header_param in urllib3

    If a value has unicode the header will be returned
    as 'name="value"; name*=utf-8''value' else
    'name="value"'
"""


import email.utils
#import mimetypes
import warnings

import requests
import requests.packages.urllib3 as urllib3
from requests.packages.urllib3.packages import six
from .monkeypatch import monkeypatch_method



REQUESTS_V = [int(s) for s in requests.__version__.split('.')]

if REQUESTS_V < [2, 4, 0] or  REQUESTS_V > [2, 19, 0]:
    warnings.warn("""\
We need to patch requests 2.4.0 up to 2.19.0, make sure your version of requests \
needs this patch, greater than 2.4.3 we do not know if this patch applys."""
                  )
    raise ImportError('Requests 2.4.0 to 2.10.0 is required!')
#elif requests_v > [3, 0, 0]:
#    #does not require this patch
#    pass
else:
    @monkeypatch_method(urllib3.fields)
    def format_header_param(name, value):
        """
        Helper function to format and quote a single header parameter.

        Particularly useful for header parameters which might contain
        non-ASCII values, like file names. This follows RFC 2231, as
        suggested by RFC 2388 Section 4.4.

        :param name:
            The name of the parameter, a string expected to be ASCII only.
        :param value:
            The value of the parameter, provided as a unicode string.
        """
        if not any(ch in value for ch in '"\\\r\n'):
            result = '%s="%s"' % (name, value)
            try:
                result.encode('ascii')
            except UnicodeEncodeError:
                pass
            else:
                return result

        value_encode = value
        if not six.PY3: # Python 2:
            value_encode = value.encode('utf-8')

        value = '%s="%s"; %s*=%s' % (
            name, value,
            name, email.utils.encode_rfc2231(value_encode, 'utf-8')
        )
        return value
