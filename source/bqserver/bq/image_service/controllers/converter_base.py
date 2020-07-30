""" Base class defining command line converter API
"""

from __future__ import with_statement

__author__    = "Dmitry Fedorov"
__version__   = "0.1"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import os.path
from subprocess import call
#from collections import OrderedDict
from bq.util.compat import OrderedDict
from itertools import groupby
from bq.util.locks import Locks
import bq.util.io_misc as misc
import bq.util.responses as responses

from .exceptions import ImageServiceException, ImageServiceFuture
from .process_token import ProcessToken
from .defaults import default_format, default_tile_size, block_reads

import logging
log = logging.getLogger('bq.image_service.converter')

################################################################################
# Format - the definition of a format
################################################################################

class Format(object):

    def __init__(self, name='', fullname='', ext=[], reading=False, writing=False, multipage=False, metadata=False, samples=(0,0), bits=(0,0)):
        self.name      = name
        self.fullname  = fullname
        self.ext       = ext
        self.reading   = reading
        self.writing   = writing
        self.multipage = multipage
        self.metadata  = metadata
        self.samples_per_pixel_min_max = samples
        self.bits_per_sample_min_max   = bits

    def supportToString(self):
        s = []
        if self.reading   is True:
            s.append('reading')
        if self.writing   is True:
            s.append('writing')
        if self.multipage is True:
            s.append('multipage')
        if self.metadata  is True:
            s.append('metadata')
        return ','.join(s)

################################################################################
# ConverterBase
################################################################################

class ConverterBase(object):
    name = 'base_converter'
    required_version = '0.0.0'
    installed = False
    version = None
    installed_formats = None # OrderedDict containing Format and keyed by format name
    CONVERTERCOMMAND = 'convert' if os.name != 'nt' else 'convert.exe'
    MINIMUM_FILE_SIZE = 16

    #######################################
    # Init
    #######################################

    #@staticmethod
    @classmethod
    def init(cls):
        cls.version = cls.get_version()
        cls.installed = cls.get_installed()
        if cls.installed is not False:
            cls.get_formats()

    #######################################
    # Version and Installed
    #######################################

    # overwrite with appropriate implementation
    @classmethod
    def get_version (cls):
        '''returns the version of command line utility'''
        return {
            'full': '0.0.0',
            'numeric': [0,0,0],
            'major': 0,
            'minor': 0,
            'build': 0,
        }

    @classmethod
    def get_installed (cls):
        '''Returns true if converter is installed'''
        if cls.version is not None and 'full' in cls.version:
            if not cls.ensure_version(cls.required_version):
                log.warning('%s needs update! Has: %s Needs: %s', cls.name, cls.version['full'], cls.required_version)
            else:
                return True
        return False

    @classmethod
    def check_version ( cls, needed ):
        '''checks if converter is of proper version'''
        if cls.version is None or not 'numeric' in cls.version:
            return False
        if isinstance(needed, str):
            needed = [int(s) for s in needed.split('.')]
        has = cls.version['numeric']
        return needed <= has

    @classmethod
    def ensure_version ( cls, needed ):
        '''checks if converter is of proper version and sets installed to false if its older'''
        cls.installed = cls.check_version ( needed )
        return cls.installed

    #######################################
    # Formats
    #######################################

    # overwrite with appropriate implementation
    @classmethod
    def get_formats(cls):
        '''inits supported file formats'''
        if cls.installed_formats is None:
            cls.installed_formats = OrderedDict() # OrderedDict containing Format and keyed by format name

    @classmethod
    def formats(self):
        '''return the XML with supported file formats'''
        return self.installed_formats

    #######################################
    # Supported
    #######################################

    # overwrite with appropriate implementation
    @classmethod
    def supported(cls, token, **kw):
        '''return True if the input file format is supported'''
        ifnm = token.first_input_file()
        return False


    #######################################
    # Meta - returns a dict with all the metadata fields
    #######################################

    # overwrite with appropriate implementation
    @classmethod
    def meta(cls, token, **kw):
        '''returns a dict with file metadata'''
        ifnm = token.first_input_file()
        series = token.series
        return {}

    #######################################
    # The info command returns the "core" metadata (width, height, number of planes, etc.)
    # as a dictionary
    #######################################

    # overwrite with appropriate implementation
    @classmethod
    def info(cls, token, **kw):
        '''returns a dict with file info'''
        ifnm = token.first_input_file()
        series = token.series
        if not cls.installed:
            return {}
        if not os.path.exists(ifnm):
            return {}

        rd = cls.meta(token)
        core = [ 'image_num_series', 'image_num_x', 'image_num_y', 'image_num_z', 'image_num_c', 'image_num_t',
                 'image_pixel_format', 'image_pixel_depth',
                 'pixel_resolution_x', 'pixel_resolution_y', 'pixel_resolution_z',
                 'pixel_resolution_unit_x', 'pixel_resolution_unit_y', 'pixel_resolution_unit_z' ]

        #return {k:v for k,v in rd.iteritems() if k in core}
        return dict ( (k,v) for k,v in rd.iteritems() if k in core)

    #######################################
    # Conversion
    #######################################

    @classmethod
    def run_command(cls, command ):
        return misc.run_command( command )

    @classmethod
    def run_read(cls, ifnm, command ):
        with Locks(ifnm, failonread=(not block_reads)) as l:
            if l.locked is False: # dima: never wait, respond immediately
                raise ImageServiceFuture((1,10))
            command, tmp = misc.start_nounicode_win(ifnm, command)
            log.debug('run_read command: [%s]', misc.toascii(command))
            out = cls.run_command( command )
            misc.end_nounicode_win(tmp)
        return out

    @classmethod
    def run(cls, ifnm, ofnm, args, **kw ):
        '''converts input filename into output using exact arguments as provided in args'''
        if not cls.installed:
            return None
        failonread = kw.get('failonread') or (not block_reads)
        tmp = None
        with Locks(ifnm, ofnm, failonexist=True) as l:
            if l.locked: # the file is not being currently written by another process
                command = [cls.CONVERTERCOMMAND]
                command.extend(args)
                log.debug('Run command: [%s]', misc.toascii(command))
                proceed = True
                if ofnm is not None and os.path.exists(ofnm) and os.path.getsize(ofnm)>16:
                    if kw.get('nooverwrite', False) is True:
                        proceed = False
                        log.warning ('Run: output exists before command [%s], skipping', misc.toascii(ofnm))
                    else:
                        log.warning ('Run: output exists before command [%s], overwriting', misc.toascii(ofnm))
                if proceed is True:
                    command, tmp = misc.start_nounicode_win(ifnm, command)
                    try:
                        retcode = call (command)
                    except Exception:
                        retcode = 100
                        log.exception('Error running command: %s', command)
                    misc.end_nounicode_win(tmp)
                    if retcode == 99:
                        # in case of a timeout
                        log.info ('Run: timed-out for [%s]', misc.toascii(command))
                        if ofnm is not None and os.path.exists(ofnm):
                            os.remove(ofnm)
                        raise ImageServiceException(412, 'Requested timeout reached')
                    if retcode!=0:
                        log.info ('Run: returned [%s] for [%s]', retcode, misc.toascii(command))
                        return None
                    if ofnm is None:
                        return str(retcode)
                    # output file does not exist for some operations, like tiles
                    # tile command does not produce a file with this filename
                    # if not os.path.exists(ofnm):
                    #     log.error ('Run: output does not exist after command [%s]', ofnm)
                    #     return None
            elif l.locked is False: # dima: never wait, respond immediately
                raise ImageServiceFuture((1,15))

        # make sure the write of the output file have finished
        if ofnm is not None and os.path.exists(ofnm):
            with Locks(ofnm, failonread=failonread) as l:
                if l.locked is False: # dima: never wait, respond immediately
                    raise ImageServiceFuture((1,15))

        # safeguard for incorrectly converted files, sometimes only the tiff header can be written
        # empty lock files are automatically removed before by lock code
        if os.path.exists(ofnm) and os.path.getsize(ofnm) < cls.MINIMUM_FILE_SIZE:
            log.error ('Run: output file is smaller than %s bytes, probably an error, removing [%s]', cls.MINIMUM_FILE_SIZE, ofnm)
            os.remove(ofnm)
            return None
        return ofnm

    @classmethod
    def convert(cls, token, ofnm, fmt=None, extra=None, **kw):
        '''converts a file and returns output filename'''
        command = ['-input', token.input]
        if ofnm is not None:
            command.extend (['-output', ofnm])
        if fmt is not None:
            command.extend (['-format', fmt])
        if token.series is not None:
            command.extend (['-series', str(token.series)])
        #command.extend (extra)
        return cls.run( token.input, ofnm, command )

    # overwrite with appropriate implementation
    @classmethod
    def convertToOmeTiff(cls, token, ofnm, extra=None, **kw):
        '''converts input filename into output in OME-TIFF format'''
        ifnm = token.first_input_file()
        series = token.series
        return cls.run(ifnm, ofnm, ['-input', ifnm, '-output', ofnm, '-format', 'OmeTiff', '-series', '%s'%series] )

    # overwrite with appropriate implementation
    @classmethod
    def thumbnail(cls, token, ofnm, width, height, **kw):
        '''converts input filename into output thumbnail'''
        ifnm = token.first_input_file()
        series = token.series
        return cls.run(ifnm, ofnm, ['-input', ifnm, '-output', ofnm, '-format', 'jpeg', '-series', '%s'%series, '-thumbnail'] )

    # overwrite with appropriate implementation
    @classmethod
    def slice(cls, token, ofnm, z, t, roi=None, **kw):
        '''extract Z,T plane from input filename into output in OME-TIFF format'''
        #z1,z2 = z
        #t1,t2 = t
        #x1,x2,y1,y2 = roi
        ifnm = token.first_input_file()
        series = token.series
        return cls.run(ifnm, ofnm, ['-input', ifnm, '-output', ofnm, '-format', 'OmeTiff', '-series', '%s'%series, 'z', '%s'%z, 't', '%s'%t] )

    @classmethod
    def tile(cls, token, ofnm, level=None, x=None, y=None, sz=None, **kw):
        '''extract tile from image
        default interface:
            Level,X,Y tile from input filename into output in TIFF format
        alternative interface, not required to support and may return None in this case
        scale=scale, x1=x1, y1=y1, x2=x2, y2=y2, arbitrary_size=False '''
        ifnm = token.first_input_file()
        series = token.series
        return cls.run(ifnm, ofnm, ['-input', ifnm, '-output', ofnm, '-format', 'tiff', '-series', '%s'%series, '-tile'] )

    @classmethod
    def writeHistogram(cls, token, ofnm, **kw):
        '''export histogram for a file with tiles'''
        ifnm = token.first_input_file()
        series = token.series
        return cls.run(ifnm, ofnm, ['-input', ifnm, '-output', ofnm, '-format', 'tiff', '-series', '%s'%series, '-histogram'] )


#ConverterBase.init()
