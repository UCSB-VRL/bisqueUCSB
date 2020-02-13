"""
Returns histogram of an image
       ex: histogram
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

__all__ = [ 'HistogramOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv

log = logging.getLogger("bq.image_service.operations.histogram")

class HistogramOperation(BaseOperation):
    '''Returns histogram of an image
       ex: histogram'''
    name = 'histogram'

    def __str__(self):
        return 'histogram: returns a histogram of an image, ex: histogram'

    def dryrun(self, token, arg):
        ofile = '%s.histogram.xml'%(token.data)
        return token.setXmlFile(fname=ofile)

    def action(self, token, arg):
        if not token.isFile():
            raise ImageServiceException(400, 'Histogram: input is not an image...' )
        ifile = token.first_input_file()
        ofile = '%s.histogram.xml'%(token.data)
        log.debug('Histogram %s: %s to %s', token.resource_id, ifile, ofile)

        command = token.drainQueue()
        if not os.path.exists(ofile):
            # use resolution level if available to find the best estimate for very large images
            command.extend(['-ohstxml', ofile])

            dims = token.dims or {}
            num_x = int(dims.get('image_num_x', 0))
            num_y = int(dims.get('image_num_y', 0))
            width = 1024 # image sizes good enough for histogram estimation
            height = 1024 # image sizes good enough for histogram estimation

            # if image has multiple resolution levels find the closest one and request it
            num_l = dims.get('image_num_resolution_levels', 1)
            if num_l>1 and '-res-level' not in token.getQueue():
                try:
                    scales = [float(i) for i in dims.get('image_resolution_level_scales', '').split(',')]
                    sizes = [(round(num_x*i),round(num_y*i)) for i in scales]
                    relatives = [max(width/float(sz[0]), height/float(sz[1])) for sz in sizes]
                    relatives = [i if i<=1 else 0 for i in relatives]
                    level = relatives.index(max(relatives))
                    command.extend(['-res-level', str(level)])
                except (Exception):
                    pass

            self.server.imageconvert(token, ifile, None, extra=command)

        return token.setXmlFile(fname=ofile)
