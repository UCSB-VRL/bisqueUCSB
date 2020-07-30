"""
Provides a tile of an image :
       arg = l,tnx,tny,tsz
       or
       arg = s,x1,y1,x2,y2

       # 4 parameter request:
       # gridded tile size interface,
       # it is the fastest possible especially if hitting the native tile size
       l: level of the pyramid, 0=100%, 1=50%, 2=25%, ...
       tnx, tny: x and y tile number on the grid
       tsz: tile size
       All values are in range [0..N]
       ex: tile=0,2,3,512

       # 5 parameter request:
       # arbitrary size and scale that uses tiled-pyramidal files
       # this might get slower with unfavorable tile sizes
       # scale will currently only support available pyramidal power of two levels
       s: scale, 1.0=100%, 0.5=50%, 0.25=25%, ...
       x1, y1: x and y coordinates of the top-left corner, same as ROI interface
       x2, y2: x and y coordinates of the bottom-right corner, same as ROI interface
       All values are in range [0..N]
       ex: tile=1.0,10,10,999,999
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

__all__ = [ 'TileOperation' ]

from bq.util.locks import Locks
from bq.util.mkdir import _mkdir
from bq.image_service.controllers.exceptions import ImageServiceException, ImageServiceFuture
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format, default_tile_size, min_level_size, block_reads, block_tile_reads

log = logging.getLogger("bq.image_service.operations.tile")

class TileOperation(BaseOperation):
    '''Provides a tile of an image :
       arg = l,tnx,tny,tsz
       l: level of the pyramid, 0 - initial level, 1 - scaled down by a factor of 2
       tnx, tny: x and y tile number on the grid
       tsz: tile size
       All values are in range [0..N]
       ex: tile=0,2,3,512'''
    name = 'tile'

    def __str__(self):
        return 'tile: returns a tile, arg = l,tnx,tny,tsz. All values are in range [0..N]'

    def dryrun(self, token, arg):
        level=0; tnx=0; tny=0; tsz=512;
        vs = arg.split(',', 4)
        if len(vs)>0 and vs[0].isdigit(): level = int(vs[0])
        if len(vs)>1 and vs[1].isdigit(): tnx = int(vs[1])
        if len(vs)>2 and vs[2].isdigit(): tny = int(vs[2])
        if len(vs)>3 and vs[3].isdigit(): tsz = int(vs[3])

        dims = token.dims or {}
        width = dims.get('image_num_x', 0)
        height = dims.get('image_num_y', 0)
        if width<=tsz and height<=tsz:
            log.debug('Dryrun tile: Image is smaller than requested tile size, passing the whole image...')
            return token

        x = tnx * tsz
        y = tny * tsz
        if x>=width or y>=height:
            raise ImageServiceException(400, 'Tile: tile position outside of the image: %s,%s'%(tnx, tny))

        # the new tile service does not change the number of z points in the image and if contains all z will perform the operation
        info = {
            'image_num_x': tsz if width-x >= tsz else width-x,
            'image_num_y': tsz if height-y >= tsz else height-y,
            #'image_num_z': 1,
            #'image_num_t': 1,
        }

        base_name = '%s.tiles'%(token.data)
        ofname    = os.path.join(base_name, '%s_%.3d_%.3d_%.3d' % (tsz, level, tnx, tny))
        return token.setImage(ofname, fmt=default_format, dims=info)

    def action(self, token, arg):
        '''arg = l,tnx,tny,tsz'''
        if not token.isFile():
            raise ImageServiceException(400, 'Tile: input is not an image...' )
        level=0; tnx=0; tny=0; tsz=512;
        vs = arg.split(',', 4)
        if len(vs)>0 and vs[0].isdigit(): level = int(vs[0])
        if len(vs)>1 and vs[1].isdigit(): tnx = int(vs[1])
        if len(vs)>2 and vs[2].isdigit(): tny = int(vs[2])
        if len(vs)>3 and vs[3].isdigit(): tsz = int(vs[3])
        log.debug( 'Tile: l:%d, tnx:%d, tny:%d, tsz:%d' % (level, tnx, tny, tsz) )

        # if input image is smaller than the requested tile size
        dims = token.dims or {}
        width = dims.get('image_num_x', 0)
        height = dims.get('image_num_y', 0)
        if width<=tsz and height<=tsz:
            log.debug('Image is smaller than requested tile size, passing the whole image...')
            return token

        # construct a sliced filename
        ifname    = token.first_input_file()
        base_name = '%s.tiles'%(token.data)
        _mkdir( base_name )
        ofname    = os.path.join(base_name, '%s_%.3d_%.3d_%.3d' % (tsz, level, tnx, tny))
        hist_name = os.path.join(base_name, '%s_histogram'%(tsz))

        # if input image does not contain tile pyramid, create one and pass it along
        if dims.get('image_num_resolution_levels', 0)<2 or dims.get('tile_num_x', 0)<1:
            pyramid = '%s.pyramid.tif'%(token.data)
            command = token.drainQueue()
            if not os.path.exists(pyramid):
                #command.extend(['-ohst', hist_name])
                command.extend(['-options', 'compression lzw tiles %s pyramid subdirs'%default_tile_size])
                log.debug('Generate tiled pyramid %s: from %s to %s with %s', token.resource_id, ifname, pyramid, command )
                r = self.server.imageconvert(token, ifname, pyramid, fmt=default_format, extra=command)
                if r is None:
                    raise ImageServiceException(500, 'Tile: could not generate pyramidal file' )
            # ensure the file was created
            with Locks(pyramid, failonread=(not block_tile_reads)) as l:
                if l.locked is False: # dima: never wait, respond immediately
                    fff = (width*height) / (10000*10000)
                    raise ImageServiceFuture((15*fff,30*fff))

            # compute the number of pyramidal levels
            # sz = max(width, height)
            # num_levels = math.ceil(math.log(sz, 2)) - math.ceil(math.log(min_level_size, 2)) + 1
            # scales = [1/float(pow(2,i)) for i in range(0, num_levels)]
            # info = {
            #     'image_num_resolution_levels': num_levels,
            #     'image_resolution_level_scales': ',',join([str(i) for i in scales]),
            #     'tile_num_x': default_tile_size,
            #     'tile_num_y': default_tile_size,
            #     'converter': ConverterImgcnv.name,
            # }

            # load the number of pyramidal levels from the file
            info2 = self.server.getImageInfo(filename=pyramid)
            info = {
                'image_num_resolution_levels': info2.get('image_num_resolution_levels'),
                'image_resolution_level_scales': info2.get('image_resolution_level_scales'),
                'tile_num_x': info2.get('tile_num_x'),
                'tile_num_y': info2.get('tile_num_y'),
                'converter': info2.get('converter'),
            }
            log.debug('Updating original input to pyramidal version %s: %s -> %s', token.resource_id, ifname, pyramid )
            token.setImage(ofname, fmt=default_format, dims=info, input=pyramid)
            ifname = pyramid


        # compute output tile size
        dims = token.dims or {}
        x = tnx * tsz
        y = tny * tsz
        if x>=width or y>=height:
            raise ImageServiceException(400, 'Tile: tile position outside of the image: %s,%s'%(tnx, tny))

        # the new tile service does not change the number of z points in the image and if contains all z will perform the operation
        info = {
            'image_num_x': tsz if width-x >= tsz else width-x,
            'image_num_y': tsz if height-y >= tsz else height-y,
            #'image_num_z': 1,
            #'image_num_t': 1,
        }

        #log.debug('Inside pyramid dims: %s', dims)
        #log.debug('Inside pyramid input: %s', token.first_input_file() )
        #log.debug('Inside pyramid data: %s', token.data )

        # extract individual tile from pyramidal tiled image
        if dims.get('image_num_resolution_levels', 0)>1 and dims.get('tile_num_x', 0)>0:
            # dima: maybe better to test converter, if imgcnv then enqueue, otherwise proceed with the converter path
            if dims.get('converter', '') == ConverterImgcnv.name:
                c = self.server.converters[ConverterImgcnv.name]
                r = c.tile(token, ofname, level, tnx, tny, tsz)
                if r is not None:
                    if not os.path.exists(hist_name):
                        # write the histogram file is missing
                        c.writeHistogram(token, ofnm=hist_name)
                # if decoder returned a list of operations for imgcnv to enqueue
                if isinstance(r, list):
                    #r.extend([ '-ihst', hist_name])
                    token.histogram = hist_name
                    return self.server.enqueue(token, 'tile', ofname, fmt=default_format, command=r, dims=info)

            # try other decoders to read tiles
            ofname = '%s.tif'%ofname
            if os.path.exists(ofname):
                return token.setImage(ofname, fmt=default_format, dims=info, hist=hist_name, input=ofname)
            else:
                r = None
                for n,c in self.server.converters.iteritems():
                    if n == ConverterImgcnv.name: continue
                    if callable( getattr(c, "tile", None) ):
                        r = c.tile(token, ofname, level, tnx, tny, tsz)
                        if r is not None:
                            if not os.path.exists(hist_name):
                                # write the histogram file if missing
                                c.writeHistogram(token, ofnm=hist_name)
                            return token.setImage(ofname, fmt=default_format, dims=info, hist=hist_name, input=ofname)

        raise ImageServiceException(500, 'Tile could not be extracted')

