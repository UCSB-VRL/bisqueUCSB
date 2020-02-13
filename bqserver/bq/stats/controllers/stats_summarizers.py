###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007 by the Regents of the University of California     ##
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
Statistics summarizers : map a vector of strings or numbers to a tag document summarizing the vector

DESCRIPTION
===========

 3) REDUCE: [uniform vector of numbers or strings -> summary as XML]
    A summarizer function is applied to the vector of objects to produce some summary
    the summary is returned as an XML document
    for example: summary "vector" could simply pass the input vector for output
                 summary "histogram" could bin the values of the input vector and could work on both text and numbers 
                 summary "max" would return max value of the input vector

EXTENSIONS
===========

Summarizers are added by simply deriving from StatSummarizer and adding your code here

"""

__module__    = "statistics_service.py"
__author__    = "Dmitry Fedorov"
__version__   = "1.0"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

from lxml import etree
import sys
import logging
import math
from urllib import quote

log = logging.getLogger('bisquik.SS.summarizers')

__all__ = [ 'StatSummarizer' ] 


################################################################################
# Base class for operators
################################################################################

class StatSummarizer (object):
    '''Maps vector of numbers or strings into an etree of a summary''' 
    name = "StatSummarizer"    
    version = '1.0'        
    def __init__(self):
        #self.server = server
        pass

    def __call__(self, v_in, **kw):
        return self.do_reduce(v_in, **kw)              
        
    def do_reduce(self, v_in, **kw):
        # this one does nothing really 
        return {}


################################################################################
# util
################################################################################  

def are_all_numbers(v):
    for n in v:
        if isinstance(n, float): continue
        elif isinstance(n, int): continue
        elif isinstance(n, long): continue
        elif isinstance(n, complex): continue
        elif n is None: continue
        else: return False
    return True                                

def string_histogram(v):
    h = {}
    for n in v:
        if n in h: h[n] += 1
        else: h[n] = 1
    return h   
    
def dict_to_lists_sorted(d):
    lk = []
    lv = []
    keys = sorted(d.keys())
    for k in keys:
        lk.append( k );
        lv.append( d[k] );
    return lk,lv
 
def histogram_edges_to_centroids(e):
    c = []
    for i in range(len(e)-1):
        c.append( (e[i]+e[i+1])/2.0 )
    return c

################################################################################
# Operator implementations
################################################################################       
        
class StatSummarizerVector (StatSummarizer):
    '''simply passes the input vector into the output''' 
    name = "vector"   
    version = '1.2'         
    def do_reduce(self, v_in, **kw):
        return { self.name:v_in }

class StatSummarizerVectorSorted (StatSummarizer):
    '''returns sorted input vector''' 
    name = "vector-sorted"   
    version = '1.1'         
    def do_reduce(self, v_in, **kw):
        v_in = sorted(v_in)
        return { self.name:v_in }

class StatSummarizerSet (StatSummarizer):
    '''returns a set with the elements of the input vector''' 
    name = "set"   
    version = '1.3'         
    def do_reduce(self, v_in, **kw):
        v_in = set(v_in)
        return { self.name:v_in }

class StatSummarizerUnique (StatSummarizerSet):
    '''returns unique elements of the input vector''' 
    name = "unique"   

class StatSummarizerSetSorted (StatSummarizer):
    '''returns a sorted set with the elements of the input vector''' 
    name = "set-sorted"   
    version = '1.1'         
    def do_reduce(self, v_in, **kw):
        v_in = set(v_in)
        v_in = sorted(v_in)
        return { self.name:v_in }

class StatSummarizerUniqueSorted (StatSummarizerSetSorted):
    '''returns sorted unique elements of the input vector''' 
    name = "unique-sorted"   

class StatSummarizerCount (StatSummarizer):
    '''returns the number of elelments''' 
    name = "count" 
    version = '1.1'           
    def do_reduce(self, v_in, **kw):
        v_in = len(v_in)
        return { self.name:v_in }          

class StatSummarizerSum (StatSummarizer):
    '''returns the sum of elelments''' 
    name = "sum"   
    version = '1.1'         
    def do_reduce(self, v_in, **kw):
        #v = math.fsum(v_in) # python 2.6
        v_in = sum(v_in)
        return { self.name:v_in } 

class StatSummarizerMax (StatSummarizer):
    '''returns the max of elelments''' 
    name = "max"  
    version = '1.1'          
    def do_reduce(self, v_in, **kw):
        if len(v_in)>0: v_in = max(v_in)          
        return { self.name:v_in } 

class StatSummarizerMin (StatSummarizer):
    '''returns the min of elelments''' 
    name = "min"  
    version = '1.1'          
    def do_reduce(self, v_in, **kw):
        if len(v_in)>0: v_in = min(v_in)          
        return { self.name:v_in } 

# only provide histogram if numpy is available
try:
    import numpy
    
    class StatSummarizerHistogram (StatSummarizer):
        '''returns the histogram of elelments, uses "numbins" with default 100''' 
        name = "histogram"   
        version = '1.2'
        def do_reduce(self, v_in, numbins=25, **kw):
            numbins = int(numbins)
            if not are_all_numbers(v_in) or len(set(v_in))<numbins:
                # compute string histogram
                h = string_histogram(v_in)
                k,v = dict_to_lists_sorted(h)
                return { self.name:v, 'bin_centroids':k }
            else:
                v = numpy.histogram(v_in, int(numbins))  
                #appendTag(response, 'bin_edges', reduce(str_join, v[1]) )
                return { self.name:v[0], 'bin_centroids':histogram_edges_to_centroids(v[1]) }

    class StatSummarizerMean (StatSummarizer):
        '''returns the mean of elelments''' 
        name = "mean"
        version = '1.1'      
        def do_reduce(self, v_in, **kw):
            v_in = numpy.mean(v_in)
            return { self.name:v_in } 
    
    class StatSummarizerMedian (StatSummarizer):
        '''returns the median of elelments''' 
        name = "median"
        version = '1.1'        
        def do_reduce(self, v_in, **kw):
            v_in = numpy.median(v_in)
            return { self.name:v_in } 
            
    class StatSummarizerStd (StatSummarizer):
        '''returns the standard deviation of elelments''' 
        name = "std"
        version = '1.1'      
        def do_reduce(self, v_in, **kw):
            v_in = numpy.std(v_in)
            return { self.name:v_in }


except ImportError, e:
    pass



