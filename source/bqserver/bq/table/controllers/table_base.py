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
Table base for importerters

"""

__author__    = "Dmitry Fedorov <dima@dimin.net>"
__version__   = "1.0"
__copyright__ = "Center for Bio-Image Informatics, University of California at Santa Barbara"

# default imports
import os
import logging
import pkg_resources
import itertools
from pylons.controllers.util import abort
from collections import namedtuple, OrderedDict
import re
import types
import copy

try:
    import ply.yacc as yacc
    import ply.lex as lex
    from ply.lex import TOKEN
except:
    import yacc as yacc
    import lex as lex
    from lex import TOKEN

log = logging.getLogger("bq.table.base")

try:
    import numpy as np
except ImportError:
    log.info('Numpy was not found but required for table service!')

try:
    import tables
except ImportError:
    log.info('Tables was not found but required for table service!')

try:
    import pandas as pd
except ImportError:
    log.info('Pandas was not found but required for table service!')


__all__ = [ 'TableBase' ]



#---------------------------------------------------------------------------------------
# Abstract table query language
#---------------------------------------------------------------------------------------

OrConditionTuple = namedtuple('OrConditionTuple', ['left', 'right'])
AndConditionTuple = namedtuple('AndConditionTuple', ['left', 'right'])
ConditionTuple = namedtuple('ConditionTuple', ['left', 'comp', 'right'])
CellSelectionTuple = namedtuple('CellSelectionTuple', ['selectors', 'agg', 'alias'])
SelectorTuple = namedtuple('SelectorTuple', ['dimname', 'dimvalues'])


#---------------------------------------------------------------------------------------
# Supported aggregation functions
#---------------------------------------------------------------------------------------

def _get_agg_fct(agg):
    return {
            'mean': np.nanmean,
            'min': np.nanmin,
            'max': np.nanmax,
            'median': np.nanmedian,
            'std': np.nanstd,
            'var': np.nanvar
           }.get(agg)

def _check_aggfct(agg):
    if _get_agg_fct(agg) is not None:
        return agg
    else:
        raise ParseError("Unknown aggregation function: '%s'" % agg)


#---------------------------------------------------------------------------------------
# Query string parser; generates abstract tuple language query
#---------------------------------------------------------------------------------------

class ParseError(Exception): pass

class TableQueryLexer:
    # constant patterns
    decimal_constant = '((0)|([1-9][0-9]*))'
    exponent_part = r"""([eE][-+]?[0-9]+)"""
    fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
    floating_constant = '((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+'))'

    keywords = ( 'AND', 'OR', 'AS' )
    tokens = keywords + ('ID', 'LP', 'RP', 'LB', 'RB', 'LC', 'RC', 'COLON', 'COMMA', 'STRVAL', 'INTVAL', 'FLOATVAL',
                         'PLUS', 'MINUS',
                         'LT', 'LE', 'GT', 'GE', 'EQ', 'NE')

    #t_TAGVAL   = r'\w+\*?'
    t_PLUS              = r'\+'
    t_MINUS             = r'-'
    t_LP                = r'\('
    t_RP                = r'\)'
    t_LB                = r'\['
    t_RB                = r'\]'
    t_LC                = r'\{'
    t_RC                = r'\}'
    t_LE                = r'<='
    t_GE                = r'>='
    t_LT                = r'<'
    t_GT                = r'>'
    t_EQ                = r'='
    t_NE                = r'!='
    t_COLON             = r'[:;]'
    t_COMMA             = r','

    t_ignore = ' \t\n'

    # the following floating and integer constants are defined as
    # functions to impose a strict order

    @TOKEN(floating_constant)
    def t_FLOATVAL(self, t):
        t.value = float(t.value)
        return t

    @TOKEN(decimal_constant)
    def t_INTVAL(self, t):
        t.value = int(t.value)
        return t

    def t_STRVAL(self,t):
        r"(?:'(?:\\'|[^'])*')|(?:\"(?:\\\"|[^\"])*\")"
        t.value = t.value[1:-1].replace(r'\"', r'"').replace(r"\'", r"'")
        return t

    def t_ID(self,t):
        r'[a-zA-Z_][0-9a-zA-Z_]*'
        if t.value.upper() in self.keywords:
            t.value = t.value.upper()
            t.type = t.value
        else:
            t.value = t.value.lower()
            t.type = 'ID'
        return t

    def t_error(self,t):
        raise ParseError( "Illegal character '%s'" % t.value[0] )
        t.lexer.skip(1)

    def __init__(self):
        self.lexer = lex.lex(module=self, optimize=False, debug=False)

    def tokenize(self,data):
        'Debug method!'
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if tok:
                yield tok
            else:
                break

class TableQueryParser:
    # standard precendence rules
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE'),
        ('left', 'GT', 'GE', 'LT', 'LE'),
        ('right', 'UPLUS', 'UMINUS')
    )

    def __init__(self):
        """Create new parser and set up parse tables."""
        self.lexer = TableQueryLexer()
        self.tokens = self.lexer.tokens
        self.filter_parser = yacc.yacc(module=self,write_tables=False,debug=False,optimize=False, start='query')
        self.agg_parser = yacc.yacc(module=self,write_tables=False,debug=False,optimize=False, start='agg_list')

    def parse_filter(self, query, colnames):
        self.colnames = colnames
        return self.filter_parser.parse(query,lexer=self.lexer.lexer,debug=False)

    def parse_agg(self, query, colnames):
        self.colnames = colnames
        return self.agg_parser.parse(query,lexer=self.lexer.lexer,debug=False)

    def p_error(self,p):
        if p:
            raise ParseError("Unexpected symbol: '%s'" % p.value)
        else:
            raise ParseError("Unexpected end of query")

    def p_query(self, p):
        '''query : slice_cond LC filter_cond RC
                 | slice_cond
                 | LC filter_cond RC
        '''
        if len(p) == 5:
            p[0] = (p[1], p[3])
        elif len(p) == 2:
            p[0] = (p[1], None)
        else:
            p[0] = (None, p[2])

    # TODO: retire the first rule (single cell_sel without '[',']') once UI is updated
    def p_slice_cond(self,p):
        '''slice_cond : cell_sel
                      | slice_list
        '''
        if len(p[1]) == 0:
            p[0] = []
        elif isinstance(p[1][0], CellSelectionTuple):
            p[0] = p[1]
        else:
            p[0] = [ CellSelectionTuple(selectors=p[1], agg=None, alias=None) ]

    def p_slice_list(self,p):
        '''slice_list : slice_list COMMA LB cell_sel RB
                      | LB cell_sel RB
        '''
        if len(p) == 6:
            p[0] = p[1] + [ CellSelectionTuple(selectors=p[4], agg=None, alias=None) ]
        else:
            p[0] = [ CellSelectionTuple(selectors=p[2], agg=None, alias=None) ]

    def p_agg_list(self,p):
        '''agg_list : agg_list COMMA ID LP cell_sel RP AS STRVAL
                    | agg_list COMMA ID LP cell_sel RP
                    | ID LP cell_sel RP AS STRVAL
                    | ID LP cell_sel RP
        '''
        if len(p) == 9:
            p[0] = p[1] + [ CellSelectionTuple(selectors=p[5], agg=_check_aggfct(p[3]), alias=p[8]) ]
        elif len(p) == 7:
            if isinstance(p[1], list):
                p[0] = p[1] + [ CellSelectionTuple(selectors=p[5], agg=_check_aggfct(p[3]), alias=None) ]
            else:
                p[0] = [ CellSelectionTuple(selectors=p[3], agg=_check_aggfct(p[1]), alias=p[6]) ]
        else:
            p[0] = [ CellSelectionTuple(selectors=p[3], agg=_check_aggfct(p[1]), alias=None) ]

    def p_filter_cond(self,p):
        '''filter_cond : filter_cond OR and_expr
                       | and_expr
        '''
        if len(p) == 4:
            p[0] = OrConditionTuple(left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_and_expr(self,p):
        '''and_expr : and_expr AND comp_cond
                    | comp_cond
        '''
        if len(p) == 4:
            p[0] = AndConditionTuple(left=p[1], right=p[3])
        else:
            p[0] = p[1]

    def p_comp_cond(self,p):
        '''comp_cond : LP filter_cond RP
                     | LB cell_sel RB EQ unary_expr
                     | LB cell_sel RB NE unary_expr
                     | LB cell_sel RB GT unary_expr
                     | LB cell_sel RB GE unary_expr
                     | LB cell_sel RB LT unary_expr
                     | LB cell_sel RB LE unary_expr
        '''
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = ConditionTuple(left=CellSelectionTuple(selectors=p[2], agg=None, alias=None), comp=p[4], right=p[5])

    def p_unary_expr(self,p):
        '''unary_expr : MINUS unary_expr %prec UMINUS
                      | PLUS unary_expr %prec UPLUS
                      | INTVAL
                      | FLOATVAL
                      | STRVAL
        '''
        if len(p) == 3:
            p[0] = (p[2] if p[1] == '+' or isinstance(p[2], basestring) else -p[2])
        else:
            p[0] = p[1]

    def p_cell_sel(self,p):
        '''cell_sel : cell_sel COMMA single_dim_sel
                    | single_dim_sel
        '''
        if len(p) == 4:
            p[3] = SelectorTuple(dimname=p[3].dimname or '__dim%s__' % (len(p[1])+1), dimvalues=p[3].dimvalues)
            if p[3].dimname not in ['__dim2__', 'field'] and any(isinstance(v, basestring) for v in p[3].dimvalues):
                raise ParseError('values %s not allowed for dimension \'%s\'' % (p[3].dimvalues, p[3].dimname))
            p[0] = p[1] + [ p[3] ]
        else:
            p[1] = SelectorTuple(dimname=p[1].dimname or '__dim1__', dimvalues=p[1].dimvalues)
            if p[1].dimname not in ['__dim2__', 'field'] and any(isinstance(v, basestring) for v in p[1].dimvalues):
                raise ParseError('values %s not allowed for dimension \'%s\'' % (p[1].dimvalues, p[1].dimname))
            p[0] = [ p[1] ]

    def p_single_dim_sel(self,p):
        '''single_dim_sel : STRVAL EQ range_sel
                          | range_sel
        '''
        if len(p) == 4:
            p[0] = SelectorTuple(dimname=p[1], dimvalues=p[3])
        else:
            p[0] = SelectorTuple(dimname=None, dimvalues=p[1])

    def p_range_sel(self,p):
        '''range_sel : COLON
                     | index_expr
                     | index_expr COLON
                     | COLON index_expr
                     | index_expr COLON index_expr
        '''
        if len(p) == 2:
            p[0] = [None] if p[1] in [':', ';'] else [p[1]]
        elif len(p) == 3:
            if p[2] in [':', ';']:
                p[0] = [p[1],None]
            else:
                p[0] = [None,self._adjust_endcol(p[2])]
        else:
            p[0] = [p[1],self._adjust_endcol(p[3])]

    def _adjust_endcol(self, endcol):
        if isinstance(endcol, int):
            endcol += 1
        else:
            endcol = self.colnames.index(endcol)
            endcol += 1
            if endcol >= len(self.colnames):
                endcol = None
            else:
                endcol = self.colnames[endcol]
        return endcol

    def p_index_expr(self,p):
        '''index_expr : INTVAL
                      | STRVAL
        '''
        p[0] = p[1]

#---------------------------------------------------------------------------------------
# Table base
#---------------------------------------------------------------------------------------

class TableBase(object):
    '''Formats tables into output format'''

    name = ''
    version = '1.0'
    ext = 'table'
    mime_type = 'text/plain'

    # general functionality defined in the base class

    def __str__(self):
        return '%s(data: %s, sizes: %s, headers: %s, ops: %s)'%(type(self), type(self.data), self.sizes, self.headers, self.t_ops)

    def isloaded(self):
        """ Returns table information """
        return self.t is not None


    # functions to be defined in the individual drivers

    def __init__(self, uniq, resource, path, **kw):
        """ Returns table information """
        table = kw.get('table')
        if table is not None:  # "copy constructor"
            self.path = path or table.path
            self.resource = resource or table.resource
            self.uniq = uniq or table.uniq
            self.url = kw.get('url', table.url)
            self.subpath = kw.get('subpath', table.subpath)
            self.tables = kw.get('tables', table.tables)
            self.t = kw.get('t', table.t)
            self.t_ops = kw.get('t_ops', table.t_ops)
            self.data = kw.get('data', table.data)
            self.offset = kw.get('offset', table.offset)
            self.headers = kw.get('headers', table.headers)
            self.types = kw.get('types', table.types)
            self.sizes = kw.get('sizes', table.sizes)
            self.cb = kw.get('cb', table.cb)
            self.meta = kw.get('meta', table.meta)
        else:
            self.path = path
            self.resource = resource
            self.uniq = uniq
            self.url = kw.get('url')
            self.subpath = kw.get('subpath') # list containing subpath to elements within the resource
            self.tables = kw.get('tables') # {'path':.., 'type':..} for all available tables in the resource
            self.t = kw.get('t') # represents a pointer to the actual element being operated on based on the driver
            self.t_ops = kw.get('t_ops', None) or []    # operations to be performed on t
            self.data = kw.get('data') # Numpy array or pandas dataframe
            self.offset = kw.get('offset', 0)
            self.headers = kw.get('headers')
            self.types = kw.get('types')
            self.sizes = kw.get('sizes')
            self.cb = kw.get('cb')   # callback to retrieve records on demand (if needed)
            self.meta = kw.get('meta', None) or {}

    def close(self):
        """Close table; OVERWRITE IN SUBCLASS"""
        pass

    # ------------- TODO: move to subclasses -------------
    def as_array(self):
        if isinstance(self.data, pd.core.frame.DataFrame):
            return self.data.as_matrix()   # convert to numpy array
        else:
            return self.data

    def as_table(self):
        if isinstance(self.data, pd.core.frame.DataFrame):
            return self.data
        else:
            if self.data.ndim == 1:
                return pd.DataFrame(self.data)
            else:
                raise RuntimeError("cannot convert multi-dim array into dataframe")
    # ------------- TODO: move to subclasses -------------

    def info(self, **kw):
        """ Returns table information """
        raise NotImplementedError()

    def run_query( self, query_op=None, sels=None, cond=None, want_cell_coord=False, keep_dims=None ):
        """
        Actual query processor operating on abstract tuple language

        Input:     query to run (selection and/or filter condition),
                   want coord back (or only values, if False)
                   dims to keep (higher dims use only slice "0" values)
        Output:    TableBase subclass (may be different type from self)
        """
        if query_op is not None:
            if query_op.keys()[0] == 'filter':
                sels, cond = query_op['filter']
            elif query_op.keys()[0] == 'agg':
                sels = query_op['agg']

        if sels is None and cond is None:
            # no query => return as is
            return self

        if sels is not None and not isinstance(sels, list):
            sels = [sels]

        assert sels is None or all([sel.agg is not None for sel in sels]) or all([sel.agg is None for sel in sels])  # all aggs or all non aggs, cannot mix

        # no coords needed if agg
        if sels is not None and sels[0].agg is not None:
            want_cell_coord = False

        # limit dims
        if sels is not None and keep_dims is not None:
            new_sels = []
            for sel in sels:
                new_selectors = copy.deepcopy(sel.selectors)
                for dim in xrange(keep_dims, len(self.get_shape())+1):
                    if "__dim%s__"%dim not in [ single_sel.dimname for single_sel in sel.selectors ]:
                        new_selectors.append( SelectorTuple( dimname="__dim%s__"%dim, dimvalues=[0] ) )
                new_sels.append(CellSelectionTuple(selectors=new_selectors, agg=sel.agg, alias=sel.alias))
            sels = new_sels

        # push down slicing for both sels and cond
        log.debug("run_query %s sels=%s cond=%s" % (self, sels, cond))
        slices = self.get_slices(sels, cond)
        log.debug("slices=%s" % str(slices))
        if slices is None:
            # nothing selected
            data = None
            row_types = [self.get_arr().dtype]
        else:
            # get iterator based on slices & cond
            row_iter = self.get_slice_iter(slices, cond, want_cell_coord)

            # get iterator based on sels
            row_types, row_iter = self.get_sels_iter(row_iter, sels, want_cell_coord)

            # format and return result (convert into dataframe or numpy array)
            try:
                peek = row_iter.next()
                if isinstance(peek, np.ndarray):
                    data = peek
                else:
                    # set proper types
                    new_types = {}
                    for ix in xrange(len(row_types)):
                        new_types[peek.keys()[ix]] = row_types[ix]
                    data = pd.DataFrame(data=(x for x in itertools.chain([peek], row_iter)))
                    data = data.astype(dtype=new_types)
            except StopIteration:
                # empty result
                data = None

        # set empty to correct type
        if data is None:
            if isinstance(self, ArrayLike):
                data = np.empty((), dtype=row_types[0])          # empty array
            else:
                data = pd.DataFrame()                            # empty table

        # compute all other stats
        dim_sizes = [d for d in data.shape]
        offset = slices[0].start if slices is not None and len(slices)>0 and (sels is None or sels[0].agg is None) else 0
        if isinstance(data, np.ndarray):
            all_colnames = self.get_columns()
            colnames = [all_colnames[i] if all_colnames is not None else str(i) for i in xrange(slices[1].start, slices[1].stop)] if len(slices)>1 else ['0']
            #colnames = [str(i) for i in xrange(slices[1].start, slices[1].stop)] if len(slices)>1 else ['0']
            coltypes = [row_types[0]] * data.shape[1] if len(data.shape) > 1 else [row_types[0]]
        else:
            colnames = data.columns.tolist()
            coltypes = row_types

        # return the proper class
        if isinstance(data, np.ndarray) or isinstance(data, tables.array.Array):
            return ArrayLike(None, None, None, table=self, data=data, sizes=dim_sizes, offset=offset, types=coltypes, headers=colnames)
        else:
            return TableLike(None, None, None, table=self, data=data, sizes=dim_sizes, offset=offset, types=coltypes, headers=colnames)

    def read(self, **kw):
        """ Read table cells and return """
        if self.data is None:
            self.info(**kw)

        assert len(self.t_ops) <= 1   # TODO: allow sequence of ops?
        query_op = self.t_ops.pop(0) if len(self.t_ops) > 0 else None
        return self.run_query(query_op=query_op)

    def get_queriable(self):
        """ Return object of TableLike or ArrayLike subclass for query purposes"""
        raise NotImplementedError()

    def get_arr(self):
        return self.data

    def get_shape(self):
        return self.sizes

    def get_columns(self):
        return self.headers

    def get_types(self):
        return self.types

    def get_type(self, colname):
        return self.get_types()[ self._convert_to_colnum(colname) ]

    def get_slices(self, sels, cond):
        slices = None
        if sels is not None:
            for sel in sels:
                add_slices = self._selectors_to_slices(sel.selectors)
                slices = add_slices if slices is None else self._or_slices(slices, add_slices)
        if cond is not None:
            add_slices = self._cond_to_slices(cond)
            slices = add_slices if slices is None else self._or_slices(slices, add_slices)
        return slices

    def get_slice_iter(self, slices, cond, want_cell_coord=False):
        raise NotImplementedError()

    def get_sels_iter(self, row_iter, sels, want_cell_coord=False):
        raise NotImplementedError()

    def write(self, data, **kw):
        """ Write cells into a table"""
        abort(501, 'Write not implemented')

    def delete(self, **kw):
        """ Delete cells from a table"""
        abort(501, 'Delete not implemented')

    def _cond_to_slices(self, cond):
        if isinstance(cond, OrConditionTuple) or isinstance(cond, AndConditionTuple):
            # OR to keep all referenced cells
            return self._or_slices(self._cond_to_slices(cond.left), self._cond_to_slices(cond.right))
        elif isinstance(cond, ConditionTuple):
            return self._cond_to_slices(cond.left)
        elif isinstance(cond, CellSelectionTuple):
            return self._selectors_to_slices(cond.selectors)
        return tuple([ slice(0,self.sizes[dim]) for dim in range(len(self.sizes)) ])

    def _selectors_to_slices(self, sels):
        raise NotImplementedError()

    def _selectors_to_columns(self, sels):
        res = []
        if sels is not None:
            for sel in sels:
                dim = self._get_dim(sel.dimname)
                if dim == 1:
                    if len(sel.dimvalues) == 0 or all([colname is None for colname in sel.dimvalues]):
                        # select all columns
                        for ix in xrange(len(self.headers)):
                            if self.headers[ix] not in res:
                                res.append(self.headers[ix])
                    elif len(sel.dimvalues) == 1:
                        # single column
                        colname = sel.dimvalues[0]
                        if isinstance(colname, int):
                            colname = self.headers[colname]
                        if colname not in res:
                            res.append(colname)
                    else:
                        # start/stop column
                        startcolix = self._convert_to_colnum(sel.dimvalues[0]) or 0
                        stopcolix = self._convert_to_colnum(sel.dimvalues[1]) or len(self.headers)
                        for ix in xrange(startcolix, stopcolix):
                            if self.headers[ix] not in res:
                                res.append(self.headers[ix])
        return res

    def _get_dim(self, dimname):
        raise NotImplementedError()

    def _convert_to_colnum(self, colname):
        if colname is None or isinstance(colname, int):
            return colname
        for ix in xrange(len(self.headers)):
            if self.headers[ix] == colname:
                return ix
        raise RuntimeError("column %s not found" % colname)

    def _or_slices(self, slices1, slices2):
        # essentially compute "bounding" slice around slices
        res = [None] * len(slices1)
        for dim in range(len(slices1)):
            res[dim] = slice(min(slices1[dim].start, slices2[dim].start), max(slices1[dim].stop, slices2[dim].stop))
        return tuple(res)

    def _and_slices(self, slices1, slices2):
        # compute intersection of slices BUT keep all '__dim1__'/'column'/'fields'
        # (this is an artifact of treating fields like dimensions, which they really aren't)
        res = [None] * len(slices1)
        for dim in range(len(slices1)):
            if dim == 1:   # TODO: only treat dataframes as special? (self.is_dataframe() and dim == 1)
                res[dim] = slice(min(slices1[dim].start, slices2[dim].start), max(slices1[dim].stop, slices2[dim].stop))
            else:
                res[dim] = slice(max(slices1[dim].start, slices2[dim].start), min(slices1[dim].stop, slices2[dim].stop))
        return tuple(res)

#---------------------------------------------------------------------------------------
# Table-like object
# Contains table-specific query translations.
#---------------------------------------------------------------------------------------
class TableLike(TableBase):
    def __init__(self, uniq, resource, path, **kw):
        super(TableLike, self).__init__(uniq, resource, path, **kw)
        assert self.data is None or isinstance(self.data, pd.core.frame.DataFrame) or isinstance(self.data, tables.table.Table)   # TODO: make this class DataFrame and other tables as subclasses?

    def get_queriable(self):
        return self

    def get_slice_iter(self, slices, cond, want_cell_coord=False):
        offsets = [0]*len(slices)

        if self.data is None:
            # need to bring in data first
            self.data = self.cb(slices)
            assert isinstance(self.data, pd.core.frame.DataFrame) or isinstance(self.data, tables.table.Table)
            # adjust slices to start from 0 since it is already sliced and remember offsets
            for d in xrange(len(slices)):
                offsets[d] = slices[d].start
            slices = tuple([slice(0, slices[d].stop-slices[d].start) for d in xrange(len(slices))])

        ###### translator for And/Or/Condition:
        #    => ( ((coord[0],), node.iloc[coord[0]]) for coord in np.argwhere((node[:]['H'] > 0) & (node[:]['L'] > 0)) )                 FOR TABLE (IF DataFrame)    OR
        #    => ( ((row.nrow,), row) for row in node.where('(H > 0) & (L > 0)') )                                                        FOR TABLE (IF pytables)
        filter_exp = None
        if cond is not None:
            if isinstance(self.data, pd.core.frame.DataFrame):
                filter_exp = self._gen_dataframe_filter(self.data.iloc[slices[0]], cond)
            else:
                filter_exp = self._gen_table_filter(self.data, cond)

        if filter_exp is None:
            if isinstance(self.data, pd.core.frame.DataFrame):
                if want_cell_coord:
                    row_iter = ( ((row[0]+offsets[0],), row[1]) for row in self.data.iloc[slices].iterrows() )
                else:
                    row_iter = ( row[1] for row in self.data.iloc[slices].iterrows() )
            else:
                if want_cell_coord:
                    row_iter = ( ((row.nrow+offsets[0],), row) for row in self.data.iterrows(slices[0].start, slices[0].stop) )
                else:
                    row_iter = self.data.iterrows(slices[0].start, slices[0].stop)
        else:
            # have condition
            if isinstance(self.data, pd.core.frame.DataFrame):
                if want_cell_coord:
                    row_iter = ( ((coord[0]+slices[0].start+offsets[0],), self.data.iloc[(coord[0]+slices[0].start, slices[1])]) for coord in np.argwhere(filter_exp) )
                else:
                    row_iter = ( self.data.iloc[coord[0]+slices[0].start] for coord in np.argwhere(filter_exp) )
            else:
                if want_cell_coord:
                    row_iter = ( ((row.nrow+offsets[0],), row) for row in self.data.where(filter_exp) if row.nrow >= slices[0].start and row.nrow < slices[0].stop )
                else:
                    row_iter = ( row for row in self.data.where(filter_exp) if row.nrow >= slices[0].start and row.nrow < slices[0].stop )

        return row_iter

    def get_sels_iter(self, row_iter, sels, want_cell_coord=False):
        ###### translator for CellSelection:
        #    => np.mean([r['K'] for r in <rowlist from FILTER or ALL>])         IF pytables table OR
        #    => np.mean([r.loc['K'] for r in <rowlist from FILTER or ALL>])     IF pandas Series
        if sels is None:
            # no selection, include all columns
            if isinstance(self.data, pd.core.frame.DataFrame):
                sel_fct = lambda row: OrderedDict( (colname,row[colname]) for colname in row.keys() )
            else:
                sel_fct = lambda row: OrderedDict( (colname,row[colname]) for colname in self.data.colnames )
            if want_cell_coord:
                row_iter = ( OrderedDict(sel_fct(row), index=coord) for (coord, row) in row_iter )
            else:
                row_iter = ( sel_fct(row) for row in row_iter )
            # compute row types
            row_types = self.get_types()

        elif sels[0].agg is None:
            # no aggregation, just return slices
            def sel_fct_df(row):
                res = OrderedDict()
                selix = 0
                for sel in sels:
                    cols = self._selectors_to_columns(sel.selectors)
                    for col_ix in xrange(len(cols)):
                        alias = sel.alias or cols[col_ix]
                        if alias in res:
                            alias = "%s_%s" % (alias, selix)
                        res[alias] = row.loc[cols[col_ix]]
                    selix += 1
                return res

            def sel_fct_tb(row):
                res = OrderedDict()
                selix = 0
                for sel in sels:
                    cols = self._selectors_to_columns(sel.selectors)
                    for col_ix in xrange(len(cols)):
                        alias = sel.alias or cols[col_ix]
                        if alias in res:
                            alias = "%s_%s" % (alias, selix)
                        res[alias] = row[cols[col_ix]]
                    selix += 1
                return res

            if isinstance(self.data, pd.core.frame.DataFrame):
                sel_fct = sel_fct_df
            else:
                sel_fct = sel_fct_tb
            if want_cell_coord:
                row_iter = ( OrderedDict(sel_fct(row), index=coord) for (coord, row) in row_iter )
            else:
                row_iter = ( sel_fct(row) for row in row_iter )
            # compute row types
            row_types = []
            for sel in sels:
                cols = self._selectors_to_columns(sel.selectors)
                for col in cols:
                    row_types.append(self.get_type(col))

        else:
            # with aggregation => apply agg fct
            # TODO: find a way to not keep all in memory (push down agg into kernel)
            row_iters_vals_map = OrderedDict()
            row_iters_agg_map = OrderedDict()
            for row in row_iter:
                res = OrderedDict()
                res_agg = OrderedDict()
                selix = 0
                for sel in sels:
                    if isinstance(self.data, pd.core.frame.DataFrame):
                        cols = self._selectors_to_columns(sel.selectors)
                        for col_ix in xrange(len(cols)):
                            alias = sel.alias or cols[col_ix]
                            if alias in res:
                                alias = "%s_%s" % (alias, selix)
                            res[alias] = row.loc[cols[col_ix]]
                            res_agg[alias] = sel.agg
                    else:
                        cols = self._selectors_to_columns(sel.selectors)
                        for col_ix in xrange(len(cols)):
                            alias = sel.alias or cols[col_ix]
                            if alias in res:
                                alias = "%s_%s" % (alias, selix)
                            res[alias] = row[cols[col_ix]]
                            res_agg[alias] = sel.agg
                    selix += 1
                for alias in res:
                    row_iters_vals_map.setdefault(alias, []).append(res[alias])
                    row_iters_agg_map[alias] = res_agg[alias]

            res = OrderedDict( (alias,_get_agg_fct(row_iters_agg_map[alias])(row_iters_vals_map[alias])) for alias in row_iters_vals_map.keys() )
            row_iter = ( res for x in [1] )  # wrap in generator
            # compute row types
            row_types = []
            for sel in sels:
                cols = self._selectors_to_columns(sel.selectors)
                for col in cols:
                    row_types.append('float64')  # TODO: some aggregation fcts may return other types (e.g., SUM)

        return row_types, row_iter

    def _selectors_to_slices(self, sels):
        res = [ slice(0,self.sizes[dim]) for dim in range(len(self.sizes)) ]  # start from max ranges
        if sels is not None:
            for sel in sels:
                dim = self._get_dim(sel.dimname)
                if dim >= 0 and dim < len(self.sizes):
                    if isinstance(self.data, pd.core.frame.DataFrame) and dim == 1:
                        # convert the column names to column ids if needed
                        dimvals = [self._convert_to_colnum(dimval) for dimval in sel.dimvalues]
                    elif not isinstance(self.data, pd.core.frame.DataFrame) and dim == 1:
                        # cannot slice table by column (do it later)
                        dimvals = None
                    else:
                        dimvals = sel.dimvalues
                    if dimvals is not None:
                        if len(dimvals) > 1:
                            slice_start = dimvals[0] or res[dim].start
                            slice_stop = dimvals[1] or res[dim].stop
                        elif len(dimvals) == 1 and dimvals[0] is not None:
                            slice_start = dimvals[0]
                            slice_stop = dimvals[0]+1
                        else:
                            slice_start = res[dim].start
                            slice_stop = res[dim].stop
                        slice_start = max(slice_start, res[dim].start)
                        slice_stop = min(slice_stop, res[dim].stop)
                        res[dim] = slice(slice_start, slice_stop)
        return tuple(res)

    def _get_dim(self, dimname):
        if dimname in ['row', '__dim1__']:
            return 0
        elif dimname in ['field', '__dim2__']:
            return 1
        else:
            return None

    def _gen_dataframe_filter(self, arr, cond):
        if isinstance(cond, OrConditionTuple):
            left_cond = self._gen_dataframe_filter(arr, cond.left)
            right_cond = self._gen_dataframe_filter(arr, cond.right)
            return (left_cond) | (right_cond) if left_cond is not None and right_cond is not None else (left_cond or right_cond)
        elif isinstance(cond, AndConditionTuple):
            left_cond = self._gen_dataframe_filter(arr, cond.left)
            right_cond = self._gen_dataframe_filter(arr, cond.right)
            return (left_cond) & (right_cond) if left_cond is not None and right_cond is not None else (left_cond or right_cond)
        elif isinstance(cond, ConditionTuple):
            left_cond = self._gen_dataframe_filter(arr, cond.left)
            if left_cond is None:
                return None
            # if multiple left_cond, combine via 'OR'
            return reduce(lambda x,y: (x) | (y),
                   [{
                    '=': lambda x,y: (x) == (y),
                    '!=': lambda x,y: (x) != (y),
                    '<': lambda x,y: (x) < (y),
                    '<=': lambda x,y: (x) <= (y),
                    '>': lambda x,y: (x) > (y),
                    '>=': lambda x,y: (x) >= (y)
                    }[cond.comp](single_left_cond, float(cond.right))
                    for single_left_cond in left_cond])
        elif isinstance(cond, CellSelectionTuple):
            cols = self._selectors_to_columns(cond.selectors)
            return [arr[col] for col in cols] if len(cols)>=1 else None

    def _gen_table_filter(self, arr, cond):
        if isinstance(cond, OrConditionTuple):
            left_str = self._gen_table_filter(arr, cond.left)
            right_str = self._gen_table_filter(arr, cond.right)
            return "(%s) | (%s)" % (left_str, right_str) if left_str is not None and right_str is not None else (left_str or right_str)
        elif isinstance(cond, AndConditionTuple):
            left_str = self._gen_table_filter(arr, cond.left)
            right_str = self._gen_table_filter(arr, cond.right)
            return "(%s) & (%s)" % (left_str, right_str) if left_str is not None and right_str is not None else (left_str or right_str)
        elif isinstance(cond, ConditionTuple):
            left_str = self._gen_table_filter(arr, cond.left)
            if left_str is None:
                return None
            # if multiple left_cond, combine via 'OR'
            return reduce(lambda x,y: "(%s) | (%s)" % (x,y),
                   ["%s %s %s" % (single_left_str, cond.comp if cond.comp != '=' else '==', float(cond.right))
                   for single_left_str in left_str])
        elif isinstance(cond, CellSelectionTuple):
            cols = self._selectors_to_columns(cond.selectors)
            return cols if len(cols)>=1 else None

#---------------------------------------------------------------------------------------
# Array-like object
# Contains array-specific query translations.
#---------------------------------------------------------------------------------------
class ArrayLike(TableBase):
    def __init__(self, uniq, resource, path, **kw):
        super(ArrayLike, self).__init__(uniq, resource, path, **kw)
        assert self.data is None or isinstance(self.data, tables.array.Array) or isinstance(self.data, np.ndarray)  # TODO: make this class numpy array and other arrays as subclasses?

    def get_queriable(self):
        return self

    def read(self, **kw):
        if self.data is None:
            self.info(**kw)

        assert len(self.t_ops) <= 1   # TODO: allow sequence of ops?
        query_op = self.t_ops.pop(0) if len(self.t_ops) > 0 else None
        return self.run_query(query_op=query_op, keep_dims=2)   # TODO: should be able to read from all dims (need to extend API/viewer)

    def get_slice_iter(self, slices, cond, want_cell_coord=False):
        offsets = [0]*len(slices)

        if self.data is None:
            # need to bring in data first
            self.data = self.cb(slices)
            assert isinstance(self.data, tables.array.Array) or isinstance(self.data, np.ndarray)
            # adjust slices to start from 0 since it is already sliced and remember offsets
            for d in xrange(len(slices)):
                offsets[d] = slices[d].start
            slices = tuple([slice(0, slices[d].stop-slices[d].start) for d in xrange(len(slices))])

        ###### translator for And/Or/Condition:
        #    => ( (tuple(coord), node[tuple(coord)]) for coord in np.argwhere((node[Ellipsis] > 0.0) & mask_of_subset & (node[Ellipsis] > 0.0) & mask2_of_subset) )  FOR ARRAY
        filter_exp = None
        if cond is not None:
            filter_exp = self._gen_array_filter(self.data[slices], slices, cond)

        if filter_exp is None:
            if want_cell_coord:
                # this is very slow for large arrays; avoid!
                ranges = (xrange(slices[d].start, slices[d].stop) for d in xrange(len(self.data.shape)))
                row_iter = ( (tuple([coord[d]+offsets[d] for d in xrange(len(coord))]), self.data[coord]) for coord in itertools.product(*ranges) )
            else:
                row_iter = ( self.data[slices] for x in [1] )
        else:
            # have condition
            if want_cell_coord:
                # this is very slow for large arrays; avoid!
                row_iter = ( (tuple([coord[d]+slices[d].start+offsets[d] for d in xrange(len(slices))]), self.data[slices][tuple(coord)]) for coord in np.argwhere(filter_exp) )
            else:
                row_iter = ( np.where(filter_exp, self.data[slices], self._gen_nan_array(slices)) for x in [1] )

        return row_iter

    def get_sels_iter(self, row_iter, sels, want_cell_coord=False):
        ###### translator for CellSelection:
        #    => np.mean(r[slices])   where r from FILTER                        IF pytables array
        if sels is None or sels[0].agg is None:
            # no selection, include all columns
            if want_cell_coord:
                row_iter = ( OrderedDict(row, index=coord) for (coord, row) in row_iter )
            else:
                row_iter = ( row for row in row_iter )
            # compute row types
            row_types = [ self.get_types()[0] ]  # assume all same type

        else:
            # with aggregation => apply agg fct
            # TODO: find a way to not keep all in memory (push down agg into kernel)
            row_iters_vals_map = OrderedDict()
            row_iters_agg_map = OrderedDict()
            for row in row_iter:
                res = OrderedDict()
                res_agg = OrderedDict()
                selix = 0
                for sel in sels:
                    alias = sel.alias or "agg%s"%selix
                    res[alias] = row
                    res_agg[alias] = sel.agg
                    selix += 1
                for alias in res:
                    row_iters_vals_map.setdefault(alias, []).append(res[alias])
                    row_iters_agg_map[alias] = res_agg[alias]

            res = OrderedDict( (alias,_get_agg_fct(row_iters_agg_map[alias])(row_iters_vals_map[alias])) for alias in row_iters_vals_map.keys() )
            row_iter = ( res for x in [1] )  # wrap in generator
            # compute row types
            row_types = []
            for sel in sels:
                row_types.append('float64')  # TODO: some aggregation fcts may return other types (e.g., SUM)

        return row_types, row_iter

    def _selectors_to_slices(self, sels):
        res = [ slice(0,self.sizes[dim]) for dim in range(len(self.sizes)) ]  # start from max ranges
        if sels is not None:
            for sel in sels:
                dim = self._get_dim(sel.dimname)
                if dim >= 0 and dim < len(self.sizes):
                    dimvals = sel.dimvalues
                    if dimvals is not None:
                        if len(dimvals) > 1:
                            slice_start = dimvals[0] or res[dim].start
                            slice_stop = dimvals[1] or res[dim].stop
                        elif len(dimvals) == 1 and dimvals[0] is not None:
                            slice_start = dimvals[0]
                            slice_stop = dimvals[0]+1
                        else:
                            slice_start = res[dim].start
                            slice_stop = res[dim].stop
                        slice_start = max(slice_start, res[dim].start)
                        slice_stop = min(slice_stop, res[dim].stop)
                        res[dim] = slice(slice_start, slice_stop)
        return tuple(res)

    def _get_dim(self, dimname):
        if dimname in ['row', '__dim1__']:
            return 0
        elif dimname in ['field', '__dim2__']:
            return 1
        else:
            parser = re.compile('__dim(?P<num>[0-9]+)__')
            toks = re.search(parser, dimname)
            if toks is not None:
                return int(toks.groupdict()['num'])-1
        return None

    def _gen_array_filter(self, arr, slices, cond):
        if isinstance(cond, OrConditionTuple):
            return (self._gen_array_filter(arr, slices, cond.left)) | (self._gen_array_filter(arr, slices, cond.right))
        elif isinstance(cond, AndConditionTuple):
            return (self._gen_array_filter(arr, slices, cond.left)) & (self._gen_array_filter(arr, slices, cond.right))
        elif isinstance(cond, ConditionTuple):
            # get the selection slices in the CellSelectionTuple and construct boolean array of size of incoming slices
            # with cells in selection slices set to False, all others set to True
            # (this way, slices outside of condition selection are always included, the ones inside are only included if condition holds;
            # this mirrors the behavior of table column selection with conditions on some columns and projection on others)
            sel_slices = self._selectors_to_slices(cond.left.selectors)
            mask = self._gen_mask(slices, sel_slices)
            return ({
                     '=': lambda x,y: (x) == (y),
                     '!=': lambda x,y: (x) != (y),
                     '<': lambda x,y: (x) < (y),
                     '<=': lambda x,y: (x) <= (y),
                     '>': lambda x,y: (x) > (y),
                     '>=': lambda x,y: (x) >= (y)
                    }[cond.comp](arr[Ellipsis], float(cond.right))) | mask

    def _gen_mask(self, outer_slices, sel_slices):
        mask = np.ones([s.stop-s.start for s in outer_slices], dtype=bool)
        mask_slices = self._and_slices(outer_slices, sel_slices)
        mask[[slice(mask_slices[dim].start-outer_slices[dim].start, mask_slices[dim].stop-outer_slices[dim].start) for dim in xrange(len(outer_slices))]] = False
        return mask

    def _gen_nan_array(self, slices):
        shape = tuple([s.stop-s.start for s in slices])
        return np.full(shape, np.nan)

