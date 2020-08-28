import tables
import numpy
import warnings
from tables.exceptions import PerformanceWarning
from tables import Leaf

from monkeypatch import *

tables_v = [int(s) for s in tables.__version__.split('.')]

if tables_v < [2, 3, 0]:
    warnings.warn("""\
We need to patch pytables 2.3.X up to 3.0.0, versions 3.1.0 or 
greater does not require this patch, make sure your version of pytables
needs patching"""
                  , PerformanceWarning)
elif tables_v > [3, 0, 0]:
    #does not require this patch
    pass
else:
    @monkeypatch_method(Leaf)
    def _calc_nrowsinbuf(self):
        """Calculate the number of rows that fits on a PyTables buffer."""
    
        params = self._v_file.params
        # Compute the nrowsinbuf
        rowsize = self.rowsize
        buffersize = params['IO_BUFFER_SIZE']
        nrowsinbuf = buffersize // rowsize
        
        chunksize = numpy.asarray(self.chunkshape).prod()
        if nrowsinbuf < chunksize:
            nrowsinbuf = chunksize
        
        # Safeguard against row sizes being extremely large
        if nrowsinbuf == 0:
            nrowsinbuf = 1
            # If rowsize is too large, issue a Performance warning
            maxrowsize = params['BUFFER_TIMES'] * buffersize
            if rowsize > maxrowsize:
                warnings.warn("""\
    The Leaf ``%s`` is exceeding the maximum recommended rowsize (%d bytes);
    be ready to see PyTables asking for *lots* of memory and possibly slow
    I/O.  You may want to reduce the rowsize by trimming the value of
    dimensions that are orthogonal (and preferably close) to the *main*
    dimension of this leave.  Alternatively, in case you have specified a
    very small/large chunksize, you may want to increase/decrease it."""
                              % (self._v_pathname, maxrowsize),
                                 PerformanceWarning)
        return nrowsinbuf

