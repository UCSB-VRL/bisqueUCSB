""" An ordered dictionary of converters
"""

__author__    = "Dmitry Fedorov"
__version__   = "1.4"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys
import logging
import os.path
import shutil
import re
import StringIO
from lxml import etree
import datetime
import math

#from collections import OrderedDict
from bq.util.compat import OrderedDict

from .process_token import ProcessToken

import logging
log = logging.getLogger('bq.image_service.converters')

################################################################################
# ConverterDict
################################################################################

class ConverterDict(OrderedDict):
    'Store items in the order the keys were last added'

#     def __setitem__(self, key, value):
#         if key in self:
#             del self[key]
#         OrderedDict.__setitem__(self, key, value)

    def __str__(self):
        return ', '.join(['%s (%s)'%(n, c.version['full']) for n,c in self.iteritems()])

    def defaultExtension(self, formatName):
        formatName = formatName.lower()
        for c in self.itervalues():
            if formatName in c.formats():
                return c.formats()[formatName].ext[0]

    def extensions(self, name=None):
        exts = []
        if name is None:
            for c in self.itervalues():
                for f in c.formats().itervalues():
                    exts.extend(f.ext)
        else:
            c = self[name]
            for f in c.formats().itervalues():
                exts.extend(f.ext)
        return exts

    def info(self, filename, name=None):

        token = ProcessToken(ifnm=filename)
        if name is None:
            for n,c in self.iteritems():
                info = c.info(token)
                if info is not None and len(info)>0:
                    info['converter'] = n
                    return info
        else:
            c = self[name]
            info = c.info(token)
            if info is not None and len(info)>0:
                info['converter'] = name
                return info
        return None

    def canWriteMultipage(self, formatName):
        formats = []
        for c in self.itervalues():
            for n,f in c.formats().iteritems():
                if f.multipage is True:
                    formats.append(n)
        return formatName.lower() in formats

    def converters(self, readable=True, writable=True, multipage=False):
        fs = {}
        for c in self.itervalues():
            for n,f in c.formats().iteritems():
                ok = True
                if readable is True and f.reading is not True:
                    ok = False
                elif writable is True and f.writing is not True:
                    ok = False
                elif multipage is True and f.multipage is not True:
                    ok = False
                if ok is True:
                    fs.setdefault(n, c)
        return fs
