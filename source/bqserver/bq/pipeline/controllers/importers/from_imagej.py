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
ImageJ pipeline importer
"""


# default imports
import os
import logging
import pkg_resources
import tempfile
import re
import copy
import ast
from pylons.controllers.util import abort

from bq import blob_service
from bq.pipeline.controllers.pipeline_base import PipelineBase
from bq.pipeline.controllers.exporters.to_imagej import json_to_imagej

__all__ = [ 'PipelineIJ' ]

log = logging.getLogger("bq.pipeline.import.imagej")




#---------------------------------------------------------------------------------------
# Importer: CellProfiler
#---------------------------------------------------------------------------------------

def _get_parameters(step, param_name):
    res = []
    for param in step['Parameters']:
        if param.keys()[0] == param_name:
            res.append(param[param_name].strip())
    return res
    
def upload_imagej_pipeline(uf, intags):
    # analyze ImageJ macro and replace illegal operations with BisQue operations
    pipeline = {}
    with open(uf.localpath(), 'r') as fo:
        pipeline = imagej_to_json(fo)
    uf.close()
    # walk the pipeline and replace any incompatible steps with BisQue steps as well as possible
    new_pipeline = { '__Header__': pipeline['__Header__'] }
    new_step_id = 0
    old_step_id = 0
    converted_cnt = 0   # TODO: only keep up to 10 interactive params... URL gets too big otherwise
    had_save_img = False
    had_save_res = False
    for step_id in range(old_step_id, len(pipeline)-1):
        new_pipeline[str(new_step_id)] = copy.deepcopy(pipeline[str(step_id)])
        new_pipeline[str(new_step_id)]['__Meta__']['module_num'] = str(new_step_id+1)
        if pipeline[str(step_id)]['__Label__'] == 'open':
            new_pipeline[str(new_step_id)]['__Label__'] = 'BisQueLoadImage'
            new_pipeline[str(new_step_id)]['Parameters'] = []
            new_step_id += 1
        elif pipeline[str(step_id)]['__Label__'] in ['saveAs'] and _get_parameters(pipeline[str(step_id)], 'arg0')[0].lower() == 'tiff' and not had_save_img:
            new_pipeline[str(new_step_id)]['__Label__'] = 'BisQueSaveImage'
            out_name = _get_parameters(pipeline[str(step_id)], 'arg1')
            new_pipeline[str(new_step_id)]['Parameters'] = [{'arg0' : out_name[0] if len(out_name)>0 else '"output.tif"' }]
            had_save_img = True
            new_step_id += 1
        elif pipeline[str(step_id)]['__Label__'] in ['saveAs'] and _get_parameters(pipeline[str(step_id)], 'arg0')[0].lower() == 'results' and not had_save_res:
            new_pipeline[str(new_step_id)]['__Label__'] = 'BisQueSaveResults'
            out_name = _get_parameters(pipeline[str(step_id)], 'arg1')
            new_pipeline[str(new_step_id)]['Parameters'] = [{'arg0' : out_name[0] if len(out_name)>0 else '"output.csv"' }]
            had_save_res = True
            new_step_id += 1
        else:
            # keep all others unchanged
            # but check if some parameters could be treated as "interactive"
            new_pipeline[str(new_step_id)]['__Meta__']['module_num'] = str(new_step_id+1)
            new_parameters = []            
            for param in new_pipeline[str(new_step_id)]['Parameters']:
                param_key, param_val = param.items()[0]
                if converted_cnt < 10 and any([phrase in param_key.lower() for phrase in ['threshold', 'size', 'diameter', 'distance', 'smoothing', 'bound', 'difference', 'intensity']]):
                    try:
                        float(str(param_val))    # is this a number?
                        param_val = "@STRPARAM@%s" % str(param_val)
                        converted_cnt += 1
                    except ValueError:
                        pass   # skip non-numerical parameters for now
                new_parameters.append({param_key:param_val})
            new_pipeline[str(new_step_id)]['Parameters'] = new_parameters
            new_step_id += 1

    new_pipeline['__Header__']['ModuleCount'] = str(len(new_pipeline)-1)
    # write modified pipeline back for ingest
    ftmp = tempfile.NamedTemporaryFile(delete=False)
    ftmp.write(json_to_imagej(new_pipeline))
    ftmp.close()
    # ingest modified pipeline
    res = []
    with open(ftmp.name, 'rb') as fo:
        res = [blob_service.store_blob(resource=uf.resource, fileobj=fo)]
    return res

def imagej_to_json(pipeline_file):
    # TODO: write real parser
    data = {}
    step_id = 0
    in_comment=False
    data['__Header__'] = { '__Type__': 'ImageJ' }
    for fline in pipeline_file:
        line = fline.rstrip('\r\n').strip()
        if line == '' or line.startswith('//') or (line.startswith('/*') and line.endswith('*/')):
            continue
        if in_comment:
            if line.endswith('*/'):
                in_comment=False
            continue
        if line.startswith('/*'):
            in_comment=True
            continue
        if line == '}':
            # end of block
            line = 'endblock();'
        elif line.startswith('} while'):
            # end of "do {...} while" block
            line = 'enddo(' + line.split('(',1)[1]
        elif any([line.startswith(fct) for fct in ['for (', 'for(', 'while (', 'while(', 'if (', 'if(']]):
            # start of block
            line = line.rstrip('{').rstrip()
            fctname = '__%s__' % line.split('(',1)[0].strip()
            args = line.split('(',1)[1].rstrip(')').split(';')
            line = fctname + '(' + ','.join(['"%s"' % arg for arg in args]) + ');'
        elif any([line.startswith(fct) for fct in ['} else {', '}else{']]):
            line = '__else__();'
        elif any([line.startswith(fct) for fct in ['do {', 'do{']]):
            # start of block
            line = 'startdo();'
        elif line.startswith('function'):
            # function definition
            toks = line[len('function'):].split('(')
            fname = toks[0].strip()
            args = [arg.strip() for arg in toks[1].split(')')[0].split(',')]
            line = 'function(%s,%s);' % (fname, ','.join(args))
        elif line.startswith('return'):
            # function return
            retval = line[len('return'):].strip().rstrip(';').rstrip()
            line = 'return(%s);' % retval
        elif line.startswith('macro'):
            # macro definition
            mname = line[len('macro'):].split('{')[0].strip()
            line = 'macro(%s);' % mname
        ### at this point, line is either (1) fct call or (2) assignment ###
        try:
            line = line.rstrip(';').rstrip()
            stree = ast.parse(line)   # TODO: replace AST
            if isinstance(stree.body[0].value, ast.Call):
                # some fct call
                if isinstance(stree.body[0].value.func, ast.Attribute):
                    tag = stree.body[0].value.func.value.id + '.' + stree.body[0].value.func.attr
                else:
                    tag = stree.body[0].value.func.id
                paran_off = line.index('(')
                arg_offs = [arg.col_offset for arg in stree.body[0].value.args] + [len(line)]
                params = []
                for argidx in range(0,len(arg_offs)-1):
                    start_off = arg_offs[argidx]-1
                    end_off = arg_offs[argidx+1]-1
                    # find the real start of the arg in case of redundant (((...)))
                    while line[start_off] != ',' and start_off > paran_off:
                        start_off -= 1
                    arg = line[start_off+1 : end_off].strip().rstrip(',').rstrip()
                    params.append({'arg'+str(argidx) : arg})
                if isinstance(stree.body[0], ast.Assign):
                    resvar = stree.body[0].targets[0].id
                    params.append({'resvar' : resvar })
                step = { "__Label__": tag, "__Meta__": {}, "Parameters": params }
            elif isinstance(stree.body[0], ast.Assign):
                # assignment op
                if isinstance(stree.body[0].targets[0], ast.Attribute):
                    resvar = stree.body[0].targets[0].value.id + '.' + stree.body[0].targets[0].attr
                else:
                    resvar = stree.body[0].targets[0].id
                rexpr_off = stree.body[0].value.col_offset
                rexpr = line[rexpr_off:].rstrip()
                step = { "__Label__": "assign", "__Meta__": {}, "Parameters": [{'arg0': rexpr}, {'resvar': resvar}] }
            else:
                abort (400, 'ImageJ macro line "%s" cannot be parsed' % fline.rstrip('\r\n').strip())
        except SyntaxError:
            abort (400, 'ImageJ macro line "%s" cannot be parsed' % fline.rstrip('\r\n').strip())
        data[str(step_id)] = _validate_step(step)
        step_id += 1
    return data

def _validate_step(step):
    # mark actions not compatible with BisQue
    if step['__Label__'].startswith('BisQue'):
        step['__Meta__']['__compatibility__'] = 'bisque'
    elif step['__Label__'] in ['print']:  #TODO: check for other ignored steps
        step['__Meta__']['__compatibility__'] = 'ignored'
    elif any([step['__Label__'].startswith(pre) for pre in ['Dialog.', 'File.']]) or step['__Label__'] in ['open', 'save', 'saveAs', 'macro', 'getDirectory', 'waitForUser']:  #TODO: check for other incompatible steps
        step['__Meta__']['__compatibility__'] = 'incompatible'
    return step

class PipelineIJ(PipelineBase):
    name = 'imagej'
    version = '1.0'
    ext = ['ijm']

    def __init__(self, uniq, resource, path, **kw):
        super(PipelineIJ, self).__init__(uniq, resource, path, **kw)

        # allow to initialize with JSON directly 
        self.filename = None
        self.data = kw.get('data', None)
        if self.data:
            return

        # try to load the resource binary
        b = blob_service.localpath(uniq, resource=resource) or abort (404, 'File not available from blob service')
        self.filename = b.path
        self.data = {}
        raw_pipeline = []
        with open(self.filename, 'r') as pipeline_file:
            self.data = imagej_to_json(pipeline_file)
            
    def __repr__(self):
        return str(self.data)