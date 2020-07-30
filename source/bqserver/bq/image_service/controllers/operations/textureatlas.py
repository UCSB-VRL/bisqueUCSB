"""
Returns a 2D texture atlas image for a given 3D input
       ex: textureatlas
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

__all__ = [ 'TextureAtlasOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.textureatlas")

# w: image width
# h: image height
# n: numbe rof image planes, Z stacks or time points
def compute_atlas_size(w, h, n):
    # start with atlas composed of a row of images
    ww = w*n
    hh = h
    ratio = ww / float(hh);
    # optimize side to be as close to ratio of 1.0
    for r in range(2, n):
        ipr = math.ceil(n / float(r))
        aw = w*ipr;
        ah = h*r;
        rr = max(aw, ah) / float(min(aw, ah))
        if rr < ratio:
            ratio = rr
            ww = aw
            hh = ah
        else:
            break

    return (int(round(ww)), int(round(hh)))

class TextureAtlasOperation(BaseOperation):
    '''Returns a 2D texture atlas image for a given 3D input
       ex: textureatlas'''
    name = 'textureatlas'

    def __str__(self):
        return 'textureatlas: returns a 2D texture atlas image for a given 3D input'

    def dryrun(self, token, arg):
        ofile = '%s.textureatlas'%(token.data)
        dims = token.dims or {}
        num_z = int(dims.get('image_num_z', 1))
        num_t = int(dims.get('image_num_t', 1))
        width, height = compute_atlas_size(int(dims.get('image_num_x', 0)), int(dims.get('image_num_y', 0)), num_z*num_t)
        info = {
            'image_num_x': width,
            'image_num_y': height,
            'image_num_z': 1,
            'image_num_t': 1,
        }
        return token.setImage(fname=ofile, fmt=default_format, dims=info)

    def action(self, token, arg):
        #ifile = token.first_input_file()
        ofile = '%s.textureatlas'%(token.data)
        #log.debug('Texture Atlas %s: %s to %s', token.resource_id, ifile, ofile)

        dims = token.dims or {}
        num_z = int(dims.get('image_num_z', 1))
        num_t = int(dims.get('image_num_t', 1))
        width, height = compute_atlas_size(int(dims.get('image_num_x', 0)), int(dims.get('image_num_y', 0)), num_z*num_t)
        info = {
            'image_num_x': width,
            'image_num_y': height,
            'image_num_z': 1,
            'image_num_t': 1,
        }
        #return self.server.enqueue(token, 'textureatlas', ofile, fmt=default_format, command=['-textureatlas'], dims=info)

        if not os.path.exists(ofile):
            if token.hasQueue():
                token = self.server.process_queue(token) # need to process queue first since textureatlas can't deal with all kinds of inputs
            ifile = token.first_input_file()
            ofile = '%s.textureatlas'%(token.data)
            log.debug('Texture Atlas %s: %s to %s', token.resource_id, ifile, ofile)
            self.server.imageconvert(token, ifile, ofile, fmt=default_format, extra=['-textureatlas'], dims=info)
        return token.setImage(ofile, fmt=default_format, dims=info, input=ofile, queue=[])

