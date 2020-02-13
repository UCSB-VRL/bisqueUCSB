"""
returns XML with local path to the processed image
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

__all__ = [ 'LocalPathOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken

log = logging.getLogger("bq.image_service.operations.localpath")

class LocalPathOperation(BaseOperation):
    '''Provides local path for response image'''
    name = 'localpath'

    def __str__(self):
        return 'localpath: returns XML with local path to the processed image'

    def dryrun(self, token, arg):
        return token.setXml('')

    def action(self, token, arg):
        if token.hasQueue():
            ifile = token.data
        else:
            ifile = token.first_input_file()
        ifile = os.path.abspath(ifile)
        log.debug('Localpath %s: %s', token.resource_id, ifile)

        res = etree.Element ('resource', type='file', value=ifile)
        if os.path.exists(ifile):
            etree.SubElement (res, 'tag', name='status', value='requires access for creation')

        #else:
        #    res = etree.Element ('resource')

        return token.setXml( etree.tostring(res) )
