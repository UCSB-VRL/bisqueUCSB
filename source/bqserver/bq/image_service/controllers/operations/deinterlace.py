"""
Provides a deinterlaced image
       ex: deinterlace
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

__all__ = [ 'DeinterlaceOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.deinterlace")

class DeinterlaceOperation(BaseOperation):
    '''Provides a deinterlaced image
       ex: deinterlace'''
    name = 'deinterlace'

    def __str__(self):
        return 'deinterlace: returns a deinterlaced image'

    # def dryrun(self, token, arg):
    #     arg = arg.lower() or 'avg'
    #     if arg not in ['odd', 'even', 'avg']:
    #         raise ImageServiceException(400, 'Deinterlace: parameter must be either "odd", "even" or "avg"')
    #     ofile = '%s.deinterlace_%s'%(token.data, arg)
    #     return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        arg = arg.lower() or 'avg'
        if arg not in ['odd', 'even', 'avg']:
            raise ImageServiceException(400, 'Deinterlace: parameter must be either "odd", "even" or "avg"')
        ifile = token.first_input_file()
        ofile = '%s.deinterlace_%s'%(token.data, arg)
        log.debug('Deinterlace %s: %s to %s', token.resource_id, ifile, ofile)

        return self.server.enqueue(token, 'deinterlace', ofile, fmt=default_format, command=['-deinterlace', arg])
