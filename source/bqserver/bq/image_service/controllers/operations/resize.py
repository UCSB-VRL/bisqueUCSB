"""
Provide images in requested dimensions
       arg = w,h,method[,AR|,MX]
       w - new width
       h - new height
       method - NN or BL, or BC (Nearest neighbor, Bilinear, Bicubic respectively)
       if either w or h is ommited or 0, it will be computed using aspect ratio of the image
       if ,AR is present then the size will be used as bounding box and aspect ration preserved
       if ,MX is present then the size will be used as maximum bounding box and aspect ratio preserved
       with MX: if image is smaller it will not be resized!
       #size_arg = '-resize 128,128,BC,AR'
       ex: resize=100,100
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

__all__ = [ 'ResizeOperation', 'Resize3DOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format

log = logging.getLogger("bq.image_service.operations.resize")

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

class ResizeOperation(BaseOperation):
    '''Provide images in requested dimensions
       arg = w,h,method[,AR|,MX]
       w - new width
       h - new height
       method - NN or BL, or BC (Nearest neighbor, Bilinear, Bicubic respectively)
       if either w or h is ommited or 0, it will be computed using aspect ratio of the image
       if ,AR is present then the size will be used as bounding box and aspect ration preserved
       if ,MX is present then the size will be used as maximum bounding box and aspect ratio preserved
       with MX: if image is smaller it will not be resized!
       #size_arg = '-resize 128,128,BC,AR'
       ex: resize=100,100'''
    name = 'resize'

    def __str__(self):
        return 'resize: returns an Image in requested dimensions, arg = w,h,method[,AR|,MX]'

    # def dryrun(self, token, arg):
    #     ss = arg.split(',')
    #     size = [0,0]
    #     method = 'BL'
    #     textAddition = ''

    #     if len(ss)>0 and ss[0].isdigit():
    #         size[0] = int(ss[0])
    #     if len(ss)>1 and ss[1].isdigit():
    #         size[1] = int(ss[1])
    #     if len(ss)>2:
    #         method = ss[2].upper()
    #     if len(ss)>3:
    #         textAddition = ss[3].upper()

    #     if size[0]<=0 and size[1]<=0:
    #         raise ImageServiceException(400, 'Resize: size is unsupported: [%s]'%arg )

    #     if method not in ['NN', 'BL', 'BC']:
    #         raise ImageServiceException(400, 'Resize: method is unsupported: [%s]'%arg )

    #     # if the image is smaller and MX is used, skip resize
    #     dims = token.dims or {}
    #     if maxBounding and dims.get('image_num_x',0)<=size[0] and dims.get('image_num_y',0)<=size[1]:
    #         log.debug('Resize: Max bounding resize requested on a smaller image, skipping...')
    #         return token

    #     ofile = '%s.size_%d,%d,%s,%s' % (token.data, size[0], size[1], method, textAddition)
    #     return token.setImage(ofile, fmt=default_format)

    def action(self, token, arg):
        log.debug('Resize %s: %s', token.resource_id, arg)

        #size = tuple(map(int, arg.split(',')))
        ss = arg.split(',')
        size = [0,0]
        method = 'BL'
        aspectRatio = ''
        maxBounding = False
        textAddition = ''

        if len(ss)>0 and ss[0].isdigit():
            size[0] = int(ss[0])
        if len(ss)>1 and ss[1].isdigit():
            size[1] = int(ss[1])
        if len(ss)>2:
            method = ss[2].upper()
        if len(ss)>3:
            textAddition = ss[3].upper()

        if len(ss)>3 and (textAddition == 'AR'):
            aspectRatio = ',AR'
        if len(ss)>3 and (textAddition == 'MX'):
            maxBounding = True
            aspectRatio = ',AR'

        if size[0]<=0 and size[1]<=0:
            raise ImageServiceException(400, 'Resize: size is unsupported: [%s]'%arg )

        if method not in ['NN', 'BL', 'BC']:
            raise ImageServiceException(400, 'Resize: method is unsupported: [%s]'%arg )

        # if the image is smaller and MX is used, skip resize
        dims = token.dims or {}
        num_x = int(dims.get('image_num_x', 0))
        num_y = int(dims.get('image_num_y', 0))
        if maxBounding and num_x<=size[0] and num_y<=size[1]:
            log.debug('Resize: Max bounding resize requested on a smaller image, skipping...')
            return token
        if token.dryrun != True and (num_x<=0 or num_y<=0):
            raise ImageServiceException(400, 'Resize: image improperly decoded, has side of 0px' )
        if token.dryrun != True and (size[0]<=0 or size[1]<=0) and (num_x<=0 or num_y<=0):
            raise ImageServiceException(400, 'Resize: new image size cannot be guessed due to missing info' )

        ifile = token.first_input_file()
        ofile = '%s.size_%d,%d,%s,%s' % (token.data, size[0], size[1], method, textAddition)
        args = ['-resize', '%s,%s,%s%s'%(size[0], size[1], method,aspectRatio)]
        try:
            width = height = 1
            width, height = compute_new_size(num_x, num_y, size[0], size[1], aspectRatio!='', maxBounding)
        except ZeroDivisionError:
            if token.dryrun == True:
                log.warning('Resize warning while guessing size %s: [%sx%s] to [%sx%s]', token.resource_id, num_x, num_y, width, height)
            else:
                raise ImageServiceException(400, 'Resize: new image size cannot be guessed due to missing info' )

        log.debug('Resize %s: [%sx%s] to [%sx%s] for [%s] to [%s]', token.resource_id, num_x, num_y, width, height, ifile, ofile)

        # if image has multiple resolution levels find the closest one and request it
        num_l = dims.get('image_num_resolution_levels', 1)
        if num_l>1 and '-res-level' not in token.getQueue():
            try:
                scales = [float(i) for i in dims.get('image_resolution_level_scales', '').split(',')]
                #log.debug('scales: %s',  scales)
                sizes = [(round(num_x*i),round(num_y*i)) for i in scales]
                #log.debug('scales: %s',  sizes)
                relatives = [max(width/float(sz[0]), height/float(sz[1])) for sz in sizes]
                #log.debug('relatives: %s',  relatives)
                relatives = [i if i<=1 else 0 for i in relatives]
                #log.debug('relatives: %s',  relatives)
                level = relatives.index(max(relatives))
                args.extend(['-res-level', str(level)])
            except (Exception):
                pass

        info = {
            'image_num_x': width,
            'image_num_y': height,
            'pixel_resolution_x': dims.get('pixel_resolution_x', 0) * (num_x / float(width)),
            'pixel_resolution_y': dims.get('pixel_resolution_y', 0) * (num_y / float(height)),
        }
        return self.server.enqueue(token, 'resize', ofile, fmt=default_format, command=args, dims=info)



class Resize3DOperation(BaseOperation):
    '''Provide images in requested dimensions
       arg = w,h,d,method[,AR|,MX]
       w - new width
       h - new height
       d - new depth
       method - NN or TL, or TC (Nearest neighbor, Trilinear, Tricubic respectively)
       if either w or h or d are ommited or 0, missing value will be computed using aspect ratio of the image
       if ,AR is present then the size will be used as bounding box and aspect ration preserved
       if ,MX is present then the size will be used as maximum bounding box and aspect ratio preserved
       with MX: if image is smaller it will not be resized!
       ex: resize3d=100,100,100,TC'''
    name = 'resize3d'

    def __str__(self):
        return 'resize3d: returns an image in requested dimensions, arg = w,h,d,method[,AR|,MX]'

    def dryrun(self, token, arg):
        ss = arg.split(',')
        size = [0,0,0]
        method = 'TC'
        textAddition = ''

        if len(ss)>0 and ss[0].isdigit():
            size[0] = int(ss[0])
        if len(ss)>1 and ss[1].isdigit():
            size[1] = int(ss[1])
        if len(ss)>2 and ss[2].isdigit():
            size[2] = int(ss[2])
        if len(ss)>3:
            method = ss[3].upper()
        if len(ss)>4:
            textAddition = ss[4].upper()

        ofile = '%s.size3d_%d,%d,%d,%s,%s' % (token.data, size[0], size[1], size[2], method,textAddition)
        return token.setImage(ofile, fmt=default_format)

    def action(self, token, arg):
        if not token.isFile():
            raise ImageServiceException(400, 'Resize3D: input is not an image...' )
        log.debug('Resize3D %s: %s', token.resource_id, arg )

        #size = tuple(map(int, arg.split(',')))
        ss = arg.split(',')
        size = [0,0,0]
        method = 'TC'
        aspectRatio = ''
        maxBounding = False
        textAddition = ''

        if len(ss)>0 and ss[0].isdigit():
            size[0] = int(ss[0])
        if len(ss)>1 and ss[1].isdigit():
            size[1] = int(ss[1])
        if len(ss)>2 and ss[2].isdigit():
            size[2] = int(ss[2])
        if len(ss)>3:
            method = ss[3].upper()
        if len(ss)>4:
            textAddition = ss[4].upper()

        if len(ss)>4 and (textAddition == 'AR'):
            aspectRatio = ',AR'
        if len(ss)>4 and (textAddition == 'MX'):
            maxBounding = True
            aspectRatio = ',AR'

        if size[0]<=0 and size[1]<=0 and size[2]<=0:
            raise ImageServiceException(400, 'Resize3D: size is unsupported: [%s]'%arg )

        if method not in ['NN', 'TL', 'TC']:
            raise ImageServiceException(400, 'Resize3D: method is unsupported: [%s]'%arg )

        # if the image is smaller and MX is used, skip resize
        dims = token.dims or {}
        w = dims.get('image_num_x', 0)
        h = dims.get('image_num_y', 0)
        z = dims.get('image_num_z', 1)
        t = dims.get('image_num_t', 1)
        d = max(z, t)
        if w==size[0] and h==size[1] and d==size[2]:
            return token
        if maxBounding and w<=size[0] and h<=size[1] and d<=size[2]:
            return token
        if (z>1 and t>1) or (z==1 and t==1):
            raise ImageServiceException(400, 'Resize3D: only supports 3D images' )

        ifile = token.first_input_file()
        ofile = '%s.size3d_%d,%d,%d,%s,%s' % (token.data, size[0], size[1], size[2], method,textAddition)
        log.debug('Resize3D %s: %s to %s', token.resource_id, ifile, ofile)

        width, height = compute_new_size(w, h, size[0], size[1], aspectRatio!='', maxBounding)
        zrestag = 'pixel_resolution_z' if z>1 else 'pixel_resolution_t'
        info = {
            'image_num_x': width,
            'image_num_y': height,
            'image_num_z': size[2] if z>1 else 1,
            'image_num_t': size[2] if t>1 else 1,
            'pixel_resolution_x': dims.get('pixel_resolution_x', 0) * (w / float(width)),
            'pixel_resolution_y': dims.get('pixel_resolution_y', 0) * (h / float(height)),
            zrestag: dims.get(zrestag, 0) * (d / float(size[2])),
        }
        command = token.drainQueue()
        if not os.path.exists(ofile):
            # if image has multiple resolution levels find the closest one and request it
            num_l = dims.get('image_num_resolution_levels', 1)
            if num_l>1 and '-res-level' not in command:
                try:
                    scales = [float(i) for i in dims.get('image_resolution_level_scales', '').split(',')]
                    #log.debug('scales: %s',  scales)
                    sizes = [(round(w*i),round(h*i)) for i in scales]
                    #log.debug('scales: %s',  sizes)
                    relatives = [max(size[0]/float(sz[0]), size[1]/float(sz[1])) for sz in sizes]
                    #log.debug('relatives: %s',  relatives)
                    relatives = [i if i<=1 else 0 for i in relatives]
                    #log.debug('relatives: %s',  relatives)
                    level = relatives.index(max(relatives))
                    command.extend(['-res-level', str(level)])
                except (Exception):
                    pass

            command.extend(['-resize3d', '%s,%s,%s,%s%s'%(size[0], size[1], size[2], method, aspectRatio)])
            self.server.imageconvert(token, ifile, ofile, fmt=default_format, extra=command)

        return token.setImage(ofile, fmt=default_format, dims=info, input=ofile)
