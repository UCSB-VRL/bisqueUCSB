# -*- mode: python -*-
"""Main server for features
"""

__author__ = "Dmitry Fedorov, Kris Kvilekval, Carlos Torres and Chris Wheat"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import os
import logging
import pkg_resources
import tables
import urllib
from PytablesMonkeyPatch import pytables_fix
import inspect
import pkgutil
import Queue
import importlib
import urlparse
import hashlib
import uuid
from lxml import etree
import traceback
from collections import namedtuple
from paste.fileapp import FileApp
from pylons.controllers.util import forward
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons.controllers.util import abort
from tg import expose, flash, config, response, request
from bq.core.service import ServiceController
from bq.util.locks import Locks
from bq.util.mkdir import _mkdir
from bq.features.controllers.ID import ID
from bq.features.controllers.Feature import BaseFeature
from bq.features.controllers.utils import mex_validation
from bq.features.controllers.TablesInterface import CachedRows, WorkDirRows, CachedTables, WorkDirTable, QueryPlan
from bq.features.controllers.var import FEATURES_TABLES_FILE_DIR, EXTRACTOR_DIR, FEATURES_WORK_DIR

from exceptions import FeatureServiceError,FeatureExtractionError, FeatureImportError, InvalidResourceError

FeatureResource = namedtuple('FeatureResource',['image','mask','gobject'])
FeatureResource.__new__.__defaults__ = ('', '', '')

ResourceRequest = namedtuple('ResourceRequest', ['feature_resource','exception'])
ResourceRequest.__new__.__defaults__ = (FeatureResource, None)


log = logging.getLogger("bq.features")


class Feature_Archive(dict):
    """
        List of included descriptors:
        SURF, ORB, SIFT, HTD, EHD, CLD, CSD, SCD, DCD
        FREAK, BRISK, TAS, PFTAS, ZM, HAR, FFTSD
        RSD, many more...
    """
    def __init__(self):
        """
            Looks into extractors/feature_module for extractor. Once found
            it will import the library and parse the module for all classes
            inheriting FeatureBase
        """
        extractors = [name for module_loader, name, ispkg in pkgutil.iter_modules([EXTRACTOR_DIR]) if ispkg]
        for module in extractors:
            try:
                extractor = importlib.import_module('bq.features.controllers.extractors.' + module + '.extractor')  # the module needs to have a file named
                for n, item in inspect.getmembers(extractor):  # extractor.py to import correctly
                    if inspect.isclass(item) and issubclass(item, BaseFeature) and item.disabled==False:
                        #log.debug('Imported Feature: %s' % item.name)
                        item.library = module #for the list of features
                        self[item.name] = item

            except FeatureImportError, e:
                log.warning('Failed to import: %s reason %s ', module, e)
                #log.debug('Failed to import: %s\n%s'%(module, traceback.format_exc()))
                continue

            except StandardError, e:  # need to pick a narrower error band but not quite sure right now
                log.warning('Failed to import: %s reason %s ', module, e)
                #log.debug('Failed to import: %s\n%s'%(module, traceback.format_exc()))
                continue
        log.debug("Imported Features: %s", self.keys())


FEATURE_ARCHIVE = Feature_Archive()

###############################################################
# Features Inputs
###############################################################

class ResourceList(object):
    """
        list of all unique elements and their hashes
        sorted by hashes
    """
    def __init__(self, feature_name, format_name, **kw):
        self.resource_list = {}
        self.exception_list = []

        try:
            self.format = FORMAT_DICT[format_name]
        except KeyError:
            #through an exception to be picked up by the main try block
            raise FeatureServiceError(404, 'Format: %s  was not found' % format_name)

        try:
            self.feature = FEATURE_ARCHIVE[feature_name]
        except KeyError:
            #through an exception to be picked up by the main try block
            raise FeatureServiceError(404, 'Feature: %s requested was not found' % feature_name)


    def hash_response(self):
        """
            Hashes all the resources together in order with
            their status along with the feature being
            extracted.
            Form: feature name::resource hash:status;resource hash:...;
        """
        m = hashlib.md5()
        m.update('%s::'%self.feature.name)
        for resource_hash in self.resource_list:
            feature_resource, exc = self.resource_list[resource_hash]
            if exc is None:
                status = '200'
            else:
                status = str(exc.code)
            m.update('%s:%s;'%(resource_hash, status))
        return m.hexdigest()

    def check_response_in_workdir(self):
        """
            Checks the workdir to see if the
            current response is already there
        """
        return os.path.exists(self.path_in_workdir())

    def path_in_workdir(self):
        """
            Returns path to a response in the workdir
        """
        filename = self.hash_response()
        return os.path.join(FEATURES_WORK_DIR, self.feature.name, filename[0], '%s.h5' % filename)

    def append(self, resource):
        """
            appends to element lists and orders the list by hash
            on the first append the types are checked

            @input_dict : dictionary where the keys are the input types and the values are the uris
        """
        exception = None

        try: #check if user has access to resource
            resource = mex_validation(resource)
        except InvalidResourceError as e:
            exception = FeatureExtractionError(resource, e.code, e.message)

        resource_hash = self.feature.hash_resource(resource) #the hash will change if redirects
        if resource_hash not in self.resource_list:
            self.resource_list[resource_hash] = ResourceRequest(feature_resource=resource, exception=exception)

    def add_exc(self, resource_hash, exception):
        """
            Adds an exception onto a ResourceRequest. The perfored exception is FeatureExtractionError

            @param: resource_hash - the hash of the FeatureResource
            @param: exception - FeatureExtractionError

            @returns: bool - False if resource is not found or True otherwise
        """
        resource_request = self.get(resource_hash)[1]
        if resource_request is None:
            return False
        else:
            self.resource_list[resource_hash] = ResourceRequest(feature_resource=resource_request, exception=exception)
            return True

    def get(self, resource_hash):
        """
            Looks up a resource hash in the list of resources and return the resource

            @param: resource_hash - the hash of the FeatureResource
            @return: (resource_hash, ResourceRequest), if not found returns None
        """
        if resource_hash in self.resource_list:
            resource_request = self.resource_list[resource_hash]
            return (resource_hash, resource_request)
        else:
            return

    def create_query_plan(self, feature):
        """
            returns an organized query queue with all the resources in resource
            list by the first few hash elements
        """
        query_plan = QueryPlan(feature)
        for hash in self.resource_list:
            query_plan.push(hash)
        return query_plan

    def __getitem__(self, index):
        """get with index, the list is always ordered """
        resource_hash = sorted(self.resource_list.keys())[index]
        resource_request = self.resource_list[resource_hash]
        return (resource_hash, resource_request.feature_resource, resource_request.exception)

    def __len__(self):
        return len(self.resource_list)

    def __iter__(self):
        """returns an ordered list of the hashes"""
        return iter(sorted(self.resource_list.keys()))


def clean_url(url):
    """
        If a quote is found that the beginning of the url
        remove both quotes from the beginning and end of
        the url, also checks if the urls are strings
        @param: url -

        @return: url without quotes
    """
    if isinstance(url, list):
        if len(url)==1:
            url = url[0]
        else:
            raise FeatureServiceError(400, 'Request Error: Only one resource per resource type')

    if url is None:
        return url
    if url.startswith('"'):
        url = url[1:]
        if url.endswith('"'):
            url = url[:-1]
    url = urllib.unquote(url)
    return url


def parse_request(feature_name, format_name='xml', method='GET', **kw):
    """
        Parses request, constructs and returns a ResourceList

        @param: feature_name - (ex. HTD, EHD,...)
        @param: format_name - (ex. xml, csv, hdf)(default: xml)
        @param: method - method of the requests (default: GET)
        @param: kw - query of the url

        @return: ResourceList
    """
    resource_list = ResourceList(feature_name, format_name)

    # validating request
    if method=='POST' and 1>request.headers['Content-type'].count('xml/text'):
        if not request.body:
            raise FeatureServiceError(400, 'Document Error: No body attached to the POST')
        try:
            #log.debug('body : %s'% request.body)
            body = etree.fromstring(request.body)
        except etree.XMLSyntaxError:
            raise FeatureServiceError(400, 'Document Error: document was not formatted correctly')

        def append_resource_list(feature_node):
            uri = feature_node.attrib.get('uri')
            if uri is None: #protect against malformed xml
                return
            o = urlparse.urlparse(uri)
            path = o.path
            query = urlparse.parse_qs(o.query)
            resource = FeatureResource(image=clean_url(query.get('image','')),
                                       mask=clean_url(query.get('mask','')),
                                       gobject=clean_url(query.get('gobject','')))
            if tuple(resource) != ('', '', ''): #skip nodes with nothing in them
                log.debug('Resource: %s'%str(resource))
                resource_list.append(resource)

        if body.tag == 'resource':
            # iterating through elements in the dataset parsing and adding to ElementList
            for feature_node in body.xpath('feature'):
                append_resource_list(feature_node)

        elif body.tag == 'feature':
            append_resource_list(body)

        else:
            raise FeatureServiceError(400, 'Document Error: document was not formatted correctly')

        if len(resource_list)<1: #checks to see if no resourses are there or the format was not proper resulting in no elements
            raise FeatureServiceError(400, 'No resources were found!')

    elif method == 'GET':
        resource = FeatureResource(image=clean_url(kw.get('image', '')),
                                   mask=clean_url(kw.get('mask', '')),
                                   gobject=clean_url(kw.get('gobject', '')))
        if resource == ('', '', ''):
            raise FeatureServiceError(400, 'Request Error: No excepted resources were provided')
        resource_list.append(resource)

    else:
        log.debug('Request Error: http request was not formed correctly')
        raise FeatureServiceError(400, 'http request was not formed correctly')

    return resource_list


def operations(resource_list):
    """
        Performs the bulk of the work in the feature service.
        Makes requests to the table for calculations and performs
        the feature calculations error handling

        If a feature has been set to cache the feature will be stored
        in the features cache tables otherwise the requests will be
        constructed directly in the workdir

        Also if a request has been found to be be calculated already and
        saved in the workdir, this function will be skipped.

        @resource_list - a ResourceList object constaining the list
        of resources for feature calculations
    """
    feature = resource_list.feature()
    if resource_list.check_response_in_workdir() is False: #skip to format reponse if true
        if feature.cache is True: #checks if the feature caches
            table_list = [CachedTables(feature), CachedTables(ID())]
            Rows = CachedRows
        else:
            table_list = [WorkDirTable(feature)]
            Rows = WorkDirRows

        for table in table_list:
            query_plan = resource_list.create_query_plan(table.feature)
            rows = Rows(table.feature)
            for results in table.find(query_plan):
                for (row_exists, id) in results:
                    _id, request_resource = resource_list.get(id)
                    if row_exists is True:
                        log.debug("Returning Resource: %s from cache" % str(request_resource.feature_resource))
                    else:
                        log.debug("Resource: %s was not found in the table" % str(request_resource.feature_resource))
                        try:
                            rows.push(request_resource)
                        except FeatureExtractionError as feature_extractor_error: #if error occured the exception is added to the resource
                            if not resource_list.add_exc(id, feature_extractor_error):
                                log.debug('Exception: Resource ID: %s not found' % (str(id)))
                                raise FeatureServiceError(500, 'Resource hash was not found')
                            log.debug('Exception: Error Code %s : Error Message %s' % (str(feature_extractor_error.code), feature_extractor_error.message))


            table.set_path(resource_list.path_in_workdir())

            # store features
            table.store(rows)


def format_response(resource_list):
    """
        Formats and returns a response in the format specified.
        If a response has been found to be stored in the workdir
        the response will be read for the workdir otherwise the
        response will be constructed for features in the cached
        table of the feature service

        @resource_list - a ResourceList object constaining the list
        of resources to be returned

        @return: header - a dictionary of parameters provided in
        the header for a particular format
        @return: body - the body of the requests, can either
        be an iter, string document or a forward FileApp
    """
    feature = resource_list.feature()
    format = resource_list.format(feature)

    if resource_list.check_response_in_workdir() is False:
        table = CachedTables(feature) # queries for results in the feature tables
        body = format.return_from_tables(table, resource_list)
    else:
        table = WorkDirTable(feature).set_path(resource_list.path_in_workdir()) #returns unindexed table from the workdir
        body = format.return_from_workdir(table, resource_list)

    header = format.return_header()
    return header, body


###############################################################
# Features Outputs
###############################################################
class Format(object):
    """
        Base Class of formats for output
    """
    name = 'Format'
    #limit = 'Unlimited'
    description = 'Discription of the Format'
    content_type = 'text/xml'
    ext = None

    def __init__(self, feature):
        self.feature = feature

    @staticmethod
    def _make_uri(feature, resource):
        """
            Constructs a url for a feature request

            @param: feature - feature object provides feature
            information
            @resource - a FeatureResource containing url resource for
            one request
        """
        query = []
        if resource.image: query.append('image=%s' % resource.image)
        if resource.mask: query.append('mask=%s' % resource.mask)
        if resource.gobject: query.append('gobject=%s' % resource.gobject)
        query = '&'.join(query)
        return '%s://%s/features/%s/xml?%s'%(request.scheme,request.host,feature.name,query)

    def return_header(self):
        """
            returns a dictionary of parameters
            provided in the header for a particular
            format
        """
        return {'Content-Type': self.content_type}

    def _construct_from_cache(self, table, resource_list, feature):
        """
            Formats a response for a feature from the feature cache
            tables containing the requests provided in the resources list

            @param: table - cached table object that allows access
            to the cached tables in the feature service
            @param: resource_list - the resource lists object containing
            all the resources proccessed on during the request
            @param: feature - the feature module containing info about
            each specific feature

            @yield: rows of a request
        """
        # pylint: disable=no-member
        idx = 0
        query_plan = resource_list.create_query_plan(feature)
        for query in table.get(query_plan):
            for rows, hash in query:
                (hash, request_resource) = resource_list.get(hash)
                (resource, error) = request_resource
                if error is None:
                    if rows is not None:  # a feature was found for the query
                        for r in rows:
                            yield self.construct_row(idx, self.feature, resource, r)
                        idx += 1
                    else:  # no feature was found from the query, adds an error message to the CSV
                        yield self.construct_error_row(idx, self.feature, FeatureExtractionError(resource, 404, 'The feature was not found in the table.'))
                        idx += 1
                else:
                    yield self.construct_error_row(idx, self.feature, error)
                    idx += 1

    def _construct_from_workdir(self, table, resource_list, feature):
        """
            Formats a response for a feature from a feature workir
            table containing the requests provided in the resources list

            @param table - workdir table object that allows access
            to the workdir table created by the feature service
            @param: resource_list - the resource lists object containing
            all the resources proccessed on during the request
            @param: feature - the feature module containing info about
            each specific feature

            @yield: rows of a request
        """
        # pylint: disable=no-member
        idx = 0
        for (row, status) in table.get():
            resource = FeatureResource(image=row['image'], mask=row['mask'], gobject=row['gobject'])
            if status['status']==200:
                yield self.construct_row(idx, feature, resource, row)
                idx += 1
            else:
                yield self.construct_error_row(idx, feature, FeatureExtractionError(resource, status['status'], 'An error occured during feature extraction'))
                idx += 1


#-------------------------------------------------------------
# Formatters - XML
# MIME types:
#   text/xml
#-------------------------------------------------------------
class Xml(Format):
    """
        Handles responses in XML and provides
        info about XML responses
    """
    name = 'XML'
    description = 'Extensible Markup Language'
    content_type = 'text/xml'

    @staticmethod
    def construct_row(idx, feature, resource, row):
        """
            Formats a response in xml which has returned
            the feature

            @param: feature - feature object provided informtion for
            the construction of the row for a specific feature
            @param: resource - a FeatureResource containing the uri of
            the request
            @param: row - a pytable row element from either
            a cached table or workdir table
        """
        uri = Xml._make_uri(feature, resource)
        subelement = etree.Element('feature', uri=uri, type=str(feature.name), value= ",".join('%g' % item for item in row['feature']))
        if feature.parameter:
            # creates list of parameters to append to the xml
            for parameter_name in feature.parameter:
                etree.SubElement(subelement, 'tag', name=parameter_name, value=str(row[parameter_name]))
        return subelement

    @staticmethod
    def construct_error_row(idx, feature, error):
        """
            Formats a response in xml which has returned
            an error in the feature service

            @param: idx - the index of the specific node
            @param: feature - feature object provided informtion for
            the construction of the row for a specific feature
            @param: error -  a FeatureExtractionError object returning
            info about the resource and the exception that occured

            @yield: etree xml node
        """
        uri = Xml._make_uri(feature, error.resource)
        subelement = etree.Element('feature',uri=uri, type=str(feature.name))
        etree.SubElement(subelement, 'tag', name='error', value='%s:%s'%(str(error.code), error.message))
        return subelement

    def return_from_tables(self, table, resource_list):
        """
            Wrties the output as xml. If only one nodes is returned
            from _construct_from_cache the root node will be named
            feature else the root not will be named resource

            @param: table - cached table object that allows access
            to the cached tables in the feature service
            @param: resource_list - the resource lists object containing
            all the resources proccessed on during the request

            @yield: nodes of xml
        """
        node_gen = self._construct_from_cache(table, resource_list, self.feature)

        try:
            node_one = next(node_gen)
        except StopIteration: #no elements
            pass
        try:
            node_two = next(node_gen)
            #there is more than one node
            yield '<resource uri = "%s">'%str(request.url.replace('&','&amp;'))
            yield etree.tostring(node_one)
            yield etree.tostring(node_two)
        except StopIteration: #no elements
            #only one node
            yield etree.tostring(node_one)
        else:
            #yield the rest of the nodes
            for n in node_gen:
                yield etree.tostring(n)
            yield '</resource>'

    def return_from_workdir(self, table, resource_list):
        """
            Translates workdir response table to xml. If only one nodes
            is returned from _construct_from_workdir the root node will
            be named feature else the root not will be named resource

            @param: table - workdir table object that allows access
            to the workdir table created by the feature service
            @param: resource_list - the resource lists object containing
            all the resources proccessed on during the request

            @yield: nodes of xml
        """
        node_gen = self._construct_from_workdir(table, resource_list, self.feature)
        try:
            node_one = next(node_gen)
        except StopIteration: #no elements
            pass

        try:
            node_two = next(node_gen)
            #there is more than one node
            yield '<resource uri = "%s">'%str(request.url.replace('&','&amp;'))
            yield etree.tostring(node_one)
            yield etree.tostring(node_two)
        except StopIteration: #no elements
            #only one node
            yield etree.tostring(node_one)
        else:
            #yield the rest of the nodes
            for n in node_gen:
                yield etree.tostring(n)
            yield '</resource>'

#-------------------------------------------------------------
# Formatters - CSV
# MIME types:
#   text/csv
#   text/comma-separated-values
#-------------------------------------------------------------
class Csv(Format):
    """
        Handles responses in CSV and provides
        info about CSV responses
    """
    name = 'CSV'
    description = 'Returns csv file format with columns as resource ... | feature | feature attributes...'
    content_type = 'text/csv'
    ext = '.csv'


    @staticmethod
    def construct_row(idx, feature, resource, row):
        """
            Formats a response in csv which has returned
            the feature

            @param: feature - feature object provided informtion for
            the construction of the row for a specific feature
            @param: resource - a FeatureResource containing the uri of
            the request
            @param: row - a pytable row element from either
            a cached table or workdir table

            @yield: csv row string
        """
        value_string = ",".join('%g' % i for i in row['feature'])  # parses the table output and returns a string of the vector separated by commas
        resource_uris = [resource.image or '', resource.mask or '', resource.gobject or '']
        parameter = ['%s'%str(row[pn]) for pn in feature.parameter]
        line = str("%s%s"%(",".join([str(idx), feature.name] + resource_uris + ['"%s"'%value_string] + parameter + ['']),os.linesep))
        return line

    @staticmethod
    def construct_error_row(idx, feature, error):
        """
            Formats a response in csv which has returned
            an error in the feature service

            @param: idx - the index of the specific node
            @param: feature - feature object provided informtion for
            the construction of the row for a specific feature
            @param: error -  a FeatureExtractionError object returning
            info about the resource and the exception that occured

            @yield: csv row string
        """
        resource = error.resource
        resource_uris = [resource.image or '', resource.mask or '', resource.gobject or '']
        parameter = ['' for pn in feature.parameter]
        line = str("%s%s"%(",".join([str(idx), feature.name] + resource_uris + ['']  +  parameter + ['%s:%s'%(str(error.code),str(error.message))]),os.linesep))
        return line

    def return_header(self):
        """
            @return: csv headers
        """
        # creating a file name
        filename = 'feature.csv'# uuid.uuid4().hex  # think of how to name the files
        try:
            disposition = 'attachment; filename="%s"' % filename.encode('ascii')
        except UnicodeEncodeError:
            disposition = 'attachment; filename="%s"; filename*="%s"' % (filename.encode('utf8'), filename.encode('utf8'))
        return {'Content-Type': self.content_type, 'Content-Disposition':disposition}

    def return_from_tables(self, table, resource_list):
        """
            Wrties the output as csv.

            @param: table - cached table object that allows access
            to the cached tables in the feature service
            @param: resource_list - the resource lists object containing
            all the resources proccessed on during the request

            @yield: csv row string
        """
        resource_names = ['image','mask','gobject']#self.feature.resource
        # creates a title row and writes it to the document
        yield str("%s%s"%(",".join(['index', 'feature type'] + resource_names + ['feature'] + self.feature.parameter + ['error']),os.linesep))
        for r in self._construct_from_cache(table, resource_list, self.feature):
            yield r

    def return_from_workdir(self, table, resource_list):
        """
            Translates workdir response table to csv.

            @param: table - workdir table object that allows access
            to the workdir table created by the feature service
            @param: resource_list - the resource lists object containing
            all the resources proccessed on during the request

            @yield: csv row string
        """
        resource_names = ['image','mask','gobject']
        # creates a title row and writes it to the document
        yield str("%s%s"%(",".join(['index', 'feature type'] + resource_names + ['feature'] + self.feature.parameter + ['error']),os.linesep))
        for r in self._construct_from_workdir(table, resource_list, self.feature):
            yield r


#-------------------------------------------------------------
# Formatters - Hierarchical Data Format 5
# MIME types:
#   text
#-------------------------------------------------------------
class Hdf(Format):
    """
        Constructs a workdir table for the features
        requested and responses
    """
    name = 'HDF'
    description = 'Returns HDF5 file with columns as resource ... | feature | feature attributes...'
    content_type = 'application/hdf5'
    ext = '.h5'

    @staticmethod
    def construct_row(idx, feature, resoure, row):
        """
            Returns rows from an hdf5 table

            @param: feature - feature object provided informtion for
            the construction of the row for a specific feature
            @param: resource - a FeatureResource containing the uri of
            the request
            @param: row - a pytable row element from either
            a cached table or workdir table

            @return: feature rows and a status rows to be place into hdf5 table
        """
        return WorkDirRows(feature).construct_row(feature, resoure, row)


    @staticmethod
    def construct_error_row(idx, feature, error):
        """
            Constructs and hdf5 row for a feature
            which has returned an error in the feature service

            @param: idx - the index of the specific node
            @param: feature - feature object provided informtion for
            the construction of the row for a specific feature
            @param: error -  a FeatureExtractionError object returning
            info about the resource and the exception that occured

            @return: feature rows and a status rows to be place into hdf5 table
        """
        return WorkDirRows(feature).construct_error_row(feature, error)


    def return_from_tables(self, table, resource_list):
        """
            Builds and hdf5 table in the workdir and then
            returns that table form the workdir

            @param: table - cached table object that allows access
            to the cached tables in the feature service
            @param: resource_list - the resource lists object containing
            all the resources proccessed on during the request

            @returns: return_from_workdir(workdir_feature_table, resource_list)
        """
        row_list = []
        status_list = []

        for (feature, status) in self._construct_from_cache(table, resource_list, self.feature):
            row_list.append(feature)
            status_list.append(status)

        #writing the output to an uncached table
        workdir_feature_table = WorkDirTable(self.feature).set_path(resource_list.path_in_workdir())
        workdir_rows = WorkDirRows(self.feature)
        workdir_rows.row_queue['feature'] = Queue.Queue()
        workdir_rows.row_queue['feature'].put((row_list,status_list))
        workdir_feature_table.store(workdir_rows)
        return self.return_from_workdir(workdir_feature_table, resource_list)


    def return_from_workdir(self, table, resource_list):
        """
            Returns a hdf5 file from the workdir

            @param: table - workdir table object that allows access
            to the workdir table created by the feature service
            @param: resource_list - the resource lists object containing
            all the resources proccessed on during the request

            @yield: fileapp object with path set to the hdf5 file in
            the feature workdir
        """
        # since the uncached table is already saved in the workdir the file is just
        # returned
        try:
            disposition = 'attachment; filename="%s"' % (table.filename).encode('ascii')
        except UnicodeEncodeError:
            disposition = 'attachment; filename="%s"; filename*="%s"' % ((table.filename).encode('utf8'), (table.filename).encode('utf8'))

        #waits table that is being constructed
        with Locks(table.path):
            pass

        return forward(FileApp(table.path, allowed_methods=('GET','POST'), content_type=self.content_type, content_disposition=disposition))


#-------------------------------------------------------------
# Formatters - No Ouptut
# MIME types:
#   text/xml
#-------------------------------------------------------------
class NoOutput(Format):
    name = 'No Output'
    description = 'Has no body attached to the response'
    content_type = None


#-------------------------------------------------------------
# Formatters - Numpy
# Only for internal use
#-------------------------------------------------------------
class NumPy(Format):
    """
    """
    name = 'numpy'
    description = 'Returns numpy arrays for features'
    content_type = None

    def return_from_tables(self, table, element_list, **kw):
        query_queue = element_list.get_query_queue()
        numpy_response = []
        for query in table.get(query_queue):
            for results in query:
                numpy_response.append(results[0])
        return numpy_response


#-------------------------------------------------------------
# Formatters - LocalPath
# Only for internal use
#-------------------------------------------------------------
class LocalPath(Format):
    """
    """
    name = 'localpath'
    description = 'returns the path and the hash were a feature is stored'
    content_type = None

    def return_from_tables(self, table, element_list, **kw):
        localpath = []
        for hash in element_list:
            localpath.append((os.path.join(table.get_path(),hash[:self.feature.hash]),hash))
        return localpath

    def return_from_workdir(self, table, filename, **kw):
        pass


FORMAT_DICT = {
    'xml'      : Xml,
    'csv'      : Csv,
    'hdf'      : Hdf,
    'none'     : NoOutput,
    #'localpath': LocalPath
}


###################################################################
# ##  Documentation
###################################################################

class FeatureDoc():
    """
    Feature Documentation Class is to organize the documention for
    the feature server
    (it will always output in xml)
    """
    def __init__(self):
        pass

    def feature_server(self):
        """
            Returns xml of the commands allowed on the feature server
        """
        resource = etree.Element('resource', uri=str(request.url))
        command  = etree.SubElement(resource, 'command', name='FEATURE_NAME', value='Documentation of specific feature')
        command  = etree.SubElement(resource, 'command', name='list', value='List of available features')
        command  = etree.SubElement(resource, 'command', name='formats', value='List of output formats')
        command  = etree.SubElement(resource, 'command', name='format/FORMAT_NAME', value='Documentation of specific format')
        command  = etree.SubElement(resource, 'command', name='/FEATURE_NAME/FORMAT_NAME?image|mask|gobject=URL[&image|mask|gobject=URL]', value='Returns feature in format specified')
        command  = etree.SubElement(resource, 'attribute', name='resource', value='The name of the resource depends on the requested feature')
        return etree.tostring(resource)


    def feature_list(self):
        """
            Returns xml of given feature
        """
        resource = etree.Element('resource', uri=str(request.url))
        resource.attrib['description'] = 'List of working feature extractors'
        feature_library = {}
        for featuretype in FEATURE_ARCHIVE.keys():
            feature_module = FEATURE_ARCHIVE[featuretype]

            if feature_module.library not in feature_library:
                feature_library[feature_module.library] = etree.SubElement(resource, 'library', name=feature_module.library)

            feature = etree.SubElement(
                                  feature_library[feature_module.library],
                                  'feature',
                                  name=featuretype,
                                  permission="Published",
                                  uri='/features/%s' % featuretype
            )

        return etree.tostring(resource)


    def feature(self, feature_name):
        """
            Returns xml of information about the features
        """
        try:
            feature_module = FEATURE_ARCHIVE[feature_name]
        except KeyError:
            #through an exception to be picked up by the main try block
            raise FeatureServiceError(404, 'Feature: %s requested was not found'%feature_name)

        feature_module = feature_module()
        #Table = Tables(feature_module)
        xml_attributes = {
                          'description':str(feature_module.description),
                          'feature_length':str(feature_module.length),
                          'required_resources': ','.join(feature_module.resource),
                          'cache': str(feature_module.cache),
                          'confidence': str(feature_module.confidence)
                          #'table_length':str(len(Table)) this request takes a very long time in the current state
                         }
        if len(feature_module.parameter) > 0:
            xml_attributes['parameters'] = ','.join(feature_module.parameter)
        if feature_module.additional_resource is not None:
            xml_attributes['additional_resource'] = ','.join(feature_module.additional_resource)

        resource = etree.Element('resource', uri=str(request.url))
        feature = etree.SubElement(resource, 'feature', name=str(feature_module.name))

        for key, value in xml_attributes.iteritems():
            info = etree.SubElement(feature, 'tag', name=key, value=value)
        return etree.tostring(resource)


        return etree.tostring(resource)

    def format_list(self):
        """
            Returns List of Formats
        """
        resource = etree.Element('resource', uri=str(request.url))
        resource.attrib['description'] = 'List of Return Formats'
        for format_name in FORMAT_DICT.keys():
            format = FORMAT_DICT[format_name]
            feature = etree.SubElement(resource,
                                      'format',
                                      name=format_name,
                                      permission="Published",
                                      uri='format/%s' % format_name)
        response.headers['Content-Type'] = 'text/xml'
        return etree.tostring(resource)

    def format(self, format_name):
        """
            Returns documentation about format
        """
        try:
            format = FORMAT_DICT[format_name]
        except KeyError:
            #through an exception to be picked up by the main try block
            raise FeatureServiceError(404, 'Format: %s  was not found'%format_name)

        xml_attributes = {
                          'Name':str(format.name),
                          'Description':str(format.description),
                          'content_type': str(format.content_type)
                          }

        resource = etree.Element('resource', uri=str(request.url))
        feature = etree.SubElement(resource, 'format', name=str(format.name))

        for key, value in xml_attributes.iteritems():
            info = etree.SubElement(feature, 'tag', name=key, value=value)
        return etree.tostring(resource)

###################################################################
# ## Feature Service Controller
###################################################################

class featuresController(ServiceController):

    service_type = "features"

    def __init__(self, server_url):
        super(featuresController, self).__init__(server_url)
        self.baseurl = server_url
        _mkdir(FEATURES_TABLES_FILE_DIR)

        log.debug('importing features')
        self.docs = FeatureDoc()

    ###################################################################
    # ## Feature Service Entry Points
    ###################################################################
    @expose()
    def _default(self, *args, **kw):
        """
            Entry point for features calculation and command and feature documentation
        """
        # documentation
        log.info('%s : %s'%(request.method, request.url))

        if not args and request.method =='GET':
            body = self.docs.feature_server()  #print documentation
            header = {'Content-Type': 'text/xml'}
            log.info('Content-Type: %s  Returning Feature List'%(header['Content-Type']))
        elif len(args) == 1 and request.method =='GET' and not kw:
            try:
                body = self.docs.feature(args[0])
                header = {'Content-Type':'text/xml'}
                log.info('Content-Type: %s Returning Feature Info: %s'%(header['Content-Type'], args[0]))

            except FeatureServiceError as e:
                log.error('%s' % str(e))
                abort(e.error_code, e.error_message)

        # calculating features
        elif len(args) == 2:
            try:
                resource_list = parse_request(args[0], args[1], request.method, **kw)
                operations(resource_list)
                header, body = format_response(resource_list)
                log.info('Content Type: %s  Returning Feature: %s'%(header['Content-Type'],args[0]))

            except FeatureServiceError as e:
                log.error('%s' % str(e))
                abort(e.error_code, e.error_message)

        else:
            log.error('Malformed Request: Not a valid features request')
            abort(400, 'Malformed Request: Not a valid features request')

        response.headers.update(header)
        log.info('Response HEADERS: %s' % response.headers)
        return body


    @expose()
    def format(self,*args):
        """
            entry point for format documentation
        """
        return self.formats(*args)


    @expose()
    def formats(self, *args):
        """
            entry point for format documentation
        """
        log.info('%s : %s'%(request.method, request.url))
        if request.method == 'GET':
            if len(args) < 1: #returning list of useable formats
                body = self.docs.format_list()
                header = {'Content-Type': 'text/xml'}
                log.info('Content Type: %s  Returning Format Type List' % (header['Content-Type']))

            elif len(args) < 2: #returining info on specific format
                try:
                    body = self.docs.format(args[0])
                    header = {'Content-Type':'text/xml'}
                    log.info('Content-Type: %s  Returning Format Type: %s' % (header['Content-Type'], args[0]))

                except FeatureServiceError as e:
                    log.error('%s' % str(e))
                    abort(e.error_code, e.error_message)
            else:
                log.error('Malformed Request: Not a valid features request')
                abort(400, 'Malformed Request: Not a valid features request')

            response.headers.update(header)
            return body

        else:
            log.error('Malformed Request: Not a valid features request only excepts GET method')
            abort(400, 'Malformed Request: Not a valid features request only excepts GET method')


    @expose()
    def list(self):
        """
            entry point for list of features
        """
        log.info('%s : %s'%(request.method, request.url))
        if request.method == 'GET':
            header = {'Content-Type': 'text/xml'}
            response.headers.update(header)
            feature_list = self.docs.feature_list()
            log.info('Content Type:%s  Returning Feature List' % header['Content-Type'])
            return feature_list
        else:
            log.error('Malformed Request: Not a valid features request only excepts GET method')
            abort(400, 'Malformed Request: Not a valid features request only excepts GET method')


#######################################################################
### Initializing Service
#######################################################################

def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.info ("initialize " + uri)
    service = featuresController(uri)
    # directory.register_service ('features', service)

    return service

# def get_static_dirs():
#    """Return the static directories for this server"""
#    package = pkg_resources.Requirement.parse ("features")
#    package_path = pkg_resources.resource_filename(package,'bq')
#    return [(package_path, os.path.join(package_path, 'features', 'public'))]

__controller__ = featuresController
