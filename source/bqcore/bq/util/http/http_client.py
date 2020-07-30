import os
import mimetypes
import logging
import base64


import tg
from tg import config


from httplib2 import Http

import sync_request
import async_request
import async_request_pool
from .poster import encode
from .poster import streaminghttp

from bq.util.paths import data_path

log = logging.getLogger("bq.http_client")

local_client = None

try:
    from bq.core.identity import add_credentials
except ImportError:
    def add_credentials(headers):
        pass

def start(need_async=False):
    cachedir=config.get('bisque.http_client.cache_dir', data_path('client_cache'))
    global local_client
    log.debug ("starting http")
    if not os.path.exists(cachedir):
        os.makedirs(cachedir)
    local_client = Http(cachedir, disable_ssl_certificate_validation=True)
    if need_async:
        async_request_pool.start_pool_handler()

def finish(cleanup_cache=False):
    cachedir=config.get('bisque.http_client.cache_dir', data_path('client_cache'))
    if async_request_pool.isrunning():
        async_request_pool.stop_pool_handler()

    if cleanup_cache:
        import os
        for filename in os.listdir(cachedir):
            os.remove(filename)


#base_config.call_on_startup.append(start)
#base_config.call_on_shutdown.append(finish)




def prepare_credentials (client, headers, userpass=None):
    if userpass is not None:
        client.add_credentials (userpass[0], userpass[1])
        headers['authorization'] =  'Basic ' + base64.encodestring("%s:%s" % userpass ).strip()
        return
    cred = {}
    add_credentials (cred)
    if cred:
        headers.update (cred)
        return
    client.clear_credentials()


def request(url, method="GET", body=None, headers = {},
            async=False, callback=None, client=None, **kw):
    """Create an http  request

    :param url:  The url for the request
    :param method: GET, PUT, POST, HEAD, DELETE
    :param body: body of post or put (maybe string, file or iterable)
    :param async:
    :rtype response_headers, content
    """
    userpass = kw.pop('userpass', None)
    if not client:
        if not local_client:
            start()
        client = local_client
    prepare_credentials (client, headers, userpass=userpass)
    if  async and async_request_pool.isrunning():
        response_tuple = async_request_pool.request(url,
                                                    callback = callback,
                                                    method = method,
                                                    body = body,
                                                    headers = headers,
                                                    client=client)

    else:
        response_tuple =  sync_request.request (url,
                                                method=method,
                                                body=body,
                                                headers = headers,
                                                client = client,)
        if callable(callback):
            callback(url, response_tuple)

    return  response_tuple


def xmlrequest(url, method="GET", body=None, headers= {}, **kw):
    headers['content-type'] = 'text/xml'
    return request(url, method=method, body=body, headers=headers, **kw)




#def local_request(url, method="GET", body=None, headers = {}, **kw):
#    from bq.config.middleware import wsgiapp
#    from webob import Request
#    req = Request (url)
#    resp = req.get_response (wsgiapp)



def post_files (url,  fields = None, **kw):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form
    fields.  files is a sequence of (name, filename, value) elements
    for data to be uploaded as files
    Return the tuple (rsponse headers, server's response page)

    example:
      post_files ('http://..',
      fields = {'file1': open('file.jpg','rb'), 'name':'file' })
      post_files ('http://..', fields = [('file1', 'file.jpg', buffer), ('f1', 'v1' )] )
    """


    body, headers = encode.multipart_encode(fields)
    return request(url, 'POST', headers=headers, body=body, **kw)

def get_file (url, path = None):
    if path == None:
        from tempfile import NamedTemporaryFile
        f = NamedTemporaryFile(delete=False)
    else:
        f = open(path, 'wb')

    header, content = request(url)
    f.write (content)
    f.close()
    return f.name


####################

def send (req):
    'Send a webob request and return a webresponse object'

    from webob import Response
    headers, content = request(req.url,
                            method = req.method,
                            headers = req.headers,
                            body = req.body)

    response = Response()
    response.status = headers.pop ('status')
    response.headers = headers
    response.body    = content
    return response
