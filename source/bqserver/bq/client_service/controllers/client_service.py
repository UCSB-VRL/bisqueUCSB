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

  Top level web entry point for bisque system

"""

import os
import sys
import random
import logging

import pkg_resources

from urllib import urlencode
from lxml import etree

from pylons import app_globals
from pylons.i18n import ugettext as _, lazy_ugettext as l_, N_
from pylons.controllers.util import abort
from webob import Request

import tg
from tg import expose, flash, redirect, require, request
from tg import config, tmpl_context as c, session
from repoze.what import predicates


import bq
from bq.core.service import ServiceController, service_registry
from bq.client_service import model
from bq.exceptions import IllegalOperation
from bq.release import  __VERSION__
from bq.core import identity
from bq.util.hash import is_uniq_code

#import aggregate_service
from bq import data_service


import tempfile
import json
import tifffile
from PIL import Image
import io
import base64
import numpy as np

from bq.util.paths import data_path

log = logging.getLogger('bq.client_service')

UPLOAD_DIR = tg.config.get('bisque.import_service.upload_dir', data_path('uploads'))


#  Allow bq.identity to be accessed from templates
#def addBisqueToTemplate(root_vars):
#    bq = dict (identity=bisquik.identity)
#    root_vars.update (dict (bq=bq))
#
#turbogears.view.root_variable_providers += [addBisqueToTemplate]



class ClientServer(ServiceController):
    service_type = "client_service"

    def viewlink(self, resource):
        return self.baseuri + "view?" + urlencode ({'resource': resource})


    @expose()
    def _default (self, *path, **kw):
        if is_uniq_code(path[0]):
            redirect ("/client_service/view?resource=/data_service/%s" % path[0])

    @expose(content_type="text/xml")
    def version(self):
        response = etree.Element('resource', type='version')
        etree.SubElement (response, 'tag', name='version', value=__VERSION__)
        server = etree.SubElement (response, 'tag', name='server')

        #etree.SubElement (server, 'tag', name='environment', value=config.get('server.environment'))
        return etree.tostring(response)

    @expose(template='bq.client_service.templates.welcome')
    def index(self, **kw):
        log.info("WELCOME %s %s " , request.url, dict ( session ))
        wpublic = kw.pop('wpublic', not bq.core.identity.current)
        pybool = {'True': 'true', 'False': 'false'}
        welcome_message = config.get ('bisque.welcome_message', "Welcome to the Bisque image database")

        return dict(imageurl=None,
                    thumbnail=None,
                    wpublicjs = pybool[str(wpublic)],
                    welcome_message = welcome_message
                    )

    @expose(template='bq.client_service.templates.welcome')
    def welcomebackground(self, **kw):
        log.info("BACKGROUND %s " % session )
        wpublic = kw.pop('wpublic', not bq.core.identity.current)
        thumbnail = None
        imageurl = None
        welcome_resource = config.get ('bisque.background_resource', None)
        thumb_size = kw.get('size', '800,600')
        if welcome_resource:
            imageurl = welcome_resource
            try:
                image = data_service.get_resource(imageurl)
                thumbnail = '/image_service/image/%s?thumbnail=%s'%(image.get('resource_uniq'), thumb_size)
            except Exception:
                log.exception('bisque.background (%s) set but not available' % imageurl)
        else:
            tag_query = config.get('bisque.background_query', "welcome_background:")
            image_count  = data_service.count("image", tag_query=tag_query, wpublic=wpublic)
            wpublic_query = wpublic
            if image_count == 0 and wpublic == False:
                wpublic_query  = True
                image_count  = data_service.count("image", tag_query=tag_query, wpublic=wpublic_query)
            # None found .. pick a random
            if image_count == 0:
                image_count = data_service.count("image", wpublic=wpublic)
                tag_query  = None
                wpublic_query = wpublic
            if image_count:
                im = random.randint(0, image_count-1)
                image  = data_service.query('image', tag_query=tag_query, wpublic=wpublic_query,
                                            offset = im, limit = 1)[0]
                #imageurl = self.viewlink(image.attrib['uri'])
                thumbnail = '/image_service/image/%s?thumbnail=%s'%(image.get('resource_uniq'), thumb_size)

        redirect (base_url=thumbnail)

    @expose(template='bq.client_service.templates.browser')
    def browser(self, **kw):
        #query = kw.pop('tag_query', None)
        c.commandbar_enabled = False
        user = bq.core.identity.get_user()
        if user:
            wpublicVal='false'
        else:
            wpublicVal='true'

        #log.debug ('DDDDDDDDDDDDDDDDDDDDDD'+query)
        return dict(query=kw.pop('tag_query', None),
                    layout=kw.pop('layout', None),
                    tagOrder=kw.pop('tag_order', None),
                    tagQuery=kw.pop('tag_query', None),
                    offset=kw.pop('offset', None),
                    dataset=kw.pop('dataset', None),
                    resource=kw.pop('resource', None),
                    search=0,
                    user_id = "",
                    page = kw.pop('page', 'null'),
                    view  = kw.pop('view', ''),
                    count = kw.pop ('count', '10'),
                    wpublic = kw.pop('wpublic', wpublicVal),
                    analysis = None)

    @expose(template='bq.client_service.templates.about')
    def about(self, **kw):
        from bq.release import __VERSION__
        version = '%s'%__VERSION__
        return dict(version=version)


    # Test

    @expose ()
    def xcheck (self, url):
        from bq.config.middleware import bisque_app
        req = Request.blank (url)
        req.headers['Authorization'] = "Mex %s" % identity.mex_authorization_token()
        response = req.get_response(bisque_app)
        return response.body



    @expose(template='bq.client_service.templates.test')
    def test(self):
        """from bq.export_service.controllers.tar_streamer import TarStreamer
        tarStreamer = TarStreamer()
        tarStreamer.sendResponseHeader('Bisque.tar')
        return tarStreamer.stream(['C:\\Python27\\TarStreamer\\file1.tif', 'C:\\Python27\\TarStreamer\\file2.tif', 'C:\\Python27\\TarStreamer\\file3.tif'])
        """
        return dict()

    # USE /services instead
    # @expose (content_type="application/xml")
    # def services(self):
    #     resource = etree.Element ('resource', uri=tg.url('/client_service/services'))
    #     for service_type, service_list in service_registry.items():
    #         for service in service_list:
    #             etree.SubElement (resource, 'tag', name=service_type, value=service.uri)

    #     #tg.response.content_type = "text/xml"
    #     return etree.tostring(resource)



    # Once the mask editing is complete, it will send a POST request here, with
    # json data as the payload.
    # data['orig_urls'] contains a list of the original mask URLs
    # data['stack'] contains a list of PNG files of the user edits
    @expose()
    def mask_receiver(self, **kw):
        log.info('CKPT202-ckck-beginning')
        from bq.config.middleware import bisque_app
        data = json.loads(request.body)
        new_stack = list()  # stack of original masks as numpy arrays
        old_stack = list()  # stack of user edits as numpy arrays

        no_mask = False
        log.info('CKPT202-ckck-02')
        # Get stack of original masks
        for url in data['orig_urls']:
                if len(url) == 0:
                    no_mask = True
                    break
                url = url.decode()
                url = str(url.split('/')[-1])
                req = Request.blank('/image_service/' + url)
                # the line below is for authentication
                req.headers['Cookie'] = request.headers['Cookie']    
                response = req.get_response(bisque_app)
                b_bytes = io.BytesIO(response.body)
                img = Image.open(b_bytes)
                old_stack.append(np.array(img))

        # Get stack of user edits as numpy arrays
        for item in data['stack']:
                # Slices without user edits are blank strings.
                # Create empty arrays for these.
                if len(item) == 0:
                    new_stack.append(None)
                    continue
                # decode binary64 string, convert to numpy array
                b_str = item.decode().split(',')[1]
                b_bytes = base64.b64decode(b_str)
                img = Image.open(io.BytesIO(b_bytes))
                new_stack.append(np.array(img))

        log.info('CKPT202-ckck-03')
        shape = [i.shape for i in new_stack if i is not None][0]
        new_stack = [np.zeros(shape[:2] + (4,), dtype='uint8') if i is None else i for i in new_stack]
        
        x_edit = np.stack(new_stack, axis=0)
        
        if len(old_stack) == 0:
            old_stack = np.zeros((len(new_stack),) + shape[:2] + (3,), dtype='uint8')

        # Stack array list into large arrays
        #x_edit = np.stack(new_stack, axis=0)
        x_orig = np.stack(old_stack, axis=0)
        x_out = x_orig.astype('int32')

        log.info('CKPT202-ckck-04')
        # Mask indicates points where alpha channel == 255.
        # If alpha == 0, the user edit is transparent, and
        # should not change the original mask.
        mask = (x_edit[..., 3] == 255)

        # Create the composite image
        x_out[mask] = x_edit[mask][:,:3]

        log.info('CKPT202-ckck-05asf')
        # The next section converts the RGB segmentation mask back to one-hot
        # encoded labels.
        if no_mask:
            fuse_list = np.array([
                     [  0,   0,   0],
                     [255,   0,   0],
                     [  0, 255,   0],
                     [  0,   0, 255],
                     [255, 255,   0],
                     [255,   0, 255],
                     [  0, 255, 255],
                     [255, 255, 255],
            ])

        else:
            # Convert the "fuse" parameter from the URL into an array of ints
            fuse_list = str(data['orig_urls'][0]).split('?')[1].split('&fuse=')[1].split(';:m&')[0]
            fuse_list = [[int(i) for i in j.split(',')] for j in fuse_list.split(';')]
            fuse_list = [[0,0,0]] + fuse_list
            fuse_list = np.array(fuse_list)


        # The next few lines are to compute a mapping from RGB to label. For
        # example, if label 1 is [255,0,0], and label 2 is [0,255,0], all
        # green pixels should map to label 2, and red map to label 1

        # Concat 3 uint8 values into a single int with 24 significant bits
        # This makes indexing easier, with each color being a single unique int
        fuse_list = np.dot(fuse_list, 256**np.arange(3))
        mapping_dict = {v: i for i, v in enumerate(fuse_list)}

        # Apply same concat trick to RGB segmentaiton image
        x_out = np.dot(x_out, 256**np.arange(3))
        orig_shape = x_out.shape

        vals, inds = np.unique(x_out, return_inverse=True)

        # Apply the final mapping for RGB color as a 24 bit int to label for
        # each pixel
        inds_map = np.array([mapping_dict[k] for k in vals])
        x_out = inds_map[inds]
        x_out = x_out.reshape(orig_shape)

        # Make segmentation 1-hot, where 0 is false and 255 is true
        x_1hot = 255*np.eye(len(fuse_list))[x_out].astype('uint8')

        # CZYX axes order
        x_1hot = x_1hot.transpose((3, 0, 1, 2))[1:]

        log.info('CKPT202-ckck-08')
        # if there isn't a mask to start with, I make the OME_XML myself
        if no_mask:
            new_fname = 'scan.tiff'
            desc = '<?xml version="1.0" encoding="UTF-8"?><OME ' + \
                'xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06" ' + \
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' + \
                'xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 ' + \
                'http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd" ' + \
                'UUID="urn:uuid:0f998096-5fa6-11ed-8066-0242ac110004"  ' + \
                'Creator="tifffile.py 2022.10.10"><Image ID="Image:0" Name="Image0">' + \
                '<Pixels ID="Pixels:0" DimensionOrder="XYZCT" Type="uint8" ' + \
                'SizeX="502" SizeY="502" SizeZ="40" SizeC="7" SizeT="1" SignificantBits="8" PhysicalSizeX="1.0" PhysicalSizeXUnit="microns" PhysicalSizeY="1.0" PhysicalSizeYUnit="microns" PhysicalSizeZ="1.0" PhysicalSizeZUnit="microns"><Channel ID="Channel:0:0" SamplesPerPixel="1"><LightPath/></Channel><Channel ID="Channel:0:1" SamplesPerPixel="1"><LightPath/></Channel><Channel ID="Channel:0:2" SamplesPerPixel="1"><LightPath/></Channel><Channel ID="Channel:0:3" SamplesPerPixel="1"><LightPath/></Channel><Channel ID="Channel:0:4" SamplesPerPixel="1"><LightPath/></Channel><Channel ID="Channel:0:5" SamplesPerPixel="1"><LightPath/></Channel><TiffData IFD="0" ' + \
                'PlaneCount="240"/></Pixels></Image></OME>'

        else:        
            # This will get the original tifffile from the blob service
            # This is needed to transfer metadata from the old file to the new one
            blob_url = data['orig_urls'][0].split('?')[0].replace('image_service', 'blob_service')
            req = Request.blank(blob_url)
            req.headers['Cookie'] = request.headers['Cookie']
            response = req.get_response(bisque_app)
            b_bytes = io.BytesIO(response.body)
            tif_orig = tifffile.TiffFile(b_bytes)
            desc = tif_orig.pages[0].description  # this desc is the ome-xml metadata
            log.info('CKPT202-ckck ' + str(desc))
            # Get the original name, then add "-edited" to it
            img_orig_url = blob_url.replace('blob_service', 'data_service')
            req = Request.blank(img_orig_url)
            req.headers['Cookie'] = request.headers['Cookie']
            response = req.get_response(bisque_app)
            orig_fname = etree.fromstring(response.body).get('name')
            new_fname = orig_fname.replace('.ome.tiff', '-edited.ome.tiff')
            tiff_meta = None
        
        # A weird thing I don't really understand, but the internal transfer
        # seems to only work when the tempfile library is used. BytesIO objects,
        # actual files on disk, etc do not seem to work.
        f_out = tempfile.NamedTemporaryFile('w+b', suffix = '.tiff',
            dir = UPLOAD_DIR, delete=False)

        # Save tifffile. compress=6 means use zlib
        tifffile.imsave(f_out, x_1hot, compress=6, description=desc, metadata=tiff_meta)

        # Set the file pointer back at 0 after writing. A weird tempfile thing.
        f_out.seek(0)

        # bisque metadata for the new image file. Different from the OME_TIFF metadata
        metadata = etree.Element('resource', name=new_fname)
        metadata = unicode(etree.tostring(metadata))

        log.info('CKPT202-ckck-416-550pm')
        # store the array in bisque
        import_service = service_registry.find_service('import')
        log.info('CKPT202-ckck-416-550pm---v2')
        trans_resp = import_service.transfer_internal(file = f_out,
            file_resource = metadata)       

        log.info('CKPT202-ckck-422')

        # The response from import service will contain a URI for the saved resource.
        # Parse this from XML response, and return to the user. The JS front-end will
        # redirect the user to the resource when transfer is finished.
        trans_resp = etree.fromstring(trans_resp)
        resp_uri = trans_resp.getchildren()[0].get('uri')
        tg.response.headers['Content-Type'] = 'text/plain'

        log.info('CKPT202-ckck-431')
        return resp_uri

    @expose("bq.client_service.templates.view")
    def view(self, resource, **kw):
        query = ''
        log.debug ("VIEW")
        #resource=kw.pop('resource', '')
        #if resource is None:
        #    abort(404)

        return dict(resource=resource)

    @expose("bq.client_service.templates.embedded")
    def embedded(self, **kw):
        log.debug ("EMBEDDED")
        return dict()

    @expose("bq.client_service.templates.view")
    def create(self, **kw):
        query = ''
        type_=kw.pop('type', None)

        if type_:
            resource = data_service.new_resource (type_, **kw)

            # Choose widgets to instantiate on the viewer by the type
            # of the resource.
            log.debug ('created %s  -> %s' % (type_, uri))
            return dict(resource=resource) #, tag_views=None, wpublic = None, search = None)
        raise IllegalOperation("create operation requires type")


    @expose("bq.client_service.templates.movieplayer")
    def movieplayer(self, **kw):
        resource=kw.pop('resource', None)
        return dict(resource=resource)

    @expose("bq.client_service.templates.help")
    def help(self, **kw):
        resource=kw.pop('resource', None)
        return dict(resource=resource)

    @expose(content_type='text/html')
    def form(self, **kw):
        bb = tg.request.body_file_raw.seek(0)
        bb = tg.request.body_file_raw.read()


        log.debug ("FORM %s %s" , kw, bb)
        return str(kw)



client_server = None
def initialize(uri):
    global client_server
    client_server = ClientServer(uri)
    return client_server

def uri():
    return client_server.baseuri
