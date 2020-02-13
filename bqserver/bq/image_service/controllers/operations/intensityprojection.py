"""
Provides an intensity projected image with all available plains
       intensityprojection=max|min
       ex: intensityprojection=max
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

__all__ = [ 'IntensityProjectionOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.intensityprojection")

class IntensityProjectionOperation(BaseOperation):
    '''Provides an intensity projected image with all available plains
       intensityprojection=max|min
       ex: intensityprojection=max'''
    name = 'intensityprojection'

    def __str__(self):
        return 'intensityprojection: returns a maximum intensity projection image, intensityprojection=max|min'

    # def dryrun(self, token, arg):
    #     arg = arg.lower()
    #     if arg not in ['min', 'max']:
    #         raise ImageServiceException(400, 'IntensityProjection: parameter must be either "max" or "min"')
    #     ofile = '%s.iproject_%s'%(token.data, arg)
    #     return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        arg = arg.lower()
        if arg not in ['min', 'max']:
            raise ImageServiceException(400, 'IntensityProjection: parameter must be either "max" or "min"')

        ifile = token.first_input_file()
        ofile = '%s.iproject_%s'%(token.data, arg)
        log.debug('IntensityProjection %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        if arg == 'max':
            command = ['-projectmax']
        else:
            command = ['-projectmin']

        info = {
            'image_num_z': 1,
            'image_num_t': 1,
        }
        return self.server.enqueue(token, 'intensityprojection', ofile, fmt=default_format, command=command, dims=info)
