# -*- mode: python -*-
"""Main server for ingest}
"""
import os
import logging
import pkg_resources

from tempfile import NamedTemporaryFile
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, flash, controllers, request
from repoze.what import predicates

from bq.core.service import ServiceMixin
from bq.core.service import ServiceController
from bq.exceptions import BQException
from bq.ingest import model
from lxml import etree
from bq import data_service
from bq import image_service
from bq import blob_service

from bq.util import http


log = logging.getLogger("bq.ingest")

class IngestException(BQException):
    "Ingest Exceptions"

def image_ingest (blob):
    """Ingest a simple image given the blob..
    """
    blob_uri = blob.get('blob_uri')
    original_name = blob.get('original_uri').rsplit('/',1)[1]

    #content = blob_service.stream (blob_uri)
    #f = NamedTemporaryFile(delete=False)
    #for block in content:
    #    f.write(block)
    #f.close()
    #fname = f.name

    #log.debug ('NAME = %s' % fname)
    #info = image_service.new_image(src=open(fname,'rb'), name=original_name)
    info = image_service.uri(blob_uri).info().get()
    if info==None:
        image=None
        raise IngestException(_('unable to create image file'))
    log.debug ('imageservice=%s' % info)
    #image = data_service.new_image (**info)
    tags = etree.Element('request')
    etree.SubElement(tags, 'tag', name="filename", value=original_name)
    data_service.append_resource(image, tree=tags)
    return image


def match_best_ingester (root, blob):
    return image_ingest


class ingestController(controllers.RestController, ServiceMixin):
#class ingestController(ServiceController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()
    service_type = "ingest_service"

    def __init__(self, server_url):
        ServiceMixin.__init__(self,server_url)

    @expose('bq.ingest.templates.index')
    def get_all(self, **kw):
        """Add your first page here.. """

        log.info("INGEST /")
        return dict(msg=_('Hello from ingest'))

    @expose(content_type="text/xml")
    def post(self, *path, **kw):
        path = "/".join ([''] + list (path))
        xml = request.body_file.read()
        log.debug ("POST %s %s " % (str(path), xml))
       # return new_blobs(body = xml)

    def new_blobs(self, body, **kw):
        log.info("new_blobs %s" % body)
        root = etree.XML (body)
        ingested = []
        skipped = []
        for blob in root:
            # For each blob found map to a ingest task.
            # Each ingest task will be responsible for creating the
            # actual resource or ignoring the blob

            try:
                ingester = match_best_ingester(root, blob)
                resource = ingester (blob)
                ingested.append(resource)
                continue
            except IngestException:
                skipped.append(blob)
            except Exception:
                log.exception("Unknown exception during ingest")
            skipped.append(blob)
        return




def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    service =  ingestController(uri)
    #directory.register_service ('ingest', service)

    return service

def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'ingest', 'public'))]

def get_model():
    from bq.ingest import model
    return model

__controller__ =  ingestController
