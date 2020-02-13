"""
cleans local cache for a given image
"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

import os
import sys
import math
import logging
import pkg_resources
from lxml import etree
import shutil

__all__ = [ 'CacheCleanOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken

log = logging.getLogger("bq.image_service.operations.cleancache")

class CacheCleanOperation(BaseOperation):
    '''Cleans local cache for a given image'''
    name = 'cleancache'

    def __str__(self):
        return 'cleancache: cleans local cache for a given image'

    def dryrun(self, token, arg):
        return token.setXml('')

    def action(self, token, arg):
        ofname = token.data
        log.debug('Cleaning local cache %s: %s', token.resource_id, ofname)
        path = os.path.dirname(ofname)
        fname = os.path.basename(ofname)
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                if name.startswith(fname):
                    os.remove(os.path.join(root, name))
            for name in dirs:
                if name.startswith(fname):
                    #os.removedirs(os.path.join(root, name))
                    shutil.rmtree(os.path.join(root, name))
        return token.setHtml( 'Clean' )

