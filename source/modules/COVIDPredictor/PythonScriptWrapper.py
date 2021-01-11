import sys
import io
from lxml import etree
import optparse
import logging
import os
# It is importing from source

logging.basicConfig(filename='PythonScript.log', filemode='a', level=logging.DEBUG) 
log = logging.getLogger('bq.modules')

from bqapi.comm import BQCommError
from bqapi.comm import BQSession

# ROOT_DIR = './'
# sys.path.append(os.path.join(ROOT_DIR, "source/"))
from prediction import predict_label


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
        # ip = image.pixels() #(.format'jpg')
        # with open(self.in_file, 'wb') as f:
        #     f.write(ip.fetch())
        # return
    
    def run(self):
        """
        Run Python script

        """
        bq = self.bqSession
        try:
            bq.update_mex('Pre-process the images')
            self.preprocess(bq)
        except (Exception, ScriptError) as e:
            log.exception("Exception during preprocess")
            bq.fail_mex(msg = "Exception during pre-process: %s" % str(e))
            return
        #call script
        outputs = predict_label(bq, log, **self.options.__dict__)

        for output in outputs:
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
            if isinstance(r_xml, basestring):
                r_xml = etree.fromstring(r_xml) 
            res_type = r_xml.get('type', None) or r_xml.get('resource_type', None) or r_xml.tag
            # append reference to output
            if res_type in ['table', 'image']:
                outputTag.append(r_xml)
                #etree.SubElement(outputTag, 'tag', name='output_table' if res_type=='table' else 'output_image', type=res_type, value=r_xml.get('uri',''))
            else:
                outputTag.append(r_xml)
                #etree.SubElement(outputTag, r_xml.tag, name=r_xml.get('name', '_'), type=r_xml.get('type', 'string'), value=r_xml.get('value', ''))
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

        log.debug('\n\nPARAMS : %s \n\n Options: %s' % (args, options))
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

            try:
                self.setup()
            except Exception as e:
                log.exception("Exception during setup")
                self.bqSession.fail_mex(msg = "Exception during setup: %s" %  str(e))
                return

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

if __name__=="__main__":
    PythonScriptWrapper().main()
