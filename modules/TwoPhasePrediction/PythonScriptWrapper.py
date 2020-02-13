import sys
import io
from lxml import etree
import optparse
import logging

from pymks import PrimitiveBasis
from pymks.stats import correlate
from sklearn.externals import joblib
import numpy as np
import h5py
from predict_strength import predict


logging.basicConfig(filename='PythonScript.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')

from bqapi.comm import BQCommError
from bqapi.comm import BQSession

# def predict(bq, log, table_url, **kw):
#     '''
#     Predicts effective strength of 3-D RVE of a 2-phase composite with strength contrast s2/s1 = 5
#     Args: 
#     - table_path - path to dream3d file containing microstructure data (phase labels)
#     - predictor_path - path to sav file containing calibrated model (LinearRegression)
#     - reducer_path - path to sav file containing dimensionality reducer (Principal Component Basis)
#     - ms_path - path to microstructure data (phase lables) inside dream3d file
#     Returns:
#     - y - predicted effective strength 
#     '''
# 
#     predictor_path='./predictor.sav'
#     reducer_path='./reducer.sav'
#     ms_path='/DataContainers/SyntheticVolumeDataContainer/CellData/Phases'
# 
#     # Default settings for 2-pt stats
#     p_axes = (0,1,2)
#     corrs = [(1,1)]
#     
#     # Read hdf5 table
#     table_uniq = table_url.split('/')[-1]
#     table_service = bq.service ('table')
# 
#     # Get dataset 
#     data = table_service.load_array(table_uniq, ms_path.lstrip('/'))
#     ms = np.squeeze(data)
# 
#     # f = h5py.File(table_path, 'r')
#     # data = f[ms_path].value
#     # ms = np.squeeze(data)
#     
#     # Get phase labels as local states
#     states = np.unique(ms)
#     if len(states) > 2 :
#         print('WARNING: Model is only for two-phase materials! All extra phases will be considered as the second (hard) phase')
#         ms[ms > states[0]] = states[0]   
#     
#     # Get the size of the RVE
#     if len(ms.shape) == 4:
#         dims = ms.shape[1:4]
#     elif len(ms.shape) == 3:
#         dims = ms.shape
#         ms = np.expand_dims(ms,0)
#     else:
#         print('ERROR: 3-D RVE(s) are expected!')
#         return None
#     
#     # Load model and dimensionality reducer
#     predictor = joblib.load(predictor_path)
#     reducer = joblib.load(reducer_path)
#     
#     # Get the number of PC components used
#     n_comps = predictor.named_steps['poly'].n_input_features_
# 
#     # Get the size of the calibration RVE
#     nx_cal = int(np.round((reducer.components_.shape[1])**(1.0/3.0)))
#     dims_cal = np.array((nx_cal,nx_cal,nx_cal))
#     
#     # Compute 2-pt stats
#     n_states = len(states)
#     p_basis = PrimitiveBasis(n_states=n_states, domain=states)
#     tps = correlate(ms, p_basis, periodic_axes=p_axes, correlations=corrs)
#     
#     # Check size of the provided MVE: truncate if large, pad if small
#     if np.prod(dims) > reducer.components_.shape[1]:
#         tps = truncate(tps, [len(ms),dims_cal[0],dims_cal[1],dims_cal[2],1])
#         dims = dims_cal
#         print('Microstructure volume is larger than calibration RVE. 2-pt correlation function is truncated')
#     elif np.prod(dims) < reducer.components_.shape[1]:
#         tps = pad(tps, [len(ms),dims_cal[0],dims_cal[1],dims_cal[2],1])
#         dims = dims_cal
#         print('Microstructure volume is smaller than calibration RVE. 2-pt correlation function is padded')
#     
#     # Convert 2-pt stats to a vector
#     tps_v = np.reshape(tps,(len(ms), np.prod(dims)))
# 
#     # Get low-dimensional representation
#     x = reducer.transform(tps_v)
#     
#     # Get the property prediction
#     y = predictor.predict(x[:,0:n_comps])
# 
#     # outtable_xml = table_service.store_array(y, name='predicted_strength')
#     # return [ outtable_xml ]
#     out_strength_xml = '<tag name="strength"><tag name="strength" type="string" value="%s"/><tag name="link" type="resource" value="%s"/></tag>' %(str(y[0]), table_url)
#     return [out_strength_xml]

def truncate(a, shape):
    '''truncates the edges of the array based on the shape. '''
    
    a_shape = np.array(a.shape)
    n = len(shape)
    new_shape = a_shape.copy()
    new_shape[:n] = shape
    diff_shape = a_shape - new_shape
    index0 = (diff_shape + (diff_shape % 2) * (new_shape % 2)) // 2
    index1 = index0 + new_shape
    multi_slice = tuple(slice(index0[ii], index1[ii]) for ii in range(n))
    return a[multi_slice]

def pad(a, shape):
    '''pads the array with zeros to make for the shape'''
    
    a_shape = np.array(a.shape)
    diff = shape-a_shape
    pad_1 = (diff/2.0).astype(int)
    pad_2 = diff - pad_1
    
    padding = []
    for ii in range(len(pad_1)):
        padding.append((pad_1[ii],pad_2[ii]))
    
    return np.pad(a,padding,'constant',constant_values=(0,0))    

# predictor_path = 'predictor.sav'
# reducer_path = 'reducer.sav'
# # table_path = 'example_27x27x27.dream3d'
# table_path = 'example_55x55x55.dream3d'

# y_hat = predict(table_path,predictor_path,reducer_path)
# print y_hat




# if __name__ == "__main__":
#     import optparse
#     parser = optparse.OptionParser()
#     parser.add_option("-c", "--credentials", dest="credentials",
#                       help="credentials are in the form user:password")
#     #parser.add_option('--table_path')
#     #parser.add_option('--mex_url')
#     #parser.add_option('--auth_token')

#     (options, args) = parser.parse_args()


#     if options.credentials is None:
#         table_path, mex_url,  auth_token  = args[:3]
#         bq = BQSession().init_mex(mex_url, auth_token)
#     else:
#         table_path = args.pop(0)

#         if not options.credentials:
#             parser.error('need credentials')
#         user,pwd = options.credentials.split(':')

#         bq = BQSession().init_local(user, pwd)

#     logging.debug("Path is {}".format(table_path))
#     table_uniq = table_path.split('/')[-1]
#     predict(bq, table_uniq)







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
        bq = self.bqSession
        
        # call script
        outputs = predict( bq, log, **self.options.__dict__ )
        
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
