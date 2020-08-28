"""
Returns an image composed of user defined frames form input
       arg = frames
       ex: frames=1,2,5 or ex: frames=1,-,5 or ex: frames=-,5 or ex: frames=4,-
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

__all__ = [ 'FramesOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.frames")

class FramesOperation(BaseOperation):
    '''Returns an image composed of user defined frames form input
       arg = frames
       ex: frames=1,2,5 or ex: frames=1,-,5 or ex: frames=-,5 or ex: frames=4,-'''
    name = 'frames'

    def __str__(self):
        return 'frames: Returns an image composed of user defined frames form input, arg = frames'

    # def dryrun(self, token, arg):
    #     arg = arg.lower()
    #     ofile = '%s.frames_%s'%(token.data, arg)
    #     return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        if not arg:
            raise ImageServiceException(400, 'Frames: no frames provided')

        ifile = token.first_input_file()
        ofile = '%s.frames_%s'%(token.data, arg)
        log.debug('Frames %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        info = {
            'image_num_z': 1,
            'image_num_t': 1,
            #if 'image_num_p' in info: token.dims['image_num_p'] = info['image_num_p']
        }
        return self.server.enqueue(token, 'frames', ofile, fmt=default_format, command=['-page', arg], dims=info)
