"""
HDF5 table exporter
"""

import os
import io
import logging
import datetime as dt
import tempfile
import tables

__all__ = [ 'ExporterHDF' ]

log = logging.getLogger("bq.table.export.hdf")


from bq.table.controllers.table_exporter import TableExporter


#---------------------------------------------------------------------------------------
# exporters: HDF
#---------------------------------------------------------------------------------------

class ExporterHDF (TableExporter):
    '''Formats tables as HDF5'''

    name = 'hdf'
    version = '1.0'
    ext = 'h5'
    mime_type = 'application/octet-stream'

    def info(self, table):
        # TODO
        return None

    def format(self, table):
        """ converts table to HDF5 """
        # requester can package returned byte stream into pytables in-memory file like this:
        #    h5file = tables.open_file('array.h5', driver="H5FD_CORE", driver_core_image=<received byte stream>, driver_core_backing_store=0)
        # array can then be accessed via
        #    h5file.root.array.read()
        # OR, bytes can be saved into HDF5 file.
        name = 'array'
        arr = table.as_array()
        with tables.open_file('array.h5', "w", driver="H5FD_CORE", driver_core_backing_store=0, filters=tables.Filters(complevel=5)) as h5file:  # compression level 5
            h5file.create_array(h5file.root, name, arr)
            return h5file.get_file_image()
