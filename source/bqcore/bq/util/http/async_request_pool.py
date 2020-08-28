###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009                                          ##
##      by the Regents of the University of California                       ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========


    def mycallback(request, result):
        headers, content = result
        print request, " ==> " , headers, len(content)
    sites = [ 'http://cnn.com', 'http://yahoo.com', 'http://news.google.com']
    for url in sites:
        request(url, callback = mycallback)



DESCRIPTION
===========

"""

import threading

from .thread_pool import  ThreadPool, WorkRequest, NoResultsPending
import httplib2


main_pool = None
class HTTPAsyncRequest(WorkRequest):
    """Helper class for initialization of thread_pool WorkRequest with
    an http request
    """
    def __init__(self, uri, method, body, headers, callback, client):
        super(HTTPAsyncRequest, self).__init__(
            callable_ =  client.request,
            args = [ uri ],
            kwds = { 'method': method, 'body':body, 'headers':headers },
            callback = callback)

class HTTPThreadPool (threading.Thread):
    """Maintain a thread pool"""
    def __init__(self, num_workers = 3, **kw):
        threading.Thread.__init__(self, **kw)
        #self.setDaemon(True)
        #self.daemon = True
        self.stopping =False
        self.pool =  ThreadPool( num_workers, **kw)
        self.start()

    def putRequest(self, r):
        return self.pool.putRequest(r)

    def run(self):
        while True:
            if  self.stopping:
                break
            try:
                self.pool.poll( timeout=1)
            except NoResultsPending:
                continue
        self.pool.dismissWorkers(do_join=True)

    def stop(self):
        self.stopping = True


def request(uri, method="GET", body=None, headers={}, callback=None, client= None, **kw):
    """Make an aynchrounous request adding user credential if available
    Return: ( Request, None)
    """

    return (main_pool.putRequest (
        HTTPAsyncRequest(uri,
                         method=method,
                         body = body,
                         headers=headers,
                         callback = callback,
                         client=client)),
            None)




def start_pool_handler():
    global main_pool
    if main_pool is None:
        main_pool = HTTPThreadPool()


def stop_pool_handler():
    global main_pool
    if main_pool is not None:
        main_pool.stop()


def isrunning():
    return main_pool != None

if __name__ == "__main__":

    client = httplib2.Http(disable_ssl_certificate_validation=True)

    start_pool_handler()

    def mycallback(request, result):
        headers, content = result
        print request, " ==> " , headers, len(content)
    sites = [ 'http://cnn.com', 'http://yahoo.com', 'http://news.google.com']


    for url in sites:
        request(url, callback = mycallback, client = client)
        print url

    stop_pool_handler()

