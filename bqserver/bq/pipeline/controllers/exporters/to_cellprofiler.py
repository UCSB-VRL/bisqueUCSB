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
CellProfiler pipeline exporter
"""

# default imports
import os
import copy
import logging

from bq.pipeline.controllers.pipeline_exporter import PipelineExporter

__all__ = [ 'ExporterCellProfiler' ]

log = logging.getLogger("bq.pipeline.export.cellprofiler")

#---------------------------------------------------------------------------------------
# exporters: CellProfiler
#---------------------------------------------------------------------------------------

def json_to_cellprofiler(pipeline):
    res = 'CellProfiler Pipeline: http://www.cellprofiler.org\n' + \
          'Version:'+(pipeline['__Header__'].get('Version', '') or '1')+'\n' + \
          'DateRevision:'+(pipeline['__Header__'].get('DateRevision', '') or '20140723174500')+'\n' + \
          'GitHash:'+(pipeline['__Header__'].get('GitHash', '') or '6c2d896')+'\n' + \
          'ModuleCount:'+str(len(pipeline)-1)+'\n' + \
          'HasImagePlaneDetails:'+(pipeline['__Header__'].get('HasImagePlaneDetails', '') or 'False')+'\n' + \
          'MessageForUser:'+(pipeline['__Header__'].get('MessageForUser', '') or '|Generated pipeline.')+'\n\n'
    
    for step_id in range(0,len(pipeline)-1):
        flags = pipeline[str(step_id)]['__Meta__']
        flags['module_num'] = str(step_id+1)
        res += pipeline[str(step_id)]['__Label__']+':['+'|'.join([tag+':'+flags[tag] for tag in flags if not tag.startswith('__')])+']\n'
        log.debug("HEADERR: %s" % res)   #!!!
        for param in pipeline[str(step_id)]['Parameters']:
            tag = param.keys()[0]
            res += '    '+tag+':'+param[tag]+'\n'
        res += '\n'
    return res

class ExporterCellProfiler (PipelineExporter):
    '''Formats pipelines in CellProfiler format'''

    name = 'cellprofiler'
    version = '1.0'
    ext = 'cppipe'
    mime_type = 'text/plain'

    def get_pre_post_ops(self, pipeline):
        """returns the pre/post pipeline operations"""
        res = { 'PreOps' : [], 'PostOps': [] }
        for step_id in range(0,len(pipeline)-1):
            step_name = pipeline[str(step_id)]['__Label__']
            if step_name == 'BisQueLoadImages':
                channel_ids = self._get_parameters(pipeline[str(step_id)], 'Channel')
                for channel_id in channel_ids:
                    if channel_id.isdigit():
                        res['PreOps'] += [ {'service':'image_service', 'id':'@INPUT', 'ops':'/remap:%s/format:tiff'%channel_id, 'filename':'part%s.tif'%channel_id} ]
                    else:
                        res['PreOps'] += [ {'service':'image_service', 'id':'@INPUT', 'ops':'/format:tiff', 'filename':'part%s.tif'%channel_id} ]
            elif step_name == 'BisQueSaveImage':
                prefixes = self._get_parameters(pipeline[str(step_id)], 'Name')
                res['PostOps'] += [ {'service':'postblob', 'type':'image', 'name':prefixes[0],  'filename':'%s.tiff'%prefixes[0]} ]
            elif step_name == 'BisQueSaveTables':
                prefixes = self._get_parameters(pipeline[str(step_id)], 'Name')                
                res['PostOps'] += [ {'service':'postblob', 'type':'table', 'name':prefix,  'filename':'%s.csv'%prefix} for prefix in prefixes ]
            elif step_name == 'BisQueExtractGObjects':
                table_name = self._get_parameters(pipeline[str(step_id)], 'Data to extract')
                gobject_type = self._get_parameters(pipeline[str(step_id)], 'GObject type')
                gobject_label = self._get_parameters(pipeline[str(step_id)], 'GObject label')
                gobject_color = self._get_parameters(pipeline[str(step_id)], 'GObject color')
                if gobject_type[0].lower() == 'ellipse':
                    x_coord = self._get_parameters(pipeline[str(step_id)], 'XCoord column')
                    y_coord = self._get_parameters(pipeline[str(step_id)], 'YCoord column')
                    orientation = self._get_parameters(pipeline[str(step_id)], 'Orientation column')
                    major_axis = self._get_parameters(pipeline[str(step_id)], 'MajorAxis column')
                    minor_axis = self._get_parameters(pipeline[str(step_id)], 'MinorAxis column')
                    res['PostOps'] += [ {'service':'postellipse',
                                         'label':gobject_label[0],
                                         'color':gobject_color[0],
                                         'x_coord':x_coord[0],
                                         'y_coord':y_coord[0], 
                                         'orientation':orientation[0], 
                                         'major_axis':major_axis[0], 
                                         'minor_axis':minor_axis[0], 
                                         'filename':'gobjects_%s.csv'%table_name[0]} ]
        return res
        
    def bisque_to_native(self, pipeline):
        """converts BisQue... steps into CellProfiler steps"""
        pipeline_res = { '__Header__': pipeline['__Header__'] }
        new_step_id = 0
        for step_id in range(0,len(pipeline)-1):
            step_name = pipeline[str(step_id)]['__Label__']
            if step_name == 'BisQueLoadImages':
                """
                Example:
                ---------------------------------------------
                BisQueLoadImages:[module_num:...]
                    Channel:1
                    Name to assign these images:OrigBlue
                    Name to assign these objects:Cell
                    Select the image type:Grayscale image
                    Channel:2
                    Name to assign these images:OrigGreen
                    Name to assign these objects:Nucleus
                    Select the image type:Grayscale image
                    Channel:3
                    Name to assign these images:OrigRed
                    Name to assign these objects:Cytoplasm
                    Select the image type:Grayscale image
                ---------------------------------------------
                """
                channel_ids = self._get_parameters(pipeline[str(step_id)], 'Channel')
                img_names = self._get_parameters(pipeline[str(step_id)], 'Name to assign these images')
                obj_names = self._get_parameters(pipeline[str(step_id)], 'Name to assign these objects')
                img_types = self._get_parameters(pipeline[str(step_id)], 'Select the image type')                
                parts = ['part%s.tif' % channel_id for channel_id in channel_ids]
                
                # add 'Images' module
                pipeline_res[str(new_step_id)] = { '__Meta__': { 'module_num':str(new_step_id+1), \
                                                                 'svn_version':r'\'Unknown\'', \
                                                                 'variable_revision_number':'2', \
                                                                 'show_window':'False', \
                                                                 'notes':'None', \
                                                                 'batch_state':r'array(\x5B\x5D, dtype=uint8)', \
                                                                 'enabled':'True', \
                                                                 'wants_pause':'False' }, \
                                                   '__Label__': 'Images', \
                                                   'Parameters': [ {'':''},
                                                                   {'Filter images?':'Images only'},
                                                                   {'Select the rule criteria':'and (extension does isimage) (directory doesnot startwith ".")'} ] }
                new_step_id += 1
                # add 'Metadata' module
                pipeline_res[str(new_step_id)] = { '__Meta__': { 'module_num':str(new_step_id+1), \
                                                                 'svn_version':r'\'Unknown\'', \
                                                                 'variable_revision_number':'4', \
                                                                 'show_window':'False', \
                                                                 'notes':'None', \
                                                                 'batch_state':r'array(\x5B\x5D, dtype=uint8)', \
                                                                 'enabled':'True', \
                                                                 'wants_pause':'False' }, \
                                                   '__Label__': 'Metadata', \
                                                   'Parameters': [ { 'Extract metadata?':'No' },                                                               
                                                                   { 'Metadata data type':'Text' },
                                                                   { 'Metadata types':'{}' },
                                                                   { 'Extraction method count':'1' },
                                                                   { 'Metadata extraction method':'Extract from image file headers' },
                                                                   { 'Metadata source':'File name' },
                                                                   { 'Regular expression':r"""^(?P<Plate>.*)_(?P<Well>\x5BA-P\x5D\x5B0-9\x5D{2})_s(?P<Site>\x5B0-9\x5D)_w(?P<ChannelNumber>\x5B0-9\x5D)""" },
                                                                   { 'Regular expression':r"""(?P<Date>\x5B0-9\x5D{4}_\x5B0-9\x5D{2}_\x5B0-9\x5D{2})$""" },
                                                                   { 'Extract metadata from':'All images' },
                                                                   { 'Select the filtering criteria':'and (file does contain "")' },
                                                                   { 'Metadata file location':'' },
                                                                   { 'Match file and image metadata':r'\x5B\x5D' },
                                                                   { 'Use case insensitive matching?':'No' } ] }
                new_step_id += 1
                # add 'NamesAndTypes' module
                parameters = [ { 'Assign a name to':'Images matching rules' },
                               { 'Select the image type':'Grayscale image' },
                               { 'Name to assign these images':'None' },
                               { 'Match metadata':r'\x5B\x5D' },
                               { 'Image set matching method':'Order' },
                               { 'Set intensity range from':'Image metadata' },
                               { 'Assignments count':str(len(channel_ids)) },
                               { 'Single images count':'0' } ]
                for part_idx in range(0, len(parts)):
                    parameters += [ { 'Select the rule criteria':'and (file does contain "%s")'%parts[part_idx] },
                                    { 'Name to assign these images':img_names[part_idx] },
                                    { 'Name to assign these objects':obj_names[part_idx] },
                                    { 'Select the image type':img_types[part_idx] },
                                    { 'Set intensity range from':'Image metadata' },
                                    { 'Retain outlines of loaded objects?':'No' },
                                    { 'Name the outline image':'None' } ] 
                pipeline_res[str(new_step_id)] = { '__Meta__': { 'module_num':str(new_step_id+1), \
                                                                 'svn_version':r'\'Unknown\'', \
                                                                 'variable_revision_number':'5', \
                                                                 'show_window':'False', \
                                                                 'notes':'None', \
                                                                 'batch_state':r'array(\x5B\x5D, dtype=uint8)', \
                                                                 'enabled':'True', \
                                                                 'wants_pause':'False' }, \
                                                   '__Label__': 'NamesAndTypes', \
                                                   'Parameters': parameters }
                new_step_id += 1
                # add 'Groups' module
                pipeline_res[str(new_step_id)] = { '__Meta__': { 'module_num':str(new_step_id+1), \
                                                                 'svn_version':r'\'Unknown\'', \
                                                                 'variable_revision_number':'2', \
                                                                 'show_window':'False', \
                                                                 'notes':'None', \
                                                                 'batch_state':r'array(\x5B\x5D, dtype=uint8)', \
                                                                 'enabled':'True', \
                                                                 'wants_pause':'False' }, \
                                                   '__Label__': 'Groups', \
                                                   'Parameters': [ { 'Do you want to group your images?':'No' },
                                                                   { 'grouping metadata count':'1' },
                                                                   { 'Metadata category':'None' } ] }
                new_step_id += 1
            elif step_name == 'BisQueSaveImage':
                """
                Example:
                ---------------------------------------------
                BisQueSaveImage:[module_num:...]
                    Select the image to save:RGBImage
                    Image bit depth:8
                    Save as grayscale or color image?:Grayscale
                    Select colormap:gray
                    Name:OutputImage
                ---------------------------------------------
                """                
                img_names = self._get_parameters(pipeline[str(step_id)], 'Select the image to save')
                bit_depths = self._get_parameters(pipeline[str(step_id)], 'Image bit depth')
                img_types = self._get_parameters(pipeline[str(step_id)], 'Save as grayscale or color image?')
                colormaps = self._get_parameters(pipeline[str(step_id)], 'Select colormap')
                prefixes = self._get_parameters(pipeline[str(step_id)], 'Name')
                pipeline_res[str(new_step_id)] = { '__Meta__': { 'module_num':str(new_step_id+1), \
                                                                 'svn_version':r'\'Unknown\'', \
                                                                 'variable_revision_number':'11', \
                                                                 'show_window':'False', \
                                                                 'notes':'None', \
                                                                 'batch_state':r'array(\x5B\x5D, dtype=uint8)', \
                                                                 'enabled':'True', \
                                                                 'wants_pause':'False' }, \
                                                  '__Label__': 'SaveImages', \
                                                  'Parameters': [ { 'Select the type of image to save':'Image' },
                                                                  { 'Select the image to save':img_names[0] },
                                                                  { 'Select the objects to save':'None' },
                                                                  { 'Select the module display window to save':'None' },
                                                                  { 'Select method for constructing file names':'Single name' },
                                                                  { 'Select image name for file prefix':'None' },
                                                                  { 'Enter single file name':prefixes[0] },
                                                                  { 'Number of digits':'4' },
                                                                  { 'Append a suffix to the image file name?':'No' },                                                                  
                                                                  { 'Text to append to the image name':'None' },
                                                                  { 'Saved file format':'tiff' },
                                                                  { 'Output file location':r"""Default Output Folder\x7CNone""" },
                                                                  { 'Image bit depth':bit_depths[0] },
                                                                  { 'Overwrite existing files without warning?':'Yes' },
                                                                  { 'When to save':'Every cycle' },
                                                                  { 'Rescale the images? ':'No' },
                                                                  { 'Save as grayscale or color image?':img_types[0] },
                                                                  { 'Select colormap':colormaps[0] },
                                                                  { 'Record the file and path information to the saved image?':'No' },
                                                                  { 'Create subfolders in the output folder?':'No' },
                                                                  { 'Base image folder':r"""/module/CellProfiler/workdir""" },
                                                                  { 'Saved movie format':'avi' } ] }
                new_step_id += 1
            elif step_name == 'BisQueSaveTables':
                """ 
                Example:
                ---------------------------------------------
                BisQueSaveTables:[module_num:...]
                    Data to export:Image
                    Name:Image
                    Data to export:Nuclei
                    Name:Objects
                    Data to export:Cells
                    Name:Cells
                    Data to export:Cytoplasm
                    Name:Cytoplasm
                ---------------------------------------------
                """                
                export_datas = self._get_parameters(pipeline[str(step_id)], 'Data to export')
                export_prefixes = self._get_parameters(pipeline[str(step_id)], 'Name')
                parameters = [ { 'Select the column delimiter':'Comma (",")' },
                               { 'Add image metadata columns to your object data file?':'No' },
                               { 'Limit output to a size that is allowed in Excel?':'No' },
                               { 'Select the measurements to export':'No' },
                               { 'Calculate the per-image mean values for object measurements?':'No' },
                               { 'Calculate the per-image median values for object measurements?':'No' },
                               { 'Calculate the per-image standard deviation values for object measurements?':'No' },
                               { 'Output file location':r"""Default Output Folder\x7C.""" },
                               { 'Create a GenePattern GCT file?':'No' },
                               { 'Select source of sample row name':'Metadata' },
                               { 'Select the image to use as the identifier':'None' },
                               { 'Select the metadata to use as the identifier':'None' },
                               { 'Export all measurement types?':'No' },
                               { 'Press button to select measurements to export':r'None\x7CNone' },
                               { 'Representation of Nan/Inf':'NaN' },
                               { 'Add a prefix to file names?':'No' },
                               { r"""Filename prefix\x3A""":'None' },
                               { 'Overwrite without warning?':'Yes' } ]
                for export_idx in range(0, len(export_datas)):
                    parameters += [ { 'Data to export':export_datas[export_idx] },
                                    { 'Combine these object measurements with those of the previous object?':'No' },
                                    { 'File name':'%s.csv'%export_prefixes[export_idx] },
                                    { 'Use the object name for the file name?':'No' } ]
                pipeline_res[str(new_step_id)] = { '__Meta__': { 'module_num':str(new_step_id+1), \
                                                                 'svn_version':r'\'Unknown\'', \
                                                                 'variable_revision_number':'11', \
                                                                 'show_window':'False', \
                                                                 'notes':'None', \
                                                                 'batch_state':r'array(\x5B\x5D, dtype=uint8)', \
                                                                 'enabled':'True', \
                                                                 'wants_pause':'False' }, \
                                                  '__Label__': 'ExportToSpreadsheet', \
                                                  'Parameters': parameters }
                new_step_id += 1
            elif step_name == 'BisQueExtractGObjects':
                """ 
                Example:
                ---------------------------------------------
                BisQueExtractGObjects:[module_num:...]
                    Data to extract:Cells
                    GObject type:Ellipse
                    GObject label:cell
                    GObject color:255,0,0
                    XCoord column:AreaShape_Center_X
                    YCoord column:AreaShape_Center_Y
                    Orientation column:AreaShape_Orientation
                    MajorAxis column:AreaShape_MajorAxisLength
                    MinorAxis column:AreaShape_MinorAxisLength
                ---------------------------------------------
                """                
                export_datas = self._get_parameters(pipeline[str(step_id)], 'Data to extract')
                parameters = [ { 'Select the column delimiter':'Comma (",")' },
                               { 'Add image metadata columns to your object data file?':'No' },
                               { 'Limit output to a size that is allowed in Excel?':'No' },
                               { 'Select the measurements to export':'No' },
                               { 'Calculate the per-image mean values for object measurements?':'No' },
                               { 'Calculate the per-image median values for object measurements?':'No' },
                               { 'Calculate the per-image standard deviation values for object measurements?':'No' },
                               { 'Output file location':r"""Default Output Folder\x7C.""" },
                               { 'Create a GenePattern GCT file?':'No' },
                               { 'Select source of sample row name':'Metadata' },
                               { 'Select the image to use as the identifier':'None' },
                               { 'Select the metadata to use as the identifier':'None' },
                               { 'Export all measurement types?':'No' },
                               { 'Press button to select measurements to export':r'None\x7CNone' },
                               { 'Representation of Nan/Inf':'NaN' },
                               { 'Add a prefix to file names?':'No' },
                               { r"""Filename prefix\x3A""":'None' },
                               { 'Overwrite without warning?':'Yes' } ]
                for export_idx in range(0, len(export_datas)):
                    parameters += [ { 'Data to export':export_datas[export_idx] },
                                    { 'Combine these object measurements with those of the previous object?':'No' },
                                    { 'File name':'gobjects_%s.csv'%export_datas[export_idx] },
                                    { 'Use the object name for the file name?':'No' } ]
                pipeline_res[str(new_step_id)] = { '__Meta__': { 'module_num':str(new_step_id+1), \
                                                                 'svn_version':r'\'Unknown\'', \
                                                                 'variable_revision_number':'11', \
                                                                 'show_window':'False', \
                                                                 'notes':'None', \
                                                                 'batch_state':r'array(\x5B\x5D, dtype=uint8)', \
                                                                 'enabled':'True', \
                                                                 'wants_pause':'False' }, \
                                                  '__Label__': 'ExportToSpreadsheet', \
                                                  'Parameters': parameters }
                new_step_id += 1
            elif step_name == 'Crop':
                # Ignore crops for now (but keep Crop operation because it creates new ids)
                pipeline_res[str(new_step_id)] = copy.deepcopy(pipeline[str(step_id)])
                self._set_parameter(pipeline_res[str(new_step_id)], 'Select the cropping shape', 'Rectangle')
                self._set_parameter(pipeline_res[str(new_step_id)], 'Select the cropping method', 'Coordinates')
                self._set_parameter(pipeline_res[str(new_step_id)], 'Left and right rectangle positions', 'begin,end')
                self._set_parameter(pipeline_res[str(new_step_id)], 'Top and bottom rectangle positions', 'begin,end')
                pipeline_res[str(new_step_id)]['__Meta__']['module_num'] = str(new_step_id+1)
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
                res.append(param[param_name])
        return res
    
    def _set_parameter(self, step, param_name, param_value):
        for param in step['Parameters']:
            if param.keys()[0] == param_name:
                param[param_name] = param_value

    def format(self, pipeline):
        """ converts pipeline to CellProfiler format """
        pipeline = pipeline.data
        if not pipeline or '__Header__' not in pipeline or pipeline['__Header__']['__Type__'] != 'CellProfiler':
            # wrong pipeline type
            return None        
        return json_to_cellprofiler(pipeline)
