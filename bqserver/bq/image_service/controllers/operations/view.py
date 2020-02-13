"""
Dummy to accept view as a parameter
"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

import os
import sys
import math
import logging
import pkg_resources
from lxml import etree

__all__ = [ 'ViewOperation' ]

from bq.image_service.controllers.exceptions import ImageServiceException
from bq.image_service.controllers.operation_base import BaseOperation
from bq.image_service.controllers.process_token import ProcessToken

log = logging.getLogger("bq.image_service.operations.view")

class ViewOperation(BaseOperation):
    '''View operation is only needed to ignore view=deep in the request if given'''
    name = 'view'

    def __str__(self):
        return 'view: only needed to ignore view=deep in the request if given'

    def dryrun(self, token, arg):
        return token

    def action(self, token, arg):
        return token

