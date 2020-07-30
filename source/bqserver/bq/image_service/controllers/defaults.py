"""
Provides typical exceptions thrown by the image service
"""

__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys
import logging


################################################################################
# Defaults
################################################################################

default_format = 'bigtiff'
default_tile_size = 512
min_level_size = 128
block_reads = False
block_tile_reads = True
