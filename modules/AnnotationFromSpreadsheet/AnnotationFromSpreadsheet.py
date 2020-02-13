import sys
import traceback
import csv
from operator import itemgetter
import itertools
from datetime import datetime
import copy
import json

try:
    from lxml import etree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from bqapi import BQSession, BQTag, BQCommError

import logging
logging.basicConfig(filename='AnnotationFromSpreadsheet.log', level=logging.DEBUG)
log = logging.getLogger('AnnotationFromSpreadsheet')

#------------------------------------------------------------------
# utils
#------------------------------------------------------------------

system_tags = [
    'file.name',
    'geo.latitude',
    'geo.longitude',
    'geo.altitude',
    'res.width',
    'res.height',
    'res.units',
]

def get_value_by_type(t, matches_by_type, headers, row):
    if t not in matches_by_type:
        return None
    k = matches_by_type[t]['name']
    try:
        return row[headers[k]]
    except KeyError:
        return matches_by_type[t]['value']

def get_image_meta(resource):
    tag = resource.find('tag[@name="image_meta"]')
    if tag is None:
        tag = etree.SubElement(resource, 'tag', name='image_meta', type='image_meta')
    return tag

def set_value(tag, value):
    if value is not None:
        tag.set('value', str(value))

def set_tag(parent, name, value, path=None, overwrite=False):
    #print 'Adding %s: %s'%(name, value)
    if path is not None:
        pp = path.split('/')
        for p in pp:
            parent = set_tag(parent, p, value=None, path=None, overwrite=True)

    if overwrite is False:
        tag = etree.SubElement(parent, 'tag', name=name)
        set_value(tag, value)
        return tag

    tag = parent.find('tag[@name="%s"]'%name)
    if tag is None:
        tag = etree.SubElement(parent, 'tag', name=name)
        set_value(tag, value)
        return tag

    set_value(tag, value)
    return tag

#------------------------------------------------------------------
# module class
#------------------------------------------------------------------

class AnnotationHistograms(object):
    """Example Python module
    Read tags from image server and store tags on image directly
    """
    def main(self, mex_url=None, bisque_token=None, bq=None):
        bq.update_mex('Starting')

        image_url = bq.parameter_value(name='dataset_url')
        #resource_type = bq.parameter_value(name='resource_type').lower()
        overwrite_values = bq.parameter_value(name='overwrite_values') or True
        mex = bq.mex.xmltree

        tag_matching = mex.xpath('tag[@name="inputs"]/tag[@name="tag_matching"]')[0]
        spreadsheet_uuid = tag_matching.xpath('tag[@name="spreadsheet_uuid"]')[0].get('value')
        tag_matches = tag_matching.xpath('tag[@name="matches"]')[0]
        matches = {}
        matches_by_type = {}
        for m in tag_matches:
            t = m.get('type')
            n = m.get('name')
            v = m.get('value')
            k = n or t
            if k not in matches:
                matches[k] = []
            mm = {
                'type': t,
                'name': n,
                'value': v,
            }
            matches[k].append(mm)
            matches_by_type[t] = mm

        print '\n\nmatches'
        for k,m in matches.iteritems():
            print '%s: %s'%(k, m)

        print '\n\nmatches_by_type'
        for k,m in matches_by_type.iteritems():
            print '%s: %s'%(k, m)

        # fetch spreadsheet and load
        #url = '%s/table/%s/0;100000,/format:json'%(bq.bisque_root, spreadsheet_uuid)
        json_data = bq.fetchblob('/table/%s/0;100000,/format:json'%spreadsheet_uuid)
        table = json.loads(json_data)
        data = table['data']

        # index columns by header title
        headers = dict([(h, i) for i,h in enumerate(table['headers'])])
        print '\n\nheaders: ',headers

        # index rows by file name
        n = headers[matches_by_type['file.name']['name']]
        files = dict([ (r[n].strip(), i) for i,r in enumerate(data)])
        #print '\n\nFiles: ',files

        # fetch datasets
        mex_id = mex_url.split('/')[-1]
        dt = datetime.now().strftime('%Y%m%dT%H%M%S')
        if image_url is None or len(image_url)<2:
            datasets = bq.fetchxml ('/data_service/dataset')
            datasets = [d.get('uri') for d in datasets.xpath('dataset')]
        else:
            datasets = [image_url]

        # annotate resources
        print '\n\nAnnotating\n'
        resources = {}
        for ds_url in datasets:
            dataset = bq.fetchxml (ds_url, view='full')
            dataset_name = dataset.get('name')
            bq.update_mex('processing "%s"'%dataset_name)

            refs = dataset.xpath('value[@type="object"]')
            for r in refs:
                image_meta = None
                uri = r.text
                resource = bq.fetchxml (uri, view='deep')
                name = resource.get('name', '').strip()
                print '>>> Filename: ', name
                try:
                    n = files[name]
                    row = data[n]
                except KeyError:
                    resources[name] = ''
                    continue

                resources[name] = 'Annotated'
                #print 'Row: ', row

                # iterate over headers and create annotations
                for k,m in matches.iteritems():
                    if k not in headers: continue # if key not found in spreadsheet headers
                    v = str(row[headers[k]])
                    #print '%s: %s'%(k, v)
                    for mm in m:
                        tag = mm['type']
                        if tag in system_tags: continue # skip system tags, we'll use them later creating specific organization
                        set_tag(resource, name=tag, value=v, path=None, overwrite=overwrite_values)

                # Geo tags
                lat = get_value_by_type('geo.latitude', matches_by_type, headers, row)
                lon = get_value_by_type('geo.longitude', matches_by_type, headers, row)
                alt = get_value_by_type('geo.altitude', matches_by_type, headers, row)
                if lat is not None and lon is not None:
                    #if image_meta is None:
                    #    image_meta = get_image_meta(resource)
                    v = '%s,%s'%(lat,lon)
                    if alt is not None:
                        v = '%s,%s'%(v, alt)
                    set_tag(resource, 'center', v, path='Geo/Coordinates', overwrite=True)
                    # dima: proper way of storing this info in the image meta, can't be used due to IS inability to copy sub-tags as deep
                    #set_tag(image_meta, 'center', v, path='Geo/Coordinates', overwrite=True)

                # res tags
                w = get_value_by_type('res.width', matches_by_type, headers, row)
                h = get_value_by_type('res.height', matches_by_type, headers, row)
                u = get_value_by_type('res.units', matches_by_type, headers, row)
                if w is not None and h is not None:
                    if image_meta is None:
                        image_meta = get_image_meta(resource)
                    # get image width in pixels
                    try:
                        img = bq.load(uri)
                        W,H,_,_,_ = img.geometry()
                        rx = float(w)/float(W)
                        ry = float(h)/float(H)

                        set_tag(image_meta, 'pixel_resolution_x', rx, path=None, overwrite=True)
                        set_tag(image_meta, 'pixel_resolution_y', ry, path=None, overwrite=True)
                        if u is not None:
                            set_tag(image_meta, 'pixel_resolution_unit_x', u, path=None, overwrite=True)
                            set_tag(image_meta, 'pixel_resolution_unit_y', u, path=None, overwrite=True)
                    except Exception:
                        pass

                # save resource
                #print '\n\n\n'
                #print etree.tostring(resource, pretty_print=True)
                bq.postxml(uri, resource, method='PUT')

                # clear IS cache if needed
                if image_meta is not None:
                   url = '%s?cleancache'%uri.replace('/data_service/', '/image_service/')
                   bq.c.webreq (method='get', url=url)


        outputs = etree.Element('tag', name='outputs')
        summary = etree.SubElement(outputs, 'tag', name='summary')
        for r,v in resources.iteritems():
            etree.SubElement(summary, 'tag', name=r, value=v)

        bq.finish_mex(tags=[outputs])

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-c", "--credentials", dest="credentials",
                      help="credentials are in the form user:password")
    (options, args) = parser.parse_args()

    M = AnnotationHistograms()
    if options.credentials is None:
        mex_url, auth_token = args[:2]
        bq = BQSession().init_mex(mex_url, auth_token)
    else:
        mex_url = ''
        if not options.credentials:
            parser.error('need credentials')
        user,pwd = options.credentials.split(':')
        bq = BQSession().init_local(user, pwd)

    try:
        M.main(mex_url=mex_url, bq=bq )
    except Exception, e:
        bq.fail_mex(traceback.format_exc())
    sys.exit(0)
