import urlparse

import furl

def urljoin(base, partial, **kw):
    """ Join all components for a url overriding any components in base from partial

    @param base: The base url
    @param partial: The overriding url
    @param kw :  extra url parameters
    @return a new url string
    """
    updated = furl.furl (base)
    partial = furl.furl (partial)

    updated.scheme = partial.scheme or updated.scheme
    updated.username = partial.username or updated.username
    updated.password = partial.username or updated.username
    updated.host     = partial.host or updated.host
    updated.port     = partial.port or updated.port
    updated.path = urlparse.urljoin (str(updated.path), str(partial.path))
    updated.query.params  = partial.query.params or updated.query.params
    updated.query.params.update (kw)
    return updated.url


def update_url(url, params = None):
    'construct a url with new params'
    url = furl.furl (url)
    if params :
        url.query.params.update (params)
    return url.url

def strip_url_params(url):
    'strip url params returning clean url and param multidict '

    url = furl.furl(url)
    params = url.query.params.copy()
    url.query.params = {}
    return url.url, params
