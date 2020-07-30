"""
Listing of operations
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

__all__ = [ 'DimsOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.utils import safeunicode

log = logging.getLogger("bq.image_service.operations.dims")

class DimsOperation(BaseOperation):
    '''Provide image dimension information'''
    name = 'dims'

    def __str__(self):
        return 'dims: returns XML with image dimension information'

    def dryrun(self, token, arg):
        return token.setXml('')

    def action(self, token, arg):
        info = token.dims
        response = etree.Element ('response')
        if info is not None:
            image = etree.SubElement (response, 'image', resource_uniq='%s'%token.resource_id)
            for k, v in info.iteritems():
                #log.debug('%s: %s', k, v)
                tag = etree.SubElement(image, 'tag', name=safeunicode(k), value=safeunicode(v))
        return token.setXml(etree.tostring(response))
