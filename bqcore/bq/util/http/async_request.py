from threading import Thread
from urllib import urlopen
from time import time
import http_client



class URLThread(Thread):
    def __init__(self, **kw):
        super(URLThread, self).__init__()
        self.callback = kw.pop('callback', None)
        self.request_params  = kw
        self.setDaemon(True)

    def run(self):
        response_headers, content  = http_client.request (**self.request_params)

        if response_headers.status != 200:
            return
        if self.callback is not None:
            self.callback (content, response_headers)



def request(uri, method="GET", body=None, headers={}, callback=None, client= None, **kw):
    """ Make an aynchrounous request adding user credential if available"""
    http_client.prepare_credentials(http_client.local_client, headers=headers)
    return URLThread (uri=uri,
                      method=method,
                      body=body,
                      headers=headers,
                      callback=callback,**kw)


def xmlrequest(url, op = 'GET', body='', headers={}, **kw):
    '''usage: headers, response = xmlrequest("http://aaa.com")
              headers, response = xmlrequest("http://aaa.com", "POST", "<xml>...")
    '''
    http_client.prepare_credentials(http_client.local_client, headers=headers)
    headers['content-type'] = 'text/xml'
    return URLThread (uri=url,
                      method=op,
                      body=body,
                      headers=headers,
                      **kw)
