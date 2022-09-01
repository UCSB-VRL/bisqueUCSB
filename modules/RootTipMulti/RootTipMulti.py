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
from bqapi.util import fetch_image_planes, AttrDict
from lxml.builder import E


logging.basicConfig(level=logging.DEBUG)

EXEC = "./maizeG"

def gettag (el, tagname):
    for kid in el:
        if kid.get ('name') == tagname:
            return kid, kid.get('value')
    return None,None

class RootTip(object):

    def setup(self):
        #if not os.path.exists(self.images):
        #    os.makedirs(self.images)

        self.bq.update_mex('initializing')

        results = fetch_image_planes(self.bq, self.resource_url, '.')

        # extract gobject inputs
        tips = self.bq.mex.find('inputs', 'tag').find('image_url', 'tag').find('tips', 'gobject')
        with open('inputtips.csv', 'w') as TIPS:
            for point in tips.gobjects:
                print >>TIPS, "%(y)s, %(x)s" % dict(x=point.vertices[0].x,y=point.vertices[0].y)



    def start(self):
        self.bq.update_mex('executing')
        # Matlab requires trailing slash
        subprocess.call([EXEC, './'])


    def teardown(self):
        # Post all submex for files and return xml list of results
        gobjects = self._read_results()
        tags = [{ 'name': 'outputs',
                  'tag' : [{'name': 'rootimage', 'type':'image', 'value':self.resource_url,
                            'gobject' : [{ 'name': 'root_tips', 'type': 'root_tips', 'gobject' : gobjects }] }]
                  }]
        self.bq.finish_mex(tags = tags)

    def _read_results(self, ):
        results  = []
        #image = self.bq.load(self.resource_url, view='full')
        #xmax, ymax, zmax, tmax, ch = image.geometry()
        #  each line is a time point, tracked points in line
        tips = [ t for t in csv.reader(open('tips.csv','rb')) ]
        # each line is a time point, tracked points per line pt1, pt2, pt2
        angles = [ a for a in csv.reader(open('angles.csv','rb')) ]
        # We want to generate lines in time to keep the tracked point in a single object
        # <gobject name="Tip 1" >
        #    <gobject type=tipangle>
        #      <point x= y=  t=1..N  >
        #      <tag name="angle" value="" />
        #    <gobject>
        #    ...
        # </gobject>
        # <gobject name="Tip 2" >
        #
        planes = len(angles)
        tip_count   = planes and len(angles[0]) or 0
        tracks = []
        for pt in range(tip_count):
            gobs = []
            for t_plane in range(planes):
                gobs.append(
                    {'type': 'tipangle',
                     'tag': [{ 'name': 'angle', 'value': angles[t_plane][pt] }],
                     'point':[{'vertex' :
                               [{ 't': str(t_plane), 'x': str(tips[t_plane][pt*2]),
                                  'y': str(tips[t_plane][pt*2+1]) }]
                               }]
                     })
            tracks.append({'name': 'tip-%s' % pt, 'type': 'roottip', 'gobject': gobs})

        return tracks



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
        self.named_args = named
        self.staging_path = named.get('staging_path')

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

        #command = args.pop(0)

        #if command not in ('setup','teardown', 'start'):
        #    parser.error('Command must be start, setup or teardown')

        # maltab code requires trailing slash..
        #self.images = os.path.join(options.staging_path, 'images') + os.sep
        #self.image_map_name = os.path.join(options.staging_path, IMAGE_MAP)
        #self.resource_url = options.resource_url
        #self.config = options
        #self.is_dataset = 'dataset' in self.resource_url


        #command = getattr(self, command)
        #command()





if __name__ == "__main__":
    RootTip().run()
