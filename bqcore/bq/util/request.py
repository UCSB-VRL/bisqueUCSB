
import logging
import webob
from paste.proxy import make_proxy
from tg import  config



log = logging.getLogger('bq.core')


proxy = make_proxy(config, 'http://loup.ece.ucsb.edu:9090')

class Request(object):

    def __init__(self,url):
        self.url = url
    def get(self):
        'route the rquest locally if possible'

        req = webob.Request.blank(self.url)
        response = req.get_response(proxy)

        if response.status_int == 200:
            return response.body

        log.info ('ReMOTE %s' % self.url)
        return ''





