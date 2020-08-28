import socket
import functools
import inspect
import logging
from urllib import urlencode
from urlparse import urlunsplit, urlsplit, urljoin

from tg import expose, flash, require, url, request, response, redirect, config
from lxml import etree
from bq.core.lib.base import BaseController
from bq.exceptions import ConfigurationError, IllegalOperation, RequestError
from bq.util.http import http_client


log = logging.getLogger("bq.proxy")

# THIS CODE TO BE REPLACED WITH WSGIPROXY from paste project
#
#
class ProxyController (BaseController):
    """Controller to recontruct the request and forward to another server
    """
    __controller__ = None
    def __init__(self, service_type, proxy_url):
        if proxy_url[-1] != '/':
            proxy_url += '/'
        self.proxy_split = urlsplit (proxy_url)
        self.proxy_url = proxy_url
        self.uri =self.url = proxy_url
        self.service_type = service_type

    @expose ()
    def _default (self, *args, **kw):
        request_url = urljoin(self.proxy_url, '/'.join(args) + urlencode(kw))
        #url = list (self.proxy_split)
        #url[2]= '/'.join (args)
        #url[3]=urlencode (kw)
        #request_url = urlunsplit (url)
        log.debug ('proxy request for %s' % request_url)
        header, content = http_client.request (request_url,
                                               method= request.method,
                                               body  = request.body,
                                               headers = request.headers)


        response.content_type = header['content-type']
        if not header['status'].startswith ('200'):
            log.debug ("request result %s \n %s" % (header, content))
            return ""
        return content




class service_proxy (object):
    """Create proxy class based on the parameter class.

    @param cls: scanned for @exposed method, and created http proxy for those.
    @param url: the base url where to send proxied requests
    """
    __controller__ = None
    def __init__(self, service_cls, service_url):
        self.uri = service_url
        self.url = service_url
        self.wrapped = service_cls
        self.service_type = service_cls.service_type
        self.proxy_url = service_url
        for name, m in inspect.getmembers (service_cls, inspect.ismethod):
            if  hasattr(m, 'decoration'):
                self.__dict__[name] = functools.partial(self.http_call,
                                               _method=name,
                                               _fargs=inspect.getargspec(m))

    def http_call (self, *args, **kwargs):
        method = kwargs.pop('_method')
        fargs  = kwargs.pop('_fargs')
        body = kwargs.pop('body', None)
        if body is None:
            httpmethod = "GET"
            #def foo(a,b,c=4, *arglist, **kw): pass
            # formal_arguments  = ( ['a','b','c'], 'arglist', 'kw', (4, ) )
            largs =  fargs[0][1:]
            for arg in args:
                kwargs[largs.pop(0)] = arg
        else:
            httpmethod = "POST"

        url = urljoin(self.proxy_url, method + '?' + urlencode(kwargs))

        #log.debug('%s request to %s with %s' % (httpmethod, url, body[:80]+".."+body[len(body)-80:] if body is not None else None))
        #log.debug('%s request to %s with %s ...' % (httpmethod, url, body))
        try:
            headers, content = http_client.xmlrequest (
                url,
                method=httpmethod,
                body = body
                )
        except socket.error, e:
            log.exception("in request %s : %s" % (httpmethod, url))
            raise RequestError("Request Error %s" % url, (None, None))

        if not headers['status'].startswith ('200'):
            log.debug ("request result %s \n %s" % (headers, content))
            raise RequestError("Request Error %s" % url, (headers, content))
        return content




def decode_etrees (a):
    """Return a list with all etree decoded"""
    def decode_etree (arg):
        if isinstance (arg, etree._Element):
            return etree.tostring (arg)
        else:
            return arg

    return [ decode_etree(x) for x in a ]

def encode_etrees (a):
    def encode_etree (arg):
        try:
            return etree.XML (arg)
        except Exception:
            return arg
    if hasattr(a, '__iter__'):
        return [ encode_etree (x) for x in a ]
    else:
        return encode_etree (a)

def etree_wrap (f):
    """Wrap a function so that an etree can be passed in and out.
    This is used to wrap XML web-handler
    """
    @functools.wraps (f)
    def wrapper (*args, **kw):
        result = f (*decode_etrees(args), **kw)
        if type (result)==tuple:
            return tuple (encode_etrees (result))
        else:
            return encode_etrees (result)

    return wrapper


def exposexml(func):
    @expose(content_type="application/xml")
    @functools.wraps (func)
    def wrapper (*args, **kw):
        log.debug ("exposexml args=%s kw=%s" %(args, kw))
        clen = int(request.headers.get('Content-Length')) or 0
        if request.content_type == "text/xml" and request.method in ('POST', 'PUT'):
            xml = request.body_file.read(clen)
            log.debug ("xml = '%s'" % ( xml ))
            kw['body']  = etree.XML (xml)
        result =  func (*args, **kw)
        if isinstance (result, etree._Element):
            response.content_type = "text/xml"
            result = etree.tostring (result)
        return result
    return wrapper







#from bisquik.util import urlnorm
import urlparse
def fullpathurl(url):
    parts = list(urlparse.urlparse (url))
    parts [2] = parts[2] if parts[2].endswith('/') else parts[2]+'/'
    return urlparse.urlunparse(parts)

#active_proxy = config.get('bisquik.proxy.on')
#bisquik_root = fullpathurl(config.get('bisquik.root', ''))
#external_url = fullpathurl(config.get('base_url_filter.base_url', ''))
#
#class ProxyRewriteURL(object):
#    """Use to provide proxy service for bisque"""
#
#    active_proxy = active_proxy
#    bisquik_root = bisquik_root
#    external_url = external_url
#
#     def before_main(self):
#         """Cherrypy filter for XML on the way in """
# #        if not config.get ("bisquik.proxy.on"):
# #            return
#         if cherrypy.request.method.lower() not in ['post', 'put']:
#             return
#         if hasattr(cherrypy.request, 'body'):
#             body = str(cherrypy.request.body.read())
#             try:
#                 log.debug ("ProxyRewrite %s  %s->%s in %s..." %( cherrypy.request.path, self.external_url, self.bisquik_root, body[0:200]))
#                 if len(body):
#                     cherrypy.request.body = StringIO(body.replace (self.external_url, self.bisquik_root))
#             except Exception:
#                 log.debug ("BODY=%s " % body)
#                 raise

#     @classmethod
#     def for_output(cls, body):
#         if cls.active_proxy:
#             return body.replace (cls.bisquik_root, cls.external_url)
#         return body

