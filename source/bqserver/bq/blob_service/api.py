from bq.core.service import service_registry

#from controllers.blob_drivers import make_short_uuid, localpath2url, url2localpath
from bq.util.urlpaths import localpath2url, url2localpath

def find_server():
    return service_registry.find_service ('blob_service')

def store_blob(resource, fileobj=None, rooturl = None):
    "create and store a resource blob"
    server = find_server()
    return server.store_blob(resource=resource, fileobj=fileobj, rooturl=rooturl)

#def store_multi_blob(resource, unpack_dir):
#    "create and store a resource multi-blob"
#    server = find_server()
#    return server.store_multi_blob(resource=resource, unpack_dir=unpack_dir)

def create_resource(resource):
    "create a resource blob"
    server = find_server()
    return server.create_resource(resource=resource)

def localpath(uniq_ident, resource=None, blocking=True):
    "return localpath of resource by ident (uniq)"
    server = find_server()
    return server.localpath(uniq_ident, resource=resource, blocking=blocking)


def delete_blob(uniq_ident):
    "return localpath of resource by ident (uniq)"
    server = find_server()
    return server.delete_blob(uniq_ident)

def original_name(ident):
    "create  localpath if possible of resource by ident (uniq)"
    server = find_server()
    return server.originalFileName(ident)

def url2local(path):
    "decode url into a local path"
    return url2localpath(path)

def local2url(path):
    "decode local path as a url"
    return localpath2url(path)

def get_import_plugins():
    "return a listr of plugins with import function"
    server = find_server()
    return server.get_import_plugins()
