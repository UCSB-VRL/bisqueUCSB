""" Token passed between image service operations
"""

__author__    = "Dmitry Fedorov"
__version__   = "0.1"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import os
#from collections import OrderedDict
from bq.util.compat import OrderedDict

import logging
log = logging.getLogger('bq.image_service.token')

################################################################################
# ProcessToken
################################################################################

mime_types = {
    'html'      : 'text/html',
    'xml'       : 'text/xml',
    'file'      : 'application/octet-stream',
    'flash'     : 'application/x-shockwave-flash',
    'flv'       : 'video/x-flv',
    'avi'       : 'video/avi',
    'quicktime' : 'video/quicktime',
    'wmv'       : 'video/x-ms-wmv',
    'matroska'  : 'video/x-matroska',
    'webm'      : 'video/webm',
    'h264'      : 'video/mp4',
    'h265'      : 'video/mp4',
    'mpeg4'     : 'video/mp4',
    'ogg'       : 'video/ogg',
    #'jxr'       : 'image/jxr',
    #'webp'      : 'image/webp',
}

cache_info = {
    'no'    : 'no-cache',
    'day'   : 'max-age=86400',
    'days2' : 'max-age=172800',
    'week'  : 'max-age=604800',
    'month' : 'max-age=2629743',
    'year'  : 'max-age=31557600',
}

class ProcessToken(object):
    'Keep data with correct content type and cache info'

    def __str__(self):
        n = len(self.input) if isinstance(self.input, list) else 1
        return 'ProcessToken(data: %s, %s inputs: %s, dims: %s)'%(self.data, n, self.first_input_file(), self.dims)

    def __init__(self, ifnm=None, series=0):
        self.data        = None
        self.contentType = ''
        self.cacheInfo   = ''
        self.outFileName = ''
        self.httpResponseCode = 200
        self.dims        = None
        self.histogram   = None
        self.is_file     = False
        self.timeout     = None
        self.resource_name = None
        self.initial_workpath = None
        self.dryrun      = None

        #queue
        self.meta        = None
        self.resource_id = None
        self.format      = None
        self.series      = series
        self.input       = ifnm # output is in .data
        self.queue       = []

    def init(self, resource_id=None, ifnm=None, fmt=None, series=0, imagemeta=None, files=None, timeout=None, dims=None, resource_name=None, initial_workpath=None, dryrun=None):
        self.resource_id = resource_id or self.resource_id
        self.resource_name = resource_name
        self.format      = fmt or self.format
        self.series      = series or self.series
        self.timeout     = timeout or self.timeout
        self.meta        = imagemeta or self.meta
        self.dims        = dims or self.dims
        self.input       = ifnm or self.input
        self.initial_workpath = initial_workpath or self.initial_workpath
        self.queue       = []
        self.dryrun      = dryrun
        if files is not None and self.meta is not None:
            if len(files)>1 and len(set(['image_num_z','image_num_t','image_num_c']).intersection(self.meta.keys()))>0:
                self.input = files

    def setData (self, data_buf, content_type):
        self.data = data_buf
        self.contentType = content_type
        self.cacheInfo = cache_info['month']
        self.series = 0
        return self

    def setHtml (self, text):
        self.data = text
        self.contentType = mime_types['html']
        self.cacheInfo = cache_info['no']
        self.is_file = False
        self.series = 0
        return self

    def setXml (self, xml_str):
        self.data = xml_str
        self.contentType = mime_types['xml']
        self.cacheInfo = cache_info['week']
        self.is_file = False
        self.series = 0
        return self

    def setXmlFile (self, fname):
        self.data = fname
        self.contentType = 'text/xml'
        self.cacheInfo = cache_info['week']
        self.is_file = True
        self.series = 0
        return self

    def setFormat (self, fmt):
        fmt = fmt.lower()
        # mime types
        if fmt in mime_types:
            self.contentType = mime_types[fmt]
        else:
            self.contentType = 'image/' + fmt
            if fmt.startswith('mpeg'):
                self.contentType = 'video/mpeg'
        self.cacheInfo = cache_info['month']
        return self

    def setImage (self, fname, fmt, series=0, meta=None, dims=None, input=None, hist=None, queue=None, **kw):
        self.data = fname
        self.is_file = True
        self.series = series
        self.meta = meta
        self.input = input or self.input
        self.setFormat(fmt)

        if self.dims is None:
            self.dims = {}
        self.dims['format'] = fmt
        if dims is not None:
            self.dims.update(dims)

        # histogram
        self.histogram = hist

        if queue is not None:
            self.queue = queue

        # cache
        self.cacheInfo = cache_info['month']

        return self

    def setFile (self, fname, series=0):
        self.data = fname
        self.is_file = True
        self.series = series
        self.contentType = mime_types['file']
        self.cacheInfo = cache_info['year']
        return self

    def setNone (self):
        self.data = None
        self.is_file = False
        self.series = 0
        self.contentType = ''
        return self

    def setHtmlErrorUnauthorized (self):
        self.data = 'Permission denied...'
        self.is_file = False
        self.contentType = mime_types['html']
        self.cacheInfo = cache_info['no']
        self.httpResponseCode = 401
        return self

    def setHtmlErrorNotFound (self):
        self.data = 'File not found...'
        self.is_file = False
        self.contentType = mime_types['html']
        self.cacheInfo = cache_info['no']
        self.httpResponseCode = 404
        return self

    def setHtmlErrorNotSupported (self):
        self.data = 'File is not in supported image format...'
        self.is_file = False
        self.contentType = mime_types['html']
        self.cacheInfo = cache_info['no']
        self.httpResponseCode = 415
        return self

    def isValid (self):
        return self.data is not None

    def isImage (self):
        if self.contentType.startswith('image/'):
            return True
        elif self.contentType.startswith('video/'):
            return True
        elif self.contentType.lower() == mime_types['flash']:
            return True
        else:
            return False

    def isFile (self):
        return self.is_file

    def isText (self):
        return self.contentType.startswith('text/')

    def isHtml (self):
        return self.contentType == mime_types['html']

    def isXml (self):
        return self.contentType == mime_types['xml']

    def isHttpError (self):
        return (not self.httpResponseCode == 200)

    def hasFileName (self):
        return len(self.outFileName) > 0

    def testFile (self):
        if self.isFile() and not os.path.exists(self.data):
            self.setHtmlErrorNotFound()

    def getDim (self, key, def_val):
        if self.dims is None:
            return def_val
        return self.dims.get(key, def_val)

    def hasQueue (self):
        return len(self.queue)>0

    def drainQueue (self):
        commands = self.queue or []
        self.queue = []
        return commands

    def getQueue (self):
        return self.queue

    def is_multifile_series(self):
        return isinstance(self.input, list) and len(self.input)>1

    def first_input_file(self):
        return self.input[0] if isinstance(self.input, list) else self.input

    def get_speed_file(self):
        return '%s/%s.speed'%(self.initial_workpath, self.resource_id)

