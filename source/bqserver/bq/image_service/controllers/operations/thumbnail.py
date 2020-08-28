"""
Create and provide thumbnails for images:
The default values are: 128,128,BL,,jpeg
arg = [w,h][,method][,preproc][,format]
w - thumbnail width, width and hight are defined as maximum boundary
h - thumbnail height, width and hight are defined as maximum boundary
method - ''|NN|BL|BC - default, Nearest neighbor, Bilinear, Bicubic respectively
preproc - ''|MID|MIP|NIP - empty (auto), middle slice, maximum intensity projection, minimum intensity projection
format - output image format, default is JPEG
ex: ?thumbnail
ex: ?thumbnail=200,200,BC,,png
ex: ?thumbnail=200,200,BC,mid,png
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

__all__ = [ 'ThumbnailOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.util.io_misc import safeint
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.thumbnail")

def compute_new_size(imw, imh, w, h, keep_aspect_ratio, no_upsample):
    if no_upsample is True and imw<=w and imh<=h:
        return (imw, imh)

    if keep_aspect_ratio is True:
        if imw/float(w) >= imh/float(h):
            h = 0
        else:
            w = 0

    # it's allowed to specify only one of the sizes, the other one will be computed
    if w == 0:
        w = int(round(imw / (imh / float(h))))
    if h == 0:
        h = int(round(imh / (imw / float(w))))

    return (w, h)

class ThumbnailOperation(BaseOperation):
    '''Create and provide thumbnails for images:
       The default values are: 128,128,BL,,jpeg
       arg = [w,h][,method][,preproc][,format]
       w - thumbnail width, width and hight are defined as maximum boundary
       h - thumbnail height, width and hight are defined as maximum boundary
       method - ''|NN|BL|BC - default, Nearest neighbor, Bilinear, Bicubic respectively
       preproc - ''|MID|MIP|NIP - empty (auto), middle slice, maximum intensity projection, minimum intensity projection
       format - output image format, default is JPEG
       ex: ?thumbnail
       ex: ?thumbnail=200,200,BC,,png
       ex: ?thumbnail=200,200,BC,mid,png '''
    name = 'thumbnail'

    def __str__(self):
        return 'thumbnail: returns an image as a thumbnail, arg = [w,h][,method][,preproc][,format]'

    def dryrun(self, token, arg):
        ss = arg.split(',')
        size = [safeint(ss[0], 128) if len(ss)>0 else 128,
                safeint(ss[1], 128) if len(ss)>1 else 128]
        method = ss[2].upper() if len(ss)>2 and len(ss[2])>0 else 'BC'
        preproc = ss[3].lower() if len(ss)>3 and len(ss[3])>0 else ''
        preprocc = ',%s'%preproc if len(preproc)>0 else '' # attempt to keep the filename backward compatible
        fmt = ss[4].lower() if len(ss)>4 and len(ss[4])>0 else 'jpeg'

        dims = token.dims or {}
        num_x = int(dims.get('image_num_x', 0))
        num_y = int(dims.get('image_num_y', 0))
        try:
            width, height = compute_new_size(num_x, num_y, size[0], size[1], keep_aspect_ratio=True, no_upsample=True)
        except ZeroDivisionError:
            log.warning('Thumbnail warning while guessing size %s: [%sx%s] to [%sx%s]', token.resource_id, num_x, num_y, width, height)
            width = size[0]
            height = size[1]

        info = {
            'image_num_x': width,
            'image_num_y': height,
            'image_num_c': 3,
            'image_num_z': 1,
            'image_num_t': 1,
            'image_pixel_depth': 8,
            'format': fmt,
        }
        ext = self.server.converters.defaultExtension(fmt)
        ofile = '%s.thumb_%s,%s,%s%s.%s'%(token.data, size[0], size[1], method, preprocc, ext)
        #log.debug('Dryrun thumbnail [%s]', ofile)
        return token.setImage(ofile, fmt=fmt, dims=info, input=ofile)

    def action(self, token, arg):
        ss = arg.split(',')
        size = [safeint(ss[0], 128) if len(ss)>0 else 128,
                safeint(ss[1], 128) if len(ss)>1 else 128]
        method = ss[2].upper() if len(ss)>2 and len(ss[2])>0 else 'BC'
        preproc = ss[3].lower() if len(ss)>3 and len(ss[3])>0 else ''
        preprocc = ',%s'%preproc if len(preproc)>0 else '' # attempt to keep the filename backward compatible
        fmt = ss[4].lower() if len(ss)>4 and len(ss[4])>0 else 'jpeg'

        if size[0]<=0 and size[1]<=0:
            raise ImageServiceException(400, 'Thumbnail: size is unsupported [%s]'%arg)

        if method not in ['NN', 'BL', 'BC']:
            raise ImageServiceException(400, 'Thumbnail: method is unsupported [%s]'%arg)

        if preproc not in ['', 'mid', 'mip', 'nip']:
            raise ImageServiceException(400, 'Thumbnail: method is unsupported [%s]'%arg)

        ext = self.server.converters.defaultExtension(fmt)
        ifile = token.first_input_file()
        ofile = '%s.thumb_%s,%s,%s%s.%s'%(token.data, size[0], size[1], method, preprocc, ext)

        dims = token.dims or {}
        num_x = int(dims.get('image_num_x', 0))
        num_y = int(dims.get('image_num_y', 0))

        try:
            width, height = compute_new_size(num_x, num_y, size[0], size[1], keep_aspect_ratio=True, no_upsample=True)
        except ZeroDivisionError:
            raise ImageServiceException(400, 'Thumbnail: new image size cannot be guessed due to missing info' )

        info = {
            'image_num_x': width,
            'image_num_y': height,
            'image_num_c': 3,
            'image_num_z': 1,
            'image_num_t': 1,
            'image_pixel_depth': 8,
            'format': fmt,
        }

        # if image can be decoded with imageconvert, enqueue
        if dims.get('converter', '') == ConverterImgcnv.name:
            r = ConverterImgcnv.thumbnail(token, ofile, size[0], size[1], method=method, preproc=preproc, fmt=fmt)
            if isinstance(r, list):
                return self.server.enqueue(token, 'thumbnail', ofile, fmt=fmt, command=r, dims=info)

        # if image requires other decoder
        if not os.path.exists(ofile):
            intermediate = '%s.ome.tif'%(token.data)

            r = None
            if 'converter' in dims and dims.get('converter') in self.server.converters:
                r = self.server.converters[dims.get('converter')].thumbnail(token, ofile, size[0], size[1], method=method, intermediate=intermediate, preproc=preproc, fmt=fmt)

            # if desired converter failed, perform exhaustive conversion
            if r is None:
                for n,c in self.server.converters.iteritems():
                    if n in [ConverterImgcnv.name, dims.get('converter')]: continue
                    r = c.thumbnail(token, ofile, size[0], size[1], method=method, intermediate=intermediate, preproc=preproc, fmt=fmt)
                    if r is not None:
                        break
            if r is None:
                log.error('Thumbnail %s: could not generate thumbnail for [%s]', token.resource_id, ifile)
                raise ImageServiceException(415, 'Could not generate thumbnail' )
            if isinstance(r, list):
                return self.server.enqueue(token, 'thumbnail', ofile, fmt=fmt, command=r, dims=info)

        return token.setImage(ofile, fmt=fmt, dims=info, input=ofile)
