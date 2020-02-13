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

__all__ = [ 'RemapOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.remap")

class RemapOperation(BaseOperation):
    """Provide an image with the requested channel mapping
       arg = channel,channel...
       output image will be constructed from channels 1 to n from input image, 0 means black channel
       remap=display - will use preferred mapping found in file's metadata
       remap=gray - will return gray scale image with visual weighted mapping from RGB or equal weights for other number of channels
       ex: remap=3,2,1"""
    name = 'remap'

    def __str__(self):
        return 'remap: returns an image with the requested channel mapping, arg = [channel,channel...]|gray|display'

    # def dryrun(self, token, arg):
    #     arg = arg.lower()
    #     ofile = '%s.map_%s'%(token.data, arg)
    #     return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        arg = arg.lower()
        ifile = token.first_input_file()
        ofile = '%s.map_%s'%(token.data, arg)
        log.debug('Remap %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        num_channels = 0
        if arg == 'display':
            args = ['-fusemeta']
            num_channels = 3
        elif arg=='gray' or arg=='grey':
            args = ['-fusegrey']
            num_channels = 1
        else:
            args = ['-remap', arg]
            num_channels = len(arg.split(','))

        info = {
            'image_num_c': num_channels,
        }
        return self.server.enqueue(token, 'remap', ofile, fmt=default_format, command=args, dims=info)
