###############################################################################
##  BisQue                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2015 by the Regents of the University of California     ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################

"""
Bisque pipeline importer
"""


# default imports
import os
import logging
import json
import pkg_resources
import tempfile
from pylons.controllers.util import abort

from bq import blob_service
from bq.pipeline.controllers.pipeline_base import PipelineBase

__all__ = [ 'PipelineBisque' ]

log = logging.getLogger("bq.pipeline.import.bqworkflow")




#---------------------------------------------------------------------------------------
# Importer: Bisque workflow
#---------------------------------------------------------------------------------------

def upload_bisque_pipeline(uf, intags):
    with open(uf.localpath(), 'rb') as fo:
        res = [blob_service.store_blob(resource=uf.resource, fileobj=fo)]
    uf.close()
    return res
        
def bqworkflow_to_json(pipeline_file):
    raw_pipeline = pipeline_file.read()
    pipeline = json.loads(raw_pipeline)
    return pipeline

class PipelineBisque(PipelineBase):
    name = 'bqworkflow'
    version = '1.0'
    ext = ['bq']

    def __init__(self, uniq, resource, path, **kw):
        super(PipelineBisque, self).__init__(uniq, resource, path, **kw)

        # try to load the resource binary
        b = blob_service.localpath(uniq, resource=resource) or abort (404, 'File not available from blob service')
        self.filename = b.path
        self.data = {}
        with open(self.filename, 'r') as pipeline_file:
            self.data = bqworkflow_to_json(pipeline_file)
                
    def __repr__(self):
        return str(self.data)