# -*- mode: python -*-
""" Base Feature library
"""

import os
import tables
import logging
import uuid
from tg.configuration import config
from .var import FEATURES_TABLES_FILE_DIR

log = logging.getLogger("bq.features.Feature")

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

###############################################################
# Feature Object
###############################################################
class BaseFeature(object):
    """
        Initalizes Feature table and calculates descriptor to be
        placed into the HDF5 table
    """
    #initalize feature attributes

    #feature name (the feature service will refer to the feature by this name)
    name = 'Feature'

    #A short descriptio of the feature
    description = """Feature vector is the generic feature object. If this description is
    appearing in the description for this feature no description has been provided for this
    feature"""

    #parent class tag
    child_feature = []

    #Limitations that may be imposed on the feature
    limitations = """This feature has no limitation"""

    #there are currently only 3 resources in the feature server
    #image, mask, gobject
    #required resource type(s)
    resource = ['image']
    
    #additional resources type(s)
    additional_resource = None

    #parameters that will be shown on the output
    parameter = []

    #length of the feature
    length = 0

    #format the features are stored in
    feature_format = "float32"

    #option for feature to be stored in hdf5 cache
    #cache = True
    cache = False

    #option of turing on the index
    #index = True

    #Number of characters to use from the hash to name
    #the tables
    hash = 2

    #list of feature catagories. ex. color,texture...
    type = []
    
    #will turn off the feature in the feature service if set to true
    disabled = False
    
    #Confidence stands for the amount of a features correctness based on the unittest comparison.
    #good - feature compares exactly with the linux and windows binaries
    #fair - feature is within %5 mismatch of either linux and windows binaries
    #poor - feature is greater than %5 mismatch of either linux and windows binaries
    #untested - feature has not been tested in the unittest comparison
    confidence = 'untested'

    def __init__ (self):
        self.path = os.path.join(FEATURES_TABLES_FILE_DIR, self.name)
        
        #set cache in site.cfg
        self.cache = str2bool(config.get('bisque.feature.%s.cache'%self.name, None) #checks for specific feature
                     or config.get('bisque.feature.default.cache', None) #checks the default
                     or 'False') #sets a default if nothing is specified


    def localfile(self, hash):
        """
            returns the path to the table given the hash
        """
        return os.path.join(self.path, hash[:self.hash]+'.h5')

    @staticmethod
    def hash_resource(feature_resource):
        """
            returns a hash given all the uris
        """
        query = []
        if feature_resource.image: query.append('image=%s' % feature_resource.image)
        if feature_resource.mask: query.append('mask=%s' % feature_resource.mask)
        if feature_resource.gobject: query.append('gobject=%s' % feature_resource.gobject)
        query = '&'.join(query)
        resource_hash = uuid.uuid5(uuid.NAMESPACE_URL, query.encode('ascii'))
        resource_hash = resource_hash.hex
        return resource_hash

    def cached_columns(self):
        """
            Columns for the cached tables
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length))
        return {
            'idnumber': tables.StringCol(32, pos=1),
            'feature' : tables.Col.from_atom(featureAtom, pos=2)
        }
        
    def workdir_columns(self):
        """
            Columns for the output table for the feature column
        """
        featureAtom = tables.Atom.from_type(self.feature_format, shape=(self.length))
        return {
            'image'   : tables.StringCol(2000, pos=1),
            'mask'    : tables.StringCol(2000, pos=2),
            'gobject' : tables.StringCol(2000, pos=3),
            'feature' : tables.Col.from_atom(featureAtom, pos=4)
        }

    def calculate(self, resource):
        """
            place holder for feature calculations
        """
        return [0]



