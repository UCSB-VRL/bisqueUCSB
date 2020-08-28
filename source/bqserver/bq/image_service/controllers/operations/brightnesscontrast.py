"""
Adjust brightnesscontrast in an image
       brightnesscontrast=brightness,contrast with both values in range [-100,100]
       ex: brightnesscontrast=0,30
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
from bq.image_service.controllers.exceptions import ImageServiceException

__all__ = [ 'BrightnessContrastOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.brightnesscontrast")

class BrightnessContrastOperation(BaseOperation):
    '''Adjust brightnesscontrast in an image
       brightnesscontrast=brightness,contrast with both values in range [-100,100]
       ex: brightnesscontrast=0,30'''
    name = 'brightnesscontrast'

    def __str__(self):
        return 'brightnesscontrast: Adjust brightness and contrast in an image, brightnesscontrast=brightness,contrast both in range [-100,100] ex: brightnesscontrast=0,30'

    # def dryrun(self, token, arg):
    #     arg = arg.lower()
    #     ofile = '%s.brightnesscontrast_%s'%(token.data, arg)
    #     return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        arg = arg.lower()
        ifile = token.first_input_file()
        ofile = '%s.brightnesscontrast_%s'%(token.data, arg)
        log.debug('Brightnesscontrast %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        return self.server.enqueue(token, 'brightnesscontrast', ofile, fmt=default_format, command=['-brightnesscontrast', arg])

