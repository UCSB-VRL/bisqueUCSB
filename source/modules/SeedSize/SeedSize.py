#!/usr/bin/env python
import os
import sys
import optparse
import subprocess
import glob
import csv
import pickle
import logging
import itertools

from bqapi import BQSession
from bqapi.util import fetch_dataset, fetch_image_pixels, d2xml



EXEC = "./seedSize"
IMAGE_MAP = "image_map.txt"

def gettag (el, tagname):
    for kid in el:
        if kid.get ('name') == tagname:
            return kid, kid.get('value')
    return None,None

class SeedSize(object):

    def setup(self):
        if not os.path.exists(self.images):
            os.makedirs(self.images)

        self.bq.update_mex('initializing')
        if self.is_dataset:
            results = fetch_dataset(self.bq, self.resource_url, self.images)
        else:
            results = fetch_image_pixels(self.bq, self.resource_url, self.images)

        with open(self.image_map_name, 'wb') as f:
            pickle.dump(results, f)
        return 0


    def start(self):
        self.bq.update_mex('executing')
        # Matlab requires trailing slash
        r = subprocess.call([EXEC, 'images/'])
        return r

    def teardown(self):
        with  open(self.image_map_name, 'rb') as f:
            self.url2file = pickle.load(f) #
            self.file2url =  dict((v,k) for k,v in self.url2file.iteritems())

        summary    = os.path.join(self.images, 'summary.csv')

        if not os.path.exists (summary):
            self.bq.fail_mex (msg = "did not find any seeds: missing %s" % summary)
            return 0

        summary_tags = self._read_summary(summary)

        # Post all submex for files and return xml list of results
        tags = []
        gobjects = []
        submexes = []
        if not self.is_dataset:
            localfiles = glob.glob(os.path.join(self.images, '*C.csv'))
            gobs = self._read_results(localfiles[0])
            #tags = [{ 'name':'image_url', 'value' : self.resource_url}]
            tags = [{ 'name': 'outputs',
                      'tag' : [{'name': 'Summary',  'tag' : summary_tags} ,
                               {'name': 'seed-resource', 'type':'image', 'value':self.resource_url,
                                'gobject' : [{ 'name': 'seeds', 'type' : 'seedsize', 'gobject':gobs }], }],
                      }]
        else:
            submexes = self._get_submexes()
            tags = [
                { 'name': 'execute_options',
                  'tag' : [ {'name': 'iterable', 'value' : 'image_url' } ]
                  },
                { 'name': 'outputs',
                  'tag' : [{'name': 'Summary',  'tag' : summary_tags },
                           {'name': 'mex_url', 'value': self.mex_url, 'type': 'mex'},
                           {'name': 'image_url', 'type':'dataset', 'value':self.resource_url,}]
                  },
                    ]
            # for i, submex in enumerate(mexlist):
            #     tag, image_url = gettag(submex, 'image_url')
            #     gob, gob_url = gettag(submex, 'SeedSize')
            #     mexlink = { 'name' : 'submex',
            #                 'tag'  : [{ 'name':'mex_url', 'value':submex.get('uri')},
            #                           { 'name':'image_url', 'value' : image_url},
            #                           { 'name':'gobject_url', 'value' : gob.get('uri') } ]
            #                 }
            #     tags.append(mexlink)
        self.bq.finish_mex(tags = tags, gobjects = gobjects, children= [('mex', submexes)])
        return 0


    def _get_submexes(self):
        submex = []
        localfiles = glob.glob(os.path.join(self.images, '*C.csv'))
        result2url = dict( (os.path.splitext(f)[0] + 'C.csv', u) for f, u in self.file2url.items())
        for result in localfiles:
            gobs = self._read_results(result)
            if result not in result2url:
                logging.error ("Can't find url for %s given files %s and map %s" %
                           result, localfiles, result2url)
            mex = { 'type' : self.bq.mex.type,
                    'name' : self.bq.mex.name,
                    'value': 'FINISHED',
                    'tag': [ { 'name': 'inputs',
                               'tag' : [ {'name': 'image_url', 'value' : result2url [result] } ]
                             },
                             { 'name': 'outputs',
                              'tag' : [{'name': 'seed-resource', 'type':'image', 'value':  result2url [result],
                                        'gobject':{ 'name': 'seeds', 'type': 'seedsize', 'gobject': gobs}, }] }]
                    }
            submex.append (mex)
        return submex

        #url = self.bq.service_url('data_service', 'mex', query={ 'view' : 'deep' })
        #response = self.bq.postxml(url, d2xml({'request' : {'mex': submex}} ))
        #return response


    def _read_summary(self, csvfile):
        #%mean(area), mean(minoraxislen), mean(majoraxislen), standarddev(area),
        #standarddev(minoraxislen), standarddev(majoraxislen), total seedcount,
        #mean thresholdused, weighted mean of percentclusters1, weighted mean of percentclusters2
        f= open(csvfile,'rb')
        rows = csv.reader (f)
        tag_names = [ 'mean_area', 'mean_minoraxis', 'mean_majoraxis',
                      'std_area', 'std_minoraxis', 'std_majoraxis',
                      'seedcount',
                      'mean_threshhold',
                      'weighted_mean_cluster_1','weighted_mean_cluster_2',
                      ]

        # Read one row(rows.next()) and zip ( name, col) unpacking in d2xml format
        summary_tags = [ { 'name': n[0], 'value' : n[1] }
                         for n in itertools.izip(tag_names, rows.next()) ]
        f.close()

        return summary_tags

    def _read_results(self, csvfile):
        results  = []
        f= open(csvfile,'rb')
        rows = csv.reader (f)
        for col in rows:
            results.append( {
                    'type' : 'seed',
                    'tag' : [ { 'name': 'area', 'value': col[0]},
                              { 'name': 'major', 'value': col[2]},
                              { 'name': 'minor', 'value': col[1]} ],
                    'ellipse' : {
                        'vertex' : [ { 'x': col[3], 'y':col[4], 'index':0 },
                                     { 'x': float(col[3]) - abs(float(col[8]) - float(col[3])), 'y':col[9], 'index':1 },
                                     { 'x': col[6], 'y':col[7], 'index':2 }]
                        }
                    })
        f.close()
        return results



    def run(self):
        logging.basicConfig(level=logging.DEBUG)

        parser  = optparse.OptionParser()
        parser.add_option('-d','--debug', action="store_true")
        parser.add_option('-n','--dryrun', action="store_true")
        #parser.add_option('--resource_url')
        #parser.add_option('--mex_url')
        #parser.add_option('--staging_path')
        #parser.add_option('--bisque_token')
        #parser.add_option('--credentials')

        # Parse named arguments from list


        (options, args) = parser.parse_args()
        named_args =dict( [ y for y in [ x.split ('=') for x in args ] if len (y) == 2] )
        args  =  [  x for x in args if '=' not in x  ]

        staging_path = '.'
        self.auth_token = named_args.get ('bisque_token')
        self.image_map_name = os.path.join(staging_path, IMAGE_MAP)
        self.resource_url = named_args.get ('image_url')
        self.mex_url = named_args.get ('mex_url')
        self.images = os.path.join(staging_path, 'images') + os.sep


        if self.auth_token:
            self.bq = BQSession().init_mex(self.mex_url, self.auth_token)
        else:
            user,pwd = options.credentials.split(':')
            self.bq = BQSession().init_local(user,pwd)

        resource_xml = self.bq.fetchxml (self.resource_url, view='short')
        self.is_dataset = resource_xml.tag == 'dataset'

        if len(args) == 1:
            commands = [ args.pop(0)]
        else:
            commands =['setup','start', 'teardown']

        #if command not in ('setup','teardown', 'start'):
        #    parser.error('Command must be start, setup or teardown')


        # maltab code requires trailing slash..

        try:
            for command in commands:
                command = getattr(self, command)
                r = command()
        except Exception, e:
            logging.exception ("problem during %s" % command)
            self.bq.fail_mex(msg = "Exception during %s: %s" % (command,  str(e)))
            sys.exit(1)

        sys.exit(r)



if __name__ == "__main__":
    SeedSize().run()
