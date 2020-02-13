# -*- coding: utf-8 -*-
"""kage - patch to handle large file uploads (no copy in cascade)"""

from paste.cascade import Cascade

class DirectCascade(Cascade):
    """Cascade-like middleware which doesn't copy wsgi.input.

    When the app handles large file uploads, this will save a considerable
    amount of time and resources.

    """

    def __call__(self, environ, start_response):
        # pylint: disable=E1101
        failed = []
        def repl_start_response(status, headers, exc_info=None):
            code = int(status.split(None, 1)[0])
            if code in self.catch_codes:
                failed.append(None)
                return _consuming_writer
            return start_response(status, headers, exc_info)

        def _consuming_writer(s): pass

        for app in self.apps[:-1]:
            environ_copy = environ.copy()
            failed = []
            try:
                v = app(environ_copy, repl_start_response)
                if not failed:
                    return v
                else:
                    if hasattr(v, 'close'):
                        # Exhaust the iterator first:
                        list(v)
                        # then close:
                        v.close()
            # Pylin misses that this is a list of exception values
            except tuple (self.catch_exceptions) as e:
                pass
        return self.apps[-1](environ, start_response)
