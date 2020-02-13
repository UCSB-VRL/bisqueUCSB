"""
Threshold an image
       threshold=value[,upper|,lower|,both]
       ex: threshold=128,both
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

__all__ = [ 'ThresholdOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.threshold")

class ThresholdOperation(BaseOperation):
    '''Threshold an image
       threshold=value[,upper|,lower|,both]
       ex: threshold=128,both'''
    name = 'threshold'

    def __str__(self):
        return 'threshold: returns a thresholded image, threshold=value[,upper|,lower|,both], ex: threshold=128,both'

    def dryrun(self, token, arg):
        arg = arg.lower()
        args = arg.split(',')
        if len(args)<1:
            return token
        method = 'both'
        if len(args)>1:
            method = args[1]
        arg = '%s,%s'%(args[0], method)
        ofile = '%s.threshold_%s'%(token.data, arg)
        return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        arg = arg.lower()
        args = arg.split(',')
        if len(args)<1:
            raise ImageServiceException(400, 'Threshold: requires at least one parameter')
        method = 'both'
        if len(args)>1:
            method = args[1]
        arg = '%s,%s'%(args[0], method)
        ifile = token.first_input_file()
        ofile = '%s.threshold_%s'%(token.data, arg)
        log.debug('Threshold %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        return self.server.enqueue(token, 'threshold', ofile, fmt=default_format, command=['-threshold', arg])
