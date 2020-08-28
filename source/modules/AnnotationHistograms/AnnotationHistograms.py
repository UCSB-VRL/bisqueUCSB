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

import logging
logging.basicConfig(filename='AnnotationHistograms.log', level=logging.DEBUG)
log = logging.getLogger('AnnotationHistograms')

class Occurrences(object):
    ''' stores info per resource '''

    def __init__(self, dataset_name=None, image_name=None, hist=None, tags=None):
        self.dataset_name = dataset_name
        self.image_name = image_name
        self.hist = hist or {}
        self.tags = tags or {}

#------------------------------------------------------------------
# utils
#------------------------------------------------------------------

# def make_directory(path):
#     try:
#         os.makedirs(path)
#     except OSError:
#         if not os.path.isdir(path):
#             raise

# def compute_unique_names(image, unique_tags):
#     # get unique tag names
#     tags = image.xpath('tag')
#     for t in tags:
#         unique_tags.add(t.get('name'))

# def compute_unique_gob_types(image, unique_gobs):
#     # get unique gob names
#     gobs = image.xpath('gobject')
#     for g in gobs:
#         unique_gobs.add(g.get('type'))

# def fetch_unique_tag_names(session):
#     unique_gobs = set()
#     url = '/data_service/image/?tag_names=true&wpublic=false'
#     q = session.fetchxml (url)

#     # get unique gob types
#     gobs = q.xpath('tag')
#     for g in gobs:
#         unique_gobs.add(g.get('name'))
#     return unique_gobs

# def fetch_unique_gob_types(session):
#     unique_gobs = set()
#     url = '/data_service/image/?gob_types=true&wpublic=false'
#     q = session.fetchxml (url)

#     # get unique gob types
#     gobs = q.xpath('gobject')
#     for g in gobs:
#         c = g.get('type', '').replace('Primary - ', '').replace('Secondary - ', '')
#         unique_gobs.add(c)
#     return unique_gobs

def find_matches(image, preferred='secondary'):
    gobs = image.xpath('//gobject')
    if len(gobs)<1:
        return []

    uuid = image.get('resource_uniq')
    filename = image.get('name')
    uri = image.get('uri')

    points = []
    for g in gobs:
        try:
            t = g.get('type')
            v = g.xpath('*/vertex')[0]
            x = float(v.get('x'))
            y = float(v.get('y'))
            points.append({'g': g, 'coord': (x,y), 'type': t})
        except IndexError:
            print 'IndexError in %s'%g
            pass
    points = sorted(points, key=itemgetter('coord'))

    delta = 150
    filtered = []
    surveyed = []
    i = 0
    for p in reversed(points):
        i=i+1
        matched = [p]
        points.remove(p)
        if p in surveyed:
            continue

        x1,y1 = p['coord']
        points2 = points
        for pp in reversed(points2):
            x2,y2 = pp['coord']
            if abs(x1-x2)<delta and abs(y1-y2)<delta:
                matched.append(pp)
                surveyed.append(pp)

        selected = None
        if len(matched) == 1:
            selected = p
        else:
            for pp in matched:
                if pp['type'].lower().startswith(preferred):
                    selected = pp
                    break

        if selected is None:
            selected = matched[0]
            print 'In %s (%s) could not select from matched points'%(filename, uri)
            for m in matched:
                print 'matched: %s, %s'%(m['type'], m['coord'])
            print 'Selected: %s, %s'%(selected['type'], selected['coord'])

        filtered.append(selected)


    filtered = list(reversed(filtered))

    if len(filtered)!=100 and len(filtered) != len(gobs):
        print '%s (%s) found %s preferred of %s'%(filename, uri, len(filtered), len(gobs))
    elif len(gobs)<100:
        print '%s (%s) has only %s annotations'%(filename, uri, len(gobs))
    return filtered

def find_gobjects (xml):
    gobs = []
    nodes = xml.xpath('//gobject/*/vertex/../..')
    for n in nodes:
        t = n.get('type')
        gobs.append({'g': n, 'type': t})

    return gobs

def find_tags (node, unique_tags, ignore_tags, use_full_path=False, path=None):
    path = path or []
    # get unique tag names
    T = {}
    tags = node.xpath('tag')
    for t in tags:
        np = None
        n = t.get('name')
        v = t.get('value')
        c = n
        if n in ignore_tags:
            continue

        if n is not None:
            if use_full_path is True:
                np = copy.deepcopy(path)
                np.append(n)
                c = '/'.join(np)
            unique_tags.add(c)

            if v is not None:
                T[c] = v

            TT = find_tags (t, unique_tags, ignore_tags, use_full_path=use_full_path, path=np or path)
            T.update(TT)

    return T

def compute_occurrences (image, matches, unique_gobs, ignore_gobs, use_full_path=False):
    # get gob histogram
    h = {}
    for m in matches:
        c = m['type']
        if c in ignore_gobs:
            continue
        c = c.replace('Primary - ', '').replace('Secondary - ', '')

        if use_full_path is True:
            # get path
            path = []
            g = m['g'].getparent()
            while g is not None:
                if g.tag != 'gobject':
                    break
                path.append(g.get('type'))
                g = g.getparent()

            # skip gob if any path part is ignored
            pint = set(path).intersection(ignore_gobs)
            if len(pint)>0:
                continue
            # get type
            path.append(c)
            c = '/'.join(path)

        unique_gobs.add(c)
        try:
            h[c] = h[c] + 1
        except KeyError:
            h[c] = 1

    return h

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
        ignore_tags = bq.parameter_value(name='ignore_tags') or []
        ignore_gobs = bq.parameter_value(name='ignore_gobs') or []

        mex_id = mex_url.split('/')[-1]
        dt = datetime.now().strftime('%Y%m%dT%H%M%S')
        if image_url is None or len(image_url)<2:
            datasets = bq.fetchxml ('/data_service/dataset')
            datasets = [d.get('uri') for d in datasets.xpath('dataset')]
        else:
            datasets = [image_url]

        # compute tag and gobject types
        #unique_tags = fetch_unique_tag_names(bq)
        #unique_tags = unique_tags - ignore_tags

        #unique_gobs = fetch_unique_gob_types(bq)


        # compute histograms per image
        unique_gobs = set()
        unique_tags = set()
        images = []
        for ds_url in datasets:
            dataset = bq.fetchxml (ds_url, view='full')
            dataset_name = dataset.get('name')
            bq.update_mex('processing "%s"'%dataset_name)

            refs = dataset.xpath('value[@type="object"]')
            for r in refs:
                image = bq.fetchxml (r.text, view='deep')
                #matches = find_matches(image, preferred='secondary')
                matches = find_gobjects (image)
                #if len(matches)<1:
                #    continue
                print 'Image %s found %s gobjects'%(image.get('resource_uniq'), len(matches))


                i = Occurrences()
                i.dataset_name = dataset.get('name')
                i.image_name = image.get('name')
                i.tags = find_tags (image, unique_tags, ignore_tags, use_full_path)
                i.hist = compute_occurrences(image, matches, unique_gobs, ignore_gobs, use_full_path)
                images.append(i)

        # write complete histogram to a CSV
        unique_tags = sorted(unique_tags)
        unique_gobs = sorted(unique_gobs)

        header = ['dataset', 'filename']
        header.extend(unique_tags)
        header.extend(unique_gobs)

        csv_filename = 'histograms_one_layer_%s_%s.csv'%(dt, mex_id)
        with open(csv_filename, 'wb') as csvfile:
            w = csv.writer(csvfile, delimiter=',')
            w.writerow(header)

            # write frequencies per image
            for i in images:
                row = [i.dataset_name, i.image_name]
                for t in unique_tags:
                    row.append(i.tags.get(t, ''))
                for g in unique_gobs:
                    row.append(i.hist.get(g, 0))
                w.writerow(row)

        # store the CSV file and write its reference into the MEX
        resource = etree.Element('resource', type='table', name='ModuleExecutions/AnnotationHistograms/%s'%(csv_filename), hidden='true' )
        blob = etree.XML(bq.postblob(csv_filename, xml=resource))
        #print etree.tostring(blob)
        blob = blob.find('./')
        #print blob
        if blob is None or blob.get('uri') is None:
            bq.fail_mex('Could not store the histogram file')
            return

        outputs = etree.Element('tag', name='outputs')
        etree.SubElement(outputs, 'tag', name='histogram', type='table', value=blob.get('uri'))
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
