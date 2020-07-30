
from bq.core.service import service_registry

def find_server(server= None):
    return service_registry.find_service ('ingest_service')
    

def uri():
    server = find_server('')
    return server.uri


def new_blobs(server=None, **kw):
    ''' Find the preferred data server and store the data there
    Excess named arguments are used as attributes for the image object
    '''
    server = find_server (server)
    
    return server.new_blobs(**kw)
