__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

import os
import logging
import sys
import inspect
from datetime import datetime
import ConfigParser

from lxml import etree
import pandas as pd

#from bqapi import *
from bqapi import BQSession, BQCommError

config_file = 'config.cfg'

fn = sys.argv[1]
dataset_name = fn.replace('.xlsx', '')
W = 2048
H = 2048

##################################################################
# create session
##################################################################

#config = ConfigParser.ConfigParser()
#config.read(config_file)
#root = config.get('Host', 'root') or 'http://bisque.ece.ucsb.edu'
#user = config.get('Host', 'user') or 'Mex'
#pswd = config.get('Host', 'password') or 'Mary:00-rvFkDRQyoheksMZnhBhi2n'
#session = BQSession().init_local(user, pswd,  bisque_root=root, create_mex=False)

mex_url = 'http://bisque.ece.ucsb.edu/module_service/mex/00-rvFkDRQyoheksMZnhBhi2n'
bisque_token = 'Mary:00-rvFkDRQyoheksMZnhBhi2n'
session = BQSession().init_mex(mex_url, bisque_token)

##################################################################
# index excel file
##################################################################


# filename-row hash
meta = {}
data = pd.read_excel(fn)
Ks = data.keys()
N = len(data['ImageName'])

for i in range(N):
    fn = data['ImageName'][i].strip(' ')
    m = {}
    for k in Ks:
        v = data[k][i]
        if isinstance(v, basestring):
            m[k] = v.strip(' ')
        else:
            m[k] = v
    meta[fn] = m

##################################################################
# load dataset
##################################################################

query_url = '/data_service/dataset?tag_query=@name:%s&offset=0&limit=10'%(dataset_name)
q = session.fetchxml (query_url)
ds = q.xpath('dataset')
if len(ds)>1:
    print 'Stopping: found more than one dataset with a given name: %s'%dataset_name
    sys.exit()
dataset_url = ds[0].get('uri')

dataset = session.fetchxml (dataset_url, view='deep')
images = dataset.xpath('value')

for m in images:
    image_url = m.text
    image = session.fetchxml (image_url, view='deep')
    if image.tag != 'image':
        continue
    #print etree.tostring(image)

    image_name = image.get('name')
    if image_name not in meta:
        print 'Image was not found in the local metadata: %s'%image_name
        continue
    m = meta[image_name]
    imu = etree.Element ('image', uri=image_url)

    # datetime
    if len(image.xpath('//tag[@name="datetime"]'))<1:
        #<tag name="datetime" type="datetime" value="2011-10-07T23:25:56.330000"/>
        v = m['Date'].strftime("%Y-%m-%d")
        v = '%sT%s'%(v, m['Time'].strftime("%H:%M:%S.%f"))
        t = etree.SubElement (imu, 'tag', name='datetime', type='datetime', value=v)

    # altitude
    if len(image.xpath('//tag[@name="altitude"]'))<1:
        v = str(m['Altitude_m'])
        t = etree.SubElement (imu, 'tag', name='altitude', type='number', value=v)
        t = etree.SubElement (imu, 'tag', name='altitude_units', value='m')

    # depth
    if len(image.xpath('//tag[@name="depth"]'))<1:
        v = str(m['AUVdepth_m'])
        t = etree.SubElement (imu, 'tag', name='depth', type='number', value=v)
        t = etree.SubElement (imu, 'tag', name='depth_units', value='m')

    # area
    if len(image.xpath('//tag[@name="area"]'))<1:
        v = str(m['ImageArea'])
        t = etree.SubElement (imu, 'tag', name='area', type='number', value=v)
        t = etree.SubElement (imu, 'tag', name='area_units', value='m^2')

    # relative_position
    if len(image.xpath('//tag[@name="relative_position_x"]'))<1:
        t = etree.SubElement (imu, 'tag', name='relative_position_x', type='number', value=str(m['LocalX_m']))
        t = etree.SubElement (imu, 'tag', name='relative_position_y', type='number', value=str(m['LocalY_m']))
        t = etree.SubElement (imu, 'tag', name='relative_position_units', value='m^2')

    # geo coordinate
    if len(image.xpath('//tag[@name="Geo"]/tag[@name="Coordinates"]/tag[@name="center"]'))<1:
        v = '%s,%s,%s'%(m['Latitude'], m['Longitude'], m['AUVdepth_m'])
        t = etree.SubElement (imu, 'tag', name='Geo')
        t = etree.SubElement (t, 'tag', name='Coordinates')
        t = etree.SubElement (t, 'tag', name='center', value=v)

    # image physical size
    if len(image.xpath('//tag[@name="image_size_x"]'))<1:
        t = etree.SubElement (imu, 'tag', name='image_size_x', type='number', value=str(m['ImageWidth_m']))
        t = etree.SubElement (imu, 'tag', name='image_size_y', type='number', value=str(m['ImageHeight_m']))
        t = etree.SubElement (imu, 'tag', name='image_size_units', value='m')

        res_x = float(m['ImageWidth_m']) / float(W)
        res_y = float(m['ImageHeight_m']) / float(H)

        mt = image.xpath('//tag[@name="image_meta" and @type="image_meta"]')
        if len(mt)>0:
            mt = mt[0]
        else:
            mt = etree.SubElement (imu, 'tag', name='image_meta', type='image_meta')

        t = mt.xpath('tag[@name="pixel_resolution_x"]')
        if len(t)>0:
            t[0].set('value', str(res_x))
        else:
            etree.SubElement (mt, 'tag', name='pixel_resolution_x', type='number', value=str(res_x))
            etree.SubElement (mt, 'tag', name='pixel_resolution_unit_x', value='m')

        t = mt.xpath('tag[@name="pixel_resolution_y"]')
        if len(t)>0:
            t[0].set('value', str(res_y))
        else:
            etree.SubElement (mt, 'tag', name='pixel_resolution_y', type='number', value=str(res_y))
            etree.SubElement (mt, 'tag', name='pixel_resolution_unit_y', value='m')

    if len(imu.xpath('//tag'))<1:
        print 'No updates needed for: %s'%image_name
        continue

    #post the image back
    print 'Image updated, storing %s to %s'%(image_name, image_url)
    print etree.tostring(imu)

    r = session.postxml(image_url, imu, method='POST')
    if r is None:
        print 'Uploading update failed'
    #print etree.tostring(r)

    #remove image cache
    cache_url = '%s?cleancache'%image_url.replace('/data_service/', '/image_service/')
    url = session.c.prepare_url(cache_url)
    r = session.c.webreq (method='GET', url=url)


