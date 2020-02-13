# -*- mode: python -*-
""" Base Feature library
"""

import os
import tables
import bq
import random
import numpy as np
import uuid
import logging
log = logging.getLogger("bq.features")
from .var import FEATURES_TABLES_FILE_DIR
import Feature


class ID(Feature.BaseFeature):
    """
        Initalizes ID table, returns ID, and places ID into the HDF5 table
    """ 
    #initalize parameters
    name = 'IDTable'
    description = """ID table"""
        
    def cached_columns(self):
        """
            Columns for the cached tables
        """
        return {
                'idnumber' : tables.StringCol(32, pos=1),
                'image'    : tables.StringCol(2000, pos=2),
                'mask'     : tables.StringCol(2000, pos=3),
                'gobject'  : tables.StringCol(2000, pos=4)
                }
        
    def output_feature_columns(self):
        """
            has no relavance to the hash tables for now
        """
        return {}
        
    def calculate(self, resource):
        return [resource.image], [resource.mask], [resource.gobject]




