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
Statistics server : provides tag documents with summarization of input data retreived from
   a given URL using a given XPath expression

DESCRIPTION
===========

 The idea for the statistics service is in the sequence of filter applied to the data
 URL specifies the documents URL, which can be: gobjects, tags or dataset
 1) QUERY: [etree -> vector of objects]
    Elements are extracted from the document into the vector using XPath expression
    at this stage the vector should only comntain:
        a) tags (where values could be either numeric or string), 
        b) primitive gobjects (only graphical elements like poits and polygones...)
        c) numerics as a result of operation in XPath
 2) MAP: [vector of objects -> uniform vector of numbers or strings]
    An operator is applied onto the vector of objects to produce a vector of numbers or strings
    The operator is specified by the user and can take specific elements and produces specific result
    for example: operator "area" could take polygon or rect and produce a number
                 operator "numeric-value" can take a "tag" and return tag's value as a number
                 possible operator functions should be extensible and maintained by the stat service
 3) REDUCE: [uniform vector of numbers or strings -> summary as XML]
    A summarizer function is applied to the vector of objects to produce some summary
    the summary is returned as an XML document
    for example: summary "vector" could simply pass the input vector for output
                 summary "histogram" could bin the values of the input vector and could work on both text and numbers 
                 summary "max" would return max value of the input vector

EXTENSIONS
===========

Operations and summarizers are added into the service by simply deriving them from
appropriate base classes and writng the code in appropriate files, just that...

"""

__module__    = "stats_server.py"
__author__    = "Dmitry Fedorov and Kris Kvilekval"
__version__   = "1.4"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"


# default imports
import os
import logging
import pkg_resources
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, flash, response
from repoze.what import predicates 
from bq.core.service import ServiceController
#from bq.stats import model

log = logging.getLogger("bq.stats")

from pylons.controllers.util import abort

# imports for stats server
from lxml import etree
import sys
import inspect
import json
    
import cStringIO
from urllib import quote
from urllib import unquote

from itertools import *
from bqapi import *

# Import all required operations
import stats_operators
import stats_summarizers

from bq import data_service

################################################################################
# utils
################################################################################
def dict2url(d, mykeys=None):
    if len(d)<=0: return ''
    if mykeys is None:
        l = ['%s=%s'%(quote(i), quote(d[i])) for i in d]
    else:
        l = ['%s=%s'%(quote(i), quote(d[i])) for i in mykeys if i in d]    
    return '%s'%'&'.join(l)
      
def getNumberedArgs(d, basename):
    if basename not in d:
        return []
    l = [d[basename]]
    i = 1
    while '%s%s'%(basename, i) in d:
        l.append(d['%s%s'%(basename, i)])
        i += 1
    return l
    
def guaranteeSize(l, n):
    if len(l)<=0: return l
    if len(l)>=n: return l
    for i in range(n-len(l)):
        l.append(l[len(l)-1])
    return l  
    
def startWithEither(s, l):
    for i in l:
        if s.startswith(i): return True
    return False

################################################################################
# statsController
################################################################################

class statsController(ServiceController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()
    service_type = "stats"

    def __init__(self, server_url):
        super(statsController, self).__init__(server_url)
        self.baseuri = server_url
        self.operators = {}
        self.summarizers = {}

        # maps
        for n,item in inspect.getmembers(stats_operators):
             if inspect.isclass(item) and issubclass(item, stats_operators.StatOperator):
                  if item.name != 'StatOperator':
                      log.debug('Adding operator: %s'%item.name)   
                      self.operators[item.name] = item()        
        
        # reduces        
        for n,item in inspect.getmembers(stats_summarizers):
             if inspect.isclass(item) and issubclass(item, stats_summarizers.StatSummarizer):
                  if item.name != 'StatSummarizer':     
                      log.debug('Adding summarizer: %s'%item.name)                            
                      self.summarizers[item.name] = item()
        # done  

    @expose(content_type='text/xml')
    def maps (self, **kw):
        stream = etree.Element ('resource')
        stream.attrib['uri'] = '%s/maps'%(self.baseuri)
        for n in self.operators:
            tag      = etree.SubElement (stream, 'tag')
            tag.attrib['name']  = n           
            tag.attrib['value'] = '%s [ver %s]'%(self.operators[n].__doc__, self.operators[n].version)
        return etree.tostring(stream)   


    @expose(content_type='text/xml')
    def reduces (self, **kw):
        stream = etree.Element ('resource')
        stream.attrib['uri'] = '%s/reduces'%(self.baseuri)
        for n in self.summarizers:
            tag      = etree.SubElement (stream, 'tag')
            tag.attrib['name']  = n            
            tag.attrib['value'] = '%s [ver %s]'%(self.summarizers[n].__doc__, self.summarizers[n].version)
        return etree.tostring(stream)           


    @expose('bq.stats.templates.index')
    def index(self, **kw):
        maps = {}
        for n in self.operators:
            maps[n] = '%s [ver %s]'%(self.operators[n].__doc__, self.operators[n].version)
        reduces = {}
        for n in self.summarizers:
            reduces[n] = '%s [ver %s]'%(self.summarizers[n].__doc__, self.summarizers[n].version)
        op_keys = sorted(maps.keys())
        sum_keys = sorted(reduces.keys())      
        
        args = {}
        for k in kw:
            if not startWithEither(k, ['url', 'xpath', 'xmap', 'xreduce', 'run' ]):
                args[k] = kw[k]
          
        return { 'operators': maps, 'op_keys': op_keys, 'summarizers': reduces, 'sum_keys': sum_keys, 'opts': kw, 'args': args }


    # 400 Bad Request
    # 401 Unauthorized
    # 500 Internal Server Error
    # 501 Not Implemented
    @expose(content_type='text/xml')
    def compute (self, **kw):
        return self.xml(**kw)

    #-------------------------------------------------------------
    # Formatters - XML
    # MIME types: 
    #   text/xml
    #-------------------------------------------------------------    
    @expose(content_type='text/xml')
    def xml (self, **kw):

        d = self.compute_stats(**kw)
        
        url = kw['url']
        stream = etree.Element ('resource', type='statistic')        
        stream.set('uri', '%s/compute?%s'%(self.baseuri, dict2url({'url':url})))
        
        for i in d:
            xpath   = i.pop('xpath')
            xmap    = i.pop('xmap')
            xreduce = i.pop('xreduce')
            title   = i.pop('title')
            r = etree.SubElement (stream, 'resource', name=title, type=xreduce)            
            r.set('uri', '/stats/compute?%s'%(dict2url({ 'url':url, 'xpath':xpath, 'xmap':xmap, 'xreduce':xreduce })))
            for k in i:     
                v = i[k]
                if hasattr(v, '__iter__') and len(v)>0: 
                    v = ','.join( [quote(unicode(x).encode ('utf8')) for x in v] )
                BQTag(name=k, value=unicode(v)).toEtree(r)
        
        filename = kw.get('filename', 'stats.xml')
        try:
            disposition = 'filename="%s"'% filename.encode('ascii')
        except UnicodeEncodeError:
            disposition = 'filename="%s"; filename*="%s"'%(filename.encode('utf8'), filename.encode('utf8'))        
        response.headers['Content-Type'] = 'text/xml'
        response.headers['Content-Disposition'] = disposition       
        return etree.tostring(stream)
    
    #-------------------------------------------------------------
    # Formatters - JSON
    # MIME types: 
    #   application/json
    # Returns
    #   { fields: ['col1', 'col2', ... ],
    #     data: [ {col1: val1, col2: val2, ...}, 
    #             {col1: val1, col2: val2, ...}, 
    #             ... 
    #           ]
    #   }
    #-------------------------------------------------------------    
    @expose(content_type='application/json')
    def json (self, **kw):

        d = self.compute_stats(**kw)
        mytitles = []
        myiters = []
        for i in d:
            xpath   = i.pop('xpath')
            xmap    = i.pop('xmap')
            xreduce = i.pop('xreduce')
            title   = i.pop('title')            
            for k in i:     
                if not hasattr(i[k], '__iter__'): 
                    myiters.append([i[k]])
                else:
                    myiters.append(i[k])
                if k != xreduce:
                    mytitles.append( ('%s (%s)'%( title, k )).replace(',', ';') )
                else:
                    mytitles.append( title.replace(',', ';') )
        
        it = izip_longest(fillvalue='', *myiters)
        ts = (t for t in it)
        rows = []
        for t in ts:
            row = {}
            for i in range(0, len(mytitles)):
                row[mytitles[i]] = t[i]
            rows.append(row)
            
        res = { 'fields': mytitles, 'data': rows }
        return json.dumps(res)
       
    #-------------------------------------------------------------
    # Formatters - CSV 
    # MIME types: 
    #   text/csv 
    #   text/comma-separated-values
    #-------------------------------------------------------------           
    @expose(content_type='text/csv') 
    def csv (self, **kw):

        d = self.compute_stats(**kw)
        mytitles = []
        myiters = []
        for i in d:
            xpath   = i.pop('xpath')
            xmap    = i.pop('xmap')
            xreduce = i.pop('xreduce')
            title   = i.pop('title')            
            for k in i:     
                if not hasattr(i[k], '__iter__'): 
                    myiters.append([i[k]])
                else:
                    myiters.append(i[k])
                if k != xreduce:
                    mytitles.append( ('%s (%s)'%( title, k )).replace(',', ';') )
                else:
                    mytitles.append( title.replace(',', ';') )
                            
        it = izip_longest(fillvalue='', *myiters)
        ts = (t for t in it)
        stream = "\n".join([(', '.join([unicode(e).encode('utf8') for e in t])) for t in ts])
        
        filename = kw.get('filename', 'stats.csv')
        try:
            disposition = 'filename="%s"'% filename.encode('ascii')
        except UnicodeEncodeError:
            disposition = 'attachment; filename="%s"; filename*="%s"'%(filename.encode('utf8'), filename.encode('utf8'))             
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = disposition
        return '%s\n%s'%( ', '.join(mytitles).encode('utf8'), stream)

    def get_request (self, url, setmode):
        request = data_service.get_resource(url, view='deep')
        # if the resource is a dataset, fetch contents of documents linked in it
        if request.tag == 'dataset' and not setmode: 
            members_uri = request.get('uri')
            if members_uri is not None:
                request = data_service.get_resource('%s/value'%members_uri, view='deep')
        return request

    #-------------------------------------------------------------   
    # this function will raise exceptions of operators or summarizers cannot take requested inputs
    #-------------------------------------------------------------    
    def compute_stats (self, **kw):
        log.info('Statistics request: %s'%kw)
      
        if not 'url' in kw:
            log.debug('Request stopped: document URL is not provided')          
            abort(400, 'document URL is not provided')      
        if not 'xpath' in kw:
            log.debug('Request stopped: XPath expression not provided')              
            abort(400, 'XPath expression not provided')                                 
        if not 'xmap' in kw or not kw['xmap'] in self.operators:
            log.debug('Request stopped: requested mapping operator was not found')              
            abort(400, 'requested mapping operator was not found')
        if not 'xreduce' in kw or not kw['xreduce'] in self.summarizers:
            log.debug('Request stopped: requested reduction operator was not found')    
            abort(400, 'requested reduction operator was not found')

        url     = getNumberedArgs(kw, 'url') #kw['url']
        xpath   = getNumberedArgs(kw, 'xpath')
        xmap    = getNumberedArgs(kw, 'xmap')
        xreduce = getNumberedArgs(kw, 'xreduce')
        titles  = getNumberedArgs(kw, 'title')
        if len(titles)<=0: titles = [None]
        maxsize = max([ len(url), len(xpath), len(xmap), len(xreduce) ])
        xpath   = guaranteeSize(xpath, maxsize)        
        xmap    = guaranteeSize(xmap, maxsize)
        xreduce = guaranteeSize(xreduce, maxsize)
        titles  = guaranteeSize(titles, maxsize)           
        setmode = 'setmode' in kw


        # -----------------------------------------------------
        # QUERY
        # -----------------------------------------------------
        #etree = data_service.load(url+'?view=deep')
        #data_service.get_resource(url, view='deep', tag_query="AAA")
        # TODO: Vey inefficient now, need to request queries to the DB!!!!!!!!!!!!!!
        #request = etree.parse('F:\dima\develop\python\dataset.xml')
        if len(url)==1:
            request = self.get_request (url[0], setmode)
        
        stream = []        
        for i in range(len(xpath)):
            
            if len(url)>1:
                request = self.get_request (url[i], setmode)
            
            # -----------------------------------------------------
            # XPath
            # -----------------------------------------------------
            objects = request.xpath(xpath[i])
            if len(objects)<1: 
                log.warning('Request stopped: XPath expression %s did not return any results' % xpath[i])
                abort(500, 'XPath expression did not return any results') 
            
            # -----------------------------------------------------
            # MAP
            # -----------------------------------------------------
            vector_alpha_num = self.operators[xmap[i]](objects, **kw)
            if len(vector_alpha_num)<1:
                log.warning('Request stopped: Map operation did not return any results')
                abort(500, 'Map operation did not return any results')             
            
            # -----------------------------------------------------
            # REDUCE
            # -----------------------------------------------------
            d = self.summarizers[xreduce[i]](vector_alpha_num, **kw)
            if len(d)<1:
                log.warning('Request stopped: Summarizer operation did not return any results')                    
                abort(500, 'Summarizer operation did not return any results')                  
            d['xpath']   = xpath[i]
            d['xmap']    = xmap[i]
            d['xreduce'] = xreduce[i]
            d['title']   = titles[i] or '%s of %s for %s'%( xreduce[i], xmap[i], xpath[i] )
            stream.append(d)                  
        
        return stream        


def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    service =  statsController(uri)
    #directory.register_service ('stats', service)

    return service

def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'stats', 'public'))]

#def get_model():
#    from bq.stats import model
#    return model

__controller__ =  statsController
