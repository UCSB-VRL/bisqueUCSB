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
##        software must display the following acknowledgment: This product  ##
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

  1. Add regexp sorting for files in the composed Zip
  2. Problem with OME-XML in the imgcnv


"""

__module__    = "import_service"
__author__    = "Dmitry Fedorov, Kris Kvilekval"
__version__   = "2.4"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

# -*- mode: python -*-

# default includes
import os
import logging
import pkg_resources
#from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort
import  tg
from repoze.what import predicates
from bq.core.service import ServiceController

# additional includes
#import sys
#import time
#import threading
import shutil
import tarfile
import zipfile
import urllib
import copy
import mimetypes
import shortuuid
import posixpath
import json


from lxml import etree
from datetime import datetime
#from itertools import groupby

from tg import require, expose
from repoze.what import predicates

import bq
from bq.core import identity
from bq.util.paths import data_path
from bq import data_service
from bq import blob_service
from bq import image_service
from bq.blob_service.controllers.blob_drivers import move_file
from bq.util.io_misc import blocked_alpha_num_sort, toascii, tounicode
from bq.util.timer import Timer
from bq.util.sizeoffmt import sizeof_fmt
from bq.image_service.controllers.service import ImageServiceController
from bq.image_service.controllers.converters.converter_imgcnv import ConverterImgcnv

from bq.util.mkdir import _mkdir

log = logging.getLogger("bq.import_service")


UPLOAD_DIR = tg.config.get('bisque.import_service.upload_dir', data_path('uploads'))

FS_FILES_IGNORE = ['.', '..', 'Thumbs.db', '.DS_Store', '.Trashes']

#---------------------------------------------------------------------------------------
# Direct transfer handling (reducing filecopies )
# Patch to allow no copy file uploads (direct to destination directory)
#---------------------------------------------------------------------------------------
import cgi
#if upload handler has been inited in webob
if hasattr(cgi, 'file_upload_handler'):
    tmp_upload_dir = UPLOAD_DIR
    _mkdir(tmp_upload_dir)

    #register callables here
    def import_transfer_handler(filename):
        import tempfile
        try:
            return tempfile.NamedTemporaryFile('w+b', suffix = os.path.basename(filename), dir=tmp_upload_dir, delete = False)
        except Exception:
            return tempfile.TemporaryFile('w+b', dir=tmp_upload_dir)

    #map callables to paths here
    cgi.file_upload_handler['/import/transfer.*'] = import_transfer_handler


#---------------------------------------------------------------------------------------
# Misc functions
#---------------------------------------------------------------------------------------

def is_filesystem_file(filename):
    filename = os.path.basename(filename)
    if filename in FS_FILES_IGNORE: # skip ignored files
        return True
    if filename.startswith('._'): # MacOSX files starting at '._'
        return True
    return False

def sanitize_filename(filename):
    """ Removes any path info that might be inside filename, and returns results. """
    return urllib.unquote(filename).split("\\")[-1].split("/")[-1]


def merge_resources (*resources):
    """merge attributes and subtags of parameters

    later resource overwrite earlier ones
    """
    final = copy.deepcopy (resources[0])
    log.debug ('initially : %s' , etree.tostring(final))
    for rsc in resources[1:]:
        final.attrib.update(rsc.attrib)
        final.extend (copy.deepcopy (list (rsc)))
        log.debug ('updated : %s -> %s', etree.tostring(rsc), etree.tostring(final))
    return final

def overwrite_xmlattr(parent, node, name, value, type=None):
    xl = parent.xpath('%s[@name="%s"]'%(node, name))
    if len(xl)>0:
        t = xl[0]
    else:
        t = etree.SubElement(parent, 'tag', name=name )
    t.set('value', value)
    if type is not None:
        t.set('type', type)


#---------------------------------------------------------------------------------------
# File object
#---------------------------------------------------------------------------------------

class UploadedResource(object):
    """ Object encapsulating upload resource+file """
    filename = None      # The  filename  to be stored with the resource
    fileobj  = None      # The fileobj (if coming from an upload form)
    path     = None      # A path to the file, if already local
    orig     = None      # original name passed by the uploader
    ts       = None      # upload timestamp

    def __init__(self, resource, fileobj=None, orig=None, ts=None, path=None ):
        self.resource = resource
        self.fileobj = fileobj
        self.orig = orig or resource.get('name')
        self.ts = ts or datetime.now().isoformat(' ')

        # Set the path and filename of the UploadFile
        # A local path will be available in 'value'
        if path is not None:
            self.path = path
        else:
            self.path = resource.get('value')
            if self.path:
                self.path = blob_service.url2local(self.path)

        # If the uploader has given it a name, then use it, or figure a name out
        if resource.get ('name'):
            self.filename = sanitize_filename(resource.get('name'))
        elif fileobj:
            # POSTed fileobject will have a filename (which may be path)
            # http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/forms/file_uploads.html
            if self.path is None:
                self.path = getattr(fileobj, 'filename', None) or getattr (fileobj, 'name', None)
            self.filename = sanitize_filename (self.path)
            #resource.set('name', self.filename)

    def localpath(self):
        'retrieve a local path for this uploaded resource'
        if self.fileobj is None:
            return self.path

        if os.name == 'nt' and self.fileobj is not None:
            return self.path

        filename = getattr(self.fileobj, 'name', None)
        if filename and filename[0] == '<' and filename[-1] == '>': #pylint: disable=unsubscriptable-object
            # special case: file was not created using open();
            # in this case 'name' attribute is some string that indicates the source of the file object, of the form '<...>'.
            # (see https://docs.python.org/2.7/library/stdtypes.html#file-objects)
            filename = None
        return filename or getattr(self.fileobj, 'filename', None) or self.path

    def ensurelocal(self, localpath):
        '''retrieve a local path for this uploaded resource'''
        if self.path is not None:
            return self.path
        if os.name != 'nt':
            self.path = self.path or getattr(self.fileobj, 'name', None) or getattr(self.fileobj, 'filename', None)
        if self.path is None:
            if os.name == 'nt':
                _mkdir (os.path.dirname(localpath))
            move_file (self.fileobj, localpath)
            self.path = localpath
            self.fileobj = open(localpath, 'rb')
        return self.path

    def close(self):
        '''close fileobj'''
        if self.fileobj:
            self.fileobj.close()

    def get_type(self):
        if self.resource is None:
            return None
        return self.resource.get('type') or self.resource.get('resource_type') or self.resource.tag

    def __del__ (self):
        self.close()

    def __str__(self):
        return 'UploadFile([%s] [%s] [%s] [%s] [%s])'%(self.path, self.filename, etree.tostring(self.resource), self.fileobj, self.orig)




#---------------------------------------------------------------------------------------
# controller
#---------------------------------------------------------------------------------------

class import_serviceController(ServiceController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()
    service_type = "import"

    def __init__(self, server_url):
        super(import_serviceController, self).__init__(server_url)

        # special mime-types for proprietary images able to store multiple series
        # define the list here in order to minimize info calls on these images
        # will have to figure how many series are inside to create proper resources
        self.series_exts = image_service.proprietary_series_extensions()
        self.non_image_exts = image_service.non_image_extensions()
        log.debug('Series extensions: %s', self.series_exts)
        for e in self.series_exts:
            mimetypes.add_type('image/series', '.%s'%e)
        self.series_headers = image_service.proprietary_series_headers()

        self.filters = {}
        self.filters['zip-bisque']        = self.filter_zip_bisque
        self.filters['zip-multi-file']    = self.filter_zip_multifile
        self.filters['zip-time-series']   = self.filter_zip_tstack
        self.filters['zip-z-stack']       = self.filter_zip_zstack
        self.filters['zip-5d-image']      = self.filter_5d_image
        self.filters['zip-proprietary']   = self.filter_zip_proprietary
        self.filters['zip-dicom']         = self.filter_zip_dicom
        self.filters['image/proprietary'] = self.filter_series_proprietary
        self.filters['image-part-5D']     = self.filter_part_5d
        # extra filter for Dream3D pipeline files (JSON)
        self.filters['application/json']  = self.filter_json

        self.plugins = blob_service.get_import_plugins()
        for p in self.plugins:
            mime_import = 'import/%s'%(p.name)
            mimetypes.add_type(mime_import, '.%s'%p.ext)
            self.filters[mime_import] = p.process_on_import


    @expose('bq.import_service.templates.upload')
    @require(predicates.not_anonymous())
    def index(self, **kw):
        """Add your first page here.. """
        return dict()

#------------------------------------------------------------------------------
# zip/tar.gz support functions
#------------------------------------------------------------------------------

    # unpacking that preserves structure
    def unZip(self, filename, foldername):
        z = zipfile.ZipFile(filename, 'r')

        # first test if archive is valid
        names = z.namelist()
        for name in names:
            if name.startswith('/') or name.startswith('\\') or name.startswith('..'):
                z.close()
                return []

        # extract members if all is fine
        z.extractall(foldername)
        z.close()
        return names

    # unpacking that preserves structure
    def unTar(self, filename, foldername):
        z = tarfile.open(filename, 'r')

        # first test if archive is valid
        names = z.getnames()
        for name in names:
            if name.startswith('/') or name.startswith('\\') or name.startswith('..'):
                z.close()
                return []

        # extract members if all is fine
        z.extractall(foldername)
        z.close()
        return names

    # unpacking that flattens file structure
    def unTarFlat(self, filename, folderName):
        z = tarfile.open(filename, 'r')
        names = []
        for n in z.getnames():
            basename = os.path.basename(n)
            i = z.getmember(n)
            if basename and i.isfile() is True:
                filename = os.path.join(folderName, basename)
                with file(filename, 'wb') as f:
                    f.write(z.extractfile(i).read())
                names.append(basename)
        z.close()
        return names

    # unpacking that flattens file structure
    def unZipFlat(self, filename, folderName):
        z = zipfile.ZipFile(filename, 'r')
        names = []
        for n in z.namelist():
            basename = os.path.basename(n)
            i = z.getinfo(n)
            if basename and i.compress_type is not zipfile.ZIP_STORED and i.file_size > 0:
                filename = os.path.join(folderName, basename)
                with file(filename, 'wb') as f:
                    f.write(z.read(n))
                names.append(basename)
        z.close()
        return names

    def unPack(self, filename, folderName, preserve_structure=False):
        if preserve_structure is False:
            try:
                return self.unZipFlat(filename, folderName)
            except zipfile.BadZipfile:
                return self.unTarFlat(filename, folderName)
        else:
            try:
                return self.unZip(filename, folderName)
            except zipfile.BadZipfile:
                return self.unTar(filename, folderName)

    def unpackPackagedFile(self, uf, preserve_structure=True, folderName=None):
        ''' This method unpacked uploaded file into a proper location '''

        uniq = uf.resource.get('resource_uniq') or shortuuid.uuid()
        unpack_dir = os.path.join(UPLOAD_DIR, bq.core.identity.get_user().name, uniq)

        filepath = uf.localpath()
        if filepath is None:
            log.debug('unpackPackagedFile file object has no local path: [%s], move local', uf.fileobj)
            filepath = uf.ensurelocal( os.path.join(unpack_dir, os.path.basename(uf.resource.get('name'))))

        if folderName is None:
            unpack_dir = os.path.join(unpack_dir, '%s.UNPACKED'%os.path.basename(uf.filename))
            unpack_dir = unpack_dir.replace('\\', '/')
        else:
            unpack_dir = folderName
        _mkdir (unpack_dir)

        log.debug('unpackPackagedFile, filepath: [%s]', filepath )
        log.debug('unpackPackagedFile, unpack_dir: [%s]', unpack_dir )

        # unpack the contents of the packaged file
        try:
            members = self.unPack(filepath, unpack_dir, preserve_structure)
        except Exception:
            log.exception('Problem unpacking %s in %s' , filepath, unpack_dir)
            raise

        return unpack_dir, members

#------------------------------------------------------------------------------
# process separate packaged resources (zip/tar.gz)
#------------------------------------------------------------------------------

    def process_packaged_separate(self, uf, **kw):
        unpack_dir, members = self.unpackPackagedFile(uf)
        members = list(set(members)) # remove duplicates
        members = [ m for m in members if is_filesystem_file(m) is not True ] # remove file system internal files
        members = sorted(members, key=blocked_alpha_num_sort) # use alpha-numeric sort
        members = [ '%s/%s'%(unpack_dir, m) for m in members ] # full paths
        members = [ m for m in members if os.path.isdir(m) is not True ] # remove directories

        basepath = '%s/'%unpack_dir
        resources = []
        for filename in members:
            name = os.path.join('%s.unpacked'%uf.resource.get('name'), filename.replace(basepath, '')).replace('\\', '/')
            resource = etree.Element ('resource', name=name, value=filename, ts=uf.ts)
            # append all other input annotations
            resource.extend (copy.deepcopy (list (uf.resource)))

            myf = UploadedResource(fileobj=open(filename, 'rb'), resource=resource)
            resources.append(self.process(myf))

        return unpack_dir, resources

#------------------------------------------------------------------------------
# zip/tar.gz Import for 5D image
#------------------------------------------------------------------------------

    def process_packaged_5D(self, uf, **kw):
        log.debug('process_packaged_5D: %s', kw)

        unpack_dir, members = self.unpackPackagedFile(uf)
        members = [ m for m in members if is_filesystem_file(m) is not True ] # remove file system internal files
        members = sorted(members, key=blocked_alpha_num_sort) # use alpha-numeric sort
        members = [ '%s/%s'%(unpack_dir, m) for m in members ] # full paths
        #members = [ m for m in members if os.path.exists(m) is True ] # remove missing files
        members = [ m for m in members if os.path.isdir(m) is not True ] # remove directories

        z = int(kw['number_z']) if 'number_z' in kw else None
        t = int(kw['number_t']) if 'number_t' in kw else None
        c = int(kw.get('number_c', 0))

        # try to guess automatically the number of planes for only Z or only T series
        num_pages = len(members)/c if c>1 else len(members)
        if z==0 and t is None:
            z=num_pages
            t=1
        elif t==0 and z is None:
            t=num_pages
            z=1

        resource = etree.Element ('image', name='%s.series'%uf.resource.get('name'), resource_type='image')
        for v in members:
            val = etree.SubElement(resource, 'value' )
            val.text = blob_service.local2url(v)

        #find image meta in the input resource
        image_meta = None
        x = uf.resource.xpath('tag[@name="image_meta" and @type="image_meta"]')
        if len(x)>0:
            x = x[0]
            resource.append(copy.deepcopy(x))
            uf.resource.remove(x)
            image_meta = resource.xpath('tag[@name="image_meta" and @type="image_meta"]')[0]
        else:
            image_meta = etree.SubElement(resource, 'tag', name='image_meta', type='image_meta') #, resource_unid='image_meta' )

        overwrite_xmlattr(image_meta, 'tag', name='storage', value='multi_file_series')
        overwrite_xmlattr(image_meta, 'tag', name='image_num_z', value='%s'%z, type='number' )
        overwrite_xmlattr(image_meta, 'tag', name='image_num_t', value='%s'%t, type='number' )
        if c>1:
            overwrite_xmlattr(image_meta, 'tag', name='image_num_c', value='%s'%c, type='number' )
        overwrite_xmlattr(image_meta, 'tag', name='dimensions', value='XYCZT' )
        if float(kw.get('resolution_x', 0))>0:
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_x', value='%s'%kw['resolution_x'], type='number' )
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_unit_x', value='microns' )
        if float(kw.get('resolution_y', 0))>0:
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_y', value='%s'%kw['resolution_y'], type='number' )
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_unit_y', value='microns' )
        if float(kw.get('resolution_z', 0))>0:
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_z', value='%s'%kw['resolution_z'], type='number' )
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_unit_z', value='microns' )
        if float(kw.get('resolution_t', 0))>0:
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_t', value='%s'%kw['resolution_t'], type='number' )
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_unit_t', value='seconds' )

        # append all other input annotations
        resource.extend (copy.deepcopy (list (uf.resource)))

        # pass a temporary top directory where the sub-files are stored
        return unpack_dir, blob_service.store_blob(resource=resource, rooturl = blob_service.local2url('%s/'%unpack_dir))

#------------------------------------------------------------------------------
# process proprietary series file and create multiple resources if needed
#------------------------------------------------------------------------------

    def process_series_proprietary(self, uf, intags):
        ''' process proprietary series file and create multiple resources if needed '''
        log.debug('process_series_proprietary: %s %s', uf, intags )
        resources = []

        # first upload the first series
        name = '%s#0'%uf.resource.get('name')
        value = '%s#0'%(uf.resource.get('value') or uf.resource.get('name'))

        resource = etree.Element ('image', name=name, value=value, resource_type='image', ts=uf.ts)
        # append all other input annotations
        resource.extend (copy.deepcopy (list (uf.resource)))
        resource = blob_service.store_blob(resource=resource, fileobj=uf.fileobj)
        iname = name # resource.get('name')
        ivalue = resource.get('value')
        resources.append(resource)

        # then include resources for subsequent series
        for n in range(intags.get('image_num_series', 0))[1:]:
            name = iname.replace('#0', '#%s'%n) if '#' in iname else '%s#%s'%(iname, n)
            value = ivalue.replace('#0', '#%s'%n) if '#' in ivalue else '%s#%s'%(ivalue, n)

            resource = etree.Element ('image', name=name, value=value, resource_type='image', ts=uf.ts)
            # append all other input annotations
            resource.extend (copy.deepcopy (list (uf.resource)))
            resource = blob_service.store_blob(resource=resource)
            resources.append(resource)
        return resources

#------------------------------------------------------------------------------
# multi-series files supported by decoders
#------------------------------------------------------------------------------

    def process_packaged_series_proprietary(self, uf, intags):
        ''' Unpack and insert a proprietary multi-file-multi-image series '''
        log.debug('process_packaged_series_proprietary: %s %s', uf, intags )

        unpack_dir, members = self.unpackPackagedFile(uf)
        members = [ m for m in members if is_filesystem_file(m) is not True ] # remove file system internal files
        members = sorted(members, key=blocked_alpha_num_sort) # use alpha-numeric sort
        members = [ '%s/%s'%(unpack_dir, m) for m in members ] # full paths
        members = [ m for m in members if os.path.isdir(m) is not True ] # remove directories
        log.debug('process_packaged_series_proprietary members: %s', members)

        # first find the header file
        headers = []

        # first priority are fixed named files
        for m in members:
            if os.path.basename(m) in self.series_headers:
                headers.append(m)

        # second priority all files with the series extension
        for m in members:
            ext = os.path.splitext(m)[-1].lower().replace('.', '')
            if ext in self.series_exts and m not in headers:
                headers.append(m)
        log.debug('headers: %s', headers)

        # get file info and know how many sub-series are there
        num_series = 0
        for header in headers:
            log.debug('filename: %s', header)
            info = image_service.get_info(header)
            log.debug('info: %s', info)
            if info is not None and info.get('image_num_series', 0)>0:
                num_series = info.get('image_num_series', 0)
                break
        log.debug('detected header: %s', header)

        if num_series<1:
            return unpack_dir, []

        members.remove(header)

        # insert sub-series with the first value as a header file
        n = 0
        if num_series>1:
            name = '%s#%s'%(os.path.splitext(uf.resource.get('name'))[0], n)
        else:
            name = os.path.splitext(uf.resource.get('name'))[0]
        resource = etree.Element ('image', name=name, resource_type='image', ts=uf.ts)

        # add header first
        val = etree.SubElement(resource, 'value' )
        if num_series>1:
            val.text = '%s#%s'%(blob_service.local2url(header), n)
        else:
            val.text = blob_service.local2url(header)

        # add the rest of the files later without #
        for v in members:
            val = etree.SubElement(resource, 'value' )
            val.text = blob_service.local2url(v)

        # append all other input annotations
        resource.extend (copy.deepcopy (list (uf.resource)))
        resource = blob_service.store_blob(resource=resource, rooturl=blob_service.local2url('%s/'%unpack_dir))

        resources = [resource]

        # insert the rest of the series
        # use final storage location of the first resource and submit directly to data service
        values = resource.xpath('value')
        values = [v.text for v in values]
        for n in range(num_series)[1:]:
            resource = etree.Element ('image', name=name.replace('#0', '#%s'%n), resource_type='image', ts=uf.ts)

            # add values
            for v in values:
                val = etree.SubElement(resource, 'value' )
                val.text = v.replace('#0', '#%s'%n)

            # append all other input annotations
            resource.extend (copy.deepcopy (list (uf.resource)))

            #all resource values should have been previously stored (this will register the resource)
            resources.append(blob_service.store_blob(resource=resource))

        return unpack_dir, resources


#------------------------------------------------------------------------------
# dicom files
#------------------------------------------------------------------------------

    def process_packaged_dicom(self, uf, intags):
        ''' Unpack and insert a set of DICOM files '''
        log.debug('process_packaged_dicom: %s %s', uf, intags )

        unpack_dir, members = self.unpackPackagedFile(uf)
        members = [ m for m in members if is_filesystem_file(m) is not True ] # remove file system internal files
        members = sorted(members, key=blocked_alpha_num_sort) # use alpha-numeric sort
        members = [ '%s/%s'%(unpack_dir, m) for m in members ] # full paths
        members = [ m for m in members if os.path.isdir(m) is not True ] # remove directories
        log.debug('process_packaged_dicom members: %s', members)

        # first group dicom files based on their metadata
        images, blobs, geometry = ConverterImgcnv.group_files_dicom(members)

        log.debug('process_packaged_dicom blobs: %s', blobs)
        log.debug('process_packaged_dicom images: %s', images)
        log.debug('process_packaged_dicom geometry: %s', geometry)

        resources = []
        base_name = uf.resource.get('name')
        base_path = '%s/'%unpack_dir

        log.debug('base_name: %s', base_name)
        log.debug('base_path: %s', base_path)

        # first insert blobs
        for b in blobs:
            name = posixpath.join(base_name, b.replace(base_path, '') )
            value = blob_service.local2url(b)
            resource = etree.Element ('resource', name=name, ts=uf.ts, value=value )
            resource.extend (copy.deepcopy (list (uf.resource)))
            #resources.append(blob_service.store_blob(resource=resource, rooturl = blob_service.local2url('%s/'%unpack_dir)))
            resources.append(self.process(UploadedResource(resource=resource, path=b)))

        # now insert images
        for i in range(len(images)):
            im = images[i]
            g = geometry[i]
            updated_name = None
            rooturl = blob_service.local2url('%s/'%unpack_dir)

            if len(im) == 1:
                name = posixpath.join(base_name, im[0].replace(base_path, '') )
                value = blob_service.local2url(im[0])
                resource = etree.Element ('image', name=name, resource_type='image', ts=uf.ts, value=value )
            else:
                name = posixpath.join(base_name, im[0].replace(base_path, '') )
                #updated_name = os.path.basename(im[0])
                rooturl = blob_service.local2url(os.path.dirname(im[0])+'/')
                #rooturl = blob_service.local2url(im[0])

                #name = base_name
                resource = etree.Element ('image', name=name, resource_type='image', ts=uf.ts)
                for v in im:
                    val = etree.SubElement(resource, 'value', type='string' )
                    val.text = blob_service.local2url(v)

                image_meta = etree.SubElement(resource, 'tag', name='image_meta', type='image_meta', resource_unid='image_meta' )
                etree.SubElement(image_meta, 'tag', name='storage', value='multi_file_series' )
                etree.SubElement(image_meta, 'tag', name='image_num_z', value='%s'%g['z'], type='number' )
                etree.SubElement(image_meta, 'tag', name='image_num_t', value='%s'%g['t'], type='number' )
                etree.SubElement(image_meta, 'tag', name='dimensions', value='XYCZT' )

            resource.extend (copy.deepcopy (list (uf.resource)))
            ConverterImgcnv.meta_dicom_parsed(im[0], resource)

            log.debug('Resource to insert: %s', etree.tostring(resource))

            # store resource
            resource = blob_service.store_blob(resource=resource, rooturl=rooturl)

            # a bit of funky processing for the multi-value case, we want files to be stored in the same path as all the other files
            # but at the same time we would like to give individual names to individual groups
            # if updated_name:
            #     log.debug('Updating resource name to: %s for: %s', updated_name, etree.tostring(resource))
            #     resource.set('name', updated_name)
            #     log.debug('Updating resource: %s', etree.tostring(resource))
            #     data_service.update_resource(resource=resource, new_resource=resource, replace=False)

            resources.append(resource)

        return unpack_dir, resources

#------------------------------------------------------------------------------
# import an image part of 5D image
#------------------------------------------------------------------------------

    def process_part_5d(self, uf, **kw):
        log.debug('process_part_5d: %s', kw)

        #dima: find resource, add part

        unpack_dir, members = self.unpackPackagedFile(uf)
        members = [ m for m in members if is_filesystem_file(m) is not True ] # remove file system internal files
        members = sorted(members, key=blocked_alpha_num_sort) # use alpha-numeric sort
        members = [ '%s/%s'%(unpack_dir, m) for m in members ] # full paths
        #members = [ m for m in members if os.path.exists(m) is True ] # remove missing files
        members = [ m for m in members if os.path.isdir(m) is not True ] # remove directories

        z = int(kw['number_z']) if 'number_z' in kw else None
        t = int(kw['number_t']) if 'number_t' in kw else None
        c = int(kw.get('number_c', 0))

        # try to guess automatically the number of planes for only Z or only T series
        num_pages = len(members)/c if c>1 else len(members)
        if z==0 and t is None:
            z=num_pages
            t=1
        elif t==0 and z is None:
            t=num_pages
            z=1

        resource = etree.Element ('image', name='%s.series'%uf.resource.get('name'), resource_type='image')
        for v in members:
            val = etree.SubElement(resource, 'value' )
            val.text = blob_service.local2url(v)

        #find image meta in the input resource
        image_meta = None
        x = uf.resource.xpath('tag[@name="image_meta" and @type="image_meta"]')
        if len(x)>0:
            x = x[0]
            resource.append(copy.deepcopy(x))
            uf.resource.remove(x)
            image_meta = resource.xpath('tag[@name="image_meta" and @type="image_meta"]')[0]
        else:
            image_meta = etree.SubElement(resource, 'tag', name='image_meta', type='image_meta') #, resource_unid='image_meta' )

        overwrite_xmlattr(image_meta, 'tag', name='storage', value='multi_file_series')
        overwrite_xmlattr(image_meta, 'tag', name='image_num_z', value='%s'%z, type='number' )
        overwrite_xmlattr(image_meta, 'tag', name='image_num_t', value='%s'%t, type='number' )
        if c>1:
            overwrite_xmlattr(image_meta, 'tag', name='image_num_c', value='%s'%c, type='number' )
        overwrite_xmlattr(image_meta, 'tag', name='dimensions', value='XYCZT' )
        if float(kw.get('resolution_x', 0))>0:
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_x', value='%s'%kw['resolution_x'], type='number' )
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_unit_x', value='microns' )
        if float(kw.get('resolution_y', 0))>0:
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_y', value='%s'%kw['resolution_y'], type='number' )
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_unit_y', value='microns' )
        if float(kw.get('resolution_z', 0))>0:
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_z', value='%s'%kw['resolution_z'], type='number' )
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_unit_z', value='microns' )
        if float(kw.get('resolution_t', 0))>0:
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_t', value='%s'%kw['resolution_t'], type='number' )
            overwrite_xmlattr(image_meta, 'tag', name='pixel_resolution_unit_t', value='seconds' )

        # append all other input annotations
        resource.extend (copy.deepcopy (list (uf.resource)))

        # pass a temporary top directory where the sub-files are stored
        return unpack_dir, blob_service.store_blob(resource=resource, rooturl = blob_service.local2url('%s/'%unpack_dir))

#------------------------------------------------------------------------------
# JSON files
#------------------------------------------------------------------------------

    def process_json(self, uf, intags):
        ''' Unpack and insert JSON file '''
        log.debug('process_json: %s %s', uf, intags )

        #uniq = uf.resource.get('resource_uniq') or shortuuid.uuid()
        #unpack_dir = os.path.join(UPLOAD_DIR, bq.core.identity.get_user().name, uniq)

        filepath = uf.localpath()
        #KGK should always have a localpath for an uploaded file
        #if filepath is None:
        #    log.debug('process_json file object has no local path: [%s], move local', uf.fileobj)
        #    filepath = uf.ensurelocal( os.path.join(unpack_dir, os.path.basename(uf.resource.get('name'))))

        resources = []
        doc = {}
        if filepath is not None:
            with open(filepath, 'r') as fo:
                doc = json.load(fo)
        elif uf.fileobj is not None:
            doc = json.load(uf.fileobj)
            uf.fileobj.seek(0)   # rewind for later reading
        else:
            log.error("No filename or fileobj for JSON file")

        # This is a poor man's detector for Dream3D pipeline files; other JSON types could be added later.
        if 'PipelineBuilder' in doc and 'Version' in doc['PipelineBuilder'] and 'Number_Filters' in doc['PipelineBuilder']:
            # Dream3D pipeline file
            #resource = etree.Element ('resource', name=doc['PipelineBuilder']['Name'], value= blob_service.local2url(filepath), resource_type='dream3d_pipeline', ts=uf.ts)
            #etree.SubElement(resource, 'tag', name='Version', value=doc['PipelineBuilder']['Version'])
            #etree.SubElement(resource, 'tag', name='Number Filters', value=str(doc['PipelineBuilder']['Number_Filters']), type='number')
            #resource = blob_service.store_blob(resource=resource, rooturl=blob_service.local2url('file://%s/'%unpack_dir))
            #resources.append(resource)
            #uf.resource.set ('name', doc['PipelineBuilder']['Name'])
            #uf.resource.set ('value', blob_service.local2url(filepath))
            uf.resource.set ('resource_type', 'dream3d_pipeline')

            etree.SubElement(uf.resource, 'tag', name='Version', value=doc['PipelineBuilder']['Version'])
            etree.SubElement(uf.resource, 'tag', name='Number Filters', value=str(doc['PipelineBuilder']['Number_Filters']), type='number')
            #resource = blob_service.store_blob(resource=resource, rooturl=blob_service.local2url('file://%s/'%unpack_dir))
            #resources.append(resource)

        #if len(resources) == 0:
        #    return unpack_dir, [self.insert_resource(uf)]   # fall back to default
        #else:
        #    return unpack_dir, resources
        return [self.insert_resource(uf)]   # fall back to default


#------------------------------------------------------------------------------
# Import archives exported by a BISQUE system
#------------------------------------------------------------------------------
    def safePath(self, path, base):
        path = os.path.normpath(path)
        if path.startswith(os.path.normpath(base)): # on windows normpath changes slashes
            return path
        else:
            return os.path.basename(path)

    def parseFile(self, filename, path, relpath):
        log.debug('parseFile filename: [%s] path: [%s] relpath: [%s]', filename, path, relpath)
        mpath = self.safePath(os.path.join(path, filename), path)
        log.debug('parseFile mpath: [%s]', mpath)
        if not os.path.exists(mpath):
            return etree.Element ('tag', name=filename)
        xml = etree.parse(mpath).getroot()

        log.debug('parseFile xml: %s', etree.tostring(xml))

        # if a resource has a value pointing to a file
        bpath = self.safePath(os.path.join(path, os.path.dirname(filename), xml.get('value', '')), path)
        if xml.get('value') is not None and os.path.exists(bpath) is True:
            xml.set('name', os.path.join(relpath, os.path.dirname(filename), xml.get('value')).replace('\\', '/'))
            del xml.attrib['value']
            return blob_service.store_blob(resource=xml, fileobj=open(bpath, 'rb'))

        # if a resource is a multi-blob resource
        elif xml.tag != 'dataset' and len(xml.xpath('value'))>0:
            subdir = os.path.dirname(filename)
            xml.set('name', os.path.join(relpath, subdir, xml.get('name')).replace('\\', '/'))
            for v in xml.xpath('value'):
                bpath = self.safePath(os.path.join(path, subdir, v.text), path).replace('\\', '/')
                if os.path.exists(bpath) is True:
                    v.text = blob_service.local2url(bpath)
            return blob_service.store_blob(resource=xml, rooturl = blob_service.local2url('%s/'%path))

        # if a resource is an xml doc
        elif xml.tag not in ['dataset', 'mex', 'user', 'system', 'module', 'store']:
            return data_service.new_resource(resource=xml)

        # dima: if a res is an xml of a system type, store as blob
        elif xml.tag in ['mex', 'user', 'system', 'module', 'store']:
            return etree.Element (xml.tag, name=xml.get('name', ''))
        #    return blob_service.store_blob(resource=xml)

        # if the resource is a dataset
        elif xml.tag == 'dataset':
            members = xml.xpath('/dataset/value')
            for member in members:
                r = self.parseFile(member.text, path, relpath)
                member.text = r.get('uri')
            return data_service.new_resource(resource=xml)

    # dima: need to pass relative storage path
    def process_packaged_bisque(self, f, tags):
        ''' Process packages file containing Bisque archive '''
        log.debug('process_packaged_bisque: %s', f)
        relpath = os.path.dirname(f.orig)
        unpack_dir, members = self.unpackPackagedFile(f)

        # parse .bisque.xml
        resources = []
        header = os.path.join(unpack_dir, '.bisque.xml')
        if os.path.exists(header):
            xml = etree.parse(header).getroot()
            members = xml.xpath('value')
            for m in members:
                r = self.parseFile(m.text, unpack_dir, relpath)
                if r is not None:
                    resources.append(r)
        return unpack_dir, resources

#---------------------------------------------------------------------------------------
# packaging misc
#---------------------------------------------------------------------------------------

    def cleanup_packaging(self, unpack_dir):
        "cleanup and packaging details "
        if os.path.isdir(unpack_dir):
            try:
                shutil.rmtree (unpack_dir, ignore_errors=True)
            except OSError:
                log.warning('Problem removing upload directory: %s', unpack_dir)


#---------------------------------------------------------------------------------------
# filters, take f and return a list of file names
#---------------------------------------------------------------------------------------

    def filter_zip_multifile(self, f, intags):
        unpack_dir, resources = self.process_packaged_separate(f, intags=intags)
        self.cleanup_packaging(unpack_dir)
        return resources

    def filter_zip_bisque(self, f, intags):
        unpack_dir, resources = self.process_packaged_bisque(f, intags)
        self.cleanup_packaging(unpack_dir)
        return resources

    def filter_zip_tstack(self, f, intags):
        unpack_dir, resource = self.process_packaged_5D(f, number_t=0, **intags)
        self.cleanup_packaging(unpack_dir)
        return [resource]

    def filter_zip_zstack(self, f, intags):
        unpack_dir, resource = self.process_packaged_5D(f, number_z=0, **intags)
        self.cleanup_packaging(unpack_dir)
        return [resource]

    def filter_5d_image(self, f, intags):
        unpack_dir, resource = self.process_packaged_5D(f, **intags)
        self.cleanup_packaging(unpack_dir)
        return [resource]

    def filter_series_proprietary(self, f, intags):
        resources = self.process_series_proprietary(f, intags)
        return resources

    def filter_zip_proprietary(self, f, intags):
        unpack_dir, resources = self.process_packaged_series_proprietary(f, intags)
        self.cleanup_packaging(unpack_dir)
        return resources

    def filter_zip_dicom(self, f, intags):
        unpack_dir, resources = self.process_packaged_dicom(f, intags)
        self.cleanup_packaging(unpack_dir)
        return resources

    def filter_part_5d(self, f, intags):
        unpack_dir, resource = self.process_part_5d(f, **intags)
        return [resource]

    def filter_json(self, f, intags):
        #unpack_dir, resources = self.process_json(f, intags)
        #self.cleanup_packaging(unpack_dir)
        resources = self.process_json(f, intags)
        return resources

#------------------------------------------------------------------------------
# file ingestion support functions
#------------------------------------------------------------------------------

    def insert_resource(self, uf):
        """ effectively inserts the file into the bisque database and returns
        a document describing an ingested resource
        """
        # try inserting the file in the blob service
        try:
            # determine if resource is already on a blob_service store
            log.debug('Inserting %s', uf)
            resource = blob_service.store_blob(resource=uf.resource, fileobj=uf.fileobj)
            log.debug('Inserted resource :::::\n %s', etree.tostring(resource) )
        except Exception, e:
            log.exception("Error during store %s" ,  etree.tostring(uf.resource))
            return None
        finally:
            uf.close()

        #uf.fileobj = None
        #uf.resource = resource
        return resource

    def process_filtered(self, uf, intags):
        # start processing
        log.debug('processing filtered, ingest tags: %s',  intags )
        error = None

        #if uf.localpth is None:
        #    move_file (fp, localpath)

        # Ensure the uploaded file is local and named properly.
        #tags = copy.deepcopy (list (uf.resource))
        #name = uf.resource.get('name')
        #del uf.resource[:]
        #resource = self.insert_resource (uf)
        #resource.set('name', name)
        #resource.extend (tags)

        try:
            # call filter on f with ingest tags
            #resources = self.filters[ intags['type'] ](UploadedResource(resource, orig=uf.orig), intags)
            resources = self.filters[ intags['type'] ](uf, intags)
        except Exception, e:
            log.exception('Problem in processing file: %s : %s'  ,  intags.get ('type',''), str(uf))
            error = 'Problem processing the file: %s'%e

        # some error during pre-processing
        if error is not None:
            log.debug('filters error: %s',  error )
            resource = etree.Element('file', name=uf.filename)
            etree.SubElement(resource, 'tag', name='error', value=error)
            return resource

        # some error during pre-processing
        if len(resources)<1:
            log.debug('error while extracting images, none extracted' )
            resource = etree.Element('file', name=uf.filename)
            etree.SubElement(resource, 'tag', name='error', value='error while extracting images, none extracted')
            return resource

        # if only one resource was inserted, return right away
        if len(resources)==1:
            return resources[0]

        # multiple resources ingested, we need to group them into a dataset and return a reference to it
        # now we'll just return a stupid stub
        dataset = etree.Element('dataset', name='%s'%(uf.filename))
        etree.SubElement(dataset, 'tag', name='upload_datetime', value=uf.ts, type='datetime' )

        #if resource.get('uri') is not None:
        #    etree.SubElement(dataset, 'tag', name="original_upload", value=resource.get('uri'), type='resource' )

        index=0
        for r in resources:
            # check for ingest errors here as well
            if r.get('uri') is not None:
                # index is giving trouble
                #v = etree.SubElement(resource, 'value', index='%s'%index, type='object')
                v = etree.SubElement(dataset, 'value', type='object')
                v.text = r.get('uri')
            else:
                s = 'Error ingesting element %s with the name "%s"'%(index, r.get('name'))
                etree.SubElement(dataset, 'tag', name="error", value=s )
            index += 1

        log.debug('processed resource :::::\n %s',  etree.tostring(dataset) )
        resource = data_service.new_resource(resource=dataset, view='deep')
        log.debug('process created resource :::::\n %s',  etree.tostring(resource) )
        return resource

    def process(self, uf):
        """ processes the UploadedResource and either ingests it inplace or first applies
        some special pre-processing, the function returns a document
        describing an ingested resource
        """

        # This forces the the filename to part of actually file
        #if uf.path and not os.path.basename (uf.path).endswith( uf.filename):
        #    newpath = "%s-%s" % (uf.path, uf.filename)
        #    shutil.move ( uf.path, newpath)
        #    uf.path = newpath
        #    uf.resource.set ('value', 'file://%s' % newpath)

        # first if tags are present ensure they are in an etree format
        # figure out if a file requires special processing
        intags = {}
        xl = uf.resource.xpath('//tag[@name="ingest"]')
        if len(xl):
            intags = dict([(t.get('name'), t.get('value'))
                           for t in xl[0].xpath('tag')
                           if t.get('value') is not None and t.get('name') is not None ])
            # remove the ingest tags from the tag document
            uf.resource.remove(xl[0])

        log.debug('Resource type: %s', uf.get_type())
        needs_guessing = (uf.get_type() == 'resource' or uf.get_type() == 'image')

        # append processing tags based on file type and extension
        mime = None
        if needs_guessing is True:
            log.debug('Guessing the mime type for: %s', sanitize_filename(uf.filename))
            mime = mimetypes.guess_type(sanitize_filename(uf.filename))[0]
        if mime in self.filters:
            intags['type'] = mime

        # take care of funny extension cases: force deep guessing
        # 1) no extension, which might be in a form of some long string
        # 2) numerical extension as is used in Nanoscope images with numerical extensions
        ext = os.path.splitext(uf.filename)[1]
        noext = (ext == '' or len(ext)>10 or ext.isdigit() is True)
        if ext.replace('.', '') in self.non_image_exts:
            needs_guessing = False
        if needs_guessing is True and mime is None and noext:
            log.debug('process: setting mime to "image/series"' )
            mime = 'image/series'

        # check if an image can be a series
        log.debug('mime: %s', mime)
        log.debug('process uf: %s', uf)
        if mime == 'image/series':
            filename = uf.localpath()
            if filename is None and uf.fileobj is not None:
                log.debug('process, file object has no local path: [%s], move local', uf.fileobj)
                filename = uf.ensurelocal( os.path.join(UPLOAD_DIR, bq.core.identity.get_user().name, shortuuid.uuid(), os.path.basename(uf.resource.get('name'))))

            log.debug('process filename: %s', filename)
            info = image_service.get_info(filename)
            log.debug('process info: %s', info)
            if info is not None:
                if info.get('image_num_x', 0)>1 and noext:
                    intags['type'] = 'image/proprietary'
                if info.get('image_num_series', 0)>1:
                    intags['type'] = 'image/proprietary'
                    intags['image_num_series'] = info.get('image_num_series', 0)

        # try to annotate DICOM files
        filename = uf.localpath()
        if needs_guessing and filename is not None:
            ConverterImgcnv.meta_dicom(filename, xml=uf.resource)

        # no processing required
        log.debug('process intags: %s', intags)
        if intags.get('type') not in self.filters:
            return self.insert_resource(uf)
        # Processing is required
        return self.process_filtered(uf, intags)

    def ingest(self, files):
        """ ingests each elemen of the list of files
        """
        response = etree.Element ('resource', type='uploaded')
        for f in files:
            log.info ("processing %s", f)
            x = self.process(f)
            log.info ("processed %s -> %s", toascii(f), toascii(x))
            if x is not None:
                response.append(x)
            else:
                log.error ("while ingesting %s", toascii(f))
                etree.SubElement(response, 'tag', name="error", value='Error ingesting file' )
        return response

#------------------------------------------------------------------------------
# Main import for files
# Accepts multi-part form with a file and associated tags in XML format
# form parts should be something like this: file and file_resource
#
# The tag XML document is in the following form:
# <resource>
#     <tag name='any tag' value='any value' />
#     <tag name='another' value='new value' />
# </resource>
#
#
#The document can also contain special tag for prosessing and additional info:
#<resource>
#    <tag name='any tag' value='any value' />
#    <tag name='ingest'>
#
#        Permission setting for imported image as: 'private' or 'published'
#        <tag name='permission' value='private' />
#        or
#        <tag name='permission' value='published' />
#
#        Image is a multi-file compressed archive, should be uncompressed and images ingested individually:
#        <tag name='type' value='zip-multi-file' />
#        or
#        Image is a compressed archive containing multiple files composing a time-series image:
#        <tag name='type' value='zip-time-series' />
#        or
#        Image is a compressed archive containing multiple files composing a z-stack image:
#        <tag name='type' value='zip-z-stack' />
#        or
#        Image is a compressed archive containing multiple files composing a 5-D image:
#        <tag name='type' value='zip-5d-image' />
#        This tag must have two additional tags with numbers of T and Z planes:
#        <tag name='number_z' value='XXXX' />
#        <tag name='number_t' value='XXXXX' />
#
#    </tag>
#</resource>
#
#Example for a file "example.zip":
#
#<resource>
#    <tag name='any tag' value='any value' />
#    <tag name='ingest'>
#        <tag name='permission' value='published' />
#        <tag name='type' value='zip-5d-image' />
#        <tag name='number_z' value='XXXX' />
#        <tag name='number_t' value='XXXXX' />
#    </tag>
#</resource>
#
#------------------------------------------------------------------------------

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def _default(self, *args, **kw):
        log.debug ("import_default %s %s", args, kw)
        if len(args) and args[0].startswith('transfer'):
            return self.transfer (**kw)

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def transfer(self, **kw):
        """Recieve a multipart form with images and possibly tag documents

        :param kw: A keyword dictionary of file arguments.  The
        arguments are organized as follows: Each datafile and its tag
        document are associated by the parameters named 'x' and
        'x_resource' where x can be any string.

        """
        try:
            return self.transfer_internal(**kw)
        except Exception, e:
            log.exception("During transfer: %s" , str(kw))
            abort(500, 'Internal error during upload')



    @classmethod
    def multipart_processing (cls, uploaded, headers):
        import multipart
        upload_dir = os.path.join(UPLOAD_DIR, bq.core.identity.get_user().name)
        config={'MAX_MEMORY_FILE_SIZE' : 0,
                'UPLOAD_DIR' : upload_dir,
                #'UPLOAD_KEEP_FILENAME': True,  # uses full filename
                #'UPLOAD_KEEP_EXTENSIONS': True,
                'UPLOAD_DELETE_TMP' :False,
        }

        class g(object):
            resource = None
            fileobj = None  # A file descriptor to the tmp file
            filename = None # Original filename
            filepath = None # local path to the file

        def on_field (field):
            log.debug ("FIELD %s=%s", field.field_name, field.value)
            g.resource = field.value

        def on_file(fle):
            log.debug ("FILE %s %s %s", fle.actual_file_name, fle.field_name, fle.size)
            g.filepath = os.path.join (upload_dir, fle.actual_file_name)
            g.filename = fle.file_name
            g.fileobj = g.filepath and open (g.filepath, 'rb') #tmp File will be deleted unless we open it.

        _mkdir(upload_dir)
        with open (uploaded) as input_stream:
            parser = multipart.multipart.create_form_parser(headers, on_field,on_file, config=config)
            content_length = headers.get('Content-Length')
            if content_length is not None:
                content_length = int(content_length)
            else:
                content_length = float('inf')
            bytes_read = 0

            while True:
                # Read only up to the Content-Length given.
                max_readable = min(content_length - bytes_read, 1048576*128) # 128 MB chunks
                buff = input_stream.read(max_readable)

                # Write to the parser and update our length.
                parser.write(buff)
                bytes_read += len(buff)

                # If we get a buffer that's smaller than the size requested, or if we
                # have read up to our content length, we're done.
                if len(buff) != max_readable or bytes_read == content_length:
                    break

            # Tell our parser that we're done writing data.
            parser.finalize()
        return g

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def transfer_x_file (self):
        log.info ("X_file %s ", tg.request.headers) # ,  tg.request.body_file.read())

        uploaded  = tg.request.headers.get ('X-File', None)
        if uploaded is None:
            log.error ("No X-file was set for special upload")
            abort (400, "No X-file header")

        try:
            g = None
            if os.path.exists (uploaded):
                with Timer () as t:
                    g = self.multipart_processing (uploaded, tg.request.headers)
                filesize = os.path.getsize (uploaded)
                log.info("multipart parsing %s in %s (%s/s) -> %s", uploaded, t.interval, sizeof_fmt(filesize/t.interval), g.filepath)
                os.remove (uploaded)
            else:
                log.error ("Unable to access X-File %s", uploaded)
                abort (400, "No server access to uploaded file")

            if g.resource is None:
                g.resource = "<resource/>"
            log.debug ("reading XML %s" ,  g.resource)
            try:
                g.resource = etree.fromstring(g.resource)
                #pylint: disable=maybe-no-member
                if g.filename and g.resource.attrib.get ('name', None) is None:
                    g.resource.set ('name', os.path.basename (g.filename))
                if g.filepath:
                    g.resource.set ('value', "file://%s" % g.filepath)
            except etree.XMLSyntaxError:
                log.exception ("while parsing %s" , g.resource)
                abort (400, "illegal xml")

            response =  self.ingest ([UploadedResource (fileobj = g.fileobj, resource=g.resource)])
            return etree.tostring (response)
        except Exception as e:
            log.exception ("During upload")
            abort (400, "Unable to complete upload")
        finally:
            if os.path.exists (uploaded):
                log.error ("Removing left over file: %s", uploaded)
                os.remove (uploaded)
            if g and g.fileobj:
                g.fileobj.close()
            if g and os.path.exists (g.filepath):
                os.remove (g.filepath)


    def transfer_internal(self, **kw):
        """Recieve a multipart form with images and possibly tag documents

        :param kw: A keyword dictionary of file arguments.  The
        arguments are organized as follows: Each datafile and its tag
        document are associated by the parameters named 'x' and
        'x_resource' where x can be any string.

        """
        #log.debug("TRANSFER %s"  % kw)
        #log.debug("BODY %s " % request.body[:100])
        files = []
        transfers = dict(kw)
        '''find a related parameter (to pname) containing resource XML

            :param transfer: hash of form parameters
            :param pname   : field parameter of file object
            '''

        def find_upload_resource(transfers, pname):
            log.debug ("transfers %s " , str(transfers))

            resource = transfers.pop(pname+'_resource', None) #or transfers.pop(pname+'_tags', None)
            log.debug ("found %s _resource/_tags %s ", pname, tounicode(resource))
            if resource is not None:
                try:
                    if hasattr(resource, 'file'):
                        log.warn("XML Resource has file tag")
                        resource = resource.file.read()
                    if isinstance(resource, basestring):
                        log.debug ("reading XML %s" ,  resource)
                        try:
                            resource = etree.fromstring(resource)
                        except etree.XMLSyntaxError:
                            log.exception ("while parsing %s" , resource)
                            raise
                except Exception:
                    log.exception("Couldn't read resource parameter %s" , toascii(resource))
                    resource = None
            return resource

        log.debug("INITIAL TRANSFER %s"  , str( transfers))
        for pname, f in dict(transfers).items():
            # We skip specially named fields (we will pull them out when processing the actual file)
            if pname.endswith ('_resource') or pname.endswith('_tags'): continue
            # This is a form field with an attached file (<input type='file'>)
            if hasattr(f, 'file'):
                # Uploaded File from multipart-form
                transfers.pop(pname)
                resource = find_upload_resource(transfers, pname)
                if resource is None:
                    resource = etree.Element('resource', name=sanitize_filename (getattr(f, 'filename', '')))
                files.append(UploadedResource(fileobj=f.file, resource=resource))
                #log.debug ("TRANSFERRED %s %s" ,  f.filename, etree.tostring(resource))
            if pname.endswith('.uploaded'):
                # Entry point for NGINX upload and insert
                transfers.pop(pname)
                try:
                    # parse the nginx record
                    resource = etree.fromstring (f)
                except etree.XMLSyntaxError:
                    log.exception ("while parsing %s" , f)
                    abort(400, 'Error while parsing transfered XML')
                # Read the record original record (not the nginx one)
                payload_resource = find_upload_resource(transfers, pname.replace ('.uploaded', ''))
                if payload_resource is None:
                    payload_resource = etree.Element('resource')
                if payload_resource is not None:
                    log.debug ("Merging resources %s with %s" ,
                               etree.tostring(resource),
                               etree.tostring(payload_resource))
                    resource = merge_resources (resource, payload_resource )
                upload_resource  = UploadedResource(resource=resource)
                files.append(upload_resource)
                log.debug ("UPLOADED %s %s" , upload_resource, etree.tostring(resource))
        log.debug("TRANSFER after files %s"  , str( transfers))

        for pname, f in transfers.items():
            if pname.endswith ('_resource'):
                transfers.pop(pname)
                try:
                    resource = etree.fromstring(f)
                except etree.XMLSyntaxError:
                    log.exception ("while parsing %s" , str(f))
                    abort(400, 'Error while parsing transfered XML')
                files.append(UploadedResource(resource=resource))

        log.debug("TRANSFER after resources %s"  , str( transfers))
        # Should reject anything not matching

        # process the file list see if some files need special processing
        # e.g. ZIP needs to be unpacked
        # then ingest all
        log.debug ('ingesting files %s' % [tounicode (o.filename) for o in files])
        response = self.ingest(files)
        # respopnd with an XML containing links to created resources
        return etree.tostring(response)

    @expose("bq.import_service.templates.upload")
    @require(predicates.not_anonymous())
    def upload(self, **kw):
        """ Main upload entry point """
        return dict()

    @expose("bq.import_service.templates.uploaded")
    @require(predicates.not_anonymous())
    def transfer_legacy(self, **kw):
        """This is a legacy function for non html5 enabled browsers, this will only accept one upload
           no tag uploads are allowed either
        """
        if 'file' not in kw:
            return dict(error='No file uploaded...')
        resource = self.process( kw['file'] )
        if resource is not None and resource.get('uri') is None:
            # try to define the error
            t=resource.xpath('//tag[@name="error"]')
            if len(t)>0:
                return dict(error=t[0].get('value'))
        elif resource is not None and resource.get('uri') is not None:
            return dict(uri = resource.get('uri'), info = dict(resource.attrib), error=None)

        return dict(error = 'Some problem uploading the file have occured')

    # DEPRECATED ENTRY POINT !
    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def insert(self, url, filename=None, permission='private',  user=None, **kw):
        """insert a URL to a fixed resource. This allows  insertion
        of  resources  when they are already present on safe media
        i.e on the local server drives or remote irods, hdfs etc.
        """
        log.info ('insert %s for %s' ,  url, user)
        #log.warn ("DEPRECATED ENTRY POINT: use insert_resource")

        # Tricky we pass a name that will eventually own the resource,
        # but the web request needs to be authenticated with an admins
        # account for this to occur.
        if user is not None and identity.is_admin():
            identity.current.set_current_user( user )
        if filename is None:
            filename = os.path.basename (url)
        resource = etree.Element('resource', name=filename, permission=permission, value=url)
        if 'tags' in kw:
            try:
                tags = etree.fromstring(kw['tags'])
                resource.extend(list(tags))
            except Exception,e: # dima: possible exceptions here, ValueError, XMLSyntaxError
                del kw['tags']
        kw['insert_resource'] = etree.tostring(resource)
        return self.transfer (** kw)

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def insert_inplace(self,  user=None, **kw):
        """insert a  fixed resource. This allows  insertion
        of  resources  when they are already present on safe media
        i.e on the local server drives or remote irods, hdfs etc.

        Supported URL schemes must be enabled in blob_storage.
        This routine will report an error for illegal schemes

        When admin credentials are presented with request, this routine
        can create resources for any user specified by the user parameter.

        Other arguments should be valid bisque resource documents
        and follow the naming scheme of <param>_resource

        @param user: a user name that is valid on bisque
        @param kw : any number <param>_resource containing <resource ..> XML
        """
        # Note: This entrypoint should allow permission and tags to be inserted
        # in a similar way to tranfers.. maybe combining the two would be needed.
        log.info ('insert_inplace %s %s ' % (user, kw))

        if user is not None and identity.current.user_name == 'admin':
            identity.current.set_current_user( user )

        return self.transfer (**kw)



#---------------------------------------------------------------------------------------
# bisque init stuff
#---------------------------------------------------------------------------------------

def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    service =  import_serviceController(uri)
    return service

def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'import_service', 'public'))]


__controller__ =  import_serviceController
