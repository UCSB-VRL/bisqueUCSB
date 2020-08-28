"""
Rearranges dimensions of an image
       arg = xzy|yzx
       xz: XYZ -> XZY
       yz: XYZ -> YZX
       ex: rearrange3d=xz
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

__all__ = [ 'Rearrange3DOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.rearrange3d")

class Rearrange3DOperation(BaseOperation):
    '''Rearranges dimensions of an image
       arg = xzy|yzx
       xz: XYZ -> XZY
       yz: XYZ -> YZX
       ex: rearrange3d=xz'''
    name = 'rearrange3d'

    def __str__(self):
        return 'rearrange3d: rearrange dimensions of a 3D image, arg = [xzy,yzx]'

    def dryrun(self, token, arg):
        arg = arg.lower()
        ifile = token.data
        ofile = '%s.rearrange3d_%s'%(token.data, arg)
        return token.setImage(ofile, fmt=default_format)

    def action(self, token, arg):
        if not token.isFile():
            raise ImageServiceException(400, 'Rearrange3D: input is not an image...' )
        log.debug('Rearrange3D %s: %s', token.resource_id, arg )
        arg = arg.lower()

        if arg not in ['xzy', 'yzx']:
            raise ImageServiceException(400, 'Rearrange3D: method is unsupported: [%s]'%arg )

        # if the image must be 3D, either z stack or t series
        dims = token.dims or {}
        x = dims['image_num_x']
        y = dims['image_num_y']
        z = dims['image_num_z']
        t = dims['image_num_t']
        if (z>1 and t>1) or (z==1 and t==1):
            raise ImageServiceException(400, 'Rearrange3D: only supports 3D images' )

        nz = y if arg == 'xzy' else x
        info = {
            'image_num_x': x if arg == 'xzy' else y,
            'image_num_y': z,
            'image_num_z': nz if z>1 else 1,
            'image_num_t': nz if t>1 else 1,
        }
        ifile = token.first_input_file()
        ofile = '%s.rearrange3d_%s'%(token.data, arg)
        command = token.drainQueue()
        if not os.path.exists(ofile):
            command.extend(['-rearrange3d', '%s'%arg])
            # dima: fix the case of a fliped output for
            if arg == 'yzx':
                command.extend(['-flip'])
            self.server.imageconvert(token, ifile, ofile, fmt=default_format, extra=command)

        return token.setImage(ofile, fmt=default_format, dims=info, input=ofile)
