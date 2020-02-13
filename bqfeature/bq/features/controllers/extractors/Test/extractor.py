# -*- mode: python -*-
""" Test library
"""
import tables
import logging
from bq.features.controllers import Feature
from bq.features.controllers.exceptions import FeatureExtractionError

log = logging.getLogger("bq.features.TestFeature")

class SimpleTestFeature(Feature.BaseFeature):
    """
        Test Feature
        This extractor is completely useless to calculate any 
        useful feature. 
        Purpose: to test the reliability of the feature service
    """
    #parameters
    name = 'SimpleTestFeature'
    description = """Dummy Test Feature Extractor (test feature) Calculates random numbers for features"""
    length = 64
    feature_format = 'int32'

    def calculate(self, resource):
        """ Calculates features for DTFE"""
        
        #initalizing
        descriptor = [x for x in range(64)]
                
        #initalizing rows for the table
        return descriptor
        
        
class UncachedTestFeature(SimpleTestFeature):
    """
        Uncached Test Feature 
        This extractor is completely useless to calculate any 
        useful feature. 
        Purpose: to test the reliability of the feature service
    """
    #parameters
    name = 'UncachedTestFeature'
    description = """Feature Test Uncached returns a very predicable vector"""
    cache = False
    


class MultiVectorTestFeature(SimpleTestFeature):
    """
        Test Feature parameters
        This extractor is completely useless to calculate any 
        useful feature. 
        Purpose: to test the reliability of the feature service        
    """
    #parameters
    name = 'MultiVectorTestFeature'
    description = """Feature Test Uncached returns a very predicable vector"""
    length = 64
    
    def calculate(self, resource):
        
        #initalizing
        descriptor = [[i*x for x in xrange(64)] for i in xrange(20)]
                
        #initalizing rows for the table
        return [descriptor]

class UncachedMultiVectorTestFeature(MultiVectorTestFeature):
    """
        Test Feature parameters
        This extractor is completely useless to calculate any 
        useful feature. 
        Purpose: to test the reliability of the feature service        
    """
    #parameters
    name = 'UncachedMultiVectorTestFeature'
    description = """Feature Test Uncached returns a very predicable vector"""
    cache = False
    


class ParametersTestFeature(SimpleTestFeature):
    """
        Test Feature parameters
        This extractor is completely useless to calculate any 
        useful feature. 
        Purpose: to test the reliability of the feature service        
    """
    #parameters
    name = 'ParametersTestFeature'
    description = """Feature Test Uncached returns a very predicable vector"""
    length = 64
    parameter = ['x', 'y', 'scale', 'type']   

    def cached_columns(self):
        """
            Columns for the cached tables
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length ))
    
        return {
            'idnumber'  : tables.StringCol(32,pos=1),
            'feature'   : tables.Col.from_atom(featureAtom, pos=2),
            'x'         : tables.Float32Col(pos=3),
            'y'         : tables.Float32Col(pos=4),
            'scale'     : tables.Float32Col(pos=5),         
            'type'      : tables.StringCol(10,pos=6)
        }
    
    def workdir_columns(self):
        """
            Columns for the output table for the feature column
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length ))

        return {
            'image'     : tables.StringCol(2000,pos=1),
            'mask'      : tables.StringCol(2000,pos=2),
            'gobject'   : tables.StringCol(2000,pos=3),
            'feature'   : tables.Col.from_atom(featureAtom, pos=4),
            'x'         : tables.Float32Col(pos=5),
            'y'         : tables.Float32Col(pos=6),
            'scale'     : tables.Float32Col(pos=7),
            'type'      : tables.StringCol(10,pos=8) 
        }
    
    def calculate(self, resource):
        """ Calculates features for DTFE"""
        
        #initalizing
        descriptor = [x for x in range(64)]
              
        #initalizing rows for the table
        return ([descriptor], [7], [11], [39], ['test'])



class UncachedParametersTestFeature(ParametersTestFeature):
    """
        Test Feature parameters
        This extractor is completely useless to calculate any 
        useful feature. 
        Purpose: to test the reliability of the feature service        
    """
    #parameters
    name = 'UncachedParametersTestFeature'
    description = """Feature Test Uncached returns a very predicable vector"""
    cache = False

class ExceptionTestFeature(SimpleTestFeature):
    """
        Exception Test Feature
        
        This feature will produce an feature calculation
        exceptions when asked to calculate.
    """
    #parameters
    name = 'ExceptionTestFeature'
    description = """Exception Test Feature will always raise a feature extraction exception error"""

    def calculate(self, resource):
        """ Calculates features for DTFE"""
        
        raise  FeatureExtractionError(resource, 500,'This feature will never calculate anything')
    