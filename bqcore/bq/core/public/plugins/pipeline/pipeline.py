from bq.blob_service.controllers.blob_plugins import ResourcePlugin
from bq.pipeline.controllers.importers.from_dream3d import upload_dream3d_pipeline
from bq.pipeline.controllers.importers.from_cellprofiler import upload_cellprofiler_pipeline
from bq.pipeline.controllers.importers.from_imagej import upload_imagej_pipeline
from bq.pipeline.controllers.importers.from_bqworkflow import upload_bisque_pipeline

class Dream3DPipelinePlugin (ResourcePlugin):
    '''Dream.3D Pipeline resource''' 
    name = "Dream3DPipelinePlugin"  
    version = '1.0'
    ext = 'json'
    resource_type = 'dream3d_pipeline'
    mime_type = 'application/json'
    
    def __init__(self):
        pass
    
    def process_on_import(self, f, intags):
        return upload_dream3d_pipeline(f, intags)
    
class BisquePipelinePlugin (ResourcePlugin):
    '''Bisque Pipeline resource''' 
    name = "BisquePipelinePlugin"  
    version = '1.0'
    ext = 'bq'
    resource_type = 'bisque_pipeline'
    mime_type = 'application/json'
    
    def __init__(self):
        pass
    
    def process_on_import(self, f, intags):
        return upload_bisque_pipeline(f, intags)

class CellprofilerPipelinePlugin (ResourcePlugin):
    '''Cellprofiler Pipeline resource''' 
    name = "CellprofilerPipelinePlugin"  
    version = '1.0'
    ext = 'cp'
    resource_type = 'cellprofiler_pipeline'
    mime_type = 'text/plain'
    
    def __init__(self):
        pass
    
    def process_on_import(self, f, intags):
        return upload_cellprofiler_pipeline(f, intags)

class CellprofilerPipeline2Plugin (ResourcePlugin):
    '''Cellprofiler Pipeline resource''' 
    name = "CellprofilerPipelinePlugin"  
    version = '1.0'
    ext = 'cppipe'
    resource_type = 'cellprofiler_pipeline'
    mime_type = 'text/plain'
    
    def __init__(self):
        pass

    def process_on_import(self, f, intags):
        return upload_cellprofiler_pipeline(f, intags)
    
class ImageJPipelinePlugin (ResourcePlugin):
    '''ImageJ Pipeline resource''' 
    name = "ImageJPipelinePlugin"  
    version = '1.0'
    ext = 'ijm'
    resource_type = 'imagej_pipeline'
    mime_type = 'text/plain'
    
    def __init__(self):
        pass
    
    def process_on_import(self, f, intags):
        return upload_imagej_pipeline(f, intags)