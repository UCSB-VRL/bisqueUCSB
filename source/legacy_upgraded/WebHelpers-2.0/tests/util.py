from unittest import TestCase

import routes

def raises(exc, func, *args, **kw):
    try:
        func(*args, **kw)
    except exc:
        pass
    else:
        tup = func.__name__, e.__name__
        raise AssertionError("%s() did not raise %s" % tup)

def test_environ():
    return {
        'HTTP_HOST': 'bob.local:5000',
        'PATH_INFO': '/test',
        'QUERY_STRING': 'test=webhelpers&framework=pylons',
        'REQUEST_METHOD': 'GET',
        'SERVER_NAME': '0.0.0.0',
        'SCRIPT_NAME': '',
        'pylons.environ_config': dict(session='test.session'),
        'test.session': {},
        'wsgi.multiprocess': False,
        'wsgi.multithread': True,
        'wsgi.run_once': False,
        'wsgi.url_scheme': 'http'
        }


class WebHelpersTestCase(TestCase):
    """Establishes a faux-environment for tests"""
    def test_environ(self):
        return {
            'HTTP_HOST': 'bob.local:5000',
            'PATH_INFO': '/test',
            'QUERY_STRING': 'test=webhelpers&framework=pylons',
            'REQUEST_METHOD': 'GET',
            'SERVER_NAME': '0.0.0.0',
            'SCRIPT_NAME': '',
            'pylons.environ_config': dict(session='test.session'),
            'test.session': {},
            'wsgi.multiprocess': False,
            'wsgi.multithread': True,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'http'
            }

