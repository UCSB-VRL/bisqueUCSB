"""
ResourceCache used to cache resources to speed up retrieval of images without constantly
asking data service for meta-data view of a resource. It is required to have a fast etag
lookup on a data service in order to validate the cache state.
"""

__author__    = "Dmitry Fedorov and Kris Kvilekval"
__version__   = "1.4"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys
import logging
from datetime import datetime

from bq import data_service
from bq import blob_service
from bq.core import identity

import bq.util.io_misc as misc

import logging
log = logging.getLogger('bq.image_service.cache')

################################################################################
# Resource and Blob caching
################################################################################

class ResourceDescriptor(object):
    '''cached and parsed descriptor of a system resource'''

    valid_period = 15000 # in ms

    def __init__(self, uniq):
        self.uniq = uniq
        self.ts_resource = None
        self.resource = None
        self.meta = None
        self.ts_files = None
        self.files = None

    def validate(self):
        if self.ts_resource is not None:
            diff = datetime.now() - self.ts_resource
            ms = diff.total_seconds()*1000.0
            if ms>self.valid_period:
                #log.debug('%s resource is outdated, removing cache'%self.uniq)
                self.ts_resource = None
                self.resource = None
                self.meta = None

        if self.ts_files is not None:
            diff = datetime.now() - self.ts_files
            ms = diff.total_seconds()*1000.0
            if ms>self.valid_period:
                #log.debug('%s blob is outdated, removing cache'%self.uniq)
                self.ts_files = None
                self.files = None

    def get_resource(self):
        self.validate()
        if self.resource is not None:
            #log.debug('%s resource from cache'%self.uniq)
            return self.resource
        self.resource = data_service.resource_load (uniq=self.uniq, view='image_meta')
        self.ts_resource = datetime.now()
        return self.resource

    def get_metadata(self):
        self.get_resource()

        meta = None
        try:
            meta = self.resource.xpath('tag[@type="image_meta"]')[0]
            meta = dict((i.get('name'), misc.safetypeparse(i.get('value'))) for i in meta.xpath('tag'))
            if len(meta)==0:
                meta=None
        except (AttributeError, IndexError):
            meta = None
        self.meta = meta
        return self.meta

    def get_blobs(self, blocking=True):
        self.validate()
        if self.files is not None:
            # dima: do file existence check here
            # re-request blob service if unavailable
            #log.debug('%s blob from cache'%self.uniq)
            return self.files
        self.get_resource()
        self.files = blob_service.localpath(self.uniq, resource=self.resource, blocking=blocking)
        self.ts_files = datetime.now()
        return self.files


################################################################################
# ResourceCache
################################################################################

class ResourceCache(object):
    '''Provide resource and blob caching'''

    def __init__(self):
        self.d = {}

    def get_descriptor(self, ident):
        user = identity.get_user_id()
        if user not in self.d:
            self.d[user] = {}
        d = self.d[user]
        if ident not in d:
            d[ident] = ResourceDescriptor(ident)
        return d[ident]

    def get_resource(self, ident):
        d = self.get_descriptor(ident)
        return d.get_resource()

    def get_meta(self, ident):
        d = self.get_descriptor(ident)
        return d.get_metadata()

    def get_blobs(self, ident, blocking=True):
        ''' Blocking option allows fail exceptions on resources that are being fetched by other processes
        '''
        d = self.get_descriptor(ident)
        return d.get_blobs(blocking=blocking)

