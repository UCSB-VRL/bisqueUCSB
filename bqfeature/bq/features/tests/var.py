"""
var.py

Feature Constant Variables

"""
from datetime import datetime
import urllib

CONFIG_FILE = 'setup.cfg'
DEFAULT_RESULTS_DIR = 'Results'
DEFAULT_LOCAL_DIR = 'SampleData'
DEFAULT_TEMPORARY_DIR = 'temp'
DEFAULT_ROOT = 'localhost:8080'
DEFAULT_USER = 'test'
DEFAULT_PASSWORD = 'test'
DEFAULT_FEATURE_RESPONSE_HDF5 = 'Feature_Response_Results.h5'
DEFAULT_FEATURE_SAMPLE_HDF5 = 'Feature_Past_Response_Results.h5'
DEFAULT_FEATURE_PARALLEL_RESPONSE_HDF5 = 'Feature_Parallel_Response_Results.h5'
DEFAULT_FEATURE_PARALLEL_SAMPLE_HDF5 = 'Feature_Parallel_Past_Response_Results.h5'
TEST_PATH = 'tests_%s'%urllib.quote(datetime.now().strftime('%Y%m%d%H%M%S%f'))  #set a test dir on the system so not too many repeats occur