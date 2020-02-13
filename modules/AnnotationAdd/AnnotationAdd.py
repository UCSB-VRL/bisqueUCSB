import sys
import traceback
import csv
from operator import itemgetter
import itertools
from datetime import datetime

try:
    from lxml import etree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from bqapi import BQSession, BQTag, BQCommError

import logging
logging.basicConfig(filename='AnnotationAdd.log', level=logging.DEBUG)
log = logging.getLogger('AnnotationAdd')

def annotation_add(resource, ann='tag', ann_name=None, ann_value=None, ann_type=None, add_if_exists=False):
    modified = []
    if ann_name is not None and ann_value is not None:
        xpath = '//%s[@name="%s" and @value="%s"]'%(ann, ann_name, ann_value)
        if ann_type is not None:
            xpath = xpath.replace(']', ' and @type="%s"]'%ann_type)
        anns = resource.xpath(xpath)
        if len(anns) < 1 or add_if_exists is True:
                g = etree.SubElement(resource, ann, name=ann_name, value=ann_value)
                if ann_type is not None:
                    g.set('type', ann_type)
                modified.append({'g': g})
    return modified

class AnnotationAdd(object):
    """Example Python module
    Read tags from image server and store tags on image directly
    """
    def main(self, mex_url=None, bisque_token=None, bq=None):
        #  Allow for testing by passing an alreay initialized session
        if bq is None:
            bq = BQSession().init_mex(mex_url, bisque_token)
        pars = bq.parameters()
        image_url            = pars.get('dataset_url', None)
        annotation_type      = pars.get('annotation', None)
        ann_name             = pars.get('annotation_name', None)
        ann_value            = pars.get('annotation_value', None)
        ann_type             = pars.get('annotation_type', None) if pars.get('annotation_type', None) != '' else None
        add_if_exists        = pars.get('add_if_exists', None)

        bq.update_mex('Starting')
        mex_id = mex_url.split('/')[-1]
        if image_url is None or len(image_url)<2:
            datasets = bq.fetchxml ('/data_service/dataset')
            datasets = [d.get('uri') for d in datasets.xpath('dataset')]
        else:
            datasets = [image_url]
        total = 0
        changes = []

        # delete annotations for each element in the dataset
        for ds_url in datasets:
            dataset = bq.fetchxml (ds_url, view='deep')
            dataset_name = dataset.get('name')
            bq.update_mex('processing "%s"'%dataset_name)

            refs = dataset.xpath('value[@type="object"]')
            for r in refs:
                url = r.text
                image = bq.fetchxml (url, view='deep')
                uuid = image.get('resource_uniq')
                modified = annotation_add(image, ann=annotation_type, ann_name=ann_name, ann_value=ann_value, ann_type=ann_type, add_if_exists=add_if_exists)

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
                'name': 'added',
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

    M = AnnotationAdd()
    if options.credentials is None:
        mex_url, auth_token = args[:2]
        M.main(mex_url, auth_token)
    else:
        if not options.credentials:
            parser.error('need credentials')
        user,pwd = options.credentials.split(':')

        bq = BQSession().init_local(user, pwd)
        M.main(bq=bq)



