"""
Provide an RGB image with the requested channel fusion
       arg = W1R,W1G,W1B;W2R,W2G,W2B;W3R,W3G,W3B;W4R,W4G,W4B
       output image will be constructed from channels 1 to n from input image mapped to RGB components with desired weights

       fuse=display: will use preferred mapping found in file's metadata
       fuse=gray: will return gray scale image with visual weighted mapping from RGB or equal weights for other number of channels
       fuse=grey: will return gray scale image with visual weighted mapping from RGB or equal weights for other number of channels

       ex: fuse=255,0,0;0,255,0;0,0,255;255,255,255:A
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

import bq.util.io_misc as misc

__all__ = [ 'FuseOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.fuse")

class FuseOperation(BaseOperation):
    """Provide an RGB image with the requested channel fusion
       arg = W1R,W1G,W1B;W2R,W2G,W2B;W3R,W3G,W3B;W4R,W4G,W4B
       output image will be constructed from channels 1 to n from input image mapped to RGB components with desired weights

       fuse=display: will use preferred mapping found in file's metadata
       fuse=gray: will return gray scale image with visual weighted mapping from RGB or equal weights for other number of channels
       fuse=grey: will return gray scale image with visual weighted mapping from RGB or equal weights for other number of channels

       ex: fuse=255,0,0;0,255,0;0,0,255;255,255,255:A"""
    name = 'fuse'

    def __str__(self):
        return 'fuse: returns an RGB/Gray image with the requested channel fusion, arg=[W1R,W1G,W1B;W2R,W2G,W2B;...[:METHOD]][display][gray]'

    def dryrun(self, token, arg):
        method = 'a'
        num_channels = 3
        arg = arg.lower()

        if arg == 'display':
            args = ['-fusemeta']
            argenc = 'display'
        elif arg == 'gray' or arg == 'grey':
            args = ['-fusegrey']
            num_channels = 1
            argenc = 'gray'
        else:
            args = ['-fusergb', arg]

            if ':' in arg:
                (arg, method) = arg.split(':', 1)
            elif '.' in arg:
                (arg, method) = arg.split('.', 1)
            argenc = ''.join([hex(int(i)).replace('0x', '') for i in arg.replace(';', ',').split(',') if i is not ''])

            # test if all channels are valid
            dims = token.dims or {}
            img_num_c = misc.safeint(dims.get('image_num_c'), 0)
            groups = [i for i in arg.split(';') if i is not '']
            # if there are more groups than input channels
            if len(groups)>img_num_c:
                groups = groups[img_num_c:]
                for i, g in enumerate(groups):
                    channels = [misc.safeint(i, 0) for i in g.split(',')]
                    # we can skip 0 weighted channels even if they are outside of the image channel range
                    #if max(channels)>0:
                    #    raise ImageServiceException(400, 'Fuse: requested fusion of channel outside bounds %s>%s (%s)'%(img_num_c+i, img_num_c, g))

        if method != 'a':
            args.extend(['-fusemethod', method])

        info = {
            'image_num_c': num_channels,
        }

        #ifile = token.first_input_file()
        ofile = '%s.fuse_%s_%s'%(token.data, argenc, method)
        return token.setImage(ofile, fmt=default_format, dims=info, input=ofile)

    def action(self, token, arg):
        method = 'a'
        num_channels = 3
        arg = arg.lower()

        if arg == 'display':
            args = ['-fusemeta']
            argenc = 'display'
        elif arg == 'gray' or arg == 'grey':
            args = ['-fusegrey']
            num_channels = 1
            argenc = 'gray'
        else:
            args = ['-fusergb', arg]

            if ':' in arg:
                (arg, method) = arg.split(':', 1)
            elif '.' in arg:
                (arg, method) = arg.split('.', 1)
            argenc = ''.join([hex(int(i)).replace('0x', '') for i in arg.replace(';', ',').split(',') if i is not ''])

            # test if all channels are valid
            dims = token.dims or {}
            img_num_c = misc.safeint(dims.get('image_num_c'), 0)
            groups = [i for i in arg.split(';') if i is not '']
            # if there are more groups than input channels
            if len(groups)>img_num_c:
                groups = groups[img_num_c:]
                for i, g in enumerate(groups):
                    channels = [misc.safeint(i, 0) for i in g.split(',')]
                    # we can skip 0 weighted channels even if they are outside of the image channel range
                    if max(channels)>0:
                        raise ImageServiceException(400, 'Fuse: requested fusion of channel outside bounds %s>%s (%s)'%(img_num_c+i, img_num_c, g))

        if method != 'a':
            args.extend(['-fusemethod', method])

        info = {
            'image_num_c': num_channels,
        }

        ifile = token.first_input_file()
        ofile = '%s.fuse_%s_%s'%(token.data, argenc, method)
        log.debug('Fuse %s: %s to %s with [%s:%s]', token.resource_id, ifile, ofile, arg, method)

        return self.server.enqueue(token, 'fuse', ofile, fmt=default_format, command=args, dims=info)
