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
ImageJ pipeline exporter
"""

# default imports
import os
import fnmatch
import copy
import logging

from bq.pipeline.controllers.pipeline_exporter import PipelineExporter

__all__ = [ 'ExporterImageJ' ]

log = logging.getLogger("bq.pipeline.export.imagej")

#---------------------------------------------------------------------------------------
# exporters: ImageJ
#---------------------------------------------------------------------------------------

def json_to_imagej(pipeline):
    res = ''
    
    for step_id in range(0,len(pipeline)-1):
        if pipeline[str(step_id)]['__Label__'] == 'endblock':
            line = '}'
        elif pipeline[str(step_id)]['__Label__'] == 'enddo':
            line = '} while(' + ','.join([param.values()[0] for param in pipeline[str(step_id)]['Parameters']]) + ');'
        elif pipeline[str(step_id)]['__Label__'] in ['__for__', '__if__', '__while__']:
            line = pipeline[str(step_id)]['__Label__'].strip('_') + '(' + ';'.join([param.values()[0].strip('"') for param in pipeline[str(step_id)]['Parameters']]) + ') {'
        elif pipeline[str(step_id)]['__Label__'] == '__else__':
            line = '} else {'
        elif pipeline[str(step_id)]['__Label__'] == 'startdo':
            line = 'do {'
        elif pipeline[str(step_id)]['__Label__'] == 'function':
            params = [param.values()[0] for param in pipeline[str(step_id)]['Parameters']]
            line = 'function %s(%s) {' % (params[0], ','.join(params[1:]))
        elif pipeline[str(step_id)]['__Label__'] == 'return':
            line = 'return %s;' % pipeline[str(step_id)]['Parameters'][0].values()[0]
        elif pipeline[str(step_id)]['__Label__'] == 'macro':
            line = 'macro %s {' % pipeline[str(step_id)]['Parameters'][0].values()[0]
        else:
            resvar = None
            params = []
            for param in pipeline[str(step_id)]['Parameters']:
                if 'resvar' in param.keys():
                    resvar = param.values()[0]
                else:
                    params.append(param.values()[0])
            if pipeline[str(step_id)]['__Label__'] == 'assign':
                # assignment
                line = (resvar + ' = ' if resvar is not None else '') + ','.join(params) + ';'
            else:
                # fct call
                line = (resvar + ' = ' if resvar is not None else '') + pipeline[str(step_id)]['__Label__'] + '(' + ','.join(params) + ');'
        res += line + '\n'
    return res

class ExporterImageJ (PipelineExporter):
    '''Formats pipelines in ImageJ format'''

    name = 'imagej'
    version = '1.0'
    ext = 'ijm'
    mime_type = 'text/plain'

    def get_pre_post_ops(self, pipeline):
        """returns the pre/post pipeline operations"""
        res = { 'PreOps' : [], 'PostOps': [] }
        for step_id in range(0,len(pipeline)-1):
            step_name = pipeline[str(step_id)]['__Label__']
            if step_name == 'BisQueLoadImage':
                res['PreOps'] += [ {'service':'image_service', 'id':'@INPUT', 'ops':'/format:tiff', 'filename':'input.tif'} ]
            elif step_name == 'BisQueLoadPolygon':
                gob_type = self._get_parameters(pipeline[str(step_id)], 'arg0')[0].strip('"')
                res['PreOps'] += [ {'service':'data_service', 'id':'@INPUT', 'ops':'//gobject[@type="%s"]/polygon/vertex'%gob_type, 'attrs':['x', 'y'], 'filename':'gobjects%s.csv'%step_id} ]
            elif step_name == 'BisQueSaveImage':
                name = '__BisQueSaveImage%s__.txt'%step_id
                fullname = '__BisQueSaveImage%s__.tif'%step_id
                new_op = {'service':'postblob', 'type':'image', 'name':name, 'filename':fullname}
                res['PostOps'] += [ new_op ]
            elif step_name == 'BisQueSaveROIs':
                gobject_type = self._get_parameters(pipeline[str(step_id)], 'arg0')[0].strip('"')
                gobject_label = self._get_parameters(pipeline[str(step_id)], 'arg1')[0].strip('"')
                gobject_color = self._get_parameters(pipeline[str(step_id)], 'arg2')[0].strip('"')
                if gobject_type.lower() == 'polygon':
                    res['PostOps'] += [ {'service':'postpolygon',
                                         'label':gobject_label,
                                         'color':gobject_color,
                                         'id_col':'id',
                                         'x_coord':'xcoord',
                                         'y_coord':'ycoord', 
                                         'filename':'gobjects%s.csv'%step_id} ]
            elif step_name == 'BisQueSaveResults':
                name = '__BisQueSaveResults%s__.txt'%step_id
                fullname = '__BisQueSaveResults%s__.csv'%step_id
                new_op = {'service':'postblob', 'type':'table', 'name':name, 'filename':fullname}
                res['PostOps'] += [ new_op ]
            elif step_name == 'BisQueAddTag':
                name = '__BisQueAddTag%s__.txt'%step_id
                new_op = {'service':'posttag', 'name':name, 'value':name}
                res['PostOps'] += [ new_op ]
        return res
        
    def bisque_to_native(self, pipeline):
        """converts BisQue... steps into ImageJ steps"""
        pipeline_res = { '__Header__': pipeline['__Header__'] }
        new_step_id = 0
        for step_id in range(0,len(pipeline)-1):
            step_name = pipeline[str(step_id)]['__Label__']
            if step_name == 'BisQueLoadImage':
                """ 
                Example:
                ---------------------------------------------
                BisQueLoadImage();
                ---------------------------------------------
                """
                pipeline_res[str(new_step_id)] = copy.deepcopy(pipeline[str(step_id)])
                pipeline_res[str(new_step_id)]['__Label__'] = 'open'
                pipeline_res[str(new_step_id)]['Parameters'] = [{'arg0': '"input.tif"'}]
                new_step_id += 1
            elif step_name == 'BisQueLoadPolygon':
                """ 
                Example:
                ---------------------------------------------
                BisQueLoadPolygon("gobject type");
                ---------------------------------------------
                """
                pipeline_res[str(new_step_id)] = copy.deepcopy(pipeline[str(step_id)])
                pipeline_res[str(new_step_id)]['__Label__'] = 'run'
                pipeline_res[str(new_step_id)]['Parameters'] = [{'arg0': '"XY Coordinates... "'}, {'arg1': '"open=gobjects%s.csv"'%step_id}]
                new_step_id += 1
            elif step_name == 'BisQueSaveImage':
                """ 
                Example:
                ---------------------------------------------
                BisQueSaveImage("image_name");
                ---------------------------------------------
                """
                name = self._get_parameters(pipeline[str(step_id)], 'arg0')[0]
                # in case name is a variable, let ImageJ store value in a file for later
                pipeline_res[str(new_step_id)] = { '__Label__': 'File.open', 'Parameters': [{'arg0':'"__BisQueSaveImage%s__.txt"'%step_id}, {'resvar':'bq_file'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'print', 'Parameters': [{'arg0':'bq_file'}, {'arg1':name}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'File.close', 'Parameters': [{'arg0':'bq_file'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = copy.deepcopy(pipeline[str(step_id)])
                pipeline_res[str(new_step_id)]['__Label__'] = 'saveAs'
                pipeline_res[str(new_step_id)]['Parameters'] = [{'arg0': '"Tiff"'}, {'arg1': '"__BisQueSaveImage%s__"'%step_id}]
                new_step_id += 1
            elif step_name == 'BisQueSaveROIs':
                """ 
                Example:
                ---------------------------------------------
                BisQueSaveROIs("polygon", "label", "color");
                ---------------------------------------------
                """
                outfile = 'gobjects%s.csv'%step_id
                pipeline_res[str(new_step_id)] = { '__Label__': 'File.open', 'Parameters': [{'arg0':'"'+outfile+'"'}, {'resvar':'bq_file'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'print', 'Parameters': [{'arg0':'bq_file'}, {'arg1':r'"id,xcoord,ycoord\n"'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'for', 'Parameters': [{'arg0':'bq_i = 0; bq_i < roiManager("count"); bq_i++'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'roiManager', 'Parameters': [{'arg0':'"select"'}, {'arg1':'bq_i'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'run', 'Parameters': [{'arg0':'"Fit Spline"'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'getSelectionCoordinates', 'Parameters': [{'arg0':'bq_xcoord'}, {'arg1':'bq_ycoord'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'for', 'Parameters': [{'arg0':'bq_j = 0; bq_j < bq_xcoord.length; bq_j++'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'print', 'Parameters': [{'arg0':'bq_file'}, {'arg1':r'bq_i + "," + bq_xcoord[bq_j] + "," + bq_ycoord[bq_j] + "\n"'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'endblock', 'Parameters': [] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'endblock', 'Parameters': [] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'File.close', 'Parameters': [{'arg0':'bq_file'}] }
                new_step_id += 1
            elif step_name == 'BisQueAddTag':
                """ 
                Example:
                ---------------------------------------------
                BisQueAddTag("tag_name", "tag_value");
                ---------------------------------------------
                """
                name = self._get_parameters(pipeline[str(step_id)], 'arg0')[0]
                value = self._get_parameters(pipeline[str(step_id)], 'arg1')[0]
                # in case name is a variable, let ImageJ store name/value in a file for later
                pipeline_res[str(new_step_id)] = { '__Label__': 'File.open', 'Parameters': [{'arg0':'"__BisQueAddTag%s__.txt"'%step_id}, {'resvar':'bq_file'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'print', 'Parameters': [{'arg0':'bq_file'}, {'arg1':name}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'print', 'Parameters': [{'arg0':'bq_file'}, {'arg1':value}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'File.close', 'Parameters': [{'arg0':'bq_file'}] }
                new_step_id += 1
            elif step_name == 'BisQueSaveResults':
                """ 
                Example:
                ---------------------------------------------
                BisQueSaveResults("table_name");
                ---------------------------------------------
                """
                name = self._get_parameters(pipeline[str(step_id)], 'arg0')[0]
                # in case name is a variable, let ImageJ store value in a file for later
                pipeline_res[str(new_step_id)] = { '__Label__': 'File.open', 'Parameters': [{'arg0':'"__BisQueSaveResults%s__.txt"'%step_id}, {'resvar':'bq_file'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'print', 'Parameters': [{'arg0':'bq_file'}, {'arg1':name}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = { '__Label__': 'File.close', 'Parameters': [{'arg0':'bq_file'}] }
                new_step_id += 1
                pipeline_res[str(new_step_id)] = copy.deepcopy(pipeline[str(step_id)])
                pipeline_res[str(new_step_id)]['__Label__'] = 'saveAs'
                pipeline_res[str(new_step_id)]['Parameters'] = [{'arg0': '"Results"'}, {'arg1': '"__BisQueSaveResults%s__.csv"'%step_id}]
                new_step_id += 1
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
                res.append(param[param_name].strip())
        return res
    
    def format(self, pipeline):
        """ converts pipeline to ImageJ format """
        pipeline = pipeline.data
        if not pipeline or '__Header__' not in pipeline or pipeline['__Header__']['__Type__'] != 'ImageJ':
            # wrong pipeline type
            return None        
        return json_to_imagej(pipeline) + '\nrun("Quit");\neval("script", "System.exit(0);");\n'
