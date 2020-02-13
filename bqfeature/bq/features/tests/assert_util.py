from lxml import etree
import tables
import numpy as np
import csv
import pdb
import tables
import os
import uuid
from bqapi import BQCommError
from bqapi.bqfeature import ParallelFeature, FeatureResource
from utils import image_tiles


class ParallelFeaturewithException(ParallelFeature):
    def errorcb(self, e):
        """
            Returns an error log
        """
        self.exception = e


def check_response(session, request, response_code, xml=None, method='GET'):
    """
    """
    try:
        if method=='GET':
            xml = session.c.fetch(request, headers={'Content-Type':'text/xml', 'Accept':'text/xml'})
        elif method=='POST' and xml:
            xml = session.postxml(request, xml)
        elif method=='POST' and xml is None:
            xml = session.c.webreq(method='POST', url=request, headers={'Content-Type':'text/xml', 'Accept':'text/xml'})
        else:
            xml = session.postxml(request, xml, method=method)
    except BQCommError as e:
        assert(e.status == response_code)
    else:
        assert(200 == response_code)


def check_feature(ns, test, feature_name, image=None, mask=None, gobject=None):
    """
        Makes request, compares results, stores request in an hdf5 table

        @param: ns
        @param: test - test name
        @param: feature_name
        @param: image
        @param: mask
        @param: gobject
    """
    temp_response_path = os.path.join(ns.temp_store,uuid.uuid4().hex)
    try:
        resources = []
        if image:   resources.append('image=%s' % image)
        if mask:    resources.append('mask=%s' % mask)
        if gobject: resources.append('gobject=%s' % gobject)
        query = '&'.join(resources)
        request = '%s/features/%s/hdf?%s' % (ns.root, feature_name, query)
        temp_response_path = ns.session.c.fetch(request, headers={'Content-Type':'text/xml', 'Accept':'text/xml'}, path=temp_response_path)
        #temp_response_path = ns.session.postxml(request, xml=None, method='GET', path=temp_response_path)
    except BQCommError as e:
        assert(e.status == 200)
    else:
        #check the hdf file for status of each request
        with tables.open_file(temp_response_path, 'r') as temp:
            temp_table = temp.root.status
            query = 'status!=200'
            index = temp_table.getWhereList(query)
            if len(index)>0:
                for i in index:
                    assert(temp_table[i]['status']==200)

    results_table_path = os.path.join(ns.results_location, ns.feature_response_results)
    past_results_table_path = os.path.join(ns.store_local_location, ns.feature_past_response_results)
    #move to a results table
    with tables.open_file(temp_response_path, 'r') as temp:
        with tables.open_file(results_table_path, 'a') as result_file:
            temp_table = temp.root.values
            if hasattr(result_file.root, 'features'):
                features = result_file.root.features
            else:
                features = result_file.create_vlarray(result_file.root, 'features', tables.Float32Atom(shape=()))

            if hasattr(result_file.root, 'test_names'):
                test_names = result_file.root.test_names
            else:
                columns = {'name': tables.StringCol(300)}
                test_names = result_file.create_table('/','test_names', columns)
                test_names.cols.name.createIndex()

            for r in temp_table:
                features.append(r['feature'])
                test_names.append([tuple([test])])

    os.remove(temp_response_path)

    #check against a past result
    if os.path.exists(past_results_table_path):
        with tables.open_file(results_table_path, 'r') as result_file:
            with tables.open_file(past_results_table_path, 'r') as past_result_file:
                test_names = result_file.root.test_names
                feature = result_file.root.features
                past_test_names = past_result_file.root.test_names
                past_feature = past_result_file.root.features
                query = 'name=="%s"' % str(test)

                index = test_names.getWhereList(query)
                index_past = past_test_names.getWhereList(query)
                if index_past.any():
                    np.testing.assert_array_almost_equal(feature[index], past_feature[index_past], 4)


def parallel_check_feature(ns, test, feature_name, image):
    """
        Tiles out an image an makes a request on each of the parts separately
        to test parallel requests.
        Makes request, compares results, stores request in an hdf5 table

        @param: ns
        @param: test - test name
        @param: feature_name
        @param: image
    """
    temp_response_path = os.path.join(ns.temp_store,uuid.uuid4().hex)
    resource_list = []
    for url in image_tiles(ns.session, image, tile_size=64):
        resource_list.append(FeatureResource(image=url))

    bqfeatures = ParallelFeaturewithException()
    bqfeatures.set_thread_num(ns.threads)
    bqfeatures.set_chunk_size(50)

    try:
        bqfeatures.fetch(ns.session, feature_name, resource_list, temp_response_path)
        if hasattr(bqfeatures, 'exception'):
            raise bqfeatures.exception
    except BQCommError as e:
        assert(e.status == 200)
    else:
        #check the hdf file for status of each request
        with tables.open_file(temp_response_path, 'r') as temp:
            temp_table = temp.root.status
            query = 'status!=200'
            index = temp_table.getWhereList(query)
            if len(index)>0:
                for i in index:
                    assert(temp_table[i]['status']==200)

    results_table_path = os.path.join(ns.results_location, ns.feature_response_results)
    past_results_table_path = os.path.join(ns.store_local_location, ns.feature_past_response_results)

    #move to a results table with the urls ordered
    with tables.open_file(temp_response_path, 'r') as temp:
        with tables.open_file(results_table_path, 'a') as result_file:
            temp_table = temp.root.values
            image_url_list = sorted(temp_table[:]['image'])
            if hasattr(result_file.root, 'features'):
                features = result_file.root.features
            else:
                features = result_file.create_vlarray(result_file.root, 'features', tables.Float32Atom(shape=()))

            if hasattr(result_file.root, 'test_names'):
                test_names = result_file.root.test_names
            else:
                test_names = result_file.create_table('/','test_names', {'name': tables.StringCol(300)})
                test_names.cols.name.createIndex()

            for url in image_url_list:
                for i in temp_table.getWhereList('image=="%s"' % url):
                    features.append(temp_table[i]['feature'])
                    test_names.append([tuple([test])])

    os.remove(temp_response_path)

    #check against a past result
    if os.path.exists(past_results_table_path):
        with tables.open_file(results_table_path, 'r') as result_file:
            with tables.open_file(past_results_table_path, 'r') as past_result_file:
                test_names = result_file.root.test_names
                feature = result_file.root.features
                past_test_names = past_result_file.root.test_names
                past_feature = past_result_file.root.features
                query = 'name=="%s"' % str(test)

                index = test_names.getWhereList(query)
                index_past = past_test_names.getWhereList(query)
                if index_past.any():
                    np.testing.assert_array_almost_equal(feature[index], past_feature[index_past], 4)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def isEqualXMLElement(element_a,element_b):
    """
        Compares etree elements together
        inputs
        @element_a(etree) - etree element
        @element_b(etree) - etree element

        output
        asserts
        Compares an element of 2 xml etree structures

        #wanted to log results and keep track of all failres
    """
    assert element_a.tag == element_b.tag, '%s != %s'%(element_a.tag,element_b.tag)

    for name in element_b.attrib:
        if name not in element_a.attrib:
            assert 0, 'Element B has an attribute element A is missing: %s'%name

    for name, value in element_a.attrib.items():
        if is_number(element_b.attrib.get(name)) and is_number(value):
            np.testing.assert_approx_equal(float(element_b.attrib.get(name)),float(value), 6)
        else:
            assert element_b.attrib.get(name) == value, 'Attribute of element A %s != attribute of element B %s' % (value,element_b.attrib.get(name))



    #compare feature vectors
    if element_a.tag =='value':
        element_a_array = np.array(element_a.text.split()).astype('float')
        element_b_array = np.array(element_b.text.split()).astype('float')
        np.testing.assert_almost_equal(element_a_array,element_b_array, 4)
    else:
        assert element_a.text==element_b.text,'Text: %s != %s'%(element_a.text,element_b.text)

    subelement_a = element_a.getchildren()
    subelement_b = element_b.getchildren()
    assert len(subelement_a)==len(subelement_b),'%s != %s'%(len(subelement_a),len(subelement_b))

    for subele_a,subele_b in zip(sorted(subelement_a, key=lambda x:x.attrib.get('image')),sorted(subelement_b, key=lambda x:x.attrib.get('image'))):
        isEqualXMLElement(subele_a,subele_b)

    assert 1


def isCSVEqual(doc_a,doc_b):
    """
        Compares csv files together
        inputs
        @element_a(etree) - etree element
        @element_b(etree) - etree element

        ouput
        asserts
        Compares an element of 2 xml etree structures

        #TODO
        #wanted to log results and keep track of all failures
        #compare the elements together
        #need to make it work for many different kind of inputs
        #only sorts on image right now
    """
    parsed_csv_a = list(csv.reader( doc_a.splitlines(), delimiter=',', quotechar='"'))
    parsed_csv_b = list(csv.reader( doc_b.splitlines(), delimiter=',', quotechar='"'))

    #check to see if the same length
    assert len(parsed_csv_a)==len(parsed_csv_b), '%s!=%s'%(len(parsed_csv_a),len(parsed_csv_b))

    #check if titles are the same
    assert parsed_csv_a[0]==parsed_csv_b[0], '%s != %s'%( '%s...'%parsed_csv_a[0][:30] if len(parsed_csv_a[0])>30 else parsed_csv_a[0],
                                                          '%s...'%parsed_csv_b[0][:30] if len(parsed_csv_b[0])>30 else parsed_csv_b[0])

    #sorting based on the resource uris
    sorted_csv_rows_a = sorted(parsed_csv_a[1:],key=lambda x:x[2])
    sorted_csv_rows_b = sorted(parsed_csv_b[1:],key=lambda x:x[2])

    for row_a,row_b in zip(sorted_csv_rows_a,sorted_csv_rows_b):
        assert len(row_a)==len(row_b), '%s!=%s'%(len(row_a),len(row_b))
        for ncol in range(1,len(row_a)):
            if parsed_csv_a[0][ncol]=='descriptor':
                element_a_array = np.array(row_a[ncol].split(',')).astype('float')
                element_b_array = np.array(row_b[ncol].split(',')).astype('float')
                np.testing.assert_array_almost_equal(element_a_array,element_b_array, decimal=4)
            elif is_number(row_a[ncol]) and is_number(row_b[ncol]):
                np.testing.assert_approx_equal(float(row_a[ncol]),float(row_b[ncol]), 6)
            else:
                assert row_a[ncol]==row_b[ncol], '%s != %s'%( '%s...'%row_a[ncol][:30] if len(row_a[ncol])>30 else row_a[ncol],
                                                              '%s...'%row_b[ncol][:30] if len(row_b[ncol])>30 else row_b[ncol])

    assert 1


def isHDFEqual(path_hdf_a,path_hdf_b):
    """
        Compares csv files together

        inputs
        @path_hdf_a(str) - path to the hdf file being compared
        @path_hdf_b(str) - path to the hdf file being compared

        ouput
        asserts
        Compares hdf5 tables

        #TODO
        #wanted to log results and keep track of all failures
        #compare the elements together
    """

    with tables.open_file(path_hdf_a,'r') as h5file_a:
        with tables.open_file(path_hdf_b,'r') as h5file_b:
           table_a = h5file_a.root.values
           table_b = h5file_b.root.values

           assert set(table_a.colnames)==set(table_b.colnames), '%s!=%s'%(table_a.colnames,table_b.colnames)

           sorted_resource_a = sorted(zip(range(len(table_a)),table_a[:]['image']), key=lambda x:x[1:])
           sorted_resource_b = sorted(zip(range(len(table_b)),table_b[:]['image']), key=lambda x:x[1:])

           for idx_a,idx_b in zip(zip(*sorted_resource_a)[0],zip(*sorted_resource_b)[0]):
               for colname in table_a.colnames:
                   if colname == 'feature':
                       np.testing.assert_array_almost_equal(table_a[idx_a][colname],table_b[idx_b][colname], 4)
                   else:
                       assert table_a[idx_a][colname] == table_b[idx_b][colname], '%s!=%s' %(table_a[idx_a][colname],
                                                                                             table_b[idx_b][colname])

    assert 1
