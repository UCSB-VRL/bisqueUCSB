""" FFMPEG command line converter
"""

__Contributors__    = "Mike Goebel"
__version__   = "0.0"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import logging
from lxml import etree

from bq.util.locks import Locks
from bq.image_service.controllers.converter_base import ConverterBase, Format
from bq.util.compat import OrderedDict
from bq.image_service.controllers.exceptions import ImageServiceException, ImageServiceFuture
import subprocess
import json
import inspect
import shutil

log = logging.getLogger('bq.image_service.converter_ffmpeg')


supported_formats = [
    ('MP4', 'MPEG4', ['mp4']),
    ('AVI', 'Microsoft AVI', ['avi']),
    ('WEBM', 'WEBM', ['webm',]),
    ('MOV', 'QuickTime Movie', ['mov']),
]



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



class ConverterFfmpeg(ConverterBase):
    # All of this metadata on the converter is made up, should be fixed at some point
    # if this code becomes a significant part of bisqueConverterImgcnv
    installed = True
    version = [1,2,3]
    installed_formats = None
    name = 'ffmpeg'
    required_version = '0.0.0'

    @classmethod
    def get_version(cls):
        return {
            'full': '.'.join([str(i) for i in cls.version]),
            'numeric': cls.version,
            'major': cls.version[0],
            'minor': cls.version[1],
            'build': cls.version[2],
        }

    @classmethod
    def get_formats(cls):
        try:
            cls.installed_formats = OrderedDict()
            for name, fullname, exts in supported_formats:
                cls.installed_formats[name.lower()] = Format(
                name=name,
                fullname=fullname,  
                ext=exts,
                reading=True,
                writing=True,
                multipage=True,
                metadata=True,
                samples=(0,0),
                bits=(8,8)
                )
        except Exception as e:
            log.info("Get formats failed with error " + str(e))
        return cls.installed_formats

    @classmethod
    def get_installed(cls):
        return True

    @classmethod
    def supported(cls, token, **kw):
        '''return True if the input file format is supported'''
        ifnm = token.first_input_file()
        all_exts = set()
        for fmt in supported_formats:
            all_exts.add(*fmt[2])
        return (ifnm.split('.')[-1].lower() in all_exts)



    @classmethod
    def convert(cls, token, ofnm, fmt=None, extra=None, **kw):
        ifnm = token.first_input_file()
        with Locks(ifnm, ofnm, failonexist=True) as l:
            if l.locked:
                #log.info('\n\n\n\nConverting video1:\n\n\n\n')
                ifnm = token.first_input_file()
                imw = token.dims['image_num_x']
                imh = token.dims['image_num_y']
                ##log.info('\n\n\n\nConverting video2:\n\n\n\n')
                ind_rs = [i for i, v in enumerate(extra) if v == '-resize']
                resize = True
                if len(ind_rs) != 1:
                    resize = False
                else:
                    #log.info('\n\n\n\nConverting video2.6:\n\n\n\n')
                    rs_string = extra[ind_rs[0]+1]
                    width, height = [int(i) for i in rs_string.split(',')[:2]]

                    #ind_rs = ind_rs[0] + 1
                    
                #log.info('\n\n\n\nConverting video3:\n\n\n\n')
                
                if resize:
                    w_out, h_out = compute_new_size(imw, imh, width, height,
                        keep_aspect_ratio=True, no_upsample=True)
                    cmd = ['ffmpeg', '-y', '-hide_banner', '-threads', '4', '-loglevel', 'error', '-i', ifnm, '-vf',
                            'scale=' + str(w_out) + ':' + str(h_out), ofnm]
                else:
                    cmd = ['ffmpeg', '-y', '-hide_banner', '-threads', '4', '-loglevel', 'error', '-i', ifnm, ofnm]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                output, error = process.communicate()

                if error is not None:
                    return None

                return ofnm

            elif l.locked is False:
                raise ImageServiceFuture((1,15))

    @classmethod
    def thumbnail(cls, token, ofnm, width, height, **kw):
        ifnm = token.first_input_file()
        with Locks(ifnm, ofnm, failonexist=True) as l:
            if l.locked is False:
                raise ImageServiceFuture((1,15))
            #log.info('Creating thumbnail:')
            
            ifnm = token.first_input_file()
            imw = token.dims['image_num_x']
            imh = token.dims['image_num_y']


            w_out, h_out = compute_new_size(imw, imh, width, height,
                    keep_aspect_ratio=True, no_upsample=True)


            cmd = ['ffmpeg', '-y', '-hide_banner', '-threads', '1','-loglevel', 'error', '-i', ifnm,
                    '-vframes', '1', '-s', str(w_out) + 'x' + str(h_out), ofnm]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output, error = process.communicate()

            if error is not None:
                return None

            return ofnm

    @classmethod
    def slice(cls, token, ofnm, z, t, roi=None, **kw):
        ifnm = token.first_input_file()
        with Locks(ifnm, ofnm, failonexist=True) as l:
            if l.locked is False:
                raise ImageServiceFuture((1,15))
            
            #log.info('Creating slice:')
            cmd = ['ffmpeg', '-y', '-hide_banner', '-threads', '1', '-loglevel', 'error',  '-i', ifnm,
                    '-vf', 'select=eq(n\\,' + str(t[0]-1) + ')', '-vframes', '1',
                    '-compression_algo', 'raw', '-pix_fmt', 'rgb24', ofnm]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output, error = process.communicate()

            if error is not None:
                return None

            return ofnm


    @classmethod
    def tile(cls, token, ofnm, level, x, y, sz, **kw):
        return None

    @classmethod
    def info(cls, token, **kw):
        
        ifnm = token.first_input_file()
        if not cls.supported(token):
            return None

        with Locks(ifnm, failonread=(True)) as l:
            if l.locked is False:
                raise ImageServiceFuture((1,15))

            cmd = ['ffprobe', '-hide_banner', '-threads', '4', '-loglevel', 'quiet', '-print_format',
                    'json', '-show_format', '-show_streams', '-i',
                    ifnm]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            output, error = process.communicate()

            if error is not None:
                return dict()

            data = json.loads(output)

            if 'streams' not in data.keys():
                return dict()

            if 'format' not in data.keys():
                return dict()

            vid_stream = [s for s in data['streams'] if s['codec_type']=='video'][0]
            f_format = data['format']

            try:
                cmd = ['file', ifnm]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                output, error = process.communicate()
                endian = output.decode().split('(')[1].split('-')[0]

            except Exception as e:
                endian = 'little'

            out_dict = dict()
            out_dict['image_num_x'] = vid_stream['width']
            out_dict['image_num_y'] = vid_stream['height']
            out_dict['image_num_z'] = 1
            out_dict['converter'] = 'ffmpeg'
            out_dict['format'] = f_format['format_name']
            out_dict['image_num_resolution_levels'] = 0
            out_dict['raw_endian'] = endian
            out_dict['image_pixel_depth'] = 8
            out_dict['image_pixel_format'] = 'unsigned integer'
            out_dict['image_mode'] = 'RGB'
            out_dict['image_series_index'] = 0
            out_dict['image_num_p'] = 1
            out_dict['image_num_c'] = 3
            out_dict['image_num_series'] = 0
            out_dict['filesize'] = f_format['size']
            #log.info("FOOBAR " + str(f_format) + '\n\n' + str(vid_stream))
            if 'nb_frames' in vid_stream.keys():
                out_dict['image_num_t'] = vid_stream['nb_frames']
            else:
                duration = float(f_format['duration'])
                frame_rate = float(float(vid_stream['avg_frame_rate'].split('/')[0]) / float(vid_stream['avg_frame_rate'].split('/')[1]))
                out_dict['image_num_t'] = int(duration*frame_rate)

            return out_dict


    def meta(cls, token, **kw):
        return cls.info(token, **kw)


try:
    ConverterFfmpeg.init()
except Exception:
    log.warn("FFMPEG not available")



