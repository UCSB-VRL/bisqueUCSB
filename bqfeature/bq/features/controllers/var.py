# global variables
import bq
import os
from bq.util.paths import data_path
#features dirs
FEATURES_CONTOLLERS_DIR = bq.features.controllers.__path__[0]
EXTRACTOR_DIR = os.path.join(FEATURES_CONTOLLERS_DIR,'extractors')

#data dirs
FEATURES_STORAGE_FILE_DIR = data_path('features')

FEATURES_TABLES_FILE_DIR = os.path.join(FEATURES_STORAGE_FILE_DIR ,'feature_tables')
FEATURES_WORK_DIR = os.path.join(FEATURES_STORAGE_FILE_DIR , 'workdir')
FEATURES_TEMP_DIR = os.path.join(FEATURES_STORAGE_FILE_DIR, 'temp')