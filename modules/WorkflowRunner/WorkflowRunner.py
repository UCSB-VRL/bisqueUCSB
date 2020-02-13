####################################################
###     Workflow runner Module for Bisque        ###
####################################################


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
import cgi

from lxml import etree as ET
from optparse import OptionParser
from mako.template import Template

from bqapi.comm import BQSession, BQCommError
from bq.util.hash import is_uniq_code

import logging


#constants
DATA_SERVICE    = 'data_service'
BQPATH          = 'bq-path'
LOGFILE         = 'WorkflowRunner.log'


logging.basicConfig(filename=LOGFILE,level=logging.DEBUG)
log = logging.getLogger('bq.modules')


class WFError(Exception):
    def __init__(self, message):
        self.message = "WorkflowRunner error: %s" % message
    def __str__(self):
        return self.message        
        


class WorkflowRunner(object):

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to options attribute (unless already set)

            @param: mex_xml
        """
        # inputs are all non-"pipeline params" under "inputs" and all params under "pipeline_params"
        mex_inputs = mex_xml.xpath('tag[@name="inputs"]/tag[@name!="workflow_parameters"] | tag[@name="inputs"]/tag[@name="workflow_parameters"]/tag')
        if mex_inputs:
            for tag in mex_inputs:
                if tag.tag == 'tag' and tag.get('type', '') != 'system-input': #skip system input values
                    if not getattr(self.options,tag.get('name', ''), None):
                        log.debug('Set options with %s as %s'%(tag.get('name',''),tag.get('value','')))
                        setattr(self.options,tag.get('name',''),tag.get('value',''))
        else:
            log.debug('WorkflowRunner: No Inputs Found on MEX!')


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

        log.debug('WorkflowRunner: Insufficient options or arguments to start this module')
        return False

    def setup(self):
        """
            Fetches the mex and appends input_configurations to the option
            attribute
        """
        self.bqSession.update_mex('Initializing...')
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        self.output_resources = []
        
    def run(self):
        # retrieve tags
        self.bqSession.update_mex('Extracting properties')
        
        # set up initial parameters
        pipeline_params = self.bqSession.mex.xmltree.xpath('tag[@name="inputs"]/tag[@name="workflow_parameters"]/tag')
        self.global_vars = {'server_url': self.bqSession.c.root}
        for tag in pipeline_params:
            self.global_vars[tag.get('name','')] = getattr(self.options, tag.get('name',''))
        pipeline = self._read_pipeline(pipeline_url=self.options.pipeline_url)
        if not pipeline:
            raise WFError("trying to run incompatible workflow")

        # want error notification?
        error_mail = pipeline['__Header__'].get('Error_mail')

        try:
            # Run the workflow
            self.output_resources = [ET.Element('tag', name='initial state', value=cgi.escape(str(self.global_vars)))]
            for step_id in xrange(len(pipeline)-1):
                curr_step = pipeline.get(str(step_id))
                if curr_step is None:
                    raise WFError("workflow step %s missing" % step_id)
                step_label = curr_step['__Label__']
                service_name = self._prepare_param(curr_step['__Meta__']['Service'])
                method = self._prepare_param(curr_step['__Meta__']['Method'])
                path = self._prepare_param(curr_step['__Meta__']['Path'])
                extras = {}
                for meta_param in curr_step['__Meta__']:
                    if meta_param.lower() not in ['service', 'method', 'path']:
                        extras[meta_param.lower()] = curr_step['__Meta__'][meta_param]
                input_map = {}
                output_map = {}
                for param in curr_step['Parameters']:
                    if 'Inputs' in param:
                        input_map = param['Inputs']
                    if 'Outputs' in param:
                        output_map = param['Outputs']
                res = self.run_single_step(step_id, step_label, service_name, method, path, input_map, output_map, **extras)
                self.output_resources.append(ET.Element('tag', name='state after step %s'%step_id, value=cgi.escape(str(self.global_vars))))
                if isinstance(res, ET._Element):
                    self.output_resources.append(ET.Element('tag', name='reply from step %s'%step_id, value=cgi.escape(ET.tostring(res))))
        except Exception as exc:
            if error_mail is not None:
                input_map = { "recipients": error_mail, "subject": "Workflow failed", "__xmlbody__": str(exc) }
                self.run_single_step_direct(step_id='FAIL HANDLER', service_name='notify', method='POSTXML', path='email', input_map=input_map, output_map={})
            raise

    def _read_pipeline(self, pipeline_url):
        """
        read workflow json doc
        """
        pipeline_path = urlparse.urlsplit(pipeline_url).path.split('/')
        pipeline_uid = pipeline_path[1] if is_uniq_code(pipeline_path[1]) else pipeline_path[2]
        url = self.bqSession.service_url('pipeline', path = pipeline_uid, query={'format':'json'})
        pipeline = self.bqSession.c.fetch(url)
        if not pipeline:
            # bad pipeline
            return None, None
        try:
            res_pipeline = json.loads(pipeline)
        except ValueError:
            # not json
            return None, None
        return res_pipeline

    def run_single_step(self, step_id, step_label, service_name, method, path, input_map, output_map, **kw):
        # update status
        self.bqSession.update_mex("Executing step %s: %s" % (str(step_id), step_label))
        
        while True:
            res = self.run_single_step_direct(step_id, service_name, method, path, input_map, output_map)
            poll_cond = kw.get('poll_cond')
            if poll_cond is None:
                break
            else:
                # need to check output and maybe repeat
                cond_res = self._prepare_param(poll_cond, res)
                if cond_res in [True, 'True', 1, '1']:
                    log.debug("poll condition returned %s, exit polling" % cond_res)
                    break
                else:
                    log.debug("poll condition returned %s, continue polling" % cond_res)
                    poll_sleep = float(kw.get('poll_interval', 10))
                    time.sleep(poll_sleep)
        return res

    def run_single_step_direct(self, step_id, service_name, method, path, input_map, output_map):
        # prepare inputs
        try:
            prep_input_map = self._prepare_params(input_map)
        except Exception as exc:
            msg = "Step %s (%s %s/%s) failed. Reason: %s" % (step_id, method, service_name, path, exc)
            log.exception(msg)
            raise WFError(msg)

        # request service
        try:
            if method.upper() == 'GETXML':
                params = prep_input_map
                url = urlparse.urljoin( self.bqSession.service_map[service_name], path )
                res = self.bqSession.fetchxml(url=url, **params)
            elif method.upper() == 'POSTXML':
                params = {key:val for (key,val) in prep_input_map.iteritems() if key not in ['__xmlbody__']}
                url = urlparse.urljoin( self.bqSession.service_map[service_name], path )
                xml = prep_input_map.get('__xmlbody__')
                res = self.bqSession.postxml(url=url, xml=xml, **params)
            elif method.upper() == 'GETBLOB':
                params = prep_input_map
                url = urlparse.urljoin( self.bqSession.service_map[service_name], path )
                res = self.bqSession.fetchblob(url=url, **params)
            elif method.upper() == 'POSTBLOB':
                params = {key:val for (key,val) in prep_input_map.iteritems() if key not in ['__xmlbody__']}
                if service_name != 'import':
                    raise WFError("POSTBLOB method used for service other than import")
                xml = prep_input_map.get('__xmlbody__')
                res = self.bqSession.postblob(xml=xml, **params)
            else:
                raise WFError("Unknown method %s" % method)
        except Exception as exc:
            msg = "Step %s (%s %s/%s) failed. Reason: %s" % (step_id, method, service_name, path, exc)
            log.exception(msg)
            raise WFError(msg)
        
        # prepare outputs
        try:
            prep_output_map = self._prepare_params(output_map, res)
        except Exception as exc:
            msg = "Step %s (%s %s/%s) failed. Reason: %s" % (step_id, method, service_name, path, exc)
            log.exception(msg)
            raise WFError(msg)
        
        # store outputs
        self.global_vars.update(prep_output_map)
        
        return res
                
    def _prepare_params(self, param_map, doc=None):
        res = {}
        for single_input in param_map:
            val = param_map[single_input]
            val = self._prepare_param(val, doc)
            res[single_input] = val
        return res
    
    def _prepare_param(self, val, doc=None):
        run_xpath = False
        if val.startswith('xpath:'):
            run_xpath = True
            val = val[len('xpath:'):]
        # expand variables etc
        log.debug("Mako expand %s with %s" % (val, str(self.global_vars)))
        template = Template(val)
        val = template.render(**self.global_vars)
        # run xpath if requested
        if run_xpath:
            if doc is None or not isinstance(doc, ET._Element):
                raise WFError("no result XML")
            valx = doc.xpath(val)
            if len(valx) < 1:
                msg = "xpath '%s' result empty for %s" % (val, ET.tostring(doc))
                log.error(msg)
                raise WFError(msg)
            val = valx[0]
        return val

    def teardown(self):
        """
            Post the results to the mex xml.
        """
        self.bqSession.update_mex( 'Returning results')

        outputTagOuter = ET.Element('tag', name ='outputs')
        outputTag = ET.SubElement(outputTagOuter, 'tag', name='summary')
        for r_xml in self.output_resources:
            res_type = r_xml.get('type', None) or r_xml.get('resource_type', None) or r_xml.tag
            if res_type == 'tag':
                # simple tag => append to output as is
                r_xml.tag = 'tag'
                outputTag.append(r_xml)
            else:
                # r_xml is some other resource (e.g., image or table) => append reference to output
                ET.SubElement(outputTag, 'tag', name='output_table' if res_type=='table' else 'output_image', type=res_type, value=r_xml.get('uri',''))

        self.bqSession.finish_mex(tags=[outputTagOuter])

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
                raise WFError('Insufficient options or arguments to start this workflow')

            try:
                self.setup()
            except Exception as e:
                log.exception("Exception during setup")
                self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                return

            try:
                self.run()
            except (Exception, WFError) as e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
                return

            try:
                self.teardown()
            except (Exception, WFError) as e:
                log.exception("Exception during teardown")
                self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
                return

            self.bqSession.close()

if __name__ == "__main__":
    WorkflowRunner().main()
