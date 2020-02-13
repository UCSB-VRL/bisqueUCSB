"""
Provide an image negative
       ex: negative
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

__all__ = [ 'NegativeOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.negative")

class NegativeOperation(BaseOperation):
    '''Provide an image negative
       ex: negative'''
    name = 'negative'

    def __str__(self):
        return 'negative: returns an image negative'

    def dryrun(self, token, arg):
        ifile = token.data
        ofile = '%s.negative'%(token.data)
        return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        ifile = token.first_input_file()
        ofile = '%s.negative'%(token.data)
        log.debug('Negative %s: %s to %s', token.resource_id, ifile, ofile)

        return self.server.enqueue(token, 'negative', ofile, fmt=default_format, command=['-negative'])
