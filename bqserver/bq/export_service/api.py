from bq.core.service import service_registry

#from controllers.blob_storage import make_short_uuid, localpath2url, url2localpath

def find_server():
    return service_registry.find_service ('export')

# compression 
# files       
# datasets    
# urls        
# dirs        
# export_meta 
# export_mexs 
# filename    
def export(**kw):
    "export blobs, directories and "
    server = find_server()
    return server.export(**kw)

