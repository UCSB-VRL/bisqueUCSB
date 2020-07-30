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
Dream.3D pipeline exporter
"""

# default imports
import os
import fnmatch
import copy
import json
import logging

from bq.pipeline.controllers.pipeline_exporter import PipelineExporter

__all__ = [ 'ExporterDream3D' ]

log = logging.getLogger("bq.pipeline.export.dream3d")

#---------------------------------------------------------------------------------------
# exporters: Dream.3D
#---------------------------------------------------------------------------------------

def json_to_dream3d(pipeline):
    header = {}
    for key in pipeline['__Header__']:
        header[key] = pipeline['__Header__'][key]
    res = { 'PipelineBuilder': header }
    for key in pipeline:
        if key == '__Header__':
            continue
        step = { 'Filter_Human_Label': pipeline[key]['__Label__'] }
        for meta_key in pipeline[key]['__Meta__']:
            if meta_key in ['Filter_Name', 'FilterVersion']:
                step[meta_key] = pipeline[key]['__Meta__'][meta_key]
        for param in pipeline[key]['Parameters']:
            step[param.keys()[0]] = param.values()[0]
        res[key] = step
    return json.dumps(res)

class ExporterDream3D (PipelineExporter):
    '''Formats pipelines in Dream.3D format'''

    name = 'dream3d'
    version = '1.0'
    ext = 'json'
    mime_type = 'application/json'

    def get_pre_post_ops(self, pipeline):
        """returns the pre/post pipeline operations"""
        res = { 'PreOps' : [], 'PostOps': [] }
        for step_id in range(0,len(pipeline)-1):
            step_name = pipeline[str(step_id)]['__Label__']
            if step_name == 'BisQueLoadTable':
                download_to = self._get_parameters(pipeline[str(step_id)], 'Filename')[0]
                res['PreOps'] += [ {'service':'getblob', 'type':'table', 'id':'@INPUT', 'filename':download_to} ]
            elif step_name == 'BisQueSaveTable':
                upload_from = self._get_parameters(pipeline[str(step_id)], 'Filename')[0]
                res['PostOps'] += [ {'service':'postblob', 'type':'table', 'name':'output.h5', 'filename':upload_from} ]
        return res
    
    def bisque_to_native(self, pipeline):
        """converts BisQue... steps into Dream.3D steps"""
        pipeline_res = { '__Header__': pipeline['__Header__'] }
        new_step_id = 0
        for step_id in range(0,len(pipeline)-1):
            step_name = pipeline[str(step_id)]['__Label__']
            if step_name == 'BisQueLoadTable':
                """
                Example:
                ---------------------------------------------
                BisQueLoadTable
                ---------------------------------------------
                """
                pass  # remove this step (will be handled in PreOps)
            elif step_name == 'BisQueSaveTable':
                """
                Example:
                ---------------------------------------------
                BisQueSaveTable
                   Name: <output name> 
                ---------------------------------------------
                """
                pass  # remove this step (will be handled in PostOps)
            elif pipeline[str(step_id)]['__Meta__'].get('__compatibility__', '') == 'incompatible':
                return {}
            else:
                pipeline_res[str(new_step_id)] = copy.deepcopy(pipeline[str(step_id)])
                pipeline_res[str(new_step_id)]['__Meta__']['module_num'] = str(new_step_id+1)
                new_step_id += 1
        return pipeline_res
    
    def _get_parameters(self, step, param_name):
        res = []
        for param in step['Parameters']:
            if param.keys()[0] == param_name:
                res.append(param[param_name])
        return res
    
    def _set_parameter(self, step, param_name, param_value):
        for param in step['Parameters']:
            if param.keys()[0] == param_name:
                param[param_name] = param_value

    def format(self, pipeline):
        """ converts pipeline to Dream.3D format """
        pipeline = pipeline.data
        if not pipeline or '__Header__' not in pipeline or pipeline['__Header__']['__Type__'] != 'Dream.3D':
            # wrong pipeline type
            return None        
        return json_to_dream3d(pipeline)
