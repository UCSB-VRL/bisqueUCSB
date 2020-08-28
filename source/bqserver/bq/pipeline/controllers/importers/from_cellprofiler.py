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
CellProfiler pipeline importer
"""


# default imports
import os
import logging
import pkg_resources
import tempfile
from pylons.controllers.util import abort

from bq import blob_service
from bq.pipeline.controllers.pipeline_base import PipelineBase
from bq.pipeline.controllers.exporters.to_cellprofiler import json_to_cellprofiler

__all__ = [ 'PipelineCP' ]

log = logging.getLogger("bq.pipeline.import.cellprofiler")




#---------------------------------------------------------------------------------------
# Importer: CellProfiler
#---------------------------------------------------------------------------------------

def _get_parameters(step, param_name):
    res = []
    for param in step['Parameters']:
        if param.keys()[0] == param_name:
            res.append(param[param_name])
    return res
    
def upload_cellprofiler_pipeline(uf, intags):
    # analyze cellprofiler pipeline and replace illegal operations with BisQue operations
    pipeline = {}
    with open(uf.localpath(), 'r') as fo:
        pipeline = cellprofiler_to_json(fo)
    uf.close()
    # walk the pipeline and replace any incompatible steps with BisQue steps as well as possible
    # TODO: improve the quality of replacement and add BisQueExtractGObjects step generation
    new_pipeline = { '__Header__': pipeline['__Header__'] }
    new_step_id = 0
    old_step_id = 0
    # TODO: handle more cases...
    if pipeline['0']['__Label__'] == 'Images' and        \
       _get_parameters(pipeline['0'], 'Filter images?')[0] == 'Images only' and \
       pipeline['1']['__Label__'] == 'Metadata' and      \
       pipeline['2']['__Label__'] == 'NamesAndTypes' and \
       _get_parameters(pipeline['2'], 'Assign a name to')[0] == 'Images matching rules' and \
       int(_get_parameters(pipeline['2'], 'Single images count')[0]) == 0 and \
       int(_get_parameters(pipeline['2'], 'Assignments count')[0]) > 0 and \
       pipeline['3']['__Label__'] == 'Groups' and \
       _get_parameters(pipeline['3'], 'Do you want to group your images?')[0] == 'No':
        assign_cnt = int(_get_parameters(pipeline['2'], 'Assignments count')[0])
        channel_id = [ str(channel) for channel in range(1,assign_cnt+1) ] if assign_cnt > 1 else ['all']
        img_name = _get_parameters(pipeline['2'], 'Name to assign these images')
        obj_name = _get_parameters(pipeline['2'], 'Name to assign these objects')
        img_type = _get_parameters(pipeline['2'], 'Select the image type')
        params = [ {'Assignments count':str(assign_cnt)} ]
        for assign in range(assign_cnt,0,-1):
            params += [ {'Channel': channel_id[-assign]},
                        {'Name to assign these images': img_name[-assign]},
                        {'Name to assign these objects': obj_name[-assign]},
                        {'Select the image type': img_type[-assign]}
                      ]
        new_pipeline[str(new_step_id)] = { '__Label__': 'BisQueLoadImages', 
                                           '__Meta__': { 'module_num': str(new_step_id+1) }, 
                                           'Parameters': params }
        new_step_id += 1
        old_step_id += 4
    elif pipeline['0']['__Label__'] == 'LoadImages' and \
         _get_parameters(pipeline['0'], 'File type to be loaded')[0] == 'individual images' and \
         _get_parameters(pipeline['0'], 'Group images by metadata?')[0] == 'No':
        channel_id = 'all'
        img_name = _get_parameters(pipeline['0'], 'Name this loaded image')[0]
        obj_name = _get_parameters(pipeline['0'], 'Name this loaded object')[0]
        img_type = _get_parameters(pipeline['0'], 'Load the input as images or objects?')[0]
        img_type = 'Color image' if img_type == 'Images' else 'Objects'
        new_pipeline[str(new_step_id)] = { '__Label__': 'BisQueLoadImages', 
                                           '__Meta__': { 'module_num': str(new_step_id+1) }, 
                                           'Parameters': [ {'Channel': channel_id},
                                                           {'Name to assign these images': img_name},
                                                           {'Name to assign these objects': obj_name},
                                                           {'Select the image type': img_type}
                                                         ] }
        new_step_id += 1
        old_step_id += 1
    # now the rest of the pipeline...
    geo_objects = []
    colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
    color_idx = 0
    converted_cnt = 0   # TODO: only keep up to 10 interactive params... URL gets too big otherwise
    for step_id in range(old_step_id, len(pipeline)-1):
        if pipeline[str(step_id)]['__Label__'] == 'SaveImages' and \
           _get_parameters(pipeline[str(step_id)], 'Select the type of image to save')[0] == 'Image':
            img_name = _get_parameters(pipeline[str(step_id)], 'Select the image to save')[0]
            bit_depth = _get_parameters(pipeline[str(step_id)], 'Image bit depth')[0]
            img_type = _get_parameters(pipeline[str(step_id)], 'Save as grayscale or color image?')[0]
            colormap = _get_parameters(pipeline[str(step_id)], 'Select colormap')[0]
            filename = _get_parameters(pipeline[str(step_id)], 'Enter single file name')[0]
            new_pipeline[str(new_step_id)] = { '__Label__': 'BisQueSaveImage', 
                                               '__Meta__': { 'module_num': str(new_step_id+1) }, 
                                               'Parameters': [ {'Select the image to save':img_name},
                                                               {'Image bit depth': bit_depth},
                                                               {'Save as grayscale or color image?': img_type},
                                                               {'Select colormap': colormap},
                                                               {'Name': filename} ] }
            new_step_id += 1
        elif pipeline[str(step_id)]['__Label__'] == 'ExportToSpreadsheet' and \
             all([comb == 'No' for comb in _get_parameters(pipeline[str(step_id)], 'Combine these object measurements with those of the previous object?')]):
            data_exports = _get_parameters(pipeline[str(step_id)], 'Data to export')
            params = []
            for data_export in data_exports:
                params += [ {'Data to export':data_export}, {'Name':data_export} ]
            new_pipeline[str(new_step_id)] = { '__Label__': 'BisQueSaveTables', 
                                               '__Meta__': { 'module_num': str(new_step_id+1) }, 
                                               'Parameters': params }
            new_step_id += 1
        else:
            # keep all others unchanged
            # but check if some parameters could be treated as "interactive"
            new_pipeline[str(new_step_id)] = pipeline[str(step_id)]
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
        if pipeline[str(step_id)]['__Label__'] == 'IdentifyPrimaryObjects':
            obj_name = _get_parameters(pipeline[str(step_id)], 'Name the primary objects to be identified')[0]
            geo_objects.append( {'name':obj_name, 'color':colors[color_idx % len(colors)]} )
            color_idx += 1
        elif pipeline[str(step_id)]['__Label__'] == 'IdentifySecondaryObjects':
            obj_name = _get_parameters(pipeline[str(step_id)], 'Name the objects to be identified')[0]
            geo_objects.append( {'name':obj_name, 'color':colors[color_idx % len(colors)]} )
            color_idx += 1
        elif pipeline[str(step_id)]['__Label__'] == 'IdentifyTertiaryObjects':
            obj_name = _get_parameters(pipeline[str(step_id)], 'Name the tertiary objects to be identified')[0]
            geo_objects.append( {'name':obj_name, 'color':colors[color_idx % len(colors)]} )
            color_idx += 1
    # if there were any "IdentifyXXXObjects", add BisQueExportGObjects step(s) at the end
    for geo_object in geo_objects:
        new_pipeline[str(new_step_id)] = { '__Label__': 'BisQueExtractGObjects', 
                                           '__Meta__': { 'module_num': str(new_step_id+1) },
                                           'Parameters': [ {'Data to extract':geo_object['name']},
                                                           {'GObject type':'Ellipse'},
                                                           {'GObject label':geo_object['name']},
                                                           {'GObject color':geo_object['color']},                                                            
                                                           {'XCoord column':'AreaShape_Center_X'},
                                                           {'YCoord column':'AreaShape_Center_Y'},
                                                           {'Orientation column':'AreaShape_Orientation'},
                                                           {'MajorAxis column':'AreaShape_MajorAxisLength'},
                                                           {'MinorAxis column':'AreaShape_MinorAxisLength'} ] }
        new_step_id += 1
    new_pipeline['__Header__']['ModuleCount'] = str(len(new_pipeline)-1)
    # write modified pipeline back for ingest
    ftmp = tempfile.NamedTemporaryFile(delete=False)
    ftmp.write(json_to_cellprofiler(new_pipeline))
    ftmp.close()
    # ingest modified pipeline
    res = []
    with open(ftmp.name, 'rb') as fo:
        res = [blob_service.store_blob(resource=uf.resource, fileobj=fo)]
    return res

def cellprofiler_to_json(pipeline_file):
    data = {}
    is_header = True
    indent = 0
    step = {}
    step_id = 0
    header = { '__Type__': 'CellProfiler' }
    for line in pipeline_file:
        line = line.rstrip('\r\n')
        if is_header and len(line) == 0:
            # end of header reached
            data['__Header__'] = header
            is_header = False
        elif is_header and not line.startswith('CellProfiler Pipeline'):
            toks = line.split(':')
            tag = toks[0]
            val = ':'.join(toks[1:])
            header[tag] = val
        elif not is_header and len(line) == 0 and step:
            # end of step reached
            # check if step should be marked special (incompatible, modified)
            data[str(step_id)] = _validate_step(step)
            step = {}
            step_id += 1
        elif not is_header and not line.startswith(' '):
            # start of new pipeline step
            # format of line is:
            # <Step Label>:[<meta_tag>:<meta_val>|<meta_tag>:<meta_val>| ... |<meta_tag>:<meta_val>]
            toks = line.split(':')
            tag = toks[0]
            val = ':'.join(toks[1:]).lstrip('[').rstrip(']')
            step = { "__Label__": tag, "__Meta__": {}, "Parameters": [] }
            # TODO: use better parser that handles escapes ('\')
            for metas in val.split('|'):
                meta_toks = metas.split(':')
                meta_tag = meta_toks[0]
                meta_val = ':'.join(meta_toks[1:])
                step['__Meta__'][meta_tag] = meta_val
        elif not is_header and line.startswith(' '):
            # step parameter
            toks = line.strip().split(':')
            tag = toks[0]
            val = ':'.join(toks[1:])
            step['Parameters'].append( {tag:val} )                    
    # add last step                    
    if step:
        data[str(step_id)] = _validate_step(step)
    return data

def _validate_step(step):
    # mark actions not compatible with BisQue
    if step['__Label__'].startswith('BisQue'):
        step['__Meta__']['__compatibility__'] = 'bisque'
    elif step['__Label__'] in ['Crop']:  #TODO: check for other ignored steps
        step['__Meta__']['__compatibility__'] = 'ignored'
    elif step['__Label__'] in ['Images', 'LoadImages', 'Metadata', 'NamesAndTypes', 'Groups', 'SaveImages', 'ExportToSpreadsheet']:  #TODO: check for other incompatible steps
        step['__Meta__']['__compatibility__'] = 'incompatible'
    return step

class PipelineCP(PipelineBase):
    name = 'cellprofiler'
    version = '1.0'
    ext = ['cp', 'cppipe']

    def __init__(self, uniq, resource, path, **kw):
        super(PipelineCP, self).__init__(uniq, resource, path, **kw)

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
            self.data = cellprofiler_to_json(pipeline_file)
            
    def __repr__(self):
        return str(self.data)
    