import sys
import traceback
import csv
from operator import itemgetter
import itertools
from datetime import datetime
import urllib

try:
    from lxml import etree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from bqapi import BQSession, BQTag, BQCommError

import logging
logging.basicConfig(filename='AnnotationRename.log', level=logging.DEBUG)
log = logging.getLogger('AnnotationRename')

seps = {
    'type': '::',
    'name': ':',
    'value': '',
}

def rename(image, text_old, text_new, ann_type='gobject', ann_attr='type'):
    modified = []
    gobs = image.xpath('//%s[@%s="%s"]'%(ann_type, ann_attr, text_old.replace('"', '""')))
    for g in gobs:
        if g.get(ann_attr) == text_old:
            g.set(ann_attr, text_new)
            modified.append({'g': g})
    return modified

class AnnotationRename(object):
    """Example Python module
    Read tags from image server and store tags on image directly
    """
    def main(self, mex_url=None, bisque_token=None, bq=None):
        #  Allow for testing by passing an alreay initialized session
        if bq is None:
            bq = BQSession().init_mex(mex_url, bisque_token)
        pars = bq.parameters()
        image_url            = pars.get('dataset_url', None)
        annotation_type      = pars.get('annotation_type', None)
        annotation_attribute = pars.get('annotation_attribute', None)
        value_old            = pars.get('value_old', None)
        value_new            = pars.get('value_new', None)

        bq.update_mex('Starting')
        mex_id = mex_url.split('/')[-1]
        if image_url is None or len(image_url)<2:
            datasets = bq.fetchxml ('/data_service/dataset')
            datasets = [d.get('uri') for d in datasets.xpath('dataset')]
        else:
            datasets = [image_url]
        total = 0
        changes = []

        # rename annotations for each element in the dataset
        for ds_url in datasets:
            #dataset = bq.fetchxml (ds_url, view='full')

            dataset = bq.fetchxml (ds_url, view='short')
            dataset_name = dataset.get('name')
            bq.update_mex('processing "%s"'%dataset_name)

            # only fetch resources of interest
            q = urllib.quote(value_old)
            sep = seps[annotation_attribute]
            qurl = '%s/value?tag_query=%%22%s%%22%s'%(ds_url, q, sep)
            dataset = bq.fetchxml (qurl, view='short')

            #refs = dataset.xpath('value[@type="object"]')
            #for r in refs:
            #    url = r.text
            for r in dataset:
                url = r.get('uri')
                if url is None: continue

                image = bq.fetchxml (url, view='deep')
                uuid = image.get('resource_uniq')
                modified = rename(image, value_old, value_new, ann_type=annotation_type, ann_attr=annotation_attribute)
                if len(modified)>0:
                    bq.postxml(url, image, method='PUT')
                    total = total + len(modified)
                    changes.append({
                        'name': '%s (%s)'%(image.get('name'), image.get('resource_uniq')),
                        'value': '%s'%len(modified)
                    })

        changes.insert(0, {
            'name': 'Total',
            'value': '%s'%total
        })
        bq.finish_mex(tags = [{
            'name': 'outputs',
            'tag' : [{
                'name': 'renamed',
                'tag' : changes,
            }]
        }])
        sys.exit(0)
        #bq.close()


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-c", "--credentials", dest="credentials",
                      help="credentials are in the form user:password")
    #parser.add_option('--mex_url')
    #parser.add_option('--auth_token')

    (options, args) = parser.parse_args()

    M = AnnotationRename()
    if options.credentials is None:
        mex_url, auth_token = args[:2]
        M.main(mex_url, auth_token)
    else:
        if not options.credentials:
            parser.error('need credentials')
        user,pwd = options.credentials.split(':')

        bq = BQSession().init_local(user, pwd)
        M.main(bq=bq)

