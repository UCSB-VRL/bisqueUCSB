
#import threading
from threading import Thread
import socket
import errno
import tempfile
import urllib
import os
from math import ceil
import Queue
import logging
import warnings
from collections import namedtuple

#import numpy as np

from .exception import BQCommError

try: #checks for lxml if not found uses python xml
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree

log = logging.getLogger('bqapi.bqfeature')

#requires pytables to run this portion of the api
try:
    import tables
except ImportError:
    warnings.warn("Pytables was not found! bqfeatures requires pytables!")

#max requests attemps if the connection is drop when making parallel requests
MAX_ATTEMPTS = 5

FeatureResource = namedtuple('FeatureResource',['image','mask','gobject'])
FeatureResource.__new__.__defaults__ = (None, None, None)

class FeatureError(Exception):
    """
        Feature Communication Exception
    """

class Feature(object):

    def fetch(self, session, name, resource_list, path=None):
        """
            Requests the feature server to calculate features on provided resources.

            @param: session - the local session
            @param: name - the name of the feature one wishes to extract
            @param: resource_list - list of the resources to extract. format:
            [(image_url, mask_url, gobject_url),...] if a parameter is
            not required just provided None
            @param: path - the location were the hdf5 file is stored. If None is set the file will be placed in a tempfile and the pytables
            file handle will be returned. (default: None)

            @return: returns either a pytables file handle or the file name when the path is provided
        """
        url = '%s/features/%s/hdf'%(session.bisque_root,name)

        resource = etree.Element('resource')
        for (image, mask, gobject) in resource_list:
            sub = etree.SubElement(resource, 'feature')
            query = []
            if image: query.append('image=%s' % urllib.quote(image))
            if mask: query.append('mask=%s' % urllib.quote(mask))
            if gobject: query.append('gobject=%s' % urllib.quote(gobject))
            query = '&'.join(query)
            sub.attrib['uri'] = '%s?%s'%(url,query)

        log.debug('Fetch Feature %s for %s resources'%(name, len(resource_list)))

        if path is None:
            f = tempfile.NamedTemporaryFile(suffix='.h5', dir=tempfile.gettempdir(), delete=False)
            f.close()
            session.c.push(url, content=etree.tostring(resource), headers={'Content-Type':'text/xml', 'Accept':'application/x-bag'}, path=f.name)
            return tables.open_file(f.name,'r')
        log.debug('Returning feature response to %s' % path)
        return session.c.push(url, content=etree.tostring(resource), headers={'Content-Type':'text/xml', 'Accept':'application/x-bag'}, path=path)



    def fetch_vector(self, session, name, resource_list):
        """
            Requests the feature server to calculate features on provided resources. Designed more for
            requests of very view features.

            @param: session - the local session
            @param: name - the name of the feature one wishes to extract
            @param: resource_list - list of the resources to extract. format:
            [(image_url, mask_url, gobject_url),...] if a parameter is
            not required just provided None

            @return: a list of features as numpy array

            @exception: FeatureError - if any part of the request has an error the FeatureError will be raised on the
            first error.
            note: You can use fetch and read from the status table for the error.
            warning: fetch_vector will not return response if an error occurs within the request
        """
        hdf5 = self.fetch(session, name, resource_list)
        status = hdf5.root.status
        index = status.getWhereList('status>=400')
        if index.size>0: #returns the first error that occurs
            status = status[index[0]][0]
            hdf5.close()
            os.remove(hdf5.filename) #remove file from temp directory
            raise FeatureError('%s:Error occured during feature calculations' % status)
        table = hdf5.root.values
        status_table = hdf5.root.status
        feature_vector = table[:]['feature']
        hdf5.close()
        os.remove(hdf5.filename) #remove file from temp directory
        return feature_vector

    @staticmethod
    def length(session, name):
        """
            Returns the length of the feature

            @param: session - the local session
            @param: name - the name of the feature one wishes to extract

            @return: feature length
        """
        xml = session.fetchxml('/features/%s'%name)
        return int(xml.find('feature/tag[@name="feature_length"]').attrib.get('value'))

class ParallelFeature(Feature):

    MaxThread = 8
    MaxChunk = 2000
    MinChunk = 25

    def __init__(self):
        super(ParallelFeature, self).__init__()


    class BQRequestThread(Thread):
        """
            Single Thread
        """
        def __init__(self, request_queue, errorcb=None):
            """
                @param: requests_queue - a queue of requests functions
                @param: errorcb - a call back that is called if a BQCommError is raised
            """
            self.request_queue = request_queue

            if errorcb is not None:
                self.errorcb = errorcb
            else:

                def error_callback(e):
                    """
                        Default callback function

                        @param: e - BQCommError object
                    """
                    pass

                self.errorcb = error_callback
            super(ParallelFeature.BQRequestThread, self).__init__()


        def run(self):
            while True:
                if not self.request_queue.empty():
                    request = self.request_queue.get()
                    try:
                        request()
                    except BQCommError as e:
                        self.errorcb(e)
                else:
                    break


    def request_thread_pool(self, request_queue, errorcb=None, thread_count = MaxThread):
        """
            Runs the BQRequestThread

            @param: request_queue - a queue of request functions
            @param: errorcb - is called back when a BQCommError is raised
        """
        jobs = []
        log.debug('Starting Thread Pool')
        for _ in range(thread_count):
            r = self.BQRequestThread(request_queue, errorcb)
            r.daemon = True
            jobs.append(r)
            r.start()

        for j in jobs:
            j.join()
        log.debug('Rejoining %s threads'%len(jobs))
        return


    def set_thread_num(self, n):
        """
            Overrides the internal thread parameters, chunk size must also
            be set to override the request parameters

            @param: n - the number of requests made at once
        """
        self.thread_num = n


    def set_chunk_size(self, n):
        """
            Overrides the chunk size, thread num must also
            be set to override the request parameters

            @param: n - the size of each request
        """
        self.chunk_size = n


    def calculate_request_plan(self, l):
        """
            Tries to figure out the best configuration
            of concurrent requests and sizes of those
            requests based on the size of the total request
             and pre-set parameters

            @param: l - the list of requests

            @return: chunk_size - the amount of resources for request
            @return: thread_num - the amount of concurrent requests
        """
        if len(l)>self.MaxThread*self.MaxChunk:
            return (self.MaxThread, self.MaxChunk)
        else:
            if len(l)/float(self.MaxThread)>=self.MinChunk:
                return (self.MaxThread, ceil(self.MaxChunk/float(self.MaxThread)))
            else:
                t = ceil(len(l)/float(self.MinChunk))
                return (t, ceil(len(l)/float(t)))


    def chunk(self, l, chunk_size):
        """
           @param: l - list
           @return: list of resource and sets the amount of parallel requests
        """
        for i in xrange(0, len(l), chunk_size):
            yield l[i:i+chunk_size]


    def fetch(self, session, name, resource_list, path=None):
        """
            Requests the feature server to calculate provided resources.
            The request will be boken up according to the chunk size
            and made in parallel depending on the amount of threads.

            @param: session - the local session
            @param: name - the name of the feature one wishes to extract
            @param: resource_list - list of the resources to extract. format: [(image_url, mask_url, gobject_url),...] if a parameter is
            not required just provided None
            @param: path - the location were the hdf5 file is stored. If None is set the file will be placed in a tempfile and the pytables
            file handle will be returned. (default: None)

            @return: returns either a pytables file handle or the file name when the path is provided
        """
        if len(resource_list) < 1:
            log.warning('Warning no resources were provided')
            return

        log.debug('Exctracting %s on %s resources'%(name,len(resource_list)))

        if path is None:
            f = tempfile.TemporaryFile(suffix='.h5', dir=tempfile.gettempdir())
            f.close()
            table_path = f.name
        else:
            table_path = path

        stop_write_thread = False #sets a flag to stop the write thread
        # when the requests threads have finished

        class WriteHDF5Thread(Thread):
            """
                Copies small hdf5 feature tables
                into one large hdf5 feature table
            """

            def __init__(self, h5_filename_queue):
                """
                    param h5_filename_queue: a queue of temporary hdf5 files
                """
                self.h5_filename_queue = h5_filename_queue
                tables.open_file(table_path, 'w').close() #creates a new file
                super(WriteHDF5Thread, self).__init__()

            def run(self):
                """
                    While queue is not empty and stop_write_thread
                    has not been set to true, the thread will open
                    temporary hdf5 tables and copy them into the
                    main hdf5 table and then delete the temporary file.
                """
                while True:
                    if not self.h5_filename_queue.empty():
                        temp_path = self.h5_filename_queue.get()
                        log.debug('Writing %s to %s' % (temp_path, table_path))
                        try:
                            with tables.open_file(temp_path, 'a') as hdf5temp:
                                with tables.open_file(table_path, 'a') as hdf5:
                                    temp_table = hdf5temp.root.values
                                    temp_status_table = hdf5temp.root.status
                                    if not hasattr(hdf5.root, 'values'):
                                        temp_table.copy(hdf5.root,'values')
                                        temp_status_table.copy(hdf5.root,'status')
                                    else:
                                        table = hdf5.root.values
                                        status_table = hdf5.root.status
                                        table.append(temp_table[:])
                                        status_table.append(temp_status_table[:])
                                        table.flush()
                                        status_table.flush()
                        except StandardError as e:
                            log.exception('Could not read hdf5 file')
                        finally:
                            log.debug('Clean up: removing %s' % temp_path)
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

                    if stop_write_thread is True:
                        log.debug('Ending HDF5 write thread')
                        break

        write_queue = Queue.Queue()
        request_queue = Queue.Queue()

        def request_factory(partial_resource_list):
            def request():
                f = tempfile.NamedTemporaryFile(suffix='.h5', dir=tempfile.gettempdir(), delete=False)
                f.close()
                attempts = 0
                while True:
                    try:
                        path = super(ParallelFeature, self).fetch(session, name, partial_resource_list, path=f.name)
                    except socket.error as e: #if connection fails
                        if attempts>MAX_ATTEMPTS:
                            log.debug('Connection fail: Reached max attempts')
                            break
                        if e.errno == errno.WSAECONNRESET: #pylint: disable=no-member
                            attempts+=1
                            log.debug('Connection fail: Attempting to reconnect (try: %s)' % attempts)
                    try:
                        tables.is_pytables_file(path)
                    except tables.HDF5ExtError: #if fail gets corrupts during download
                        if attempts>MAX_ATTEMPTS:
                            log.debug('Failed to open hdf5 file: Reached max attempts')
                            break
                        attempts+=1
                        log.debug('HDF5 file may be corrupted: Attempted to redownload (try: %s)' % attempts)
                        if os.path.exists(path):
                            os.remove(path)

                    write_queue.put(path)
                    break

            return request

        if hasattr(self,'thread_num') and hasattr(self,'chunk_size'):
            thread_num = ceil(self.thread_num)
            chunk_size = ceil(self.chunk_size)

            if thread_num <= 0: thread_num = 1
            if chunk_size <= 0: chunk_size = 1

        else:
            thread_num, chunk_size = self.calculate_request_plan(resource_list)

        for partial_resource_list in self.chunk(resource_list, int(chunk_size)):
            request_queue.put(request_factory(partial_resource_list))

        w = WriteHDF5Thread(write_queue)
        log.debug('Starting HDF5 write thread')
        w.daemon = True
        w.start()

        self.request_thread_pool(request_queue, errorcb=self.errorcb, thread_count=int(thread_num))
        stop_write_thread = True
        w.join()

        log.debug('Returning parallel feature response to %s' % table_path)

        if path is None:
            return tables.open_file(table_path, 'r')
        else:
            return table_path

    def errorcb(self, e):
        """
            Returns an error log
        """
        log.warning('%s'%str(e))


    def fetch_vector(self, session, name, resource_list):
        """
            Requests the feature server to calculate provided resources.
            The request will be boken up according to the chunk size
            and made in parallel depending on the amount of threads.

            @param: session - the local session
            @param: name - the name of the feature one wishes to extract
            @param: resource_list - list of the resources to extract. format:
            [(image_url, mask_url, gobject_url),...] if a parameter is
            not required just provided None

            @return: a list of features as numpy array
        """
        return super(ParallelFeature, self).fetch_vector(session, name, resource_list)
