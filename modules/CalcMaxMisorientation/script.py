import numpy as np

from bqapi.comm import BQCommError


"""
CalcMaxMisorientation script
"""

def run_script(session, log, **kw):
    # init services used
    table_service = session.service ('table')

    # get input params
    dream3d_run = kw.get('dream3d_run')

    # We assume input is a previous dream3d run that may have resulted in one or more output HDFs
    table_uniq, dream3d_params = _get_output_table_uniq(session, dream3d_run)

    # Get dataset dimensions
    dims = table_service.load_array(table_uniq, 'DataContainers/ImageDataContainer/_SIMPL_GEOMETRY/DIMENSIONS')
    xDim = dims[0]
    yDim = dims[1]
    zDim = dims[2]
    
    # Parameters to select specific groups of data
    badZslice, removeSlice = {'none':(0,False), 'bottom':(0,True), 'top':(zDim-1, False)}[kw.get('remSlice', 'none')]  # exclude featureIDs touching this Z-slice (0 = bottom, zDim-1 = top)
    limitAR = float(kw.get('limitAR', 1))           # feature IDs with maxAR <= than this max aspect ratio (lower = more columnar, max value = 1)
    minAvgMisorient = float(kw.get('minAvgMisorient', 4))   # feature IDs with avg misorientation >= this (in degrees)
    minMaxAxisL = float(kw.get('minMaxAxisL', 80))          # feature IDs with max axis lengths >= this (in microns)
    remSurface = {'non-surface features':1, 'all features':2}[kw.get('remSurface', 'all features')]  # make 1 to look at non-surface features, make 2 to look at all features
    
    # Array import
    try:
        featAvgMisorient = table_service.load_array(table_uniq, 'DataContainers/ImageDataContainer/CellFeatureData/FeatureAvgMisorientations')
    except BQCommError:
        featAvgMisorient = None
    try:
        surfaceFeatures = table_service.load_array(table_uniq, 'DataContainers/ImageDataContainer/CellFeatureData/SurfaceFeatures')
    except BQCommError:
        surfaceFeatures = None
    try:
        maxAR = table_service.load_array(table_uniq, 'DataContainers/ImageDataContainer/CellFeatureData/AspectRatios', slices=[slice(None),0])
    except BQCommError:
        maxAR = None
    try:
        maxAxisL = table_service.load_array(table_uniq, 'DataContainers/ImageDataContainer/CellFeatureData/AxisLengths', slices=[slice(None),0])
    except BQCommError:
        maxAxisL = None
    try:
        cells = table_service.load_array(table_uniq, 'DataContainers/ImageDataContainer/CellData/FeatureIds')
    except BQCommError:
        cells = None
    try:
        featMisorient = table_service.load_array(table_uniq, 'DataContainers/ImageDataContainer/CellData/FeatureReferenceMisorientations')
    except BQCommError:
        featMisorient = None
    
    m = (featAvgMisorient >= minAvgMisorient)
    if maxAR is not None:
        m = m & (maxAR <= limitAR)
    if maxAxisL is not None:
        m = m & (maxAxisL >= minMaxAxisL)
    if surfaceFeatures is not None:
        m = m & (surfaceFeatures < remSurface)
    
    conditions =  np.squeeze(np.argwhere(m))
    valid_FeatIDs = conditions
    
    # # Index out bad slice, if requested
    if removeSlice:
        invalidSlice = np.unique(cells[badZslice,:,:]) # don't want anything touching this slice
        index = np.searchsorted(invalidSlice, conditions)
        valid_FeatIDs = (np.logical_not(invalidSlice[index] == conditions) * conditions)
        valid_FeatIDs = valid_FeatIDs[valid_FeatIDs != 0]
    
    #log.debug(valid_FeatIDs)
    #log.debug(featAvgMisorient[4621])
    #log.debug(maxAR[4621])
    #log.debug(maxAxisL[4621])
    
    #valid_FeatIDs = np.arange(1,featAvgMisorient.size)    # do all features
    
    # Find maximum reference misorientation for each feature in valid_FeatIDs list and save data
    maxMisorient = np.zeros(valid_FeatIDs.size)
    zeros = np.zeros_like(featMisorient)
    for i in xrange(valid_FeatIDs.size):
        vMax = np.max(np.where(cells == valid_FeatIDs[i], featMisorient, zeros))
        maxMisorient[i] = vMax
        log.debug("Feature %s" % valid_FeatIDs[i]) 
    
    # save output back to BisQue and return
    outtable_xml = table_service.store_array(maxMisorient, name='maxMisorientData')
    return [ '<tag name="maximum reference misorientation" type="table" value="%s"/>' % outtable_xml.get('uri', '') ] +   \
           [ ('<tag name="statistics"><tag name="meanMaxMisorient" value="%s"/>' % str(np.mean(maxMisorient))) + ''.join([ '<tag name="%s" value="%s"/>' % (key, value) for key, value in dream3d_params.iteritems() ]) + '</tag>' ] 

def _get_output_table_uniq(session, mex_url):
    # find input params and output table in mex
    mex = session.fetchxml(mex_url, view='deep')
    input_params = {}
    for param in mex.xpath('.//tag[@name="inputs"]/tag[@name="pipeline_params"]/tag'):
        input_params[param.get('name')] = param.get('value')
    output_table = mex.xpath('.//tag[@name="outputs"]/tag[@name="output_table"]')[0]   # assume first output table is the one
    return output_table.get('value').split('/')[-1], input_params
