from bqapi.util import save_blob
from bqapi.comm import BQSession
from bqapi.comm import BQCommError
import os
import sys
import io
import time
from lxml import etree
import optparse
import logging
from bqapi.util import *
import nibabel as nib
import pandas as pd

logging.basicConfig(filename='PythonScript.log',
                    filemode='a', level=logging.DEBUG)
log = logging.getLogger('bq.modules')

# Bisque Imports

# Module Custom Imports

ROOT_DIR = './'
NIFTI_IMAGE_PATH = 'source/Scans/'
sys.path.append(os.path.join(ROOT_DIR, "source/"))
results_outdir = 'source/UNet_Outputs/'
import nph_prediction

class ScriptError(Exception):
    def __init__(self, message):
        self.message = "Script error: %s" % message

    def __str__(self):
        return self.message


class PythonScriptWrapper(object):

    def preprocess(self, bq, **kw):
        """
        Pre-process the images
        """
        log.info('Pre-Process Options: %s' % (self.options))
        """
	1. Get the resource image
	2. call hist.py with bq, log, resource_url, seeds, threshold ( bq, log, **self.options.__dict__ )
	"""
        image = bq.load(self.options.resource_url)
        log.debug('kw is: %s', str(kw))

        predictor_uniq = self.options.resource_url.split('/')[-1]
        log.info("predictor_UNIQUE: %s" % (predictor_uniq))
        predictor_url = bq.service_url('image_service', path=predictor_uniq)
        log.info("predictor_URL: %s" % (predictor_url))
        predictor_path = os.path.join(kw.get('stagingPath', 'source/Scans'), self.getstrtime()+'-'+image.name + '.nii')
        
        predictor_path = bq.fetchblob(predictor_url, path=predictor_path)
        log.info("predictor_path: %s" % (predictor_path))
        #predictor_path = fetchImage(bq, predictor_url, dest=predictor_path, uselocalpath=True)
        #predictor_path = bq.fetch(url=predictor_url, path=predictor_path)
        reducer_uniq = self.options.reducer_url.split('/')[-1]
        reducer_url = bq.service_url('blob_service', path=reducer_uniq)
        reducer_path = os.path.join(kw.get('stagingPath', 'source/'), 'unet_model.pt')
        reducer_path = bq.fetchblob(reducer_url, path=reducer_path)

        
        self.nifti_file = os.path.join(
            self.options.stagingPath, NIFTI_IMAGE_PATH, image.name)
        log.info("process image as %s" % (self.nifti_file))
        log.info("image meta: %s" % (image))
        #ip = image.pixels().format('nii.gz').fetch() 
        #log.info("BRUHHHHHH IP: %s" % (type(ip)))
        #ip2 = image.pixels() #.format('nii')
        #log.info("BRUHHHHHH IP2: %s" % (type(ip2)))
        #log.info("BRUHHHHHH Value: %s" % (image.value))
        #img_nib = nib.load(ip)
        meta = image.pixels().meta().fetch()
        #meta = ET.XML(meta)
        meta = bq.factory.string2etree(meta)
        
        #with open(self.nifti_file, 'wb') as f:
        #    f.write(ip2.fetch())
        log.info('Executing Histogram match')
        pred = nph_prediction.main()
        log.info('Completed Histogram match')
        return pred


    def getstrtime(self):
        # format timestamp
        ts = time.gmtime()
        ts_str = time.strftime("%Y-%m-%dT%H-%M-%S", ts)
        return ts_str

    def uploadimgservice(self, bq, files):
        """
        Upload mask to image_service upon post process
        """
        mex_id = bq.mex.uri.split('/')[-1]
        log.info("BRUHHHHHH: %s" % (files))
        filename = os.path.basename(files[0])
        log.info('Up Mex: %s' % (mex_id))
        log.info('Up File: %s' % (filename))
        resource = etree.Element(
            'image', name='ModuleExecutions/nphprediction/'+filename)
        t = etree.SubElement(resource, 'tag', name="datetime", value=self.getstrtime())
        log.info('Creating upload xml data: %s ' %
                 str(etree.tostring(resource, pretty_print=True)))
        # os.path.join("ModuleExecutions","CellSegment3D", filename)
        filepath = files[0]
        # use import service to /import/transfer activating import service
        r = etree.XML(bq.postblob(filepath, xml=resource)).find('./')
        if r is None or r.get('uri') is None:
            bq.fail_mex(msg="Exception during upload results")
        else:
            log.info('Uploaded ID: %s, URL: %s' %
                     (r.get('resource_uniq'), r.get('uri')))
            bq.update_mex('Uploaded ID: %s, URL: %s' %
                          (r.get('resource_uniq'), r.get('uri')))
            self.furl = r.get('uri')
            self.fname = r.get('name')
            resource.set('value', self.furl)

        return resource

    def uploadtableservice(self, bq, files):
        """
        Upload mask to image_service upon post process
        """
        mex_id = bq.mex.uri.split('/')[-1]
        filename = os.path.basename(files)
        log.info('Up Mex: %s' % (mex_id))
        log.info('Up File: %s' % (filename))
        resource = etree.Element(
            'table', name='ModuleExecutions/nphprediction/'+filename)
        t = etree.SubElement(resource, 'tag', name="datetime", value=self.getstrtime())
        log.info('Creating upload xml data: %s ' %
                 str(etree.tostring(resource, pretty_print=True)))
        # os.path.join("ModuleExecutions","CellSegment3D", filename)
        filepath = files
        # use import service to /import/transfer activating import service
        r = etree.XML(bq.postblob(filepath, xml=resource)).find('./')
        if r is None or r.get('uri') is None:
            bq.fail_mex(msg="Exception during upload results")
        else:
            log.info('Uploaded ID: %s, URL: %s' %
                     (r.get('resource_uniq'), r.get('uri')))
            bq.update_mex('Uploaded ID: %s, URL: %s' %
                          (r.get('resource_uniq'), r.get('uri')))
            self.furl = r.get('uri')
            self.fname = r.get('name')
            resource.set('value', self.furl)

        return resource

    def run(self):
        """
        Run Python script
        """
        bq = self.bqSession
        # table_service = bq.service ('table')
        # call scripts
        try:
            bq.update_mex('Pre-process the images')
            self.preprocess(bq)
        except (Exception, ScriptError) as e:
            log.exception("Exception during preprocess")
            bq.fail_mex(msg="Exception during pre-process: %s" % str(e))
            return
        try:
            print(os.listdir(results_outdir))
            self.outfiles = []
            for files in os.listdir(results_outdir):
                if files.endswith("1.nii.gz"):
                    self.outfiles.append(results_outdir+files)
            bq.update_mex('Uploading Mask result')
            self.resimage = self.uploadimgservice(bq, self.outfiles)
            bq.update_mex('Uploading Table result')
            self.voltable = self.uploadtableservice(
                bq, 'source/volumes_unet.csv')
            self.volconvtable = self.uploadtableservice(
                bq, 'source/volumes_conv_unet.csv')
            self.predtable = self.uploadtableservice(
                bq, 'source/predictions.csv')
        except (Exception, ScriptError) as e:
            log.exception("Exception during upload result")
            bq.fail_mex(msg="Exception during upload result: %s" % str(e))
            return

        log.info('Completed the workflow: %s' % (self.resimage.get('value')))
        out_imgxml = """<tag name="Segmentation" type="image" value="%s">
			<template>
		          <tag name="label" value="Segmented Image" />
			</template>
		      </tag>""" % (str(self.resimage.get('value')))

        # format timestamp
        ts = time.gmtime()
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        vols = pd.read_csv('source/volumes_unet.csv')
        volsConv = pd.read_csv('source/volumes_conv_unet.csv')
        preds = pd.read_csv('source/predictions.csv')
        # outputs = predict( bq, log, **self.options.__dict__ )
        #outtable_xml = table_service.store_array(maxMisorient, name='maxMisorientData')
        out_xml = """<tag name="Metadata">
		<tag name="Scan" type="string" value="%s"/>
		<tag name="Ventricle" type="string" value="%s"/>
		<tag name="Subcortical" type="string" value="%s"/>
		<tag name="White Matter" type="string" value="%s"/>
		<tag name="Volumes Table" type="resource" value="%s"/>
        <tag name="Volumes Converted Table" type="resource" value="%s"/>
		<tag name="Prediction" type="string" value="%s"/>
                    </tag>""" % (str(vols.Scan[0]), str(vols.Vent[0]), str(vols.Sub[0]), str(vols.White[0]), self.voltable.get('value'), self.volconvtable.get('value'), str(preds.columns[-1]))
        outputs = [out_imgxml, out_xml]
        log.debug(outputs)
        # save output back to BisQue
        for output in outputs:
            self.output_resources.append(output)

    def setup(self):
        """
        Pre-run initialization
        """
        self.output_resources.append(output)

    def setup(self):
        """
        Pre-run initialization
        """
        self.bqSession.update_mex('Initializing...')
        self.mex_parameter_parser(self.bqSession.mex.xmltree)
        self.output_resources = []

    def teardown(self):
        """
        Post the results to the mex xml
        """
        self.bqSession.update_mex('Returning results')
        outputTag = etree.Element('tag', name='outputs')
        for r_xml in self.output_resources:
            if isinstance(r_xml, str):
                r_xml = etree.fromstring(r_xml)
            res_type = r_xml.get('type', None) or r_xml.get(
                'resource_type', None) or r_xml.tag
            # append reference to output
            if res_type in ['table', 'image']:
                outputTag.append(r_xml)
                #etree.SubElement(outputTag, 'tag', name='output_table' if res_type=='table' else 'output_image', type=res_type, value=r_xml.get('uri',''))
            else:
                outputTag.append(r_xml)
                #etree.SubElement(outputTag, r_xml.tag, name=r_xml.get('name', '_'), type=r_xml.get('type', 'string'), value=r_xml.get('value', ''))
        log.debug('Output Mex results: %s' %
                  (etree.tostring(outputTag, pretty_print=True)))
        self.bqSession.finish_mex(tags=[outputTag])

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to options attribute (unless already set)
            @param: mex_xml
        """
        # inputs are all non-"script_params" under "inputs" and all params under "script_params"
        mex_inputs = mex_xml.xpath(
            'tag[@name="inputs"]/tag[@name!="script_params"] | tag[@name="inputs"]/tag[@name="script_params"]/tag')
        if mex_inputs:
            for tag in mex_inputs:
                # skip system input values
                if tag.tag == 'tag' and tag.get('type', '') != 'system-input':
                    if not getattr(self.options, tag.get('name', ''), None):
                        log.debug('Set options with %s as %s' %
                                  (tag.get('name', ''), tag.get('value', '')))
                        setattr(self.options, tag.get(
                            'name', ''), tag.get('value', ''))
        else:
            log.debug('No Inputs Found on MEX!')

    def validate_input(self):
        """
            Check to see if a mex with token or user with password was provided.
            @return True is returned if validation credention was provided else
            False is returned
        """
        if (self.options.mexURL and self.options.token):  # run module through engine service
            return True
        # run module locally (note: to test module)
        if (self.options.user and self.options.pwd and self.options.root):
            return True
        log.debug('Insufficient options or arguments to start this module')
        return False

    def main(self):
        parser = optparse.OptionParser()
        parser.add_option('--mex_url', dest="mexURL")
        parser.add_option('--module_dir', dest="modulePath")
        parser.add_option('--staging_path', dest="stagingPath")
        parser.add_option('--bisque_token', dest="token")
        parser.add_option('--user', dest="user")
        parser.add_option('--pwd', dest="pwd")
        parser.add_option('--root', dest="root")
        (options, args) = parser.parse_args()

        # Logging initializations
        fh = logging.FileHandler('scriptrun.log', mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s ' +
                                      '(%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        log.addHandler(fh)

        try:  # pull out the mex
            if not options.mexURL:
                options.mexURL = sys.argv[-2]
            if not options.token:
                options.token = sys.argv[-1]
        except IndexError:  # no argv were set
            pass
        if not options.stagingPath:
            options.stagingPath = ''

        # Options configuration
        log.debug('PARAMS : %s Options: %s' % (args, options))
        self.options = options
        if self.validate_input():
            # initalizes if user and password are provided
            if (self.options.user and self.options.pwd and self.options.root):
                self.bqSession = BQSession().init_local(
                    self.options.user, self.options.pwd, bisque_root=self.options.root)
                self.options.mexURL = self.bqSession.mex.uri
            # initalizes if mex and mex token is provided
            elif (self.options.mexURL and self.options.token):
                self.bqSession = BQSession().init_mex(self.options.mexURL, self.options.token)
            else:
                raise ScriptError(
                    'Insufficient options or arguments to start this module')

            # Setup the mex and sessions
            try:
                self.setup()
            except Exception as e:
                log.exception("Exception during setup")
                self.bqSession.fail_mex(
                    msg="Exception during setup: %s" % str(e))
                return
            # Execute the module functionality
            try:
                self.run()
            except (Exception, ScriptError) as e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(
                    msg="Exception during run: %s" % str(e))
                return
            try:
                self.teardown()
            except (Exception, ScriptError) as e:
                log.exception("Exception during teardown")
                self.bqSession.fail_mex(
                    msg="Exception during teardown: %s" % str(e))
                return
            self.bqSession.close()
        log.debug('Session Close')


""" 
    Main entry point for test purposes
    
    # test with named argument and options at the start
    python PythonScriptWrapper.py \
    http://drishti.ece.ucsb.edu:8080/data_service/00-kDwj3vQq83vJA6SvVvVVh8 \
    15 0.05 \
    http://drishti.ece.ucsb.edu:8080/module_service/mex/00-XW6DsZR9puKj76Ezn9Mi79 \
    admin:00-XW6DsZR9puKj76Ezn9Mi79

    # Note: last two argument are the mex_url and token and remaining are parsed as options
"""
if __name__ == "__main__":
    PythonScriptWrapper().main()