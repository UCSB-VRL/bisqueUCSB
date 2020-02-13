###############################################################################
##  Bisque                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009,2010,2011,2012,2013,2014                 ##
##     by the Regents of the University of California                        ##
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
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ''AS IS'' AND ANY         ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE         ##
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR        ##
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR           ##
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,     ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ##
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## The views and conclusions contained in the software and documentation     ##
## are those of the authors and should not be interpreted as representing    ##
## official policies, either expressed or implied, of <copyright holder>.    ##
###############################################################################
"""
SYNOPSIS
========


DESCRIPTION
===========

"""
#
# Simple routines to convert nest and unested dictionaries



def parse_nested (dct,  keys=None, sep = '.'):
    """ Create a dictionary for each host listed
     h1.key.key1 = aa
     h1.key.key2 = bb


       => { 'h1' : { 'key' : { 'key1' : 'val', 'key2' : 'bb' }}}

    @param dct: A dictionary of the form { 'h1.key.key1' : 'aa' }
    @param keys: pull only elements in keys i.e. ['h1']
    @param sep:  The character separator
    """
    nested = {}
    if isinstance (dct, dict):
        dct = dct.items()

    keys = keys or [ x[0].split(sep)[0] for x in dct ]
    for dpair, val in dct:
        path = dpair.split(sep)
        if not path[0] in keys:
            continue
        param = path[-1]
        d = nested
        for path_el in path[:-1]:
            parent = d
            d = d.setdefault(path_el, {})
            # we've reached the leaf level and there is non-dict there.
            # replace with a dict
            if not isinstance(d, dict):
                #print parent, path_el, param, val
                d = parent[path_el] = { '' : parent[path_el]}
        #print "LEAF", d.get( param),  val
        if param in d and isinstance (d[param], dict):
            if not isinstance (d[param][''], list):
                d[param][''] = [ d[param]['']  ]
            d[param][''].append (val)
        else:
            d[param] = val

    return nested


def unparse_nested (dct,  keys=None, sep='.'):
    """ Create a dictionary for each host listed
     { 'h1' : { 'key' : { 'key1' : 'val', 'key2' : 'bb' }}} ==>
     h1.key.key1 = aa
     h1.key.key2 = bb
     """
    unnested = []
    if isinstance (dct, dict):
        dct = dct.items()
    for dpair, val in dct:
        if isinstance(val, dict):
            val  = unparse_nested(val, sep=sep)
        if isinstance (val, list):
            if dpair == '':
                for v in val:
                    unnested.append( (dpair, v) )
            else:
                for k, v in val:
                    if k != '':
                        unnested.append( (sep.join ([dpair, k]), v) )
                    else:
                        unnested.append( (dpair, v) )

        else:
            unnested.append ( (dpair, val ))
    return unnested





if __name__ == "__main__":
    dct = { 'A.a.a' : 1, 'A.a.b' : 2, 'A.b.a' : 3, 'B.a.a' : 4, 'C.a' : 5 }
    nest= parse_nested(dct, ['A', 'B'] )
    print nest
    print unparse_nested (nest)
    print parse_nested(dct)

    dct = { 'A.a.a' : 1, 'A.a.b' : 2, 'A.b.a' : 3, 'A.a.a.b' : 4, 'C.a' : 5 }
    print parse_nested(dct, ['A'] )


    dct = [ ('A.a.a', 1) , ('A.a.b',  2) , ('A.b.a' ,  3) , ('A.a.a.b' , 4) , ('A.a.a' ,  5) ]
    print parse_nested(dct, ['A'] )
    #assert dct == {'A': {'a': {'a': [1, {'b': 4}, 5], 'b': 2}, 'b': {'a': 3}}}


    dct = [ ('A.a.a', 1) , ('A.a.b',  2) , ('A.b.a' ,  3) , ('A.a.a.b' , 4) , ('A.a.a' ,  5), ('A.a.a.b.c' , 6)]
    nest =  parse_nested(dct, ['A'] )
    print nest
    print unparse_nested (nest)
