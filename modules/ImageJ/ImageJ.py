#################################################
###        ImageJ Module for Bisque           ###
#################################################
import os
import re
import sys
import math
import csv
import time
import urllib
import logging
import itertools
import subprocess
import json
import urlparse
from datetime import datetime

from lxml import etree
from optparse import OptionParser

#from bqapi import BQGObject, BQEllipse, BQVertex
from bqapi.util import fetch_image_pixels, save_image_pixels


#constants
DATA_SERVICE                    = 'data_service'


#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='IJfile.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')


from bqapi.comm import BQSession
#from bq.util.mkdir import _mkdir
from bq.util.hash import is_uniq_code



def _simplify_polygon(xcoords, ycoords):
    coords = [(xcoords[i], ycoords[i]) for i in range(len(xcoords))]
    simpl_coords = _simplifyDouglasPeucker(coords)
    return [coord[0] for coord in simpl_coords], [coord[1] for coord in simpl_coords]

# ----------------------------------
#  _simplifyDouglasPeucker adapted for Python from
#  (c) 2013, Vladimir Agafonkin
#  Simplify.js, a high-performance JS polyline simplification library
#  mourner.github.io/simplify-js

def _simplifyDouglasPeucker(points, tolerance=0.6):
    sqTolerance = tolerance*tolerance
    last = len(points)-1
    simplified = [points[0]]
    _simplifyDPStep(points, 0, last, sqTolerance, simplified)
    simplified.append(points[last])
    return simplified

def _simplifyDPStep(points, first, last, sqTolerance, simplified):
    maxSqDist = sqTolerance
    for i in xrange(first+1, last):
        sqDist = _getSqSegDist(points[i], points[first], points[last])
        if sqDist > maxSqDist:
            index = i
            maxSqDist = sqDist
    if maxSqDist > sqTolerance:
        if index-first > 1:
            _simplifyDPStep(points, first, index, sqTolerance, simplified)
        simplified.append(points[index])
        if last-index > 1:
            _simplifyDPStep(points, index, last, sqTolerance, simplified)

def _getSqSegDist(p, p1, p2):
    x = p1[0]
    y = p1[1]
    dx = p2[0]-x
    dy = p2[1]-y
    if dx != 0 or dy != 0:
        t = ((p[0] - x) * dx + (p[1] - y) * dy) / (dx * dx + dy * dy)
        if t > 1:
            x = p2[0]
            y = p2[1]
        elif t > 0:
            x += dx*t
            y += dy*t
    dx = p[0]-x
    dy = p[1]-y
    return dx*dx + dy*dy

# ----------------------------------


class IJError(Exception):

    def __init__(self, message):
        self.message = "ImageJ error: %s" % message
    def __str__(self):
        return self.message        
        
 
        

class ImageJ(object):
    """
        ImageJ Module
    """

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to ImageJ's options attribute (unless already set)

            @param: mex_xml
        """
        # inputs are all non-"pipeline params" under "inputs" and all params under "pipeline_params"
        mex_inputs = mex_xml.xpath('tag[@name="inputs"]/tag[@name!="pipeline_params"] | tag[@name="inputs"]/tag[@name="pipeline_params"]/tag')
        if mex_inputs:
            for tag in mex_inputs:
                if tag.tag == 'tag' and tag.get('type', '') != 'system-input': #skip system input values
                    if not getattr(self.options,tag.get('name', ''), None):
                        log.debug('Set options with %s as %s'%(tag.get('name',''),tag.get('value','')))
                        setattr(self.options,tag.get('name',''),tag.get('value',''))
        else:
            log.debug('ImageJ: No Inputs Found on MEX!')


    def validate_input(self):
        """
            Check to see if a mex with token or user with password was provided.

            @return True is returned if validation credention was provided else
            False is returned
        """
        if (self.options.mexURL and self.options.token): #run module through engine service
            return True

        if (self.options.user and self.options.pwd and self.options.root): #run module locally (note: to test module)
            return True

        log.debug('ImageJ: Insufficient options or arguments to start this module')
        return False


    def setup(self):
        """
            Fetches the mex and appends input_configurations to the option
            attribute of ImageJ
        """
        self.bqSession.update_mex('Initializing...')
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        self.output_resources = []
        self.ppops = None
        self.ppops_url = None
        

    def run(self):
        """
            The core of the ImageJ runner
        """

        module_time = datetime.now()

        #retrieve tags
        self.bqSession.update_mex('Extracting properties')

        #type check
        image_resource = self.bqSession.fetchxml(self.options.InputFile)
        if image_resource.tag != 'image':
            raise IJError("trying to run ImageJ on non-image resource")

        # run prerun operations
        filelist = self._run_prerun_ops(module_time, pipeline_url=self.options.pipeline_url, input_xml=image_resource)
            
    
        # create pipeline with correct parameters
        pipeline_params = self.bqSession.mex.xmltree.xpath('tag[@name="inputs"]/tag[@name="pipeline_params"]/tag')
        params = {}
        for tag in pipeline_params:
            params[tag.get('name','')] = getattr(self.options, tag.get('name',''))
        pipeline_file, err_file = self._instantiate_pipeline(pipeline_url=self.options.pipeline_url, params=params)
        if not pipeline_file:
            raise IJError("trying to run incompatible ImageJ pipeline")
    
        # run ImageJ on the pipeline
        self.bqSession.update_mex('Running ImageJ')
        log.debug('run: ImageJ-linux64 -batch %s on image %s', pipeline_file, filelist)
        res = 1
        with open(err_file, 'w') as fo:
            # start virtual X server
            vfb = subprocess.Popen(['Xvfb', ':0'])
            # TODO: wait for Xvfb to show up?
            time.sleep(1)
            res = subprocess.call(['/module/Fiji.app/ImageJ-linux64', # '--headless',
                                   '-macro', pipeline_file],
                                  env = { 'DISPLAY' : ':0.0' },       # use virtual X server
                                  stderr=fo, stdout=fo)
            # stop virtual X server
            vfb.terminate()
            log.debug("ImageJ returned: %s", str(res))

        # TODO: detect error somehow!!!
#         if res > 0:
#             err_msg = 'pipeline execution failed\n'
#             with open(err_file, 'r') as fo:
#                 err_msg += ''.join(fo.readlines())
#             if len(err_msg) > 1024:
#                 err_msg = err_msg[:512] + '...' + err_msg[-512:]
#             raise IJError(err_msg)

        # run postrun operations
        self.output_resources = self._run_postrun_ops(module_time, pipeline_url=self.options.pipeline_url, output_name='output_image')

    def _cache_ppops(self, pipeline_url):
        if not self.ppops or self.ppops_url != pipeline_url:            
            pipeline_path = urlparse.urlsplit(pipeline_url).path.split('/')
            pipeline_uid = pipeline_path[1] if is_uniq_code(pipeline_path[1]) else pipeline_path[2]
            url = self.bqSession.service_url('pipeline', path = '/'.join([pipeline_uid]+['ppops:imagej']))
            self.ppops = json.loads(self.bqSession.c.fetch(url))
            self.ppops_url = pipeline_url

    def _run_prerun_ops(self, module_time, pipeline_url, input_xml):
        """
        Perform any operations necessary before the pipeline runs (e.g., extract image channels) and return filelist
        """
        self._cache_ppops(pipeline_url)
        pre_ops = self.ppops['PreOps']
        input_files = []
        for op in pre_ops:
            input_files += self._run_single_op(module_time, op, input_xml)
        filelist_file = os.path.join(self.options.stagingPath, 'filelist.txt')
        with open(filelist_file, 'w') as fo:
            for input_file in input_files:
                fo.write(input_file+'\n')
        return input_files
        
    def _run_postrun_ops(self, module_time, pipeline_url, output_name):
        """
        Perform any operations necessary after the pipeline finished (e.g., upload result tables) and return created resources
        """
        self._cache_ppops(pipeline_url)
        post_ops = self.ppops['PostOps']
        created_resources = []
        for op in post_ops:            
            created_resources += self._run_single_op(module_time, op, output_name)
        return created_resources
            
    def _run_single_op(self, module_time, op, input_xml=None, output_name=None):
        """
        Perform single pre/post operation and return list of files or resources generated
        """        
        # replace special placeholders
        if 'id' in op and op['id'] == '@INPUT':
            op['id'] = input_xml.get('resource_uniq')
        if 'name' in op and op['name'] == '@OUTPUT':
            op['name'] = output_name
        if 'filename' in op and op['filename'] == '@OUTPUT':
            op['filename'] = output_name+'.tif'
        
        res = []        
        if op['service'] == 'image_service':
            # perform image_service operation
            log.debug("RUNOP %s" % str(op))            
            url = self.bqSession.service_url('image_service', path=op['id']+op['ops'])
            # TODO: don't read image into memory!!!
            image_data = self.bqSession.c.fetch(url)
            if image_data:
                image_file = os.path.join(self.options.stagingPath, op['filename'])
                with open(image_file, 'w') as fo:
                    fo.write(image_data)
                res += [image_file]
        elif op['service'] == 'data_service':
            # perform data_service operation
            doc = self.bqSession.fetchxml(url=op['id'], view='deep,clean')
            csv_file = os.path.join(self.options.stagingPath, op['filename'])
            matches = doc.xpath(op['ops'])
            if len(matches) > 0:
                with open(csv_file, 'w') as fo:
                    for match_id in xrange(0,len(matches)):
                        match = matches[match_id]
                        line = '\t'.join([match.get(attr_name, '') for attr_name in op['attrs']]) + '\n'
                        fo.write(line)
                res += [csv_file]
        elif op['service'] == 'postblob':
            filename = op['filename']
            with open(op['name']) as namef:
                resname = namef.readlines()[0].rstrip('\n')
            # upload image or table (check op['type'])            
            dt = module_time.strftime('%Y%m%dT%H%M%S')
            final_output_file = "ModuleExecutions/ImageJ/%s/%s"%(dt,resname)
            cl_model = etree.Element('resource', resource_type=op['type'], name=final_output_file)
            # module identifier (a descriptor to be found by the ImageJ model)
            etree.SubElement(cl_model, 'tag', name='module_identifier', value='ImageJ')
            # hdf filename            
            etree.SubElement(cl_model, 'tag', name='OutputFile', value=final_output_file)
            #description
            etree.SubElement(cl_model, 'tag', name='description', value = 'output from ImageJ Module')
            # post blob
            output_file = os.path.join(self.options.stagingPath, filename)
            if os.path.isfile(output_file):
                resource = self.bqSession.postblob(output_file, xml = cl_model)
                resource_xml = etree.fromstring(resource)
                res += [resource_xml[0]]
        elif op['service'] == 'posttag':
            with open(op['name']) as namef:
                lines = namef.readlines()
                resname = lines[0].rstrip('\n')
                resval = lines[1].rstrip('\n')
            res += [etree.Element('tag', name=resname, value=resval)]
        elif op['service'] == 'postpolygon':
            # add polygon gobject to mex
            # Read object measurements from csv and write to gobjects
            (header, records) = self._readCSV(os.path.join(self.options.stagingPath, op['filename']))
            if header is not None:
                parentGObject = etree.Element('gobject', type='detected shapes', name='detected shapes')
                xcoords = []
                ycoords = []
                for i in range(len(records)):
                    curr_id = int(records[i][header.index(op['id_col'])])
                    xcoords.append(float(records[i][header.index(op['x_coord'])]))
                    ycoords.append(float(records[i][header.index(op['y_coord'])]))
                    if i == len(records)-1 or curr_id != int(records[i+1][header.index(op['id_col'])]):
                        # new polygon starts => save current one
                        xcoords, ycoords = _simplify_polygon(xcoords, ycoords)
                        shape = self._get_polygon_elem(name=str(i), xcoords=xcoords, ycoords=ycoords, label=op['label'], color=op['color'])
                        if shape:
                            parentGObject.append(shape)
                        xcoords = []
                        ycoords = []
                res += [parentGObject]
        return res

    def _instantiate_pipeline(self, pipeline_url, params):
        """
        instantiate ImageJ pipeline file with provided parameters
        """
        pipeline_path = urlparse.urlsplit(pipeline_url).path.split('/')
        pipeline_uid = pipeline_path[1] if is_uniq_code(pipeline_path[1]) else pipeline_path[2]
        url = self.bqSession.service_url('pipeline', path = '/'.join([pipeline_uid]+["setvar:%s|%s"%(tag,params[tag]) for tag in params]+['exbsteps:imagej']), query={'format':'imagej'})
        pipeline = self.bqSession.c.fetch(url)
        if not pipeline:
            # bad pipeline
            return None, None
        out_pipeline_file = os.path.join(self.options.stagingPath, 'macro.ijm')
        out_error_file = os.path.join(self.options.stagingPath, 'ij_error.txt')
        with open(out_pipeline_file, 'w') as fo:
            fo.write(pipeline)
        return out_pipeline_file, out_error_file

    def teardown(self):
        """
            Post the results to the mex xml.
        """
        self.bqSession.update_mex( 'Returning results')

        outputTag = etree.Element('tag', name ='outputs')
        for r_xml in self.output_resources:
            res_type = r_xml.get('type', None) or r_xml.get('resource_type', None) or r_xml.tag
            if res_type == 'detected shapes':
                # r_xml is a set of gobjects => append to output inside image tag 
                image_resource = self.bqSession.fetchxml(self.options.InputFile)
                image_elem = etree.SubElement(outputTag, 'tag', name=image_resource.get('name'), type='image', value=image_resource.get('uri'))
                image_elem.append(r_xml)
            elif res_type == 'tag':
                # simple tag => append to output as is
                etree.SubElement(outputTag, 'tag', name=r_xml.get('name'), value=r_xml.get('value'))
            else:
                # r_xml is some other resource (e.g., image or table) => append reference to output
                etree.SubElement(outputTag, 'tag', name='output_table' if res_type=='table' else 'output_image', type=res_type, value=r_xml.get('uri',''))

        self.bqSession.finish_mex(tags=[outputTag])

    def _get_polygon_elem(self, name, **params): 
        shape = etree.Element('gobject', name=name, type=params.get('label'))
        res = etree.SubElement(shape, 'polygon')
        xcoords = params.get('xcoords')
        ycoords = params.get('ycoords')

        try:
            for i in range(len(xcoords)):
                x = xcoords[i]
                y = ycoords[i]
                etree.SubElement(res, 'vertex', x=str(x), y=str(y))            
            etree.SubElement(res, 'tag', name='color', value=params.get('color', '#FF0000'), type='color')
        
        except KeyError:
            return None
        except ValueError:
            return None
        
        return shape
        
    def _readCSV(self, fileName):
 
        if os.path.exists(fileName) == False:
            return (None, None)
 
        records = []
        handle = open(fileName, 'rb')
        csvHandle = csv.reader(handle)
        header = csvHandle.next()
 
        for row in csvHandle:
            records.append(row)
 
        handle.close()
        return (header, records)


    def main(self):
        """
            The main function that runs everything
        """
        log.info('sysargv : %s' % sys.argv )
        parser = OptionParser()

        parser.add_option('--mex_url'         , dest="mexURL")
        parser.add_option('--module_dir'      , dest="modulePath")
        parser.add_option('--staging_path'    , dest="stagingPath")
        parser.add_option('--bisque_token'    , dest="token")
        parser.add_option('--user'            , dest="user")
        parser.add_option('--pwd'             , dest="pwd")
        parser.add_option('--root'            , dest="root")
        parser.add_option('--entrypoint'      , dest="entrypoint")

        (options, args) = parser.parse_args()

        fh = logging.FileHandler('phase_%s.log' % (options.entrypoint or 'main'), mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s ' +
                                  '(%(filename)s:%(lineno)s)',datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        log.addHandler(fh)

        try: #pull out the mex

            if not options.mexURL:
                options.mexURL = sys.argv[1]
            if not options.token:
                options.token = sys.argv[2]

        except IndexError: #no argv were set
            pass

        if not options.stagingPath:
            options.stagingPath = '/module/workdir'

        log.info('\n\nPARAMS : %s \n\n Options: %s' % (args, options))
        self.options = options

        if self.validate_input():

            #initalizes if user and password are provided
            if (self.options.user and self.options.pwd and self.options.root):
                self.bqSession = BQSession().init_local( self.options.user, self.options.pwd, bisque_root=self.options.root)
                self.options.mexURL = self.bqSession.mex.uri

            #initalizes if mex and mex token is provided
            elif (self.options.mexURL and self.options.token):
                self.bqSession = BQSession().init_mex(self.options.mexURL, self.options.token)

            else:
                raise IJError('Insufficient options or arguments to start this module')

            if not self.options.entrypoint:
                # NOT a special phase => perform regular run processing
                try:
                    self.setup()
                except Exception as e:
                    log.exception("Exception during setup")
                    self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                    return

                try:
                    self.run()
                except (Exception, IJError) as e:
                    log.exception("Exception during run")
                    self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
                    return

                try:
                    self.teardown()
                except (Exception, IJError) as e:
                    log.exception("Exception during teardown")
                    self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
                    return

            else:
                # in a special phase => run special code                
                self.bqSession.fail_mex(msg = "Unknown ImageJ entrypoint: %s" %  self.options.entrypoint)
                return

            self.bqSession.close()

if __name__=="__main__":
    ImageJ().main()