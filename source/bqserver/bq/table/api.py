
#import os
import posixpath

from bq.core.service import service_registry

def find_server():
    return service_registry.find_service ('table')

#####################################################################################
# Python internal API
#####################################################################################

def get_table(uuid, path):
    "return table of resource by uniq and path"
    server = find_server()
    url = posixpath.join('/table/%s'%uuid, path)
    if 'format:' not in url:
        url = posixpath.join(url, 'format:table')
    return server.get_table(url)
