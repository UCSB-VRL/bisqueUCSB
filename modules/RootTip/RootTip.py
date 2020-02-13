#!/usr/bin/env python
import os
import sys
import optparse
import subprocess
import csv
import logging
import itertools

from bqapi import BQSession
from bqapi.util import fetch_image_planes, AttrDict

logging.basicConfig(level=logging.DEBUG)

EXEC = "./araGT"

def gettag (el, tagname):
    for kid in el:
        if kid.get ('name') == tagname:
            return kid, kid.get('value')
    return None,None

class RootTip(object):

    def setup(self):
        #if not os.path.exists(self.images):
        #    os.makedirs(self.images)
        self.status = 0
        self.bq.update_mex('initializing')

        results = fetch_image_planes(self.bq, self.resource_url, '.')


    def start(self):
        self.bq.update_mex('executing')
        # Matlab requires trailing slash
        self.status = subprocess.call([EXEC, './'])


    def teardown(self):
        # Post all submex for files and return xml list of results
        self.bq.update_mex('checking results')
        if self.status != 0:
            self.bq.fail_mex ("Bad result code form analysis: %d" % self.status)
            return
        gobjects = self._read_results()
        tags = [{ 'name': 'outputs',
                  'tag' : [{'name': 'roots', 'type':'image', 'value':self.resource_url,
                            'gobject' : [{ 'name': 'root_tips', 'type': 'root_tips', 'gobject' : gobjects }] }]
                  }]
        self.bq.update_mex('saving results')
        self.bq.finish_mex(tags = tags)

    def _read_results(self, ):
        results  = []
        image = self.bq.load(self.resource_url, view='full')
        xmax, ymax, zmax, tmax, ch = image.geometry()
        tips = csv.reader(open('tips.csv','rb'))
        angles = csv.reader(open('angle.csv','rb'))
        grates = csv.reader(open('gr.csv','rb'))
        for index, (tip, angle, gr)  in enumerate(itertools.izip(tips, angles, grates)):
            results.append({
                    'type' : 'tipangle',
                    'tag' : [{ 'name': 'angle', 'value': angle[0]},
                             { 'name': 'growth', 'value': gr[0]}, ],
                    'point' : {
                        'vertex' : [ { 'x': str(xmax - int(tip[1])), 'y':tip[0], 't':index } ] ,
                        }
                    })
        return results



    def run(self):
        parser  = optparse.OptionParser()
        parser.add_option('-d','--debug', action="store_true")
        parser.add_option('-n','--dryrun', action="store_true")
        parser.add_option('--credentials')
        parser.add_option('--image_url')

        (options, args) = parser.parse_args()
        named = AttrDict (bisque_token=None, mex_url=None, staging_path=None, image_url=None)
        for arg in list(args):
            tag, sep, val = arg.partition('=')
            if sep == '=':
                named[tag] = val
                args.remove(arg)

        if named.bisque_token:
            self.bq = BQSession().init_mex(named.mex_url, named.bisque_token)
            self.resource_url = self.bq.parameter_value ('image_url')
        elif options.credentials:
            user,pwd = options.credentials.split(':')
            self.bq = BQSession().init_local(user,pwd)
            self.resource_url =  named.image_url
        else:
            parser.error('need bisque_token or user credential')

        if self.resource_url is None:
            parser.error('Need a resource_url')

        if not args :
            commands = ['setup', 'start', 'teardown']
        else:
            commands = [ args ]

        try:
            for command in commands:
                command = getattr(self, command)
                r = command()
        except Exception, e:
            logging.exception ("problem during %s" % command)
            self.bq.fail_mex(msg = "Exception during %s: %s" % (command,  e))
            sys.exit(1)

        sys.exit(0)


if __name__ == "__main__":
    RootTip().run()
