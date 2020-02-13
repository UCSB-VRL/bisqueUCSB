# -*- mode: python -*-
"""Main server for usage}
"""
import os
import logging
import pkg_resources
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, flash, cache
from repoze.what import predicates
from bq.core.service import ServiceController

from lxml import etree
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


import bq
from bq.core import identity
from bq import data_service

log = logging.getLogger("bq.usage")
class usageController(ServiceController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()
    service_type = "usage"

    def __init__(self, server_url):
        super(usageController, self).__init__(server_url)

    @expose('bq.usage.templates.index')
    def index(self, **kw):
        """Add your first page here.. """
        return dict(msg=_('Hello from usage'))


    @expose(content_type="text/xml")
    def stats(self, **kw):
        log.info('stats %s'%kw)
        wpublic = kw.pop('wpublic',  0)
        anonymous =  identity.anonymous()

        def usage_resource ():
            log.info ("CALL EXPENSIVE")
            all_count = data_service.count("image", wpublic=wpublic, images2d=True, parent=False)
            image_count = data_service.count("image", wpublic=wpublic, permcheck = not anonymous )
            #images2d = data_service.count("image", wpublic=wpublic, images2d=True)
            tag_count = data_service.count ("tag", wpublic=wpublic, permcheck=not anonymous, parent=False)
            gob_count = data_service.count ("gobject", wpublic=wpublic, permcheck=not anonymous, parent=False)

            resource = etree.Element('resource', uri='/usage/stats')
            etree.SubElement(resource, 'tag', name='number_images', value=str(all_count))
            etree.SubElement(resource, 'tag', name='number_images_user', value=str(image_count))
            #etree.SubElement(resource, 'tag', name='number_images_planes', value=str(images2d))
            etree.SubElement(resource, 'tag', name='number_tags', value=str(tag_count))
            etree.SubElement(resource, 'tag', name='number_gobs', value=str(gob_count))

            return etree.tostring(resource)

        usage_cache = cache.get_cache ("usage")
        resource = usage_cache.get_value (
            key = identity.get_username(),
            createfunc = usage_resource,
            expiretime = 3600)
        return resource


    #http://loup.ece.ucsb.edu:9090/data_service/images?ts=%3E2010-06-01T12:00:00&ts=%3C2011-06-01T12:00:00&view=count
    #<resource>
    #<image count="3673"/>
    #</resource>
    def get_counts(self, resource_type, num_days):
        now = datetime.now().replace (hour=23, minute=59,second =59, microsecond=0)
        counts = []
        days = []
        for i in range(num_days):
            d1 = now - timedelta(days=i)
            d2 = now - timedelta(days=i+1)
            ts = ['>%s'%d2.isoformat(), '<=%s'%d1.isoformat()]
            days.append(d1.isoformat(' '))
            # dima: some error happens in data_service and this throws
            try:
                req = data_service.query(resource_type, view='count', ts=ts, permcheck=False)
                log.debug('Daily Usage for [%s - %s] %s'%(d2.isoformat(), d1.isoformat(), etree.tostring(req)))
                c = req.xpath('//%s[@count]'%resource_type)
                if len(c)>0:
                    counts.append( c[0].get('count') )
                else:
                    counts.append('0')
            except AttributeError:
                    counts.append('0')

        counts.reverse()
        days.reverse()
        return counts, days

    def get_counts_month(self, resource_type, num_months):
        now = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)+ relativedelta(months=1)
        counts = []
        months = []
        for i in range(num_months):
            d1 = now - relativedelta(months=i)
            d2 = now - relativedelta(months=i+1)
            ts = ['>%s'%d2.isoformat(), '<=%s'%d1.isoformat()]
            months.append(d2.isoformat(' '))
            # dima: some error happens in data_service and this throws
            try:
                req = data_service.query(resource_type, view='count', ts=ts, permcheck=False)
                log.debug('Monthly Usage for [%s - %s] %s'%(d2.isoformat(), d1.isoformat(), etree.tostring(req)))
                c = req.xpath('//%s[@count]'%resource_type)
                if len(c)>0:
                    counts.append( c[0].get('count') )
                else:
                    counts.append('0')
            except AttributeError:
                    counts.append('0')

        counts.reverse()
        months.reverse()
        return counts, months

    @expose(content_type="text/xml")
    def uploads(self, **kw):
        log.info('uploads %s'%kw)
        def fetch_counts():
            return  self.get_counts('image', 31)
        usage_cache = cache.get_cache ("uploads")
        counts, days = usage_cache.get_value (
            key = identity.get_username(),
            createfunc = fetch_counts,
            expiretime = 600)

        resource = etree.Element('resource', uri='/usage/uploads')
        etree.SubElement(resource, 'tag', name='counts', value=','.join(counts))
        etree.SubElement(resource, 'tag', name='days', value=','.join(days))
        return etree.tostring(resource)

    @expose(content_type="text/xml")
    def uploads_monthly(self, **kw):
        log.info('uploads %s'%kw)

        def fetch_counts():
            return  self.get_counts_month('image', 13)
        usage_cache = cache.get_cache ("uploads_monthly")
        counts, days = usage_cache.get_value (
            key = identity.get_username(),
            createfunc = fetch_counts,
            expiretime = 3600)

        resource = etree.Element('resource', uri='/usage/uploads_monthly')
        etree.SubElement(resource, 'tag', name='counts', value=','.join(counts))
        etree.SubElement(resource, 'tag', name='days', value=','.join(days))
        return etree.tostring(resource)

    @expose(content_type="text/xml")
    def analysis(self, **kw):
        log.info('uploads %s'%kw)
        def fetch_counts():
            return  self.get_counts('mex', 31)
        usage_cache = cache.get_cache ("analysis")
        counts, days = usage_cache.get_value (
            key = identity.get_username(),
            createfunc = fetch_counts,
            expiretime = 600)
        #counts, days = self.get_counts('mex', 31)
        resource = etree.Element('resource', uri='/usage/analysis')
        etree.SubElement(resource, 'tag', name='counts', value=','.join(counts))
        etree.SubElement(resource, 'tag', name='days', value=','.join(days))
        return etree.tostring(resource)

    @expose(content_type="text/xml")
    def analysis_monthly(self, **kw):
        log.info('uploads %s'%kw)
        def fetch_counts():
            return  self.get_counts_month('mex', 13)
        usage_cache = cache.get_cache ("analysis_monthly")
        counts, days = usage_cache.get_value (
            key = identity.get_username(),
            createfunc = fetch_counts,
            expiretime = 3600)
        #counts, days = self.get_counts_month('mex', 13)
        resource = etree.Element('resource', uri='/usage/analysis_monthly')
        etree.SubElement(resource, 'tag', name='counts', value=','.join(counts))
        etree.SubElement(resource, 'tag', name='days', value=','.join(days))
        return etree.tostring(resource)


def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.info ("initialize " + uri)
    service =  usageController(uri)
    #directory.register_service ('usage', service)

    return service

def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'usage', 'public'))]

#def get_model():
#    from bq.usage import model
#    return model

__controller__ =  usageController
