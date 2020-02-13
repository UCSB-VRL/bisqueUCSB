#################################################
###          Dream3D Module for Bisque UCSB   ###
#################################################
import os
import re
import sys
import time
import urllib
import logging
import itertools
import subprocess
import json
from datetime import datetime

from lxml import etree
from optparse import OptionParser


#constants
DATA_SERVICE                    = 'data_service'


#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='Dream3Dfile.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')


from bqapi.comm import BQSession
#from bq.util.mkdir import _mkdir


# replace "@..." placeholders in json structure based on provided params dict
def _replace_placeholders(myjson, input_file, output_file, params):
    if type(myjson) is dict:
        for jsonkey in myjson:
            if type(myjson[jsonkey]) in (list, dict):
                _replace_placeholders(myjson[jsonkey], input_file, output_file, params)
            elif isinstance(myjson[jsonkey], basestring):
                try:
                    if myjson[jsonkey] == '@INPUT':
                        myjson[jsonkey] = input_file
                    elif myjson[jsonkey] == '@OUTPUT':
                        myjson[jsonkey] = output_file
                    elif myjson[jsonkey].startswith('@NUMPARAM'):
                        myjson[jsonkey] = float(params[jsonkey])
                    elif myjson[jsonkey].startswith('@STRPARAM'):
                        myjson[jsonkey] = str(params[jsonkey])
                except KeyError:
                    raise Dream3DError("pipeline parameter '%s' not provided" % jsonkey)
    elif type(myjson) is list:
        for item in myjson:
            if type(item) in (list, dict):
                _replace_placeholders(item, input_file, output_file, params)
                    

class Dream3DError(Exception):
    
    def __init__(self, message):
        self.message = "Dream3D error: %s" % message
    def __str__(self):
        return self.message
  

class Dream3D(object):
    """
        Dream3D Module
    """

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to Dream3D's options attribute (unless already set)
            
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
            log.debug('Dream3D: No Inputs Found on MEX!')
    

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
        
        log.debug('Dream3D: Insufficient options or arguments to start this module')
        return False
    
    
    def setup(self):
        """
            Fetches the mex and appends input_configurations to the option
            attribute of Dream3D
        """
        self.bqSession.update_mex('Initializing...')
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        self.output_file = None

    
    def run(self):
        """
            The core of the Dream3D runner
        """
                
        #retrieve tags
        self.bqSession.update_mex('Extracting properties')
        
        #type check
        hdf_resource = self.bqSession.fetchxml(self.options.InputFile, view='deep,clean')
        if (hdf_resource.tag != 'resource' or hdf_resource.get('resource_type', '') != 'table') and hdf_resource.tag != 'table':
            raise Dream3DError("trying to run Dream3D on non-table resource")
        
        hdf_url = self.bqSession.service_url('blob_service', path=hdf_resource.get('resource_uniq'))
        self.bqSession.fetchblob(hdf_url, path=os.path.join(self.options.stagingPath, 'input.h5'))
        hdf_input_file = os.path.join(self.options.stagingPath, 'input.h5')            
        hdf_output_file = os.path.join(self.options.stagingPath, 'output.h5')

        # create pipeline with correct parameters
        pipeline_params = self.bqSession.mex.xmltree.xpath('tag[@name="inputs"]/tag[@name="pipeline_params"]/tag')
        params = {}
        for tag in pipeline_params:
            params[tag.get('name','')] = getattr(self.options, tag.get('name',''))
        pipeline_file, err_file = self._instantiate_pipeline(pipeline_url=self.options.pipeline_url, input_file=hdf_input_file, output_file=hdf_output_file, params=params)

        # run Dream3D on the pipeline
        self.bqSession.update_mex('Running Dream3D')
        log.debug('run Dream3D on %s', pipeline_file)
        res = 1        
        with open(err_file, 'w') as fo:
#             res = 0  #!!! TESTING
#             open(hdf_output_file, 'a').close()
            res = subprocess.call(['/build/Bin/PipelineRunner',
                                   '-p',
                                   pipeline_file],
                                  stderr=fo, stdout=fo)
            log.debug("Dream3D returned: %s", str(res))
        
        if res > 0:
            err_msg = 'pipeline execution failed\n'
            with open(err_file, 'r') as fo:
                err_msg += ''.join(fo.readlines())
            raise Dream3DError(err_msg)
        
        self.output_file = hdf_output_file
                    
    def _instantiate_pipeline(self, pipeline_url, input_file, output_file, params):
        """instantiate pipeline json file with provided parameters"""
        pipeline_resource = self.bqSession.fetchxml(pipeline_url, view='short')
        out_pipeline_file = os.path.join(self.options.stagingPath, 'pipeline.json')
        out_error_file = os.path.join(self.options.stagingPath, 'dream3d_error.txt')
        pipeline_url = self.bqSession.service_url('blob_service', path=pipeline_resource.get('resource_uniq'))
        self.bqSession.fetchblob(pipeline_url, path=os.path.join(self.options.stagingPath, 'pipeline_uninit.json'))
        pipeline_file = os.path.join(self.options.stagingPath, 'pipeline_uninit.json')
        with open(pipeline_file, 'r') as fi:
            pipeline = json.load(fi)
            # replace all placeholders in pipeline template
            _replace_placeholders(pipeline, input_file, output_file, params)
            # write out pipeline to provided file            
            with open(out_pipeline_file, 'w') as fo:
                json.dump(pipeline, fo)
        return out_pipeline_file, out_error_file
            
    def teardown(self):
        """
            Post the results to the mex xml.
        """
        #save the HDF output and upload it to the data service with all the meta data
        self.bqSession.update_mex( 'Returning results')
        log.debug('Storing HDF output')                        
        
        #constructing and storing HDF file
        mex_id = self.bqSession.mex.uri.split('/')[-1]
        dt = datetime.now().strftime('%Y%m%dT%H%M%S')
        final_output_file = "ModuleExecutions/Dream3D/%s_%s_%s.h5"%(self.options.OutputPrefix, dt, mex_id)
        
        #does not accept no name on the resource
        cl_model = etree.Element('resource', resource_type='table', name=final_output_file)
                
        #module identifier (a descriptor to be found by the Dream3D model)
        etree.SubElement(cl_model, 'tag', name='module_identifier', value='Dream3D')        
        
        #hdf filename
        etree.SubElement(cl_model, 'tag', name='OutputFile', value=final_output_file)
        
        #pipeline param
        #etree.SubElement(cl_model, 'tag', name='RefFrameZDir', value=self.options.RefFrameZDir)
        
        #input hdf url
        #etree.SubElement(cl_model, 'tag', name='InputFile', type='link', value=self.options.InputFile)
        
        #input pipeline
        #etree.SubElement(cl_model, 'tag', name='pipeline_url', type='link', value=self.options.pipeline_url)
        
        #description
        etree.SubElement(cl_model, 'tag', name='description', value = 'HDF output file from Dream3D Module')
                
        #storing the HDF file in blobservice
        log.debug('before postblob')   #!!!
        r = self.bqSession.postblob(self.output_file, xml = cl_model)        
        r_xml = etree.fromstring(r)
        
        outputTag = etree.Element('tag', name ='outputs')
        etree.SubElement(outputTag, 'tag', name='output_hdf', type='table', value=r_xml[0].get('uri',''))

        self.bqSession.finish_mex(tags=[outputTag])        
    
    
    def collect_outputs(self):
        """
            Perform reduce phase (i.e., examine final (top) mex and create any additional outputs based on submexes)
            THIS IS JUST AN EXAMPLE.
        """
        # collect submex output hdf urls and add them to top mex outputs section
        top_mex = self.bqSession.fetchxml(self.options.mexURL, view='deep')
        outputTag = top_mex.xpath('/mex/tag[@name="outputs"]')[0]        
        output_hdfs = top_mex.xpath('/mex/mex/tag[@name="outputs"]/tag[@name="output_hdf"]/@value')
        etree.SubElement(outputTag, 'tag', name='all_outputs', value=';'.join([id.split('/')[-1] for id in output_hdfs])) 
                                                
        self.bqSession.postxml(url=outputTag.get('uri'), xml=outputTag)
    
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
        # for the reduce phase: create output dataset of output HDFs (in this case, mexURL is top mex)
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
            options.stagingPath = ''
            
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
                raise Dream3DError('Insufficient options or arguments to start this module')
                        
            if not self.options.entrypoint:
                # NOT a reduce phase => perform regular run processing
                try:
                    self.setup()
                except Exception as e:
                    log.exception("Exception during setup")
                    self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                    return
                
                try:
                    self.run()
                except (Exception, Dream3DError) as e:
                    log.exception("Exception during run")
                    self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
                    return
    
                try:
                    self.teardown()
                except (Exception, Dream3DError) as e:
                    log.exception("Exception during teardown")
                    self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
                    return
                
            else:
                # in a reduce phase => run reduce code
                if self.options.entrypoint != 'collect_outputs':
                    self.bqSession.fail_mex(msg = "Unknown Dream3D entrypoint: %s" %  self.options.entrypoint)
                    return
                
                try:
                    self.collect_outputs()
                except (Exception, Dream3DError) as e:
                    log.exception("Exception during collect_outputs")
                    self.bqSession.fail_mex(msg = "Exception during collect_outputs: %s" % str(e))
                    return
                   
            self.bqSession.close()
    
if __name__=="__main__":
    Dream3D().main()
