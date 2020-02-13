import sys
import traceback
from operator import itemgetter
import itertools
from datetime import datetime

try:
    from lxml import etree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from bqapi import BQSession, BQTag, BQCommError

import logging
logging.basicConfig(filename='AnnotationExportGeo.log',level=logging.DEBUG)


headers = {
    'kml': '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
    'geojson': '{"type": "FeatureCollection", "features": [',
}

footers = {
    'kml': '</Document></kml>',
    'geojson': ']}',
}

separators = {
    'kml': '',
    'geojson': ',',
}

class AnnotationGeo(object):
    """Example Python module
    Read tags from image server and store tags on image directly
    """
    def main(self, mex_url=None, bisque_token=None, bq=None):
        #  Allow for testing by passing an alreay initialized session
        if bq is None:
            bq = BQSession().init_mex(mex_url, bisque_token)
        bq.update_mex('Starting')
        image_url = bq.parameter_value(name='dataset_url')
        fmt = bq.parameter_value(name='format').lower()

        mex_id = mex_url.split('/')[-1]
        dt = datetime.now().strftime('%Y%m%d%H%M%S')
        if image_url is None or len(image_url)<2:
            datasets = bq.fetchxml ('/data_service/dataset')
            datasets = [d.get('uri') for d in datasets.xpath('dataset')]
        else:
            datasets = [image_url]

        output = []
        for ds_url in datasets:
            try:
                _,uniq = ds_url.rsplit('/', 1)
                bq.update_mex('processing "%s"'%uniq)
                url = '%s/export/%s?format=%s'%(bq.bisque_root, uniq, fmt)
                o = bq.c.fetch(url, headers = {'Content-Type':'text/plain', 'Accept':'text/plain'})
                # strip header and footer from individual files
                if len(o)>0 and o.startswith(headers[fmt]) and o.endswith(footers[fmt]):
                    o = o[len(headers[fmt]):-len(footers[fmt])]

                if o is not None and len(o)>0:
                    output.append(o)
            except Exception:
                pass

        #write into a file
        out_filename = 'annotations_%s_%s.%s'%(dt, mex_id, fmt)
        with open(out_filename, 'w') as f:
            f.write(headers[fmt])
            f.write(separators[fmt].join(output))
            f.write(footers[fmt])

        # need to save the CSV file and write its reference
        resource = etree.Element('file', name='ModuleExecutions/AnnotationExportGeo/%s'%(out_filename) )
        blob = etree.XML(bq.postblob(out_filename, xml=resource))
        #print etree.tostring(blob)
        blob = blob.find('./')
        if blob is None or blob.get('uri') is None:
            bq.fail_mex('Could not store the Geo file into the system')
        else:
            bq.finish_mex(tags = [{ 'name': 'outputs',
                                    'tag' : [{ 'name': 'export',
                                               'value': blob.get('uri'),
                                               'type' : 'file' }]}])

if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-c", "--credentials", dest="credentials",
                      help="credentials are in the form user:password")
    #parser.add_option('--mex_url')
    #parser.add_option('--auth_token')

    (options, args) = parser.parse_args()

    M = AnnotationGeo()
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


