"""
Listing of operations
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

__all__ = [ 'MetaOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv
from bq.image_service.controllers.utils import safeunicode

log = logging.getLogger("bq.image_service.operations.meta")

class MetaOperation(BaseOperation):
    '''Provide image information'''
    name = 'meta'

    def __str__(self):
        return 'meta: returns XML with image meta-data'

    def dryrun(self, token, arg):
        metacache = '%s.meta'%(token.data)
        return token.setXmlFile(metacache)

    def action(self, token, arg):
        ifile = token.first_input_file()
        metacache = '%s.meta'%(token.data)
        log.debug('Meta: %s -> %s', ifile, metacache)

        if not os.path.exists(metacache):
            meta = {}
            if not os.path.exists(ifile):
                raise ImageServiceException(404, 'Meta: Input file not found...')

            dims = token.dims or {}
            converter = None
            if dims.get('converter', None) in self.server.converters:
                converter = dims.get('converter')
                meta = self.server.converters[converter].meta(token)

            if meta is None:
                # exhaustively iterate over converters to find supporting one
                for c in self.server.converters.itervalues():
                    if c.name == dims.get('converter'): continue
                    meta = c.meta(token)
                    converter = c.name
                    if meta is not None and len(meta)>0:
                        break

            if meta is None or len(meta)<1:
                raise ImageServiceException(415, 'Meta: file format is not supported...')

            # overwrite fileds forced by the fileds stored in the resource image_meta
            if token.meta is not None:
                meta.update(token.meta)
            meta['converter'] = converter
            if token.is_multifile_series() is True:
                meta['file_mode'] = 'multi-file'
            else:
                meta['file_mode'] = 'single-file'

            # construct an XML tree
            image = etree.Element ('resource', uri='/%s/%s?meta'%(self.server.base_url, token.resource_id))
            tags_map = {}
            for k, v in meta.iteritems():
                if k.startswith('DICOM/'): continue
                k = safeunicode(k)
                v = safeunicode(v)
                tl = k.split('/')
                parent = image
                for i in range(0,len(tl)):
                    tn = '/'.join(tl[0:i+1])
                    if not tn in tags_map:
                        tp = etree.SubElement(parent, 'tag', name=tl[i])
                        tags_map[tn] = tp
                        parent = tp
                    else:
                        parent = tags_map[tn]
                try:
                    parent.set('value', v)
                except ValueError:
                    pass

            if meta['format'] == 'DICOM':
                node = etree.SubElement(image, 'tag', name='DICOM')
                ConverterImgcnv.meta_dicom(ifile, series=token.series, token=token, xml=node)

            log.debug('Meta %s: storing metadata into %s', token.resource_id, metacache)
            xmlstr = etree.tostring(image)
            with open(metacache, 'w') as f:
                f.write(xmlstr)
            return token.setXml(xmlstr)

        log.debug('Meta %s: reading metadata from %s', token.resource_id, metacache)
        return token.setXmlFile(metacache)
