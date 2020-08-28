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

__all__ = [ 'DepthOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.depth")

class DepthOperation(BaseOperation):
    '''Provide an image with converted depth per pixel:
       arg = depth,method[,format]
       depth is in bits per pixel
       method is: f or d or t or e
         f - full range
         d - data range
         t - data range with tolerance
         e - equalized
         hounsfield - hounsfield space enhancement
       format is: u, s or f, if unset keeps image original
         u - unsigned integer
         s - signed integer
         f - floating point
       channel mode is: cs or cc
         cs - channels separate
         cc - channels combined
       enhancement granularity: patch,plane,volume,whole
         patch - enhances the image patch using its own histogram
         plane - enhances the image patch using the histogram of the whole image (if available)
         volume - enhances the image patch using the histogram of the whole image (not implemented)
         whole - enhances the image patch using the histogram of the whole image over time (not implemented)
       or
       window center, window width - only used for hounsfield enhancement
         ex: depth=8,hounsfield,u,,40,80
       ex: depth=8,d or depth=8,d,u,cc'''
    name = 'depth'

    def __str__(self):
        return 'depth: returns an image with converted depth per pixel, arg = depth,method[,format][,channelmode]'

    # def dryrun(self, token, arg):
    #     arg = arg.lower()
    #     ofile = '%s.depth_%s'%(token.data, arg)
    #     return token.setImage(fname=ofile, fmt=default_format)

    def action(self, token, arg):
        ms = ['f', 'd', 't', 'e', 'c', 'n', 'hounsfield']
        ds = ['8', '16', '32', '64']
        fs = ['u', 's', 'f']
        fs_map = {
            'u': 'unsigned integer',
            's': 'signed integer',
            'f': 'floating point'
        }
        cm = ['cs', 'cc']
        granularity = ['patch', 'plane'] #, 'volume', 'whole']

        d='d'; m='8'; f='u'; c='cs'; g='plane'
        arg = arg.lower()
        args = arg.split(',')
        if len(args)>0: d = args[0]
        if len(args)>1: m = args[1]
        if len(args)>2: f = args[2] or 'u'
        if len(args)>3: c = args[3] or 'cs'
        if m == 'hounsfield':
            if len(args)>4: window_center = args[4] or None
            if len(args)>5: window_width = args[5] or None
        else:
            if len(args)>4: g = args[4] or None

        if d is None or d not in ds:
            raise ImageServiceException(400, 'Depth: depth is unsupported: %s'%d)
        if m is None or m not in ms:
            raise ImageServiceException(400, 'Depth: method is unsupported: %s'%m )
        if f is not None and f not in fs:
            raise ImageServiceException(400, 'Depth: format is unsupported: %s'%f )
        if c is not None and c not in cm:
            raise ImageServiceException(400, 'Depth: channel mode is unsupported: %s'%c )
        if g is not None and g not in granularity:
            raise ImageServiceException(400, 'Depth: granularity mode is unsupported: %s'%g )
        if m == 'hounsfield' and (window_center is None or window_width is None):
            raise ImageServiceException(400, 'Depth: hounsfield enhancement requires window center and width' )

        ifile = token.first_input_file()
        ofile = '%s.depth_%s'%(token.data, arg)
        log.debug('Depth %s: %s to %s with [%s]', token.resource_id, ifile, ofile, arg)

        extra=[]
        if m == 'hounsfield':
            extra.extend(['-hounsfield', '%s,%s,%s,%s'%(d,f,window_center,window_width)])
        else:
            extra.extend(['-depth', arg])

        if g == 'patch':
            token.histogram = None

        dims = {
            'image_pixel_depth': d,
            'image_pixel_format': fs_map[f],
        }
        return self.server.enqueue(token, 'depth', ofile, fmt=default_format, command=extra, dims=dims)

