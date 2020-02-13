import sys
import io
from lxml import etree
import optparse
import logging


logging.basicConfig(filename='PythonScript.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')


from bqapi.comm import BQSession

from script import run_script


class ScriptError(Exception):
    def __init__(self, message):
        self.message = "Script error: %s" % message
    def __str__(self):
        return self.message
    
class PythonScriptWrapper(object):
    def run(self):
        """
        Run Python script
        """
        session = self.bqSession
        
        # call script
        outputs = run_script( session, log, **self.options.__dict__ )
        
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

        outputTag = etree.Element('tag', name ='outputs')
        for r_xml in self.output_resources:
            if isinstance(r_xml, basestring):
                r_xml = etree.fromstring(r_xml) 
            #res_type = r_xml.get('type', None) or r_xml.get('resource_type', None) or r_xml.tag
            # append reference to output
            outputTag.append(r_xml)
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

    def collect_outputs(self):
        """
            Perform reduce phase (i.e., examine final (top) mex and create any additional outputs based on submexes)
        """
        top_mex = self.bqSession.fetchxml(self.options.mexURL, view='deep')
        
        # add output tag if needed
        outputTag = top_mex.xpath('/mex/tag[@name="outputs"]')
        if not outputTag:
            # no "outputs" tag in mex => add it now
            etree.SubElement(top_mex, 'tag', name='outputs') 
            top_mex = self.bqSession.postxml(url=top_mex.get('uri'), xml=top_mex, view='deep')
            outputTag = top_mex.xpath('/mex/tag[@name="outputs"]')
        outtag = outputTag[0]
        
        # add multi-param output table based on submex outputs
        # from inputs, collect everything except mex_url and bisque_token
        # from outputs/statistics, collect everything except "meanMaxMisorient"
        multiparam_name = 'output_table'
        multitag = etree.SubElement(outtag, 'tag', name=multiparam_name, type='multiparam')
        colnames = etree.SubElement(multitag, 'tag', name='title')
        coltypes = etree.SubElement(multitag, 'tag', name='xmap')
        colxpaths = etree.SubElement(multitag, 'tag', name='xpath')
        etree.SubElement(multitag, 'tag', name='xreduce', value='vector')
        inputs = top_mex.xpath('/mex/mex/tag[@name="inputs"]')[0]
        for inp in inputs.xpath('./tag'):
            if inp.get('name') not in ['mex_url', 'bisque_token']:
                etree.SubElement(colnames, 'value', value=inp.get('name'))
                etree.SubElement(coltypes, 'value', value=self._get_type(inp))
                etree.SubElement(colxpaths, 'value', value='/mex/mex/tag[@name="inputs"]/tag[@name="%s"]' % inp.get('name'))
        outputs = top_mex.xpath('/mex/mex/tag[@name="outputs"]')[0]
        for outp in outputs.xpath('./tag[@name="statistics"]/tag'):
            if outp.get('name') not in ['meanMaxMisorient']:
                etree.SubElement(colnames, 'value', value=outp.get('name'))
                etree.SubElement(coltypes, 'value', value=self._get_type(outp))
                etree.SubElement(colxpaths, 'value', value='/mex/mex/tag[@name="outputs"]/tag[@name="statistics"]/tag[@name="%s"]' % outp.get('name'))
        # last column is the submex URI
        etree.SubElement(colnames, 'value', value="submex_uri")
        etree.SubElement(coltypes, 'value', value="resource-uri")
        etree.SubElement(colxpaths, 'value', value='./mex')
        
        # write back to mex
        self.bqSession.postxml(url=outtag.get('uri'), xml=outtag)

    def _get_type(self, inp):
        if inp.get('name') == 'dream3d_run':
            return 'resource-uri'
        else:
            inptype = inp.get('type', 'string')
            if inptype == 'combo':
                inptype = 'string'
            return "tag-value-%s" % inptype 

    def main(self):
        parser = optparse.OptionParser()
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
    
        fh = logging.FileHandler('phase_%s.log' % (options.entrypoint or 'scriptrun.log'), mode='a')
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
                raise ScriptError('Insufficient options or arguments to start this module')
    
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

            else:
                # in a reduce phase => run reduce code
                if self.options.entrypoint != 'collect_outputs':
                    self.bqSession.fail_mex(msg = "Unknown entrypoint: %s" %  self.options.entrypoint)
                    return

                try:
                    self.collect_outputs()
                except (Exception, ScriptError) as e:
                    log.exception("Exception during collect_outputs")
                    self.bqSession.fail_mex(msg = "Exception during collect_outputs: %s" % str(e))
                    return
                
            self.bqSession.close()

if __name__=="__main__":
    PythonScriptWrapper().main()
