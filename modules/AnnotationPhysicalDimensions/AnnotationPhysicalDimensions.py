import sys
import traceback
import csv
from operator import itemgetter
import itertools
from datetime import datetime
import copy

try:
    from lxml import etree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from bqapi import BQSession, BQTag, BQCommError

import numpy as np
import gobjects

import logging
logging.basicConfig(filename='AnnotationPhysicalDimensions.log', level=logging.DEBUG)
log = logging.getLogger('AnnotationPhysicalDimensions')

#------------------------------------------------------------------
# Dimensions
#------------------------------------------------------------------

class DimensionsPerClass(object):
    ''' stores dimensions per class name '''

    def __init__(self, class_name):
        self.class_name = class_name
        self.areas = []
        self.units_area = []
        self.lengths = []
        self.units_length = []

    def __str__(self):
        return '(%s) Areas: %s, Lengths: %s'%(self.class_name, self.areas, self.lengths)

    def add(self, area=None, length=None, units=None):
        if np.isnan(area) != True and area is not None:
            self.areas.append(area)
            self.units_area.append(units)
        if np.isnan(length) != True and length is not None:
            self.lengths.append(length)
            self.units_length.append(units)

class Dimensions(object):
    ''' stores dimensions per class name '''

    def __init__(self):
        self.classes = {}

    def add_dimension(self, class_name, area=None, length=None, units=None):
        #print '%s: %s, %s, %s'%(class_name, area, length, units)
        if class_name not in self.classes:
            self.classes[class_name] = DimensionsPerClass(class_name)
        self.classes[class_name].add(area=area, length=length, units=units)

    def add(self, gob, res=None, units=None):
        length = gob.length(res=res)
        area = gob.area(res=res)
        self.add_dimension(gob.type, area=area, length=length, units=units)

    def write(self, filename):
        maxrows = 0
        header = []
        for n,c in self.classes.iteritems():
            #print '%s\n'%c
            if len(c.areas)>0:
                header.append('%s (area)'%n)
                header.append('units')
                maxrows = max(maxrows, len(c.areas))
            if len(c.lengths)>0:
                header.append('%s (length)'%n)
                header.append('units')
                maxrows = max(maxrows, len(c.areas))

        maxcols = len(header)
        with open(filename, 'wb') as f:
            w = csv.writer(f, delimiter=',')
            w.writerow(header)

            for i in range(maxrows):
                row = [''] * maxcols
                j = 0
                for c in self.classes.itervalues():
                    try:
                        row[j] = c.areas[i]
                        row[j+1] = c.units_area[i]
                        j+=2
                    except Exception:
                        pass
                    try:
                        row[j] = c.lengths[i]
                        row[j+1] = c.units_length[i]
                        j+=2
                    except Exception:
                        pass
                w.writerow(row)


#------------------------------------------------------------------
# utils
#------------------------------------------------------------------

def image_get_res(bq, xml):
    resource = etree.Element('image', uri=xml.get('uri'), resource_uniq=xml.get('resource_uniq') )
    image = bq.factory.from_etree(resource)
    info = image.info()
    res = np.array([
        float(info.get('pixel_resolution_x', 1.0)),
        float(info.get('pixel_resolution_y', 1.0)),
        float(info.get('pixel_resolution_z', 1.0)),
        float(info.get('pixel_resolution_t', 1.0)),
        float(info.get('pixel_resolution_c', 1.0))
    ], np.float)
    units = [
        info.get('pixel_resolution_unit_x', 'px'),
        info.get('pixel_resolution_unit_y', 'px'),
        info.get('pixel_resolution_unit_z', 'px'),
        info.get('pixel_resolution_unit_t', 'px'),
        info.get('pixel_resolution_unit_c', 'px')
    ]
    return res, units

def get_gobjects (xml, ignore_gobs, use_full_path=False):
    gobs = []
    nodes = xml.xpath('//gobject/*/vertex/../..')
    for n in nodes:
        c = n.get('type')
        if c in ignore_gobs:
            continue
        gob = gobjects.factory.make(n)

        if use_full_path is True:
            path = []
            g = n.getparent()
            while g is not None:
                if g.tag != 'gobject':
                    break
                path.append(g.get('type'))
                g = g.getparent()

            # skip gob if any path part is ignored
            pint = set(path).intersection(ignore_gobs)
            if len(pint)>0:
                continue
            # set full type
            path.append(c)
            c = '/'.join(path)
            gob.type = c

        gobs.append(gob)

    return gobs

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
        use_full_path = bq.parameter_value(name='use_full_path')
        ignore_gobs = bq.parameter_value(name='ignore_gobs') or []

        mex_id = mex_url.split('/')[-1]
        dt = datetime.now().strftime('%Y%m%dT%H%M%S')
        if image_url is None or len(image_url)<2:
            datasets = bq.fetchxml ('/data_service/dataset')
            datasets = [d.get('uri') for d in datasets.xpath('dataset')]
        else:
            datasets = [image_url]

        # compute histograms per image
        ds = Dimensions()
        for ds_url in datasets:
            dataset = bq.fetchxml (ds_url, view='full')
            dataset_name = dataset.get('name')
            bq.update_mex('processing "%s"'%dataset_name)

            refs = dataset.xpath('value[@type="object"]')
            for r in refs:
                print 'Fetching %s'%r.text
                xml = bq.fetchxml (r.text, view='deep')
                if xml.tag != 'image':
                    continue
                res, units = image_get_res(bq, xml)
                gobs = get_gobjects (xml, ignore_gobs, use_full_path=use_full_path)
                for gob in gobs:
                    ds.add(gob, res=res, units=units[0])

        csv_filename = 'dimensions_%s_%s.csv'%(dt, mex_id)
        ds.write(csv_filename)

        # store the CSV file and write its reference into the MEX
        resource = etree.Element('resource', type='table', name='ModuleExecutions/AnnotationPhysicalDimensions/%s'%(csv_filename), hidden='true' )
        blob = etree.XML(bq.postblob(csv_filename, xml=resource))
        #print etree.tostring(blob)
        blob = blob.find('./')
        #print blob
        if blob is None or blob.get('uri') is None:
            bq.fail_mex('Could not store the table file')
            return

        outputs = etree.Element('tag', name='outputs')
        etree.SubElement(outputs, 'tag', name='table', type='table', value=blob.get('uri'))
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
