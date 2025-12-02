"""
Provides typical exceptions thrown by the image service
"""

__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import sys
import logging


################################################################################
# Utils
################################################################################

def safeunicode(s):
    if isinstance(s, str):
        return s
    if isinstance(s, str) is not True:
        return str(s)
    try:
        return str(s, 'latin1')
    except (UnicodeEncodeError,UnicodeDecodeError):
        try:
            return str(s, 'utf8')
        except (UnicodeEncodeError,UnicodeDecodeError):
            pass
    return str(s, 'utf8', errors='ignore')
