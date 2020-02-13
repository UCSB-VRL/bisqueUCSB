"""
Return pixel counts of a thresholded image
       pixelcounter=value, where value is a threshold
       ex: pixelcounter=128
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

__all__ = [ 'PixelCounterOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.util.io_misc import safeint

log = logging.getLogger("bq.image_service.operations.pixelcounter")

class PixelCounterOperation(BaseOperation):
    '''Return pixel counts of a thresholded image
       pixelcounter=value, where value is a threshold
       ex: pixelcounter=128'''
    name = 'pixelcounter'

    def __str__(self):
        return 'pixelcounter: returns a count of pixels in a thresholded image, ex: pixelcounter=128'

    def dryrun(self, token, arg):
        arg = safeint(arg.lower(), 256)-1
        ofile = '%s.pixelcounter_%s.xml'%(token.data, arg)
        return token.setXmlFile(fname=ofile)

    def action(self, token, arg):
        if not token.isFile():
            raise ImageServiceException(400, 'Pixelcounter: input is not an image...' )
        arg = safeint(arg.lower(), 256)-1
        ifile = token.first_input_file()
        ofile = '%s.pixelcounter_%s.xml'%(token.data, arg)
        log.debug('Pixelcounter %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        command = token.drainQueue()
        if not os.path.exists(ofile):
            command.extend(['-pixelcounts', str(arg)])
            self.server.imageconvert(token, ifile, ofile, extra=command)

        return token.setXmlFile(fname=ofile)
