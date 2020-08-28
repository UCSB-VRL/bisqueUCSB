"""
Listing of formats
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

__all__ = [ 'FormatsOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken

log = logging.getLogger("bq.image_service.operations.formats")

class FormatsOperation(BaseOperation):
    '''Provide information on supported formats'''
    name = 'formats'

    def __str__(self):
        return 'formats: Returns XML with supported formats'

    def dryrun(self, token, arg):
        return token.setXml('')

    def action(self, token, arg):
        xml = etree.Element ('resource', uri='/images_service/formats')
        for nc,c in self.server.converters.iteritems():
            format = etree.SubElement (xml, 'format', name=nc, version=c.version['full'])
            for f in c.formats().itervalues():
                codec = etree.SubElement(format, 'codec', name=f.name )
                etree.SubElement(codec, 'tag', name='fullname', value=f.fullname )
                etree.SubElement(codec, 'tag', name='extensions', value=','.join(f.ext) )
                etree.SubElement(codec, 'tag', name='support', value=f.supportToString() )
                etree.SubElement(codec, 'tag', name='samples_per_pixel_minmax', value='%s,%s'%f.samples_per_pixel_min_max )
                etree.SubElement(codec, 'tag', name='bits_per_sample_minmax',   value='%s,%s'%f.bits_per_sample_min_max )
        return token.setXml(etree.tostring(xml))
