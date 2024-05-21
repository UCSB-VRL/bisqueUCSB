
""" Openslide python deep-zoom based driver

This converter will not support the full API for now since it would be really inefficient
trying to create ome-tiff out of pyramidal tiled images, instead it will only provide
tile and thumbnail access, this will work perfectly for the UI and module access
if tiles are used, better integration will be looked at later if need arises
"""

__author__    = "Dmitry Fedorov"
__version__   = "0.1"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import os.path
from lxml import etree
import re
import tempfile
import cStringIO as StringIO
import ConfigParser
import math

#from collections import OrderedDict
from bq.util.compat import OrderedDict
from bq.util.locks import Locks
import bq.util.io_misc as misc

from bq.image_service.controllers.exceptions import ImageServiceException, ImageServiceFuture
from bq.image_service.controllers.defaults import min_level_size, block_reads, block_tile_reads
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converter_base import ConverterBase, Format
from .converter_imgcnv import ConverterImgcnv

try:
   import openslide
   from openslide import deepzoom
except (ImportError, OSError):
   pass

import logging
log = logging.getLogger('bq.image_service.converter_openslide')

################################################################################
# ConverterImaris
################################################################################

class ConverterOpenSlide(ConverterBase):
    installed = False
    version = None
    installed_formats = None
    extensions = None
    name = 'openslide'
    required_version = '0.5.1'

#     #######################################
#     # Init
#     #######################################
#
#     @classmethod
#     def init(cls):
#         #ConverterBase.init.im_func(cls)
#         ConverterBase.init(cls)
#         cls.get_formats()

    #######################################
    # Version and Installed
    #######################################

    @classmethod
    def get_version (cls):
        '''returns the version of openslide python'''
        try:
            import openslide
        except (ImportError, OSError):
            return None

        v = {}
        v['full'] = openslide.__version__

        if 'full' in v:
            d = [int(s) for s in v['full'].split('.')]
            if len(d)>2:
                v['numeric'] = d
                v['major']   = d[0]
                v['minor']   = d[1]
                v['build']   = d[2]
        return v

    #######################################
    # Formats
    #######################################

    @classmethod
    def get_formats(cls):
        '''inits supported file formats'''
        if cls.installed_formats is not None:
            return

        cls.extensions = ['.svs', '.ndpi', '.vms', '.vmu', '.scn', '.mrxs', '.svslide', '.bif']

        # Many extensions may unfortunately be .tif, we'll have to deal with that later
        cls.installed_formats = OrderedDict()
        cls.installed_formats['aperio']    = Format(name='aperio', fullname='Aperio', ext=['svs','tif','tiff'], reading=True, multipage=False, metadata=True) # tif
        cls.installed_formats['hamamatsu'] = Format(name='hamamatsu', fullname='Hamamatsu', ext=['ndpi','vms','vmu'], reading=True, multipage=False, metadata=True)
        cls.installed_formats['leica']     = Format(name='leica', fullname='Leica', ext=['scn'], reading=True, multipage=False, metadata=True)
        cls.installed_formats['mirax']     = Format(name='mirax', fullname='MIRAX', ext=['mrxs'], reading=True, multipage=False, metadata=True)
        cls.installed_formats['philips']   = Format(name='philips', fullname='Philips', ext=['tiff'], reading=True, multipage=False, metadata=True)
        cls.installed_formats['sakura']    = Format(name='sakura', fullname='Sakura', ext=['svslide'], reading=True, multipage=False, metadata=True)
        cls.installed_formats['trestle']   = Format(name='trestle', fullname='Trestle', ext=['tif'], reading=True, multipage=False, metadata=True)
        cls.installed_formats['ventana']   = Format(name='ventana', fullname='Ventana', ext=['bif', 'tif'], reading=True, multipage=False, metadata=True)
        cls.installed_formats['tiff']      = Format(name='tiff', fullname='Generic tiled TIFF', ext=['tif','tiff'], reading=True, multipage=False, metadata=True)

    #######################################
    # Supported
    # we skip generic tiff support from openslide to use imageconvert
    # openslide recognizes OME-TIFF as generic tiff and also does not read >3 channels
    # as well as saves images with >8 bits as 8 bits
    # therefore we skip openslide in favour of imgcnv: it's faster and supports all the aforementioned types
    #######################################

    @classmethod
    def supported(cls, token, **kw):
        '''return True if the input file format is supported'''
        if not cls.installed:
            return False
        #return False #!!! TODO: re-enable
        ifnm = token.first_input_file()
        log.debug('Supported for: %s', ifnm )
        #if token.is_multifile_series() is True:
        #    return False

        try:
            _, tmp = misc.start_nounicode_win(ifnm, [])
            s = openslide.OpenSlide.detect_format(tmp or ifnm)
        except (openslide.OpenSlideUnsupportedFormatError, openslide.OpenSlideError):
            s = None
        misc.end_nounicode_win(tmp)
        return (s is not None and s != 'generic-tiff')
        #return (s is not None)

    #######################################
    # The info command returns the "core" metadata (width, height, number of planes, etc.)
    # as a dictionary
    #######################################

    @classmethod
    def info(cls, token, **kw):
        '''returns a dict with file info'''
        ifnm = token.first_input_file()
        series = token.series
        if not cls.supported(token):
            return {}
        log.debug('Info for: %s', ifnm )
        with Locks(ifnm, failonread=(not block_reads)) as l:
            if l.locked is False: # dima: never wait, respond immediately
                raise ImageServiceFuture((1,10))
            if not os.path.exists(ifnm):
                return {}
            try:
                _, tmp = misc.start_nounicode_win(ifnm, [])
                slide = openslide.OpenSlide(tmp or ifnm)
            except (openslide.OpenSlideUnsupportedFormatError, openslide.OpenSlideError):
                misc.end_nounicode_win(tmp)
                return {}

            info2 = {
                'format': slide.properties[openslide.PROPERTY_NAME_VENDOR],
                'image_num_series': 0,
                'image_series_index': 0,
                'image_num_x': slide.dimensions[0],
                'image_num_y': slide.dimensions[1],
                'image_num_z': 1,
                'image_num_t': 1,
                'image_num_c': 3,
                'image_num_resolution_levels': slide.level_count,
                'image_resolution_level_scales': ','.join([str(1.0/i) for i in slide.level_downsamples]),
                'image_pixel_format': 'unsigned integer',
                'image_pixel_depth': 8
            }

            if slide.properties.get(openslide.PROPERTY_NAME_MPP_X, None) is not None:
                info2.update({
                    'pixel_resolution_x': slide.properties.get(openslide.PROPERTY_NAME_MPP_X, 0),
                    'pixel_resolution_y': slide.properties.get(openslide.PROPERTY_NAME_MPP_Y, 0),
                    'pixel_resolution_unit_x': 'microns',
                    'pixel_resolution_unit_y': 'microns'
                })
            slide.close()

            # read metadata using imgcnv since openslide does not decode all of the info
            info = ConverterImgcnv.info(ProcessToken(ifnm=tmp or ifnm, series=series), **kw)
            misc.end_nounicode_win(tmp)
            info.update(info2)
            return info
        return {}

    #######################################
    # Meta - returns a dict with all the metadata fields
    #######################################

    @classmethod
    def meta(cls, token, **kw):
        ifnm = token.first_input_file()
        if not cls.supported(token):
            return {}
        log.debug('Meta for: %s', ifnm )
        with Locks(ifnm, failonread=(not block_reads)) as l:
            if l.locked is False: # dima: never wait, respond immediately
                raise ImageServiceFuture((1,10))
            try:
                _, tmp = misc.start_nounicode_win(ifnm, [])
                slide = openslide.OpenSlide(tmp or ifnm)
            except (openslide.OpenSlideUnsupportedFormatError, openslide.OpenSlideError):
                misc.end_nounicode_win(tmp)
                return {}
            rd = {
                'format': slide.properties.get(openslide.PROPERTY_NAME_VENDOR),
                'image_num_series': 0,
                'image_num_x': slide.dimensions[0],
                'image_num_y': slide.dimensions[1],
                'image_num_z': 1,
                'image_num_t': 1,
                'image_num_c': 3,
                'image_num_resolution_levels': slide.level_count,
                'image_resolution_level_scales': ','.join([str(1.0/i) for i in slide.level_downsamples]),
                'image_pixel_format': 'unsigned integer',
                'image_pixel_depth': 8,
                'magnification': slide.properties.get(openslide.PROPERTY_NAME_OBJECTIVE_POWER),
                'channel_0_name': 'red',
                'channel_1_name': 'green',
                'channel_2_name': 'blue',
                'channel_color_0': '255,0,0',
                'channel_color_1': '0,255,0',
                'channel_color_2': '0,0,255',
                # new format
                'channels/channel_00000/name' : 'red',
                'channels/channel_00000/color': '255,0,0',
                'channels/channel_00001/name' : 'green',
                'channels/channel_00001/color': '0,255,0',
                'channels/channel_00002/name' : 'blue',
                'channels/channel_00002/color': '0,0,255',
            }

            if slide.properties.get(openslide.PROPERTY_NAME_MPP_X, None) is not None:
                rd.update({
                    'pixel_resolution_x': slide.properties.get(openslide.PROPERTY_NAME_MPP_X, 0),
                    'pixel_resolution_y': slide.properties.get(openslide.PROPERTY_NAME_MPP_Y, 0),
                    'pixel_resolution_unit_x': 'microns',
                    'pixel_resolution_unit_y': 'microns'
                })

            # custom - any other tags in proprietary files should go further prefixed by the custom parent
            for k,v in slide.properties.iteritems():
                rd['custom/%s'%k.replace('.', '/')] = v
            slide.close()

            # read metadata using imgcnv since openslide does not decode all of the info
            meta = ConverterImgcnv.meta(ProcessToken(ifnm=tmp or ifnm, series=token.series), **kw)
            meta.update(rd)
            rd = meta

            misc.end_nounicode_win(tmp)
        return rd

    #######################################
    # Conversion
    #######################################

    @classmethod
    def convert(cls, token, ofnm, fmt=None, extra=None, **kw):
        return None

    @classmethod
    def convertToOmeTiff(cls, token, ofnm, extra=None, **kw):
        return None

    @classmethod
    def thumbnail(cls, token, ofnm, width, height, **kw):
        '''converts input filename into output thumbnail'''
        ifnm = token.first_input_file()
        series = token.series
        if not cls.supported(token):
            return None
        log.debug('Thumbnail: %s %s %s for [%s]', width, height, series, ifnm)

        fmt = kw.get('fmt', 'jpeg').upper()
        with Locks (ifnm, ofnm, failonexist=True) as l:
            if l.locked: # the file is not being currently written by another process
                try:
                    _, tmp = misc.start_nounicode_win(ifnm, [])
                    slide = openslide.OpenSlide(tmp or ifnm)
                except (openslide.OpenSlideUnsupportedFormatError, openslide.OpenSlideError):
                    misc.end_nounicode_win(tmp)
                    return None
                img = slide.get_thumbnail((width, height))
                try:
                    img.save(ofnm, fmt)
                except IOError:
                    tmp = '%s.tif'%ofnm
                    img.save(tmp, 'TIFF')
                    ConverterImgcnv.thumbnail(ProcessToken(ifnm=tmp), ofnm=ofnm, width=width, height=height, **kw)
                slide.close()
                misc.end_nounicode_win(tmp)
            elif l.locked is False: # dima: never wait, respond immediately
                raise ImageServiceFuture((1,15))

        # make sure the file was written
        with Locks(ofnm, failonread=(not block_reads)) as l:
            if l.locked is False: # dima: never wait, respond immediately
                raise ImageServiceFuture((1,15))
        return ofnm

    @classmethod
    def slice(cls, token, ofnm, z, t, roi=None, **kw):
        '''extract Z,T plane from input filename into output in OME-TIFF format'''
        return None

    @classmethod
    def tile(cls, token, ofnm, level=None, x=None, y=None, sz=None, **kw):
        '''extract tile from image
        default interface:
            Level,X,Y tile from input filename into output in TIFF format
        alternative interface, not required to support and may return None in this case
        scale=scale, x1=x1, y1=y1, x2=x2, y2=y2, arbitrary_size=False '''

        # open slide driver does not support arbitrary size interface
        if kw.get('arbitrary_size', False) == True or level is None or sz is None:
            return None

        ifnm = token.first_input_file()
        series = token.series
        if not cls.supported(token):
            return None
        log.debug('Tile: %s %s %s %s %s for [%s]', level, x, y, sz, series, ifnm)

        level = misc.safeint(level, 0)
        x  = misc.safeint(x, 0)
        y  = misc.safeint(y, 0)
        sz = misc.safeint(sz, 0)
        with Locks (ifnm, ofnm, failonexist=True) as l:
            if l.locked: # the file is not being currently written by another process
                try:
                    _, tmp = misc.start_nounicode_win(ifnm, [])
                    slide = openslide.OpenSlide(tmp or ifnm)
                    dz = deepzoom.DeepZoomGenerator(slide, tile_size=sz, overlap=0)
                    img = dz.get_tile(dz.level_count-level-1, (x,y))
                    img.save(ofnm, 'TIFF', compression='LZW')
                    slide.close()
                    misc.end_nounicode_win(tmp)
                except (openslide.OpenSlideUnsupportedFormatError, openslide.OpenSlideError):
                    misc.end_nounicode_win(tmp)
                    return None

        # make sure the file was written
        with Locks(ofnm, failonread=(not block_reads)) as l:
            if l.locked is False: # dima: never wait, respond immediately
                raise ImageServiceFuture((1,15))
        return ofnm

    @classmethod
    def writeHistogram(cls, token, ofnm, **kw):
        '''writes Histogram in libbioimage format'''
        if not cls.supported(token):
            return None
        ifnm = token.first_input_file()
        log.debug('Writing histogram for %s into: %s', ifnm, ofnm )

        # estimate best level for histogram approximation
        preferred_side = 1024
        dims = token.dims or {}
        num_x = int(dims.get('image_num_x', 0))
        num_y = int(dims.get('image_num_y', 0))
        width = preferred_side
        height = preferred_side

        #scales = [float(i) for i in dims.get('image_resolution_level_scales', '').split(',')]
        # scales metadata is provided according to original data storage, not deepzoom virtual view
        sz = max(num_x, num_y)
        num_levels = int(round(math.ceil(math.log(sz, 2)) - math.ceil(math.log(min_level_size, 2)) + 1))
        scales = [1/float(pow(2,i)) for i in range(0, num_levels)]

        log.debug('scales: %s',  scales)
        sizes = [(round(num_x*i),round(num_y*i)) for i in scales]
        log.debug('scales: %s',  sizes)
        relatives = [max(width/float(sz[0]), height/float(sz[1])) for sz in sizes]
        log.debug('relatives: %s',  relatives)
        relatives = [i if i>=1 else 1000000 for i in relatives] # only allow levels containing entire blocks
        log.debug('relatives: %s',  relatives)
        level = relatives.index(min(relatives))
        log.debug('Chosen level: %s', level)

        # extract desired level and compute histogram
        try:
            _, tmp = misc.start_nounicode_win(ifnm, [])
            slide = openslide.OpenSlide(tmp or ifnm)
            dz = deepzoom.DeepZoomGenerator(slide, tile_size=preferred_side, overlap=0)
            img = dz.get_tile(dz.level_count-level-1, (0,0))
            slide.close()
            misc.end_nounicode_win(tmp)
            hist = img.histogram()
        except (openslide.OpenSlideUnsupportedFormatError, openslide.OpenSlideError):
            misc.end_nounicode_win(tmp)

        log.debug('histogram: %s', hist)

        # currently openslide only supports 8 bit 3 channel images
        # need to generate a histogram file uniformly distributed from 0..255
        channels = 3
        i = 0
        import struct
        with open(ofnm, 'wb') as f:
            f.write(struct.pack('<cccc', 'B', 'I', 'M', '1')) # header
            f.write(struct.pack('<cccc', 'I', 'H', 'S', '1')) # spec
            f.write(struct.pack('<L', channels)) # number of histograms
            # write histograms
            for c in range(channels):
                f.write(struct.pack('<cccc', 'B', 'I', 'M', '1')) # header
                f.write(struct.pack('<cccc', 'H', 'S', 'T', '1')) # spec

                # write bim::HistogramInternal
                f.write(struct.pack('<H', 8)) # uint16 data_bpp; // bits per pixel
                f.write(struct.pack('<H', 1)) # uint16 data_fmt; // signed, unsigned, float
                f.write(struct.pack('<d', 0.0)) # double shift;
                f.write(struct.pack('<d', 1.0)) # double scale;
                f.write(struct.pack('<d', 0.0)) # double value_min;
                f.write(struct.pack('<d', 255.0)) # double value_max;

                # write data
                f.write(struct.pack('<L', 256)) # histogram size, here 256
                for i in range(256):
                    f.write(struct.pack('<Q', hist[i])) # histogram data, here each color has freq of 100
        return ofnm

try:
    ConverterOpenSlide.init()
except Exception:
    log.warn("Openslide Unavailable")
