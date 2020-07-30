"""
Adjust levels in an image
       levels=minvalue,maxvalue,gamma
       ex: levels=15,200,1.2
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

__all__ = [ 'LevelsOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.levels")

class LevelsOperation(BaseOperation):
    '''Adjust levels in an image
       levels=minvalue,maxvalue,gamma
       ex: levels=15,200,1.2'''
    name = 'levels'

    def __str__(self):
        return 'levels: adjust levels in an image, levels=minvalue,maxvalue,gamma ex: levels=15,200,1.2'

    # def dryrun(self, token, arg):
    #     arg = arg.lower()
    #     ofile = '%s.levels_%s'%(token.data, arg)
    #     return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        arg = arg.lower()
        ifile = token.first_input_file()
        ofile = '%s.levels_%s'%(token.data, arg)
        log.debug('Levels %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        return self.server.enqueue(token, 'levels', ofile, fmt=default_format, command=['-levels', arg])
