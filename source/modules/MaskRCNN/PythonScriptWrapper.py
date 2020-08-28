import os, sys
import io
import time
from lxml import etree
import optparse
import logging

logging.basicConfig(filename='PythonScript.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')

# Bisque Imports
from bqapi.comm import BQCommError
from bqapi.comm import BQSession
from bqapi.util import save_blob

# Module Custome Imports
from masker import detect, fsave 

IMAGE_PATH = "source/images"

class ScriptError(Exception):
    def __init__(self, message):
        self.message = "Script error: %s" % message
    def __str__(self):
        return self.message

class PythonScriptWrapper(object):

    def preprocess(self, bq):
        log.info('Options: %s' % (self.options))
        """
        1. Get the resource image
        """
        image = bq.load(self.options.resource_url)
        dt = self.getstrtime()
        self.img_name = dt+'-'+image.name
        self.in_file = os.path.join(self.options.stagingPath, IMAGE_PATH, self.img_name)
        log.info("process image as %s" % (self.in_file))
        log.info("image meta: %s" % (image))
        ip = image.pixels() #.format('jpg')
        with open(self.in_file, 'wb') as f:
            f.write(ip.fetch())
        return

    def detect(self, bq):
        """
        2. Infer the mask for the image & write file
        """
        log.info('Executing Inference')
        image, r = detect(self.in_file)    
        log.info('Completed Inference')
        self.out_file = os.path.join(self.options.stagingPath, "mask_"+self.img_name)
        fsave(image, r, outfile=self.out_file)
        return 

    def getstrtime(self):
        # format timestamp
        ts = time.gmtime()
        ts_str = time.strftime("%Y-%m-%dT%H-%M-%S", ts)
        return ts_str    

    def uploadimgservice(self, bq, out_file):
        """
        3. Upload mask to image_service upon post process
        """
        mex_id = bq.mex.uri.split('/')[-1]
        filename = os.path.basename(out_file)
        log.info('Up Mex: %s' %(mex_id))
        log.info('Up File: %s' %(filename))
        resource = etree.Element('image', name='ModuleExecutions/MaskRCNN/'+filename)
        t = etree.SubElement(resource, 'tag', name="datetime", value=self.getstrtime())
        log.info('Creating upload xml data: %s ' % str(etree.tostring(resource, pretty_print=True)))
        filepath = out_file
        r = etree.XML(bq.postblob(filepath, xml=resource)).find('./') 
        if r is None or r.get('uri') is None:
            bq.fail_mex(msg = "Exception during upload results")
        else:
            log.info('Uploaded ID: %s, URL: %s'%(r.get('resource_uniq'), r.get('uri')))
            bq.update_mex('Uploaded ID: %s, URL: %s'%(r.get('resource_uniq'), r.get('uri')))
            self.furl = r.get('uri')
            self.fname = r.get('name')
            resource.set('value', self.furl)
        return resource

    def run(self):
        """
        Run Python script
        """
        bq = self.bqSession
        # call scripts 
        try:
            bq.update_mex('Pre-process the images')
            self.preprocess(bq)
        except (Exception, ScriptError) as e:
            log.exception("Exception during preprocess")
            bq.fail_mex(msg = "Exception during pre-process: %s" % str(e))
            return
        try:
            bq.update_mex('Infer the images')
            self.detect(bq)
        except (Exception, ScriptError) as e:
            log.exception("Exception during inference")
            bq.fail_mex(msg = "Exception during inference: %s" % str(e))
            return
        try:
            bq.update_mex('Uploading mask result')
            self.resimage = self.uploadimgservice(bq, self.out_file)
        except (Exception, ScriptError) as e:
            log.exception("Exception during upload result")
            bq.fail_mex(msg = "Exception during upload result: %s" % str(e))
            return
        log.info('Completed the workflow: %s' % (self.resimage.get('value')))
        out_imgxml="""<tag name="Segmentation" type="image" value="%s">
                      <template>
                      <tag name="label" value="Output image" />
                      </template>
                      </tag>""" %(str(self.resimage.get('value')))
        # format timestamp
        ts = time.gmtime()
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S", ts)
        # outputs = predict( bq, log, **self.options.__dict__ )
        out_xml ="""<tag name="Metadata">
                    <tag name="mask_name" type="string" value="%s"/>
                    <tag name="mask_url" type="string" value="%s"/>
                    </tag>""" %(str(self.resimage.get('name')), str(self.resimage.get('value')))
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
        self.bqSession.update_mex( 'Returning results')
        outputTag = etree.Element('tag', name ='outputs')
        for r_xml in self.output_resources:
            if isinstance(r_xml, str):
                r_xml = etree.fromstring(r_xml) 
            res_type = r_xml.get('type', None) or r_xml.get('resource_type', None) or r_xml.tag
            # append reference to output
            if res_type in ['table', 'image']:
                outputTag.append(r_xml)
            else:
                outputTag.append(r_xml)
        log.debug('Output Mex results: %s'%(etree.tostring(outputTag, pretty_print=True)))
        self.bqSession.finish_mex(tags=[outputTag])

    def mex_parameter_parser(self, mex_xml):
        """
            Parses input of the xml and add it to options attribute (unless already set)
            @param: mex_xml
        """
        # inputs are all non-"script_params" under "inputs" and all params under "script_params"
        mex_inputs = mex_xml.xpath('tag[@name="inputs"]/tag[@name!="script_params"] | tag[@name="inputs"]/tag[@name="script_params"]/tag')
        if mex_inputs:
            for tag in mex_inputs:
                if tag.tag == 'tag' and tag.get('type', '') != 'system-input': #skip system input values
                    if not getattr(self.options,tag.get('name', ''), None):
                        log.debug('Set options with %s as %s'%(tag.get('name',''),tag.get('value','')))
                        setattr(self.options,tag.get('name',''),tag.get('value',''))
        else:
            log.debug('No Inputs Found on MEX!')

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
        log.debug('Insufficient options or arguments to start this module')
        return False

    def main(self):
        parser = optparse.OptionParser()
        parser.add_option('--mex_url'         , dest="mexURL")
        parser.add_option('--module_dir'      , dest="modulePath")
        parser.add_option('--staging_path'    , dest="stagingPath")
        parser.add_option('--bisque_token'    , dest="token")
        parser.add_option('--user'            , dest="user")
        parser.add_option('--pwd'             , dest="pwd")
        parser.add_option('--root'            , dest="root")
        (options, args) = parser.parse_args()

        # Logging initializations
        fh = logging.FileHandler('scriptrun.log', mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)8s --- %(message)s ' +
                                  '(%(filename)s:%(lineno)s)',datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        log.addHandler(fh)

        try: #pull out the mex
            if not options.mexURL:
                options.mexURL = sys.argv[-2]
            if not options.token:
                options.token = sys.argv[-1]
        except IndexError: #no argv were set
            pass
        if not options.stagingPath:
            options.stagingPath = ''

        # Options configuration
        log.debug('PARAMS : %s Options: %s' % (args, options))
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
                raise ScriptError('Insufficient options or arguments to start this module')

            # Setup the mex and sessions
            try:
                self.setup()
            except Exception as e:
                log.exception("Exception during setup")
                self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                return
            # Execute the module functionality
            try:
                self.run()
            except (Exception, ScriptError) as e:
                log.exception("Exception during run")
                self.bqSession.fail_mex(msg = "Exception during run: %s" % str(e))
                return
            try:
                self.teardown()
            except (Exception, ScriptError) as e:
                log.exception("Exception during teardown")
                self.bqSession.fail_mex(msg = "Exception during teardown: %s" %  str(e))
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
if __name__=="__main__":
    PythonScriptWrapper().main()

