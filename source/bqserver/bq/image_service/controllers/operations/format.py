"""
Provides an image in the requested format
       arg = format[,stream][,OPT1][,OPT2][,...]
       some formats are: tiff, jpeg, png, bmp, raw
       stream sets proper file name and forces browser to show save dialog
       any additional comma separated options are passed directly to the encoder

       for movie formats: fps,R,bitrate,B
       where R is a float number of frames per second and B is the integer bitrate

       for tiff: compression,C
       where C is the compression algorithm: none, packbits, lzw, fax

       for jpeg: quality,V
       where V is quality 0-100, 100 being best

       ex: format=jpeg
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

__all__ = [ 'FormatOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.defaults import default_format
from bq.image_service.controllers.converters.converter_ffmpeg import supported_formats as ffmpeg_formats


log = logging.getLogger("bq.image_service.operations.format")

class FormatOperation(BaseOperation):
    '''Provides an image in the requested format
       arg = format[,stream][,OPT1][,OPT2][,...]
       some formats are: tiff, jpeg, png, bmp, raw
       stream sets proper file name and forces browser to show save dialog
       any additional comma separated options are passed directly to the encoder

       for movie formats: fps,R,bitrate,B
       where R is a float number of frames per second and B is the integer bitrate

       for tiff: compression,C
       where C is the compression algorithm: none, packbits, lzw, fax

       for jpeg: quality,V
       where V is quality 0-100, 100 being best

       ex: format=jpeg'''
    name = 'format'

    def __str__(self):
        return 'format: Returns an Image in the requested format, arg = format[,stream][,OPT1][,OPT2][,...]'

    def dryrun(self, token, arg):
        args = arg.lower().split(',')
        fmt = default_format
        if len(args)>0:
            fmt = args.pop(0).lower()

        stream = False
        if 'stream' in args:
            stream = True
            args.remove('stream')

        name_extra = '' if len(args)<=0 else '.%s'%'.'.join(args)
        ext = self.server.converters.defaultExtension(fmt)

        ofile = '%s.%s%s.%s'%(token.data, name_extra, fmt, ext)
        if stream:
            fpath = ofile.split('/')
            filename = '%s_%s.%s'%(token.resource_name, fpath[len(fpath)-1], ext)
            token.setFile(fname=ofile)
            token.outFileName = filename
        else:
            token.setImage(fname=ofile, fmt=fmt)
        log.debug('RETURNING FROM DRYRUN...')
        return token

    def action(self, token, arg):
        if not token.isFile():
            raise ImageServiceException(400, 'Format: input is not an image...' )

        args = arg.lower().split(',')
        fmt = default_format
        if len(args)>0:
            fmt = args.pop(0).lower()

        stream = False
        if 'stream' in args:
            stream = True
            args.remove('stream')

        # avoid doing anything if requested format is in requested format
        dims = token.dims or {}
        if dims.get('format','').lower() == fmt and not token.hasQueue():
            log.debug('%s: Input is in requested format, avoid reconvert...', token.resource_id)
            return token

        if fmt not in self.server.writable_formats:
            raise ImageServiceException(400, 'Requested format [%s] is not writable'%fmt )

        name_extra = '' if len(args)<=0 else '.%s'%'.'.join(args)
        ext = self.server.converters.defaultExtension(fmt)
        ifile = token.first_input_file()
        ofile = '%s.%s%s.%s'%(token.data, name_extra, fmt, ext)
        log.debug('Format %s: %s -> %s with %s opts=[%s]', token.resource_id, ifile, ofile, fmt, args)

        if not os.path.exists(ofile):
            extra = token.drainQueue()
            queue_size = len(extra)
            if len(args) > 0:
                extra.extend( ['-options', (' ').join(args)])
            elif fmt in ['jpg', 'jpeg']:
                extra.extend(['-options', 'quality 95 progressive yes'])

            r = None
            #if dims.get('converter', '') == ConverterImgcnv.name:

            # first try first converter that supports this output format
            c = self.server.writable_formats[fmt]
            #log.info('\n\n WRITABLE FORMAT %s \n\n', c)
            first_name = c.name

            fmt_in = token.dims['format'].lower()
            fmt_in_lst = list(fmt_in.split(','))
            ffmpeg_formats_set = set(i[0].lower() for i in ffmpeg_formats)

            #if there are any operations to be run on the outputw
            for single_fmt in fmt_in_lst:
                if single_fmt in ffmpeg_formats_set:
                    r = c.convert(token, ofile, single_fmt, extra=extra)
                    break

                elif c.name == ConverterImgcnv.name or queue_size < 1:
                    r = c.convert(token, ofile, fmt, extra=extra)
                    break

            # try using other converters directly
            if r is None:
                log.debug('%s could not convert [%s] to [%s] format'%(first_name, ifile, fmt))
                log.debug('Trying other converters directly')
                for n,c in self.server.converters.iteritems():
                    if n==first_name:
                        continue
                    if n == ConverterImgcnv.name or queue_size < 1:
                        r = c.convert(token, ofile, fmt, extra=extra)
                    if r is not None and os.path.exists(ofile):
                        break

            # using ome-tiff as intermediate if everything failed
            if r is None:
                log.debug('None of converters could connvert [%s] to [%s] format'%(ifile, fmt))
                log.debug('Converting to OME-TIFF and then to desired output')
                r = self.server.imageconvert(token, ifile, ofile, fmt=fmt, extra=extra, try_imgcnv=False)

            if r is None:
                log.error('Format %s: %s could not convert with [%s] format [%s] -> [%s]', token.resource_id, c.CONVERTERCOMMAND, fmt, ifile, ofile)
                raise ImageServiceException(415, 'Could not convert into %s format'%fmt )

        if stream:
            fpath = ofile.split('/')
            filename = '%s_%s.%s'%(token.resource_name, fpath[len(fpath)-1], ext)
            token.setFile(fname=ofile)
            token.outFileName = filename
            token.input = ofile
        else:
            token.setImage(fname=ofile, fmt=fmt, input=ofile)

        # if (ofile != ifile) and (fmt != 'raw'):
        #     try:
        #         info = self.server.getImageInfo(filename=ofile)
        #         if int(info['image_num_p'])>1:
        #             if 'image_num_z' in token.dims: info['image_num_z'] = token.dims['image_num_z']
        #             if 'image_num_t' in token.dims: info['image_num_t'] = token.dims['image_num_t']
        #         token.dims = info
        #     except Exception:
        #         pass 
        if (ofile != ifile):
            info = {
                'format': fmt,
            }
            if fmt == 'jpeg':
                info.update({
                    'image_pixel_depth': 8,
                    'image_pixel_format': 'unsigned integer',
                    'image_num_c': min(4, int(dims.get('image_num_c', 0))),
                })
            elif fmt not in ['tiff', 'bigtiff', 'ome-tiff', 'ome-bigtiff', 'raw']:
                info = self.server.getImageInfo(filename=ofile)
                info.update({
                    'image_num_z': dims.get('image_num_z', ''),
                    'image_num_t': dims.get('image_num_t', ''),
                })
            token.dims.update(info)
        return token


