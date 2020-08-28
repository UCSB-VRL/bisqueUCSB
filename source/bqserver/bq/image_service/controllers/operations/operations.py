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

__all__ = [ 'OperationsOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken

log = logging.getLogger("bq.image_service.operations.operations")

class OperationsOperation(BaseOperation):
    '''Provide operations information'''
    name = 'operations'

    def __str__(self):
        return 'operations: returns XML with operations information'

    def dryrun(self, token, arg):
        return token.setXml('')

    def action(self, token, arg):
        response = etree.Element ('response')
        servs    = etree.SubElement (response, 'operations', uri='/image_service/operations')
        for name,func in self.server.operations.plugins.iteritems():
            tag = etree.SubElement(servs, 'tag', name=str(name), value=str(func))
        return token.setXml(etree.tostring(response))
