from pymks import PrimitiveBasis
from pymks.stats import correlate
from sklearn.externals import joblib
import numpy as np
#import h5py
# import logging
from bqapi.comm import BQCommError
from bqapi.comm import BQSession
import logging
import os


logging.basicConfig(filename='PythonScript.log',filemode='a',level=logging.DEBUG)
log = logging.getLogger('bq.modules')

#logging.basicConfig(filename='prediction.log',level=logging.DEBUG)


def predict(bq, log, table_url, predictor_url, reducer_url, ms_path, **kw):
    '''
    Predicts effective strength of 3-D RVE of a 2-phase composite with strength contrast s2/s1 = 5
    Args:
    - table_path - path to dream3d file containing microstructure data (phase labels)
    - predictor_path - path to sav file containing calibrated model (LinearRegression)
    - reducer_path - path to sav file containing dimensionality reducer (Principal Component Basis)
    - ms_path - path to microstructure data (phase lables) inside dream3d file
    Returns:
    - y - predicted effective strength
    '''

    log.debug('kw is: %s', str(kw))
    predictor_uniq = predictor_url.split('/')[-1]
    reducer_uniq = reducer_url.split('/')[-1]
    table_uniq = table_url.split('/')[-1]

    predictor_url = bq.service_url('blob_service', path=predictor_uniq)
    predictor_path = os.path.join(kw.get('stagingPath', ''), 'predictor.sav')
    predictor_path = bq.fetchblob(predictor_url, path=predictor_path)

    reducer_url = bq.service_url('blob_service', path=reducer_uniq)
    reducer_path = os.path.join(kw.get('stagingPath', ''), 'reducer.sav')
    reducer_path = bq.fetchblob(reducer_url, path=reducer_path)

    # ms_path default: '/DataContainers/SyntheticVolumeDataContainer/CellData/Phases'

    # Default settings for 2-pt stats
    p_axes = (0,1,2)
    corrs = [(1,1)]

    # Read hdf5 table
    table_service = bq.service ('table')

    # Get dataset
    data = table_service.load_array(table_uniq, ms_path.lstrip('/'))
    ms = np.squeeze(data)

    # f = h5py.File(table_path, 'r')
    # data = f[ms_path].value
    # ms = np.squeeze(data)

    # Get phase labels as local states
    states = np.unique(ms)
    if len(states) > 2 :
        log.warn('WARNING: Model is only for two-phase materials! All extra phases will be considered as the second (hard) phase')
        ms[ms > states[0]] = states[0]

    ph_1 = np.min(states)
    ph_2 = np.max(states)

    s1 = 0.2
    s2 = 1.0
    eta = s2/s1
    f1 = np.count_nonzero(ms==ph_1)*1.0 / np.prod(ms.shape)
    f2 = np.count_nonzero(ms==ph_2)*1.0 / np.prod(ms.shape)
    sbar_up = (f1*s1) + (f2*s2)

    sbar_low = (f1/s1) + (f2/s2)
    sbar_low = 1.0/sbar_low

    # Get the size of the RVE
    if len(ms.shape) == 4:
        dims = ms.shape[1:4]
    elif len(ms.shape) == 3:
        dims = ms.shape
        ms = np.expand_dims(ms,0)
    else:
        log.error('ERROR: 3-D RVE(s) are expected!')
        return None

    # Load model and dimensionality reducer
    predictor = joblib.load(predictor_path)
    reducer = joblib.load(reducer_path)

    # Get the number of PC components used
    n_comps = predictor.named_steps['poly'].n_input_features_

    # Get the size of the calibration RVE
    nx_cal = int(np.round((reducer.components_.shape[1])**(1.0/3.0)))
    dims_cal = np.array((nx_cal,nx_cal,nx_cal))

    # Compute 2-pt stats
    n_states = len(states)
    p_basis = PrimitiveBasis(n_states=n_states, domain=states)
    tps = correlate(ms, p_basis, periodic_axes=p_axes, correlations=corrs)

    # Check size of the provided MVE: truncate if large, pad if small
    if np.prod(dims) > reducer.components_.shape[1]:
        tps = truncate(tps, [len(ms),dims_cal[0],dims_cal[1],dims_cal[2],1])
        dims = dims_cal
        log.info('Microstructure volume is larger than calibration RVE. 2-pt correlation function is truncated')
    elif np.prod(dims) < reducer.components_.shape[1]:
        tps = pad(tps, [len(ms),dims_cal[0],dims_cal[1],dims_cal[2],1])
        dims = dims_cal
        log.info('Microstructure volume is smaller than calibration RVE. 2-pt correlation function is padded')

    # Convert 2-pt stats to a vector
    tps_v = np.reshape(tps,(len(ms), np.prod(dims)))

    # Get low-dimensional representation
    x = reducer.transform(tps_v)

    # Get the property prediction
    y = predictor.predict(x[:,0:n_comps])

    # outtable_xml = table_service.store_array(y, name='predicted_strength')
    # return [ outtable_xml ]
    out_strength_xml = """<tag name="Strength">
                                <tag name="Strength" type="string" value="%s"/>
                                <tag name="sbar_up" type="string" value="%s"/>
                                <tag name="sbar_low" type="string" value="%s"/>
                                <tag name="Volume Fraction" type="string" value="%s"/>
                                <tag name="link" type="resource" value="%s"/>
                          </tag>""" %(str(y[0]*eta),str(sbar_up*eta),str(sbar_low*eta),str(f1)+', '+str(f2), table_url)
    return [out_strength_xml]

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
