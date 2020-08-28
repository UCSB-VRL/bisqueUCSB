"""
Provides rotated versions for requested images:
       arg = angle
       At this moment only supported values are 90, -90, 270, 180 and guess
       ex: rotate=90
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

__all__ = [ 'RotateOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.rotate")

def compute_rotated_size(w, h, arg):
    if arg in ['90', '-90', '270']:
        return (h, w)
    return (w, h)

class RotateOperation(BaseOperation):
    '''Provides rotated versions for requested images:
       arg = angle
       At this moment only supported values are 90, -90, 270, 180 and guess
       ex: rotate=90'''
    name = 'rotate'

    def __str__(self):
        return 'rotate: returns an image rotated as requested, arg = 0|90|-90|180|270|flip_ud|mirror_lr|guess'

    def dryrun(self, token, arg):
        ang = arg.lower()
        if ang=='270':
            ang='-90'
        ofile = '%s.rotated_%s'%(token.data, ang)
        return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        ang = arg.lower()
        angles = ['0', '90', '-90', '270', '180', 'guess', 'flip_ud', 'mirror_lr']
        if ang=='270':
            ang='-90'
        if ang not in angles:
            raise ImageServiceException(400, 'rotate: angle value not yet supported' )

        ifile = token.first_input_file()
        ofile = '%s.rotated_%s'%(token.data, ang)
        log.debug('Rotate %s: %s to %s', token.resource_id, ifile, ofile)
        if ang=='0':
            ofile = ifile

        dims = token.dims or {}
        w, h = compute_rotated_size(int(dims.get('image_num_x', 0)), int(dims.get('image_num_y', 0)), ang)
        info = {
            'image_num_x': w,
            'image_num_y': h,
        }
        command=['-rotate', ang]
        if ang == 'flip_ud':
            command=['-flip']
        if ang == 'mirror_lr':
            command=['-mirror']
        return self.server.enqueue(token, 'rotate', ofile, fmt=default_format, command=command, dims=info)
