###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007 by the Regents of the University of California     ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========

DESCRIPTION
===========

TODO
===========

  1. Accept metadata as XML file along with packed image files
  1.

"""

__module__    = "export_service"
__author__    = "Dmitry Fedorov, Kris Kvilekval, Santhoshkumar Sunderrajan"
__version__   = "1.3"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

# -*- mode: python -*-

# default includes
import os
import logging
import pkg_resources
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, flash
from repoze.what import predicates



# additional includes
import sys
import traceback
import datetime
import time
import re
import threading
import shutil
import tarfile
import zipfile
import logging
import gdata.docs
import gdata.docs.service

try:
    from cStringIO import StringIO
except Exception:
    from StringIO import StringIO

from urllib import quote
from lxml import etree

import tg
from tg import request, response, session, flash, require, abort
from repoze.what import predicates

from bq.core.service import ServiceController
from bq import data_service
from bq import image_service
from bq.core import identity
from bq.util.hash import is_uniq_code

from bqapi.bqclass import gobject_primitives

from bq.export_service.controllers.archive_streamer import ArchiveStreamer


# export plugins
try:
    import pyproj
except ImportError:
    pass
try:
    import json
except ImportError:
    pass

#---------------------------------------------------------------------------------------
# inits
#---------------------------------------------------------------------------------------

NO_BYTES=16*1024
max_size=1024*1024*1024*2
CHARREGEX=re.compile("\W+")
log  = logging.getLogger('bq.export_service')

#---------------------------------------------------------------------------------------
# controller
#---------------------------------------------------------------------------------------

log = logging.getLogger("bq.export_service")
class export_serviceController(ServiceController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()
    service_type = "export"

    def __init__(self, server_url):
        super(export_serviceController, self).__init__(server_url)
        self.exporters = {}
        if 'pyproj' in sys.modules:
            self.exporters['kml'] = ExporterKML()
            if 'json' in sys.modules:
                self.exporters['geojson'] = ExporterGeoJson()

    @expose('bq.export_service.templates.index')
    def index(self, **kw):
        """Add your first page here.. """
        return dict(msg=_('Hello from export_service'))

    def check_access(self, ident):
        resource = data_service.resource_load (uniq = ident)
        if resource is None:
            if identity.not_anonymous():
                abort(403)
            else:
                abort(401)
        return resource

    @expose()
    def _default(self, *path, **kw):
        """find export plugin and run export"""
        uniq = path[0] if len(path)>0 else None
        format = path[1] if len(path)>1 else None
        if format is None:
            format = kw.get('format')

        # check permissions
        self.check_access(uniq)

        # export
        if format in self.exporters:
            return self.exporters[format].export(uniq)

        abort(400, 'Requested export format (%s) is not supported'%format )

#------------------------------------------------------------------------------
# Google Docs Export
#------------------------------------------------------------------------------

    @expose(template='bq.export_service.templates.to_gdocs')
    @require(predicates.not_anonymous())
    def to_gdocs (self, **kw):
        return { 'opts': kw }

    @expose(template='bq.export_service.templates.to_gdocs_send')
    @require(predicates.not_anonymous())
    def to_gdocs_send (self, **kw):
        if not 'google_id' in kw: return 'Google e-mail is needed'
        if not 'google_password' in kw: return 'Google password is needed'
        if not 'document_url' in kw: return 'Document to be exported is not provided'

        # get the document
        google_id = str(kw['google_id'])
        google_pass = str(kw['google_password'])
        url = str(kw['document_url'])

        s = data_service.load(url+'?view=deep&format=csv')
        #s = data_service.get_resource(url, view='deep', format='csv')

        input_file = StringIO(s)
        #log.debug('Google Docs input: ' + s )

        # upload to google docs
        gd_client = gdata.docs.service.DocsService()
        gd_client.email = str(google_id)
        gd_client.password = str(google_pass)
        gd_client.source = 'CBI_UCSB-Bisque-1'
        try:
            gd_client.ProgrammaticLogin()
        except Exception:
            return dict(error= str(sys.exc_value) )

        m_file_handle = input_file
        m_content_type = 'text/csv'
        m_content_length = len(s)
        m_file_name = quote(url)
        m_title = 'Bisque data - '+url

        ms = gdata.MediaSource(file_handle = m_file_handle, content_type = m_content_type, content_length = m_content_length, file_name = m_file_name )
        entry = gd_client.UploadSpreadsheet(ms, m_title)
        return dict(error=None, google_url=str(entry.GetAlternateLink().href))


    #------------------------------------------------------------------
    # new ArchiveStreamer - Utkarsh
    #------------------------------------------------------------------

    @expose()
    def stream(self, **kw):
        """Create and return a streaming archive

        :param compression: tar, zip, gzip, bz2
        :param files: a comma separated list of resource URIs to include in the archive
        :param datasets: a comma separated list of dataset resource URIs to include in the archive
        :param urls: a comma separated list of any url accessible over HTTP to include in the archive

        ------------------------------------
        Sample XML when POSTing to this app
        ------------------------------------

        <resource>
            <value type="FILE">    ...    </value>
            <value type="URL">     ...    </value>
            <value type="DATASET"> ...    </value>
        </resource>

        """

        files    = []
        datasets = []
        urls     = []
        dirs     = []

        if (tg.request.method.upper()=='POST' and tg.request.body):
            try:
                data = etree.XML(tg.request.body)
            except etree.ParseError:
                data = []
            for resource in data:
                type = resource.get('type', 'url').lower()
                if (type == 'file'):
                    files.append(resource.text)
                elif (type == 'dataset'):
                    datasets.append(resource.text)
                elif (type == 'dir'):
                    dirs.append(resource.text)
                elif (type == 'url'):
                    urls.append(resource.text)
                else:
                    urls.append(resource.text)

        compression = kw.pop('compression', '')

        def extractData(kw, field):
            if field in kw:
                vals = kw.pop(field)
                if vals:
                    return vals.split(',')
            return []

        jsbool   = {'true': True, 'false': False}
        export_meta = jsbool.get(kw.get('metadata', 'true'), True);
        export_mexs = jsbool.get(kw.get('analysis', 'false'), True);

        files.extend(extractData(kw, 'files'))
        datasets.extend(extractData(kw, 'datasets'))
        urls.extend(extractData(kw, 'urls'))
        dirs.extend(extractData(kw, 'dirs'))

        filename = kw.pop('filename', 'bisque-'+time.strftime("%Y%m%d.%H%M%S"))

        archiveStreamer = ArchiveStreamer(compression)
        archiveStreamer.init(archiveName=filename, fileList=files, datasetList=datasets, urlList=urls, dirList=dirs, export_meta=export_meta, export_mexs=export_mexs)
        return archiveStreamer.stream()

    @expose()
    def initStream(self, **kw): # deprecated backward compatible name
        if 'compressionType' in kw:
            kw['compression'] = kw['compressionType']
            del kw['compressionType']
        return self.stream(**kw)

    def export(self, **kw):
        compression = kw.pop('compression', 'gzip')
        files       = kw.pop('files', None)
        datasets    = kw.pop('datasets', None)
        urls        = kw.pop('urls', None)
        dirs        = kw.pop('dirs', None)
        export_meta = kw.pop('export_meta', None)
        export_mexs = kw.pop('export_mexs', None)
        filename    = kw.pop('filename', 'bisque-'+time.strftime("%Y%m%d.%H%M%S"))

        archiveStreamer = ArchiveStreamer(compression)
        archiveStreamer.init(archiveName=filename, fileList=files, datasetList=datasets, urlList=urls, dirList=dirs, export_meta=export_meta, export_mexs=export_mexs)
        return archiveStreamer.stream()


#---------------------------------------------------------------------------------------
# exporters: Geo base
#---------------------------------------------------------------------------------------

class ExporterGeo():
    '''Supports exporting Bisque documents into geographical formats'''

    version = '1.0'
    ext = 'txt'
    mime_type = 'text/plain'

    def __init__(self):
        pass

    def bq2format(self, resource):
        "Stub defined in subclasses"
        return None

    def export(self, uniq):
        """Add your first page here.. """
        resource = data_service.resource_load (uniq = uniq, view='deep')
        fname = '%s.%s' % (resource.get('name'), self.ext)
        #log.debug('Resource 1: %s', etree.tostring(resource))

        # if the resource is a dataset, fetch contents of documents linked in it
        #if resource.tag == 'dataset':
        #    resource = data_service.get_resource('%s/value'%resource.get('uri'), view='deep')
        #log.debug('Resource 2: %s', etree.tostring(resource))

        response.headers['Content-Type'] = self.mime_type
        try:
            fname.encode('ascii')
            disposition = 'filename="%s"'%(fname)
        except UnicodeEncodeError:
            disposition = 'filename="%s"; filename*="%s"'%(fname.encode('utf8'), fname.encode('utf8'))
        response.headers['Content-Disposition'] = disposition

        return self.bq2format(resource)

    def create_transform_function(self, resource, meta=None):
        """ converts BisqueXML into KML """

        if meta is None:
            uniq = resource.get('resource_uniq')
            try:
                meta = image_service.meta(uniq)
            except Exception:
                meta = etree.Element ('image')

        # get proj4
        q = meta.xpath('tag[@name="Geo"]/tag[@name="Model"]/tag[@name="proj4_definition"]')
        prj = q[0].get('value', None) if len(q)>0 else None

        # get top_left
        q = meta.xpath('tag[@name="Geo"]/tag[@name="Coordinates"]/tag[@name="upper_left_model"]')
        top_left = q[0].get('value', None) if len(q)>0 else None
        if top_left is None:
            q = meta.xpath('tag[@name="Geo"]/tag[@name="Coordinates"]/tag[@name="upper_left"]')
            top_left = q[0].get('value', None) if len(q)>0 else None
        if top_left:
            top_left = [float(v) for v in top_left.split(',')]

        # get pixel res
        q = meta.xpath('tag[@name="Geo"]/tag[@name="Tags"]/tag[@name="ModelPixelScaleTag"]')
        res = q[0].get('value', None) if len(q)>0 else None
        if res:
            res = [float(v) for v in res.split(',')]

        # define transformation
        try:
            pproj = pyproj.Proj(prj)
        except (RuntimeError):
            pproj = None

        transform = {
            'proj_from': pproj,
            'proj_to': pyproj.Proj(init='EPSG:4326'),
            'offset': top_left,
            'res': res
        }
        log.debug('Transform: %s', str(transform))

        # closure with current transform
        def transform_coord(c):
            if transform['offset'] is None or transform['res'] is None or transform['proj_from'] is None:
                return c
            cc = ( transform['offset'][0] + c[0]*transform['res'][0], transform['offset'][1] - c[1]*transform['res'][1] )
            ccc = pyproj.transform(transform['proj_from'], transform['proj_to'], cc[0], cc[1])
            return (ccc[0], ccc[1])

        return transform_coord


#---------------------------------------------------------------------------------------
# exporters: KML
#---------------------------------------------------------------------------------------

class ExporterKML (ExporterGeo):
    '''Supports exporting Bisque documents into KML'''

    version = '1.0'
    ext = 'kml'
    #mime_type = 'text/xml'
    mime_type = 'application/vnd.google-earth.kml+xml'

    def __init__(self):
        pass

    def bq2format(self, resource):
        """ converts BisqueXML into KML """

        kml = etree.Element ('kml', xmlns='http://www.opengis.net/kml/2.2')
        doc = etree.SubElement (kml, 'Document')

        self.convert_node(resource, doc)
        return etree.tostring(kml)

    def convert_node(self, node, kml, cnvf=None):
        if node is None:
            return
        if node.tag in gobject_primitives or node.tag == 'gobject' and node.get('type') in gobject_primitives:
            self.render_gobjects(node, kml, node.tag, cnvf=cnvf)
        elif node.tag == 'gobject' and len(node)==1: # special case of a gobject wrapper of a primitive
            self.render_gobjects(node[0], kml, node.get('type'), node.get('name'), cnvf=cnvf)
        elif node.tag == 'tag':
            # skip any tags, they were added beforehand
            pass
        elif node.tag == 'dataset':
            folder = self.render_resouces(node, kml)
            vals = node.xpath('value')
            for v in vals:
                n = data_service.get_resource(v.text, view='deep')
                self.convert_node(n, folder, cnvf=cnvf)
        elif node.tag not in ['vertex', 'value']: # any other node type is a folder
            if node.tag == 'image':
                # load metadata and create coordinate transformation function
                cnvf = self.create_transform_function(node)
            folder = self.render_resouces(node, kml)
            if len(node) > 0:
                for n in node:
                    self.convert_node(n, folder, cnvf=cnvf)

    def render_resouces(self, node, kml):
        folder = etree.SubElement (kml, 'Folder')
        name = etree.SubElement (folder, 'name') # type of gobject
        descr = etree.SubElement (folder, 'description') # name of gobject

        if node.tag == 'image':
            name.text = node.get('name')
            descr.text = 'Annotations contained within image: %s'%node.get('name')
        else:
            name.text = node.get('type') or node.get('resource_type') or node.tag
            descr.text = node.get('name')

        self.render_tags(node, folder)
        return folder

    def render_tags(self, node, kml, ed=None, path=None):
        tags = node.xpath('tag')
        if len(tags)>0:
            if ed is None:
                ed = etree.SubElement (kml, 'ExtendedData')
            for t in tags:
                name = '%s/%s'%(path, t.get('name')) if path is not None else t.get('name')
                d = etree.SubElement (ed, 'Data', name=name)
                v = etree.SubElement (d, 'value')
                v.text = t.get('value')
                self.render_tags(t, kml, ed=ed, path=name)
            return ed
        return None

    def render_gobjects(self, node, kml, type=None, _val=None, cnvf=None):
        vrtx = node.xpath('vertex')
        f = getattr(self, node.tag, None)
        if len(vrtx)>0 and callable(f):

            vrtx = [(float(v.get('x')), float(v.get('y'))) for v in vrtx]
            if cnvf is not None:
                vrtx = [cnvf(v) for v in vrtx]

            folder = f(node, kml, vrtx, type or node.tag, _val)
            self.render_tags(node, folder)
            return folder
        return None

    def point(self, node, kml, vrtx, type=None, val=None):
        pm = etree.SubElement (kml, 'Placemark')
        name = etree.SubElement (pm, 'name') # type of gobject
        name.text = type or node.get('name')

        if val is not None:
            descr = etree.SubElement (pm, 'description') # name of gobject
            descr.text = val

        point = etree.SubElement (pm, 'Point')
        coord = etree.SubElement (point, 'coordinates')

        x = vrtx[0][0]
        y = vrtx[0][1]
        coord.text = '%s,%s'%(x,y)
        return pm

    def line(self, node, kml, vrtx, type=None, val=None):
        return self.polyline(node, kml, vrtx, type, val)

    def polygon(self, node, kml, vrtx, type=None, val=None):
        pm = etree.SubElement (kml, 'Placemark')
        name = etree.SubElement (pm, 'name') # type of gobject
        name.text = type or node.get('name')

        if val is not None:
            descr = etree.SubElement (pm, 'description') # name of gobject
            descr.text = val

        g = etree.SubElement (pm, 'Polygon')
        g1 = etree.SubElement (g, 'outerBoundaryIs')
        g2 = etree.SubElement (g1, 'LinearRing')
        coord = etree.SubElement (g2, 'coordinates')

        coord.text = ' '.join( ['%s,%s'%(v[0], v[1]) for v in vrtx ] )
        return pm

    def polyline(self, node, kml, vrtx, type=None, val=None):
        pm = etree.SubElement (kml, 'Placemark')
        name = etree.SubElement (pm, 'name') # type of gobject
        name.text = type or node.get('name')

        if val is not None:
            descr = etree.SubElement (pm, 'description') # name of gobject
            descr.text = val

        g = etree.SubElement (pm, 'LineString')
        coord = etree.SubElement (g, 'coordinates')

        coord.text = ' '.join( ['%s,%s'%(v[0], v[1]) for v in vrtx ] )
        return pm

    def label(self, node, kml, vrtx, type=None, val=None):
        pm = etree.SubElement (kml, 'Placemark')
        name = etree.SubElement (pm, 'name') # type of gobject
        name.text = type or node.get('name')
        val = node.get('value') or val

        if val is not None:
            descr = etree.SubElement (pm, 'description') # name of gobject
            descr.text = val

        point = etree.SubElement (pm, 'Point')
        coord = etree.SubElement (point, 'coordinates')

        x = vrtx[0][0]
        y = vrtx[0][1]
        coord.text = '%s,%s'%(x,y)
        return pm

    def circle(self, node, kml, vrtx, type=None, val=None):
        pm = etree.SubElement (kml, 'Placemark')
        name = etree.SubElement (pm, 'name') # type of gobject
        name.text = type or node.get('name')

        if val is not None:
            descr = etree.SubElement (pm, 'description') # name of gobject
            descr.text = val

        # there are no circles in KML, store custom field
        coords = ' '.join( ['%s,%s'%(v[0], v[1]) for v in vrtx ] )
        ed = etree.SubElement (pm, 'ExtendedData')
        d = etree.SubElement (ed, 'Data', name='coordinates')
        v = etree.SubElement (d, 'value')
        v.text = coords

        return pm

    def ellipse(self, node, kml, vrtx, type=None, val=None):
        return self.circle(node, kml, vrtx, type, val)

    def rectangle(self, node, kml, vrtx, type=None, val=None):
        return self.circle(node, kml, vrtx, type, val)

    def square(self, node, kml, vrtx, type=None, val=None):
        return self.circle(node, kml, vrtx, type, val)

#---------------------------------------------------------------------------------------
# exporters: GeoJson
#---------------------------------------------------------------------------------------

class ExporterGeoJson (ExporterGeo):
    '''Supports exporting Bisque documents into GeoJson'''

    version = '1.0'
    ext = 'geojson'
    #mime_type = 'application/json'
    mime_type = 'application/vnd.geo+json'

    def __init__(self):
        pass

    def bq2format(self, resource):
        """ converts BisqueXML into GeoJson """
        geoj = {
            "type": "FeatureCollection",
            "features": [],
        }

        self.convert_node(resource, geoj['features'])
        return json.dumps(geoj)

    def convert_node(self, node, kml, cnvf=None):
        #log.debug('convert_node: %s', etree.tostring(node))
        if node is None:
            return
        if node.tag in gobject_primitives or node.tag == 'gobject' and node.get('type') in gobject_primitives:
            self.render_gobjects(node, kml, node.tag, cnvf=cnvf)
        elif node.tag == 'gobject' and len(node)==1: # special case of a gobject wrapper of a primitive
            self.render_gobjects(node[0], kml, node.get('type'), node.get('name'), cnvf=cnvf)
        elif node.tag == 'tag':
            # skip any tags, they were added beforehand
            pass
        elif node.tag == 'dataset':
            # geojson does not have hierarchical elements, dum all as a flat list
            #folder = self.render_resouces(node, kml)
            vals = node.xpath('value')
            for v in vals:
                n = data_service.get_resource(v.text, view='deep')
                self.convert_node(n, kml, cnvf=cnvf)
        elif node.tag not in ['vertex', 'value']: # any other node type is a folder
            if node.tag == 'image':
                # load metadata and create coordinate transformation function
                cnvf = self.create_transform_function(node)
            # geojson does not have hierarchical elements, dum all as a flat list
            #folder = self.render_resouces(node, kml)
            if len(node) > 0:
                for n in node:
                    self.convert_node(n, kml, cnvf=cnvf)

    def render_resouces(self, node, features):
        feature = {
            'type': 'GeometryCollection',
            'properties': {
                'type': node.get('type') or node.get('resource_type') or node.tag,
                'name': node.get('name'),
            },
            'geometry': None,
            'geometries': []
        }
        if node.get('resource_uniq') is not None:
            feature['id'] = node.get('resource_uniq')

        self.render_tags(node, feature)

        features.append(feature)
        return feature['geometries']

    def render_gobjects(self, node, features, type=None, _val=None, cnvf=None):
        vrtx = node.xpath('vertex')
        f = getattr(self, node.tag, None)
        if len(vrtx)>0 and callable(f):
            feature = {
                'type': 'Feature',
                'properties': {
                    'type': node.get('type') or node.get('resource_type') or node.tag,
                },
            }
            if node.get('name') is not None:
                feature['properties']['name'] = node.get('name')


            vrtx = [(float(v.get('x')), float(v.get('y'))) for v in vrtx]
            if cnvf is not None:
                vrtx = [cnvf(v) for v in vrtx]

            f(node, feature, vrtx, type or node.tag, _val)
            self.render_tags(node, feature)
            features.append(feature)
        return None

    def render_tags(self, node, feature, ed=None, path=None):
        tags = node.xpath('tag')
        if len(tags)>0:
            for t in tags:
                name = '%s/%s'%(path, t.get('name')) if path is not None else t.get('name')
                feature['properties'][name] = t.get('value')
                self.render_tags(t, feature, ed=ed, path=name)
            return feature
        return None

    def point(self, node, feature, vrtx, type=None, val=None):
        feature['properties']['type'] = type or node.get('name')
        if val is not None:
            feature['properties']['description'] = val

        geom = {
            'type': 'Point',
            'coordinates': [vrtx[0][0], vrtx[0][1]],
        }
        feature['geometry'] = geom
        return geom

    def line(self, node, feature, vrtx, type=None, val=None):
        return self.polyline(node, feature, vrtx, type, val)

    def polygon(self, node, feature, vrtx, type=None, val=None):
        feature['properties']['type'] = type or node.get('name')
        if val is not None:
            feature['properties']['description'] = val

        crds = [[v[0], v[1]] for v in vrtx]
        crds.append(crds[0])
        geom = {
            'type': 'Polygon',
            'coordinates': [crds],
        }
        feature['geometry'] = geom
        return geom

    def polyline(self, node, feature, vrtx, type=None, val=None):
        feature['properties']['type'] = type or node.get('name')
        if val is not None:
            feature['properties']['description'] = val

        geom = {
            'type': 'LineString',
            'coordinates': [[v[0], v[1]] for v in vrtx ],
        }
        feature['geometry'] = geom
        return geom

    def label(self, node, feature, vrtx, type=None, val=None):
        feature['properties']['type'] = type or node.get('name')
        val = node.get('value') or val
        if val is not None:
            feature['properties']['description'] = val

        geom = {
            'type': 'Point',
            'coordinates': [vrtx[0][0], vrtx[0][1]],
        }
        feature['geometry'] = geom
        return geom

    # def circle(self, node, feature, vrtx, type=None, val=None):
    #     # there are no circles in GeoJsoon, skip
    #     return None

    # def ellipse(self, node, feature, vrtx, type=None, val=None):
    #     return self.circle(node, feature, vrtx, type, val)

    # def rectangle(self, node, feature, vrtx, type=None, val=None):
    #     return self.circle(node, feature, vrtx, type, val)

    # def square(self, node, feature, vrtx, type=None, val=None):
    #     return self.circle(node, feature, vrtx, type, val)

#---------------------------------------------------------------------------------------
# bisque init stuff
#---------------------------------------------------------------------------------------
def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    service =  export_serviceController(uri)
    #directory.register_service ('export_service', service)

    return service

def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'export_service', 'public'))]

__controller__ =  export_serviceController
