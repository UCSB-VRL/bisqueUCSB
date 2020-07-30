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

__all__ = [ 'SampleFramesOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.sampleframes")

class SampleFramesOperation(BaseOperation):
    '''Returns an Image composed of Nth frames form input
       arg = frames_to_skip
       ex: sampleframes=10'''
    name = 'sampleframes'

    def __str__(self):
        return 'sampleframes: returns an Image composed of Nth frames form input, arg=n'

    def dryrun(self, token, arg):
        arg = arg.lower()
        ofile = '%s.framessampled_%s'%(token.data, arg)
        return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        if not arg:
            raise ImageServiceException(400, 'SampleFrames: no frames to skip provided')

        ifile = token.first_input_file()
        ofile = '%s.framessampled_%s'%(token.data, arg)
        log.debug('SampleFrames %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        info = {
            'image_num_z': 1,
            'image_num_t': int(token.dims.get('image_num_p', 0)) / int(arg),
        }
        return self.server.enqueue(token, 'sampleframes', ofile, fmt=default_format, command=['-sampleframes', arg], dims=info)
