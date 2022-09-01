#################################################
###          Dream3D Module for Bisque        ###
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
import urlparse
from datetime import datetime

from lxml import etree
from optparse import OptionParser


#constants
DATA_SERVICE                    = 'data_service'


#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='Dream3Dfile.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')


from bqapi.comm import BQSession
from bq.util.mkdir import _mkdir
from bq.util.hash import is_uniq_code


# replace "@..." placeholders in json structure based on provided params dict
# def _replace_placeholders(myjson, input_file, output_file, params):
#     if type(myjson) is dict:
#         for jsonkey in myjson:
#             if type(myjson[jsonkey]) in (list, dict):
#                 _replace_placeholders(myjson[jsonkey], input_file, output_file, params)
#             elif isinstance(myjson[jsonkey], basestring):
#                 try:
#                     if myjson[jsonkey] == '@INPUT':
#                         myjson[jsonkey] = input_file
#                     elif myjson[jsonkey] == '@OUTPUT':
#                         myjson[jsonkey] = output_file
#                     elif myjson[jsonkey].startswith('@NUMPARAM'):
#                         myjson[jsonkey] = float(params[jsonkey])
#                     elif myjson[jsonkey].startswith('@STRPARAM'):
#                         myjson[jsonkey] = str(params[jsonkey])
#                 except KeyError:
#                     raise Dream3DError("pipeline parameter '%s' not provided" % jsonkey)
#     elif type(myjson) is list:
#         for item in myjson:
#             if type(item) in (list, dict):
#                 _replace_placeholders(item, input_file, output_file, params)


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
        self.output_resources = []
        self.ppops = None
        self.ppops_url = None
        

    def run(self):
        """
            The core of the Dream3D runner
        """

        module_time = datetime.now()

        #retrieve tags
        self.bqSession.update_mex('Extracting properties')

        #type check
        hdf_resource = self.bqSession.fetchxml(self.options.InputFile, view='deep,clean')
        if (hdf_resource.tag != 'resource' or hdf_resource.get('resource_type', '') != 'table') and hdf_resource.tag != 'table':
            raise Dream3DError("trying to run Dream3D on non-table resource")

        # run prerun operations
        filelist_file = self._run_prerun_ops(module_time, pipeline_url=self.options.pipeline_url, input_xml=hdf_resource)

        # create pipeline with correct parameters
        pipeline_params = self.bqSession.mex.xmltree.xpath('tag[@name="inputs"]/tag[@name="pipeline_params"]/tag')
        params = {}
        for tag in pipeline_params:
            params[tag.get('name','')] = getattr(self.options, tag.get('name',''))
        pipeline_file, err_file = self._instantiate_pipeline(pipeline_url=self.options.pipeline_url, params=params)
        if not pipeline_file:
            raise Dream3DError("trying to run incompatible Dream.3D pipeline")
        
        # run Dream3D on the pipeline
        self.bqSession.update_mex('Running Dream3D')
        log.debug('run Dream3D on %s', pipeline_file)
        res = 1
        with open(err_file, 'w') as fo:
            res = subprocess.call(['/dream3d/bin/PipelineRunner',
                                   '-p',
                                   pipeline_file],
                                  stderr=fo, stdout=fo)
            log.debug("Dream3D returned: %s", str(res))

        if res > 0:
            err_msg = 'pipeline execution failed\n'
            with open(err_file, 'r') as fo:
                err_msg += ''.join(fo.readlines())
            if len(err_msg) > 1024:
                err_msg = err_msg[:512] + '...' + err_msg[-512:]
            raise Dream3DError(err_msg)

        # run postrun operations
        self.output_resources = self._run_postrun_ops(module_time, pipeline_url=self.options.pipeline_url)

    def _cache_ppops(self, pipeline_url):
        if not self.ppops or self.ppops_url != pipeline_url:            
            pipeline_path = urlparse.urlsplit(pipeline_url).path.split('/')
            pipeline_uid = pipeline_path[1] if is_uniq_code(pipeline_path[1]) else pipeline_path[2]
            url = self.bqSession.service_url('pipeline', path = '/'.join([pipeline_uid]+['ppops:dream3d']))
            self.ppops = json.loads(self.bqSession.c.fetch(url))
            self.ppops_url = pipeline_url

    def _run_prerun_ops(self, module_time, pipeline_url, input_xml):
        """
        Perform any operations necessary before the pipeline runs (e.g., download input table) and return filelist file
        """
        self._cache_ppops(pipeline_url)
        post_ops = self.ppops['PreOps']
        input_files = []
        for op in post_ops:
            input_files += self._run_single_op(module_time, op, input_xml)
        filelist_file = os.path.join(self.options.stagingPath, 'filelist.txt')
        with open(filelist_file, 'w') as fo:
            for input_file in input_files:
                fo.write(input_file+'\n')
        return filelist_file
        
    def _run_postrun_ops(self, module_time, pipeline_url):
        """
        Perform any operations necessary after the pipeline finished (e.g., upload result tables) and return created resources
        """
        self._cache_ppops(pipeline_url)
        post_ops = self.ppops['PostOps']
        created_resources = []
        for op in post_ops:            
            created_resources += self._run_single_op(module_time, op)
        return created_resources
            
    def _run_single_op(self, module_time, op, input_xml=None):
        """
        Perform single pre/post operation and return list of files or resources generated
        """        
        # replace special placeholders
        if 'id' in op and op['id'] == '@INPUT':
            op['id'] = input_xml.get('resource_uniq')
        
        res = []        
        if op['service'] == 'postblob':
            # upload image or table (check op['type'])
            mex_id = self.bqSession.mex.uri.split('/')[-1]
            dt = module_time.strftime('%Y%m%dT%H%M%S')
            final_output_file = "ModuleExecutions/Dream3D/%s_%s_%s.h5"%(self.options.OutputPrefix, dt, mex_id)
            cl_model = etree.Element('resource', resource_type=op['type'], name=final_output_file)
            # module identifier (a descriptor to be found by the Dream3D model)
            etree.SubElement(cl_model, 'tag', name='module_identifier', value='Dream3D')
            # hdf filename            
            etree.SubElement(cl_model, 'tag', name='OutputFile', value=final_output_file)
            #description
            etree.SubElement(cl_model, 'tag', name='description', value = 'output from Dream3D Module')
            # post blob
            output_file = os.path.join(self.options.stagingPath, op['filename'])
            resource = self.bqSession.postblob(output_file, xml = cl_model)
            resource_xml = etree.fromstring(resource)
            res += [resource_xml[0]]
        elif op['service'] == 'getblob':
            # download table
            table_file = os.path.join(self.options.stagingPath, op['filename'])
            hdf_url = self.bqSession.service_url('blob_service', path=op['id'])
            self.bqSession.fetchblob(hdf_url, path=table_file)
            res += [table_file]
        return res

    def _instantiate_pipeline(self, pipeline_url, params):
        """
        instantiate dream.3d pipeline file with provided parameters
        """
        pipeline_path = urlparse.urlsplit(pipeline_url).path.split('/')
        pipeline_uid = pipeline_path[1] if is_uniq_code(pipeline_path[1]) else pipeline_path[2]
        url = self.bqSession.service_url('pipeline', path = '/'.join([pipeline_uid]+["setvar:%s|%s"%(tag,params[tag]) for tag in params]+['exbsteps:dream3d']), query={'format':'dream3d'})
        pipeline = self.bqSession.c.fetch(url)
        if not pipeline:
            # bad pipeline
            return None, None
        out_pipeline_file = os.path.join(self.options.stagingPath, 'pipeline.json')
        out_error_file = os.path.join(self.options.stagingPath, 'dream3d_error.txt')
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
            else:
                # r_xml is some other resource (e.g., image or table) => append reference to output
                etree.SubElement(outputTag, 'tag', name='output_table' if res_type=='table' else 'output_image', type=res_type, value=r_xml.get('uri',''))

        self.bqSession.finish_mex(tags=[outputTag])


    def collect_outputs(self):
        """
            Perform reduce phase (i.e., examine final (top) mex and create any additional outputs based on submexes)
            THIS IS JUST AN EXAMPLE.
        """
        # collect submex output hdf urls and add them to top mex outputs section
        top_mex = self.bqSession.fetchxml(self.options.mexURL, view='deep')
        outputTag = top_mex.xpath('/mex/tag[@name="outputs"]')
        if not outputTag:
            # no "outputs" tag in mex => add it now
            etree.SubElement(top_mex, 'tag', name='outputs') 
            top_mex = self.bqSession.postxml(url=top_mex.get('uri'), xml=top_mex, view='deep')
            outputTag = top_mex.xpath('/mex/tag[@name="outputs"]')
        outputTag = outputTag[0]
        output_hdfs = top_mex.xpath('/mex/mex/tag[@name="outputs"]/tag[@name="output_hdf"]/@value')
        etree.SubElement(outputTag, 'tag', name='all_outputs', value=';'.join([ohdf.split('/')[-1] for ohdf in output_hdfs]))
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
