"""
Provides ROI for requested images
       arg = x1,y1,x2,y2
       x1,y1 - top left corner
       x2,y2 - bottom right
       all values are in ranges [1..N]
       0 or empty - means first/last element
       supports multiple ROIs in which case those will be only cached
       ex: roi=10,10,100,100
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

__all__ = [ 'RoiOperation' ]

from bq.util.locks import Locks
from bq.image_service.controllers.exceptions import ImageServiceException, ImageServiceFuture
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format, block_reads

log = logging.getLogger("bq.image_service.operations.roi")

class RoiOperation(BaseOperation):
    '''Provides ROI for requested images
       arg = x1,y1,x2,y2
       x1,y1 - top left corner
       x2,y2 - bottom right
       all values are in ranges [1..N]
       0 or empty - means first/last element
       supports multiple ROIs in which case those will be only cached
       ex: roi=10,10,100,100'''
    name = 'roi'

    def __str__(self):
        return 'roi: returns an image in specified ROI, arg = x1,y1,x2,y2[;x1,y1,x2,y2], all values are in ranges [1..N]'

    def dryrun(self, token, arg):
        vs = arg.split(';')[0].split(',', 4)
        x1 = int(vs[0]) if len(vs)>0 and vs[0].isdigit() else 0
        y1 = int(vs[1]) if len(vs)>1 and vs[1].isdigit() else 0
        x2 = int(vs[2]) if len(vs)>2 and vs[2].isdigit() else 0
        y2 = int(vs[3]) if len(vs)>3 and vs[3].isdigit() else 0
        ofile = '%s.roi_%d,%d,%d,%d'%(token.data, x1-1,y1-1,x2-1,y2-1)
        info = {
            'image_num_x': x2-x1,
            'image_num_y': y2-y1,
        }
        return token.setImage(ofile, fmt=default_format, dims=info)

    def action(self, token, arg):
        if not token.isFile():
            raise ImageServiceException(400, 'Roi: input is not an image...' )
        rois = []
        for a in arg.split(';'):
            vs = a.split(',', 4)
            x1 = int(vs[0]) if len(vs)>0 and vs[0].isdigit() else 0
            y1 = int(vs[1]) if len(vs)>1 and vs[1].isdigit() else 0
            x2 = int(vs[2]) if len(vs)>2 and vs[2].isdigit() else 0
            y2 = int(vs[3]) if len(vs)>3 and vs[3].isdigit() else 0
            rois.append((x1,y1,x2,y2))
        x1,y1,x2,y2 = rois[0]

        if x1<=0 and x2<=0 and y1<=0 and y2<=0:
            raise ImageServiceException(400, 'ROI: region is not provided')

        ifile = token.first_input_file()
        otemp = token.data
        ofile = '%s.roi_%d,%d,%d,%d'%(token.data, x1-1,y1-1,x2-1,y2-1)
        log.debug('ROI %s: %s to %s', token.resource_id, ifile, ofile)

        if len(rois) == 1:
            info = {
                'image_num_x': x2-x1,
                'image_num_y': y2-y1,
            }
            command = ['-roi', '%s,%s,%s,%s'%(x1-1,y1-1,x2-1,y2-1)]
            return self.server.enqueue(token, 'roi', ofile, fmt=default_format, command=command, dims=info)

        # remove pre-computed ROIs
        rois = [(_x1,_y1,_x2,_y2) for _x1,_y1,_x2,_y2 in rois if not os.path.exists('%s.roi_%d,%d,%d,%d'%(otemp,_x1-1,_y1-1,_x2-1,_y2-1))]

        lfile = '%s.rois'%(otemp)
        command = token.drainQueue()
        if not os.path.exists(ofile) or len(rois)>0:
            # global ROI lock on this input since we can't lock on all individual outputs
            with Locks(ifile, lfile, failonexist=True) as l:
                if l.locked: # the file is not being currently written by another process
                    s = ';'.join(['%s,%s,%s,%s'%(x1-1,y1-1,x2-1,y2-1) for x1,y1,x2,y2 in rois])
                    command.extend(['-roi', s])
                    command.extend(['-template', '%s.roi_{x1},{y1},{x2},{y2}'%otemp])
                    self.server.imageconvert(token, ifile, ofile, fmt=default_format, extra=command)
                    # ensure the virtual locking file is not removed
                    with open(lfile, 'wb') as f:
                        f.write('#Temporary locking file')
                elif l.locked is False: # dima: never wait, respond immediately
                    raise ImageServiceFuture((1,15))

        # ensure the operation is finished
        if os.path.exists(lfile):
            with Locks(lfile, failonread=(not block_reads)) as l:
                if l.locked is False: # dima: never wait, respond immediately
                    raise ImageServiceFuture((1,15))

        info = {
            'image_num_x': x2-x1,
            'image_num_y': y2-y1,
        }
        return token.setImage(ofile, fmt=default_format, dims=info, input=ofile)
