"""
Features Exceptions
"""


class FeatureExtractionError(Exception):

    def __init__(self, resource, error_code=500, error_message='Internal Server Error'):
        self.code = error_code
        self.message = error_message
        self.resource = resource


class FeatureServiceError(Exception):
    
    def __init__(self, error_code=500, error_message='Internal Server Error'):
        self.error_code = error_code
        self.error_message = error_message
        
    def __str__(self):
        return 'FeatureServiceError %s:%s' % (self.error_code,self.error_message)
        
        
class FeatureImportError(Exception):
    
    def __init__(self, extractor_package_name, message=''):
        self.extractor_package_name = extractor_package_name
        self.message = message

class ConnectionError(Exception):
    
    def __init__(self, error_code=404, error_message='Resource Not Found'):
        self.code = error_code
        self.message = error_message
        
class InvalidResourceError(Exception):

    def __init__(self, resource_url='', error_code=415, error_message='Resource Not Valid'):
        self.resource_url = resource_url
        self.code = error_code
        self.message = error_message