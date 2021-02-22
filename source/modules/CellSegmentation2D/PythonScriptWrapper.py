import logging
logging.basicConfig(filename='PythonScript.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')

import os,sys
import io
import time
import optparse

try:
    from lxml import etree as ET
except ImportError:
    import lxml.etree.ElementTree as ET

try:
    #os.chdir('/source/modules/CellSegmentation2D/')
    from source import getSegmentation
except ImportError:
    #os.chdir('/source/modules/CellSegmentation2D/')
    import getSegmentation

    
	

from bqapi.comm import BQCommError
from bqapi.comm import BQSession
from bqapi.util import save_blob





# Data directories
input_dir = 'source/data/input/'
output_dir = 'source/data/output/'

class ScriptError(Exception):
    def __init__(self, message):
        self.message = "Script error: %s" % message
    def __str__(self):
        return self.message
    
class PythonScriptWrapper(object):

    def getStrTime(self):
    # format timestamp
        ts = time.gmtime()
        ts_str = time.strftime("%Y-%m-%dT%H-%M-%S", ts)
        return ts_str    

    def getImages(self,bq):
       """
       Fetch images and save in the input_dir path
       """

       log.info('Options: %s' % (self.options))

       image = bq.load(self.options.resource_url)
       dt = self.getStrTime()
       self.img_dir = os.path.join(self.options.stagingPath,input_dir)
       self.img_path = os.path.join(self.img_dir, dt+'-'+image.name)
       	
       if not os.path.exists(self.img_dir):
           os.makedirs(self.img_dir)

       ip = image.pixels().format('tiff')
       with open(self.img_path, 'wb') as f:
           f.write(ip.fetch())

       log.info("Image saved as %s" % (self.img_path))

    def uploadImgService(self, bq, files):
        """
        Upload segmented mask to image_service after processing
        """
        mex_id = bq.mex.uri.split('/')[-1]
        filename = os.path.basename(files[0])

        log.info('Up Mex: %s' %(mex_id))
        log.info('Up File: %s' %(filename))

        resource = ET.Element('image', name='ModuleExecutions/CellSegment2D/'+filename)
        t = ET.SubElement(resource, 'tag', name="datetime", value=self.getStrTime())

        log.info('Creating upload xml data: %s ' % str(ET.tostring(resource, pretty_print=True)))
        filepath = files[0]

        # use import service to /import/transfer activating import service
        r = ET.XML(bq.postblob(filepath, xml=resource)).find('./') 

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
        Get segmentation of the image
        """

        bq = self.bqSession
        
        log.info('Running segmentation script...')
        self.out_dir = os.path.join(self.options.stagingPath,out_dir)
		
        try:
            bq.update_mex('Running segmentation script...')
            self.outfiles = getSegmentation.main(self.img_path, self.out_dir)
            log.info('Segmentation successful.')
        except (Exception, ScriptError) as e:
            log.exception("Exception during segmentation")
            self.bq.fail_mex(msg = "Exception during segmentation: %s" % str(e))
            return

        
        log.info('Uploading segmentated images...')
        try:
            bq.update_mex('Uploading segmentated images...')
            self.resimage = self.uploadImgService(bq, self.outfiles)
            log.info('Segmentation successful.')
        except (Exception, ScriptError) as e:
            log.exception("Exception during result upload")
            self.bq.fail_mex(msg = "Exception during result upload: %s" % str(e))
            return


        out_imgxml="""<tag name="Segmentation" type="image" value="%s">
                <template>
                      <tag name="label" value="Segmented Image" />
                </template>
              </tag>""" %(str(self.resimage.get('value')))

        
        ts_str = self.getStrTime()
        
        # out_xml ="""<tag name="Metadata">
        #     <tag name="mask_name" type="string" value="%s"/>
        #                 <tag name="mask_url" type="string" value="%s"/>
        #             </tag>""" %(str(self.resimage.get('name')), str(self.resimage.get('value')))
        outputs = [out_imgxml] #, out_xml]

        #log.debug(outputs)
        # save output back to BisQue

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

        outputTag = ET.Element('tag', name ='outputs')
        for r_xml in self.output_resources:
            if isinstance(r_xml, basestring):
                r_xml = ET.fromstring(r_xml) 
            res_type = r_xml.get('type', None) or r_xml.get('resource_type', None) or r_xml.tag
            # append reference to output
            if res_type in ['table', 'image']:
                outputTag.append(r_xml)
                #ET.SubElement(outputTag, 'tag', name='output_table' if res_type=='table' else 'output_image', type=res_type, value=r_xml.get('uri',''))
            else:
                outputTag.append(r_xml)
                #ET.SubElement(outputTag, r_xml.tag, name=r_xml.get('name', '_'), type=r_xml.get('type', 'string'), value=r_xml.get('value', ''))
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

if __name__=="__main__":
    PythonScriptWrapper().main()
