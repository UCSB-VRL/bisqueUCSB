# -*- coding: utf-8 -*-
"""
Unit tests for table run query
"""
import sys
import pytest
import tables
import pandas as pd
import numpy as np

from ..controllers.table_base import TableLike, ArrayLike, OrConditionTuple, AndConditionTuple, ConditionTuple, CellSelectionTuple, SelectorTuple


def cb_csv(slices):
    # read only slices
    return pd.read_csv('small.csv', skiprows=xrange(1,slices[0].start+1), nrows=slices[0].stop-slices[0].start, usecols=range(slices[1].start, slices[1].stop))   # skip header line

def get_cb_excel(t):
    def cb_excel(slices):
        # read only slices
        data = pd.read_excel(t, 'my_sheet_N1', skiprows=xrange(1,slices[0].start+1), parse_cols=range(slices[1].start, slices[1].stop))
        # excel cannot read only a specified number of rows, select now
        return data[0:slices[0].stop-slices[0].start]
    return cb_excel

def _run_query(t, sels, cond, want_arr=True):
    res = t.run_query(sels=sels, cond=cond)
    return res.get_arr() if want_arr else res

def _wrap_hdf_table(t, cb=None):
    return TableLike(None, None, None, data=t if cb is None else None, offset=0, headers=t.colnames, types=[t.coltypes[h] if h in t.coltypes else '(compound)' for h in t.colnames], sizes=t.shape, cb=cb)

def _wrap_hdf_array(node):
    if node.ndim > 1:
        headers = [str(i) for i in range(0, node.shape[1])]
        types = [node.dtype.name for i in range(0, node.shape[1])]
    elif node.ndim > 0:
        headers = ['0']
        types = [node.dtype.name]
    else:
        headers = ['']
        types = [node.dtype.name]
    return ArrayLike(None, None, None, data=node, offset=0, headers=headers, types=types, sizes=node.shape)
    
def _wrap_pd_table(t, cb=None):
    return TableLike(None, None, None, data=t if cb is None else None, offset=0, headers=t.columns.tolist(), types=[ty.name for ty in t.dtypes.tolist()], sizes=(sys.maxint, t.shape[1]), cb=cb)

@pytest.mark.unit
class TestTableQuery(object):
    def test_hdf_singlecol(self):
        """Simple column select query (hdf table)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Ocean_flag'])], 
                                      agg=None, alias='bla bla')]

        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_table(t.get_node('/arrays/Vdata table: PerBlockMetadataCommon'))
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.columns[0] == 'bla bla'
        assert res.iloc[0].values[0] == 0 # pylint: disable=no-member
        assert res.iloc[44].values[0] == 1 # pylint: disable=no-member
        t.close()
        
    def test_csv_singlecol(self):
        """Simple column select query (CSV table)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['cccccc'])], 
                                      agg=None, alias='bla bla')]
        
        top = pd.read_csv('small.csv', nrows=1)  # just to get columns
        d = _wrap_pd_table(top, cb=cb_csv) # pylint: disable=no-member
        res = _run_query(d, sels=selcond, cond=None) 
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.columns[0] == 'bla bla'
        assert res.iloc[0].values[0] == 11586.285146 # pylint: disable=no-member
        assert res.iloc[14].values[0] == 29.587512 # pylint: disable=no-member

    def test_excel_singlecol(self):
        """Simple column select query (Excel)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['ssssss'])], 
                                      agg=None, alias='...my col name...')]
        
        t = pd.ExcelFile('large_1K.xls')
        top = pd.read_excel(t, 'my_sheet_N1', nrows=1)  # just to get columns
        d = _wrap_pd_table(top, cb=get_cb_excel(t)) # pylint: disable=no-member
        res = _run_query(d, sels=selcond, cond=None) 
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.columns[0] == '...my col name...'
        assert res.iloc[0].values[0] == 77246 # pylint: disable=no-member
        assert res.iloc[14].values[0] == 28282 # pylint: disable=no-member
        t.close()

    def test_hdf_twocol(self):
        """Simple two column select query (hdf table)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Ocean_flag'])],
                                      agg=None, alias='bla bla1'),
                   CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Block_coor_ulc_som_meter.x'])],
                                      agg=None, alias='bla bla2')]

        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_table(t.get_node('/arrays/Vdata table: PerBlockMetadataCommon'))
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 2
        assert res.columns[0] == 'bla bla1' and res.columns[1] ==  'bla bla2'
        assert res.iloc[0]['bla bla1'] == 0 # pylint: disable=no-member
        assert res.iloc[0]['bla bla2'] == 0.0 # pylint: disable=no-member
        assert res.iloc[44]['bla bla1'] == 1 # pylint: disable=no-member
        assert res.iloc[44]['bla bla2'] == 13655950.0 # pylint: disable=no-member
        t.close()
        
    def test_hdf_allcol(self):
        """All column select query (hdf table)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=[None, None])],
                                      agg=None, alias=None)]

        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_table(t.get_node('/arrays/Vdata table: PerBlockMetadataCommon'))
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 7
        assert set(res.columns) == set(['Block_number', 'Ocean_flag', 'Block_coor_ulc_som_meter.x', 'Block_coor_ulc_som_meter.y', 'Block_coor_lrc_som_meter.x', 'Block_coor_lrc_som_meter.y', 'Data_flag'])
        t.close()
        
    def test_hdf_somecol(self):
        """Some columns select query (hdf table)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Block_coor_ulc_som_meter.x', 'Data_flag'])],
                                      agg=None, alias=None)]

        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_table(t.get_node('/arrays/Vdata table: PerBlockMetadataCommon'))
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 4
        assert set(res.columns) == set(['Block_coor_ulc_som_meter.x', 'Block_coor_ulc_som_meter.y', 'Block_coor_lrc_som_meter.x', 'Block_coor_lrc_som_meter.y'])
        t.close()
        
    def test_hdf_halfcol(self):
        """Lower half columns select query (hdf table)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=[None, 'Block_coor_lrc_som_meter.x'])],
                                      agg=None, alias=None)]

        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_table(t.get_node('/arrays/Vdata table: PerBlockMetadataCommon'))
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 4
        assert set(res.columns) == set(['Block_number', 'Ocean_flag', 'Block_coor_ulc_som_meter.x', 'Block_coor_ulc_som_meter.y'])
        t.close()
        
    def test_excel_filter_somecol(self):
        """Filter on value of middle columns (csv)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['zzzzzz', 'ssssss.1'])], agg=None, alias=None)]
        filtercond = ConditionTuple(left=CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['zzzzzz', 'ssssss.1'])], agg=None, alias=None), comp='<', right=1000)

        t = pd.ExcelFile('large_1K.xls')
        top = pd.read_excel(t, 'my_sheet_N1', nrows=1)  # just to get columns
        d = _wrap_pd_table(top, cb=get_cb_excel(t)) # pylint: disable=no-member
        res = _run_query(d, sels=selcond, cond=filtercond)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 3
        assert res.shape[0] == 71
        assert set(res.columns) == set(['zzzzzz', 'ssssss', 'jjjjjj'])
        
    def test_excel_twocol(self):
        """Simple two column select query (excel)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['ssssss'])],
                                      agg=None, alias=None),
                   CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['llllll'])],
                                      agg=None, alias='bla bla2')]

        t = pd.ExcelFile('large_1K.xls')
        top = pd.read_excel(t, 'my_sheet_N1', nrows=1)  # just to get columns
        d = _wrap_pd_table(top, cb=get_cb_excel(t)) # pylint: disable=no-member
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 2
        assert set(res.columns) == set(['ssssss', 'bla bla2'])
        assert res.iloc[0]['ssssss'] == 77246 # pylint: disable=no-member
        assert res.iloc[0]['bla bla2'] == 19136.196304 # pylint: disable=no-member
        assert res.iloc[29]['ssssss'] == 11582 # pylint: disable=no-member
        assert res.iloc[29]['bla bla2'] == 32058.006895 # pylint: disable=no-member
        t.close()
    
    def test_hdf_rowcol(self):
        """Row and column select query (hdf table)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Ocean_flag']), SelectorTuple(dimname='row', dimvalues=[10,50])], 
                                      agg=None, alias='bla bla')]
        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_table(t.get_node('/arrays/Vdata table: PerBlockMetadataCommon'))
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.shape[0] == 40
        assert res.columns[0] == 'bla bla'
        assert res.iloc[0].values[0] == 0 # pylint: disable=no-member
        assert res.iloc[34].values[0] == 1 # pylint: disable=no-member
        t.close()
        
    def test_csv_rowcol(self):
        """Row and column select query (CSV table)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['cccccc']), SelectorTuple(dimname='row', dimvalues=[10,20])], 
                                      agg=None, alias='bla bla')]
        
        top = pd.read_csv('small.csv', nrows=1)  # just to get columns
        d = _wrap_pd_table(top, cb=cb_csv) # pylint: disable=no-member
        res = _run_query(d, sels=selcond, cond=None) 
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.shape[0] == 10
        assert res.columns[0] == 'bla bla'
        assert res.iloc[0].values[0] == 8539.802001 # pylint: disable=no-member
        assert res.iloc[9].values[0] == 4352.195533 # pylint: disable=no-member

    def test_hdf_selfilter(self):
        """Filter by one column and select a different column (hdf)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Block_number']), SelectorTuple(dimname='row', dimvalues=[10,50])], 
                                      agg=None, alias='bla bla')]
        filtercond = ConditionTuple(left=CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Ocean_flag']), SelectorTuple(dimname='row', dimvalues=[10,50])], agg=None, alias=None), comp='=', right=1)
        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_table(t.get_node('/arrays/Vdata table: PerBlockMetadataCommon'))
        res = _run_query(d, sels=selcond, cond=filtercond)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.shape[0] == 20
        assert res.columns[0] == 'bla bla'
        assert res.iloc[0].values[0] == 17 # pylint: disable=no-member
        assert res.iloc[14].values[0] == 31 # pylint: disable=no-member
        assert res.iloc[15].values[0] == 44 # pylint: disable=no-member
        t.close()
        
    def test_hdf_aggfilter(self):
        """Filter by one column and comp agg on a different column (hdf)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Block_number']), SelectorTuple(dimname='row', dimvalues=[10,50])], 
                                      agg='min', alias='min block'),
                   CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Block_number']), SelectorTuple(dimname='row', dimvalues=[10,50])], 
                                      agg='max', alias='max block')]
        filtercond = ConditionTuple(left=CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['Ocean_flag']), SelectorTuple(dimname='row', dimvalues=[10,50])], agg=None, alias=None), comp='=', right=1)
        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_table(t.get_node('/arrays/Vdata table: PerBlockMetadataCommon'))
        res = _run_query(d, sels=selcond, cond=filtercond)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 2
        assert res.shape[0] == 1
        assert set(res.columns) == set(['max block', 'min block'])
        assert res.iloc[0]['max block'] == 48 # pylint: disable=no-member
        assert res.iloc[0]['min block'] == 17 # pylint: disable=no-member
        t.close()
        
    def test_hdf_selfilter2col(self):
        """Filter by two columns (e.g., X and Y) and select a different column (csv)"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['id'])], 
                                      agg=None, alias='id')]
        filtercond = AndConditionTuple(left=AndConditionTuple(left=ConditionTuple(left=CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['cccccc'])], agg=None, alias=None), comp='>', right=10000),
                                                              right=ConditionTuple(left=CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['cccccc'])], agg=None, alias=None), comp='<', right=20000)),
                                       right=AndConditionTuple(left=ConditionTuple(left=CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['rrrrrr'])], agg=None, alias=None), comp='>', right=5000),
                                                              right=ConditionTuple(left=CellSelectionTuple(selectors=[SelectorTuple(dimname='field', dimvalues=['rrrrrr'])], agg=None, alias=None), comp='<', right=10000)))
        top = pd.read_csv('small.csv', nrows=1)  # just to get columns
        d = _wrap_pd_table(top, cb=cb_csv) # pylint: disable=no-member
        res = _run_query(d, sels=selcond, cond=filtercond) 
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.shape[0] == 2
        assert res.columns[0] == 'id'
        assert res.iloc[0].values[0] == 3 # pylint: disable=no-member
        assert res.iloc[1].values[0] == 55 # pylint: disable=no-member
        
    def test_array_filter(self):
        """Filter by three dimensions"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='__dim1__', dimvalues=[10,20]),
                                                 SelectorTuple(dimname='__dim2__', dimvalues=[10,20]),
                                                 SelectorTuple(dimname='__dim3__', dimvalues=[0,5])], 
                                      agg=None, alias=None)]
        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_array(t.get_node('/arrays/3D int array'))
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, np.ndarray)
        assert res.shape[0] == 10 and res.shape[1] == 10 and res.shape[2] == 5
        t.close()
        
    def test_array_aggfilter(self):
        """Filter by three dimensions and compute agg on filtered cells"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='__dim1__', dimvalues=[10,20]),
                                                 SelectorTuple(dimname='__dim2__', dimvalues=[10,20]),
                                                 SelectorTuple(dimname='__dim3__', dimvalues=[0,5])], 
                                      agg='mean', alias='mean')]
        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_array(t.get_node('/arrays/3D int array'))
        res = _run_query(d, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.shape[0] == 1
        assert res.columns[0] == 'mean'
        assert res.iloc[0].values[0] == 246452.0 # pylint: disable=no-member
        t.close()

    def test_array_aggfiltercond(self):
        """Filter by three dimensions and cell value and compute agg on filtered cells"""
        selcond = [CellSelectionTuple(selectors=[SelectorTuple(dimname='__dim1__', dimvalues=[10,20]),
                                                 SelectorTuple(dimname='__dim2__', dimvalues=[10,20]),
                                                 SelectorTuple(dimname='__dim3__', dimvalues=[0,5])], 
                                      agg='mean', alias='mean')]
        filtercond = ConditionTuple(left=CellSelectionTuple(selectors=[], agg=None, alias=None), comp='>', right=290000)
        t = tables.open_file('hdf5_test.h5')
        d = _wrap_hdf_array(t.get_node('/arrays/3D int array'))
        res = _run_query(d, sels=None, cond=filtercond, want_arr=False)
        res = _run_query(res, sels=selcond, cond=None)
        assert isinstance(res, pd.core.frame.DataFrame)
        assert len(res.columns) == 1
        assert res.shape[0] == 1
        assert res.columns[0] == 'mean'
        assert res.iloc[0].values[0] == 291452.0 # pylint: disable=no-member
        t.close()
