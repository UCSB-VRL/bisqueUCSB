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
SYNOPSIS
========


DESCRIPTION
===========

   The module server coordinate the execution of modules otherwise
   known as MEX.

   Clients can request an execution of a particular module by
   preparing a MEX document
   (see http://biodev.ece.ucsb.edu/projects/bisquik/wiki/Developer/ModuleSystem/MexRequestSpecification)
   and POST it the module server.
   The module server finds an appropiate engine (i.e. a node that can
   actually execute the module), registers the MEX and launches it on
   the engine.  It then return the mex uri so that the client can
   periodically check the mex status untile FINISHED or FAILED

   The module server also responds to requests by engines (engine_server)
   for inclusion/exclustion the compute grid.   Each engine has a
   number of installed modules which it communicates the module server
   in a registration document.



   module-> engine_list


"""
import os
import socket
import copy
import time
import logging
import urlparse
#import urllib
import itertools
import csv
#import numbers
from datetime import datetime
from operator import mul
from lxml import etree
from collections import OrderedDict

import tg
import transaction
from paste.proxy import make_proxy
from pylons.controllers.util import abort
from tg import controllers, expose, config, request, override_template
from tg import require
# pylint: disable=E0611,F0401
from repoze.what.predicates import not_anonymous
#from tgext.asyncjob import asyncjob_perform, asyncjob_timed_query


from bqapi import BQServer
from bq import data_service
from bq.util import http
from bq.util.xmldict import d2xml
from bq.util.thread_pool import WorkRequest, NoResultsPending
from bq.util.bisquik2db import bisquik2db  #, load_uri
from bq.util.hash import is_uniq_code
from bq.core.identity import  set_admin_mode, set_current_user, get_username
#from bq.core.permission import *
from bq.core.service import ServiceController
from bq.core.model import DBSession

from bq.data_service.controllers.resource_query import RESOURCE_READ, RESOURCE_EDIT
from bq.data_service.controllers.resource import Resource
from bq.data_service import resource_controller
from bq.data_service.model import  ModuleExecution


log = logging.getLogger('bq.module_server')


_min_submexes = 4        # min number of sub mexes (TODO: should be number of expected compute nodes)
_max_submexes = 10000    # max number of sub mexes


def request_host():
    "Return host of current request"
    try:
        host_url = request.host_url
        log.debug ("REQUEST %s" , host_url)
    except TypeError:
        log.warn ("TYPEERROR on request")
        host_url = ''
    return host_url


class MexDelagate1(controllers.TGController):

    def __init__(self, url, runner):
        pass


class MexDelegate (Resource):
    def __init__(self,  url, runner = None):
        super(MexDelegate, self).__init__(uri = url)
        self.runner = runner
        log.info ("mexdelegate %s" , self.url)

    def remap_uri (self, mex):
        """
            sets the mex url to mex document

            @param: mex - etree mex document
        """
        host_url = request_host()
        mexid = mex.get('resource_uniq')
        if mexid:
            log.debug ('delegate remap -> %s' % self.url)
            bq=BQServer()
            if host_url:
                bq.root = host_url
            mexurl = bq.prepare_url('%s%s'%(self.url,mexid)) #adds host url if no host if provided in mexurl
            mex.set ('uri', mexurl)

#        uri = mex.get('uri')
#        if uri:
#            #host_url = request_host()
#            mexid = uri.rsplit('/',1)[1]
#            log.debug ('remap -> %s' , self.url)
#            mex.set ('uri', "%s%s" % (self.url, mexid))

    def load(self, token):
        log.debug ("load of %s " , tg.request.url)
        self.mex_request_url = tg.request.url
        try:
            if is_uniq_code(token):
                return data_service.resource_load ( uniq = token)
            return data_service.resource_load(ident=int(token))
        except ValueError, e:
            abort (404)
        except Exception:
            log.exception ('While loading:')
            abort(404)
        return None
        #return load_uri(tg.request.url)

    def create(self, **kw):
        return ""

    @expose(content_type='text/xml')
    def dir(self, resource, **kw):
        parent = getattr(self, 'parent',None)
        log.info ('MEX DIR %s ' , parent)
        return ""


    @expose()
    @require(not_anonymous())
    def new(self, factory, xml, **kw):
        log.info ("MEX NEW")
        mex = xml
        if isinstance (xml, basestring):
            mex = etree.XML (xml)
        if mex.tag == "request":
            mex = mex[0]
        mex = self.create_mex(mex)
        response = etree.tostring(mex)
        tg.response.headers['Content-Type'] = 'text/xml'
        return response


    def create_mex(self, mex):
        if mex.get('value') is None:
            mex.set ('value', "PENDING")
        etree.SubElement(mex, 'tag',
                         name="start-time",
                         value=time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime()))

        log.debug ("MexDelegate %s" , etree.tostring (mex))
        #kw.pop('view', None)
        #response =  self.delegate.new (factory, mex, view='deep',**kw)
        mex = data_service.new_resource (mex, view='deep')
        self.remap_uri(mex)
        mex_id = mex.get('uri').rsplit('/', 1)[1]
        if self.runner:
            self.runner.submit (mex_id)
        return mex

    @expose()
    @require(not_anonymous())
    def modify(self, resource, xml, view=None, **kw):
        """
        Modify the mex in place.  Use to update status
        """
        #return self.delegate.modify (resource, xml, **kw)
        log.info('MEX MODIFY %s', tg.request.url)
        mex = xml
        if isinstance (xml, basestring):
            mex = etree.XML (xml)
        mex = check_mex(mex)
        mex = data_service.update(mex, view=view)
        self.remap_uri (mex)
        tg.response.headers['Content-Type'] = 'text/xml'
        return etree.tostring (mex)

    @expose()
    @require(not_anonymous())
    def get(self, resource, view=None, **kw):
        """
        fetches the resource, and returns a representation of the resource.
        """
        #mex = data_service.get_resource(resource, view=view)

        parts = urlparse.urlparse (tg.request.url)
        path = "/".join (parts.path.split ('/')[3:])
        #remove the /module_servce/mex from the path
        mex = data_service.load (path, astree=True, view=view, **kw)

        self.remap_uri (mex)
        tg.response.headers['Content-Type'] = 'text/xml'
        return etree.tostring (mex)

    @expose()
    @require(not_anonymous())
    def append(self, resource, xml, view=None, **kw):
        """
        Append a value to the mex
        """
        log.info('MEX APPEND %s', tg.request.url)
        mex = xml
        if isinstance (xml, basestring):
            mex = etree.XML(xml)
        mex = check_mex(mex)
        mex = data_service.update(mex, view=view)
        #mex =  data_service.append_resource (resource, xml, **kw)
        self.remap_uri (mex)
        tg.response.headers['Content-Type'] = 'text/xml'
        return etree.tostring (mex)


    @expose(content_type="text/xml")
    def delete(self, resource,  **kw):
        """
        Delete the resource from the database
        """
        log.info('MEX DELETE')
        raise abort(501)


def read_xml_body():
    clen = int(tg.request.headers.get('Content-Length', 0))
    content = tg.request.headers.get('Content-Type')
    if clen and content.startswith('text/xml') or content.startswith('application/xml'):
        return etree.XML(tg.request.body_file.read(clen))
    return None


def create_mex(module, name, mex = None, **kw):
    if isinstance(module, basestring):
        module = data_service.get_resource(module, view='deep')
    inputs = module.xpath('./tag[@name="inputs"]')
    formal_inputs = inputs and inputs[0]
    if mex is None:
        real_params = dict(kw)
        mex = etree.Element('mex',
                            name = module.get('name'),
                            value = 'PENDING', type = module.get('uri'))
        inputs = etree.SubElement(mex, 'tag', name='inputs')
        #mex_inputs = etree.SubElement(mex, 'tag', name='inputs')
        for mi in formal_inputs:
            param_name = mi.get('name')
            log.debug ('param check %s' , param_name)
            if param_name in real_params:
                param_val = real_params.pop(param_name)
                #etree.SubElement(mex_inputs, 'tag',
                etree.SubElement(inputs, 'tag',
                                 name = param_name,
                                 value= param_val)
                log.debug ('param found %s=%s' , param_name, param_val)
        return mex
    # Process Mex
    mex.set('name', name)
    mex.set('value', 'DISPATCH')
    mex.set('type', module.get('uri'))

    log.debug('mex original %s' , etree.tostring(mex))
    # Check that we might have an iterable resource in mex/tag[name='inputs']
    #
    # <mex> <tag name="execute_options">
    #   <tag name="iterable" value="resource_url" type="dataset">
    #        <tag name="xpath" value="./value/@text'/>
    #   </tag>
    #   <tag name="iterable" value="RefFrameZDir" type="list" />     comma-separated list of values or '...'
    #   <tag name="coupled_iter" value="true" />                     couple both
    #   <tag name="blocked_iter" value="true" />                     blocked iteration (TODO: add cost estimates)
    # </tag> </mex>
    iterables = mex.xpath('./tag[@name="execute_options"]/tag[@name="iterable"]')
    if len(iterables)==0:
        return mex

    # check for "coupled_iter" execution option
    coupled_iters = mex.xpath('./tag[@name="execute_options"]/tag[@name="coupled_iter"]')
    coupled_iter = len(coupled_iters) > 0 and (coupled_iters[0].get('value', 'false').lower() == 'true')
    log.debug("coupled_iter %s", coupled_iter)

    # check for "blocked_iter" execution option
    blocked_iters = mex.xpath('./tag[@name="execute_options"]/tag[@name="blocked_iter"]')
    iter_blocksize = int(config.get('bisque.module_service.blocksize', 1)) if len(blocked_iters) > 0 and (blocked_iters[0].get('value', 'false').lower() == 'true') else 1
    log.debug("iter_blocksize %s", iter_blocksize)

    # Build dict of iterable input names ->   dict of iterable types -> iter expressions
    iters = {}
    for itr in iterables:
        resource_tag = itr.get('value')
        resource_type = itr.get('type')
        resource_iterexpr = './value/text()' if resource_type not in ['list'] else '@'+resource_type
        for sub in itr:
            if sub.get('name') == 'xpath':
                # override of extraction expression
                resource_iterexpr = sub.get('value')
        iters.setdefault(resource_tag, {})[resource_type] =  resource_iterexpr
    log.debug ('iterables in module %s' , iters)

    # Find an iterable tags (that match name and type) in the mex inputs, add them mex_tags
    mex_inputs = mex.xpath('./tag[@name="inputs"]')[0]
    mex_tags = {}   # iterable_input name :  [ mex_xml_node1, mex_xml2 ]
    for iter_tag, iter_d in iters.items():
        for iter_type in iter_d.keys():
            log.debug ("checking name=%s type=%s" , iter_tag, iter_type)
            resource_tag = mex_inputs.xpath('.//tag[@name="%s" and @type="%s" and @value]' % (iter_tag, iter_type))
            if len(resource_tag):
                # Hmm assert len(resource_tag) == 1
                mex_tags[iter_tag] = resource_tag[0]
    log.debug ('iterable tags found in mex %s' , mex_tags)

    # all_iterables is list of all iter lists:
    # [ [(tag1, val1), (tag1, val2), ...], [(tag2, valx), (tag2, valy), ...], ... ]
    all_iterables = []
    # for each iterable found in the mex inputs, check the resource type
    for iter_tag, iterable in mex_tags.items():
        resource_value = iterable.get('value')
        resource_type = iterable.get('type')
        resource_iterexpr = iters[iter_tag][resource_type]
        if resource_type == 'list':
            # list type: value is comma-separated list itself
            members = csv.reader([resource_value], skipinitialspace=True).next()
            if '...' in members:
                if members[0] != '...' and members[1] == '...' and members[2] != '...':
                    # case "a, ..., z"
                    try:
                        start = int(members[0])
                        end = int(members[2])
                        step = 1 if start<end else -1
                    except ValueError:
                        try:
                            start = float(members[0])
                            end = float(members[2])
                            step = 1.0 if start<=end else -1.0
                        except ValueError:
                            log.error("illegal list enumeration")
                            return mex
                elif members[0] != '...' and members[1] != '...' and members[2] == '...' and members[3] != '...':
                    # case "a, b, ..., z"
                    try:
                        start = int(members[0])
                        end = int(members[3])
                        step = int(members[1])-int(members[0])
                        if step == 0:
                            step = 1
                    except ValueError:
                        try:
                            start = float(members[0])
                            end = float(members[3])
                            step = float(members[1])-float(members[0])
                        except ValueError:
                            log.error("illegal list enumeration")
                            return mex
                else:
                    log.error("illegal list enumeration")
                    return mex
                if (start < end and step < 0) or (start > end and step > 0):
                    log.error("illegal list enumeration")
                    return mex
                members = []
                val = start
                while True:
                    members.append(val)
                    if len(members)/iter_blocksize > _max_submexes:
                        log.error("too many combinations (>%s)" % _max_submexes*iter_blocksize)
                        return mex
                    valold = val
                    val += step
                    if val == valold or not((start < end and val <= end) or (start > end and val >= end)):   # step may be too small to affect val
                        break
                log.debug ('enumeration "%s" expanded to "%s..."' % (resource_value, str(members)[:100]))
        else:
            # must be dataset, assume resource_iterexpr is xpath
            resource = data_service.get_resource(resource_value, view='deep')
            # if the fetched resource doesn't match the expected type, then skip to next iterable
            if not (resource_type == resource.tag or resource_type == resource.get('type')):
                continue
            members = []
            for value in resource.xpath(resource_iterexpr):
                members.append(str(value))
                if len(members)/iter_blocksize > _max_submexes:
                    log.error("too many combinations (>%s)" % _max_submexes*iter_blocksize)
                    return mex
            log.debug ('iterated xpath %s members %s...' , resource_iterexpr, members[:100])
        # add all values to this iter_tag
        all_iterables.append([(iter_tag, value) for value in members])

    log.debug("all iterable values: %s", str(all_iterables))

    all_step_params = []
    if coupled_iter:
        # Generate coupled list of values:
        # tag1:val1, tag2:valx, tag3:vala
        # tag1:val2, tag2:valy, tag3:valb
        # ...
        if max([len(sublist) for sublist in all_iterables])/iter_blocksize > _max_submexes:   # safety check
            log.error("too many combinations (>%s)" % _max_submexes)
            return mex
        list_lengths = [len(sublist) for sublist in all_iterables]
        max_list_length = max(list_lengths)
        for step in range(0, max_list_length):
            single_step_params = {}
            for sublist in all_iterables:
                iter_tag, value = sublist[int(step*len(sublist)/max_list_length)]
                single_step_params[iter_tag] = value
            all_step_params.append(single_step_params)
    else:
        # Generate a "matrix" of iterable values:
        # tag1:val1, tag2:valx, tag3:vala
        # tag1:val2, tag2:valx, tag3:vala
        # ...
        # tag1:val1, tag2:valy, tag3:vala
        # ...
        if reduce(mul, [len(sublist) for sublist in all_iterables], 1)/iter_blocksize > _max_submexes:   # safety check
            log.error("too many combinations (>%s)" % _max_submexes)
            return mex
        for iter_combo in itertools.product(*all_iterables):
            single_step_params = {}
            for iter_tag, value in iter_combo:
                single_step_params[iter_tag] = value
            all_step_params.append(single_step_params)

    # ensure we have at least _min_submexes blocks
    total_steps = len(all_step_params)
    if total_steps == 0:
        total_steps = 1
    if iter_blocksize > 1 and (total_steps+iter_blocksize-1)/iter_blocksize < _min_submexes:
        iter_blocksize = max((total_steps+_min_submexes-1)/_min_submexes, 1)
        log.debug("adjusted blocksize to %s" % iter_blocksize)

    # Create SubMex sections with original parameters replaced with iterated members
    multi_subinputs = []
    single_step_cnt = 0
    for single_step_params in all_step_params:
        subinputs = copy.deepcopy(mex_inputs)
        # replace the iterated params
        for iter_tag, value in single_step_params.iteritems():
            resource_tag = subinputs.xpath('.//tag[@name="%s"]' % iter_tag)[0]
            if isinstance(value, etree._Element):
                elem = etree.SubElement(resource_tag.getparent(), 'tag', name=iter_tag)
                if value.get('type'):
                    elem.set('type', value.get('type'))
                for kid in value:
                    elem.append(copy.deepcopy(kid))
            else:
                etree.SubElement(resource_tag.getparent(), 'tag', name=iter_tag, value=str(value))
            resource_tag.getparent().remove (resource_tag)
        multi_subinputs.append(subinputs)
        single_step_cnt += 1
        if len(multi_subinputs) >= iter_blocksize or single_step_cnt >= len(all_step_params):
            submex = etree.Element('mex', name=name, type=module.get ('uri') if iter_blocksize == 1 else 'block')
            for subinputs in multi_subinputs:
                singlemex = submex if iter_blocksize == 1 else etree.SubElement(submex, 'mex', name=name, type=module.get ('uri'))
                input_tag = etree.SubElement(singlemex, 'tag', name='inputs')
                for kid in subinputs:
                    input_tag.append(kid)
            mex.append(submex)
            multi_subinputs = []

    log.debug('mex rewritten-> %s' , etree.tostring(mex))
    return mex


def check_mex(mex):
    if mex.tag == "request":
        mex = mex[0]
    if mex.get ('value') in ['FINISHED', 'FAILED']:
        etree.SubElement(mex, 'tag',
                         name="end-time",
                         value=time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime()))
    return mex



from tg import  session, request
from paste.registry import Registry
from beaker.session import Session, SessionObject
from pylons.controllers.util import Request

# pylint: disable=W0102
def async_dbaction (func, args=[], params={}):
    log.debug ('ASYNCH_DB %s %s %s' , str(func), str(args), str(params))
    transaction.begin()
    try:
        log.debug ('ASYNCH_DB: BEGIN')
        func(*args, **params)
        transaction.commit()
    except Exception:
        log.exception ('ASYNCH_DB %s %s %s' , str(func), str(args), str(params))
        transaction.abort()
    config.DBSession.remove()

def NO_action(module, mex, username):
    log.debug ('NO_ACTION %s %s %s' , module, mex, username)


def wait_for_query (query, retries = 10, interval = 1):
    log.debug ("WAIT query %s" , str(query))
    counter = retries
    time.sleep(1)
    found = query.first()
    while not found and counter:
        time.sleep(interval)
        counter -= 1
        found = query.first()
    return found

def POST_mex (service_uri, mex, username):
    "POST A MEX in a subthread"
    mex_url =  mex.get ('uri')
    mex_uniq = mex.get('resource_uniq')

    log.debug ("MEX Dispatch : waiting for mex")
    #Instance of 'scoped_session' has no 'query' member
    # pylint: disable=E1101
    transaction.begin()
    mexq = wait_for_query (DBSession.query(ModuleExecution).filter_by (resource_uniq =  mex_uniq))
    transaction.commit()
    if mexq is None:
        log.error('Mex not in DB: abondoning dispatch')
        POST_error(mex_url, username, {'status':'500'}, '')
        return

    mex_token = "%(user)s:%(uniq)s" % dict(user=username, uniq=mex_uniq)
    log.info("DISPATCH: POST %s  with %s for %s" , service_uri,  mex_token, mex_url )

    body = etree.tostring(mex)
    try:
        resp, content = http.xmlrequest(urlparse.urljoin(service_uri ,"execute"), "POST",
                                        body = body,
                                        headers = {'Mex': mex_uniq,
                                                   'Authorization' : "Mex %s" % mex_token})
    except socket.error:
        resp = {'status':'503', }
        content = ""
    status = resp.get('status')
    log.info ("DISPATCH: RESULT %s (%s) ->%s", service_uri, mex_url, status)
    log.debug("DISPATCH: RESULT %s", content)
    try:
        status = int(status)
    except (TypeError, ValueError):
        pass
    if status != 200:
        POST_error(mex_url, username, resp, content)


def POST_error (mex_url, username, resp, content):
    # Check if we recieved a valid mex response (may have error information)
    mextree = None
    try:
        mextree = etree.XML(content)
        if  mextree.tag == 'response':
            mextree = mextree[0]
        if mextree.tag != "mex":
            mextree = None
    except etree.ParseError:
        log.warn("Bad Mex Content %s" , content)

    if mextree is None:
        mextree = etree.Element ('mex', uri=mex_url)
    mextree.set('value', 'FAILED')
    etree.SubElement(mextree, 'tag',
                     name="end-time",
                     value=time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime()))
    etree.SubElement (mextree, 'tag',
                      name="error_message",
                      value="Problem in dispatch:%s:%s" % (resp['status'], getattr(resp,'reason','Unavailable')))
    log.debug ("MexError: %s " , etree.tostring(mextree))
    # Need to setup current user who is running mex/
    registry = Registry()
    registry.prepare()
    registry.register(session, SessionObject({}))
    registry.register(request, Request.blank('/'))
    request.identity  = {}
    transaction.begin()
    set_current_user (username)
    bisquik2db(mextree)
    transaction.commit()

def POST_over (request, result):
    log.debug ('CLEANING workers %s -> %s', str(request), str(result))
    if request.exception:
        log.error ('An exception occured in %s' % request)


#from repoze.what.predicates import Any, is_user, has_permission
class ServiceDelegate(controllers.WSGIAppController):
    """Create a proxy for the particular service addressable by the module name
    """

    def __init__(self, name, service_url, module, mexurl):
        self.name = name
        self.module = module
        self.mexurl = mexurl
        if not service_url[-1] =='/':
            service_url = service_url + '/'

        self.service_url = service_url
        proxy = make_proxy(config, service_url)
        super(ServiceDelegate, self).__init__(proxy)

    #@require(not_anonymous(msg='You need to log-in to run a module'))
    @expose()
    def _default (self, *args, **kw):
        log.info ("PROXY request %s" , '/'.join(args))
        try:
            html = super(ServiceDelegate, self)._default(*args, **kw)
        except socket.error:
            log.info('service %s at %s is not available' , self.name, self.service_url)
            override_template(self._default, "genshi:bq.core.templates.master")
            abort(503, 'The service provider for %s at %s is unavailable' % (self.name, self.service_url))
        #log.info("Service proxy return status %s body %s" % (tg.response.status_int, html))
        return html
        #html = etree.HTML (html[0])
        #self.add_title(html, 'HELLO')
        #return etree.tostring(html)

    @require(not_anonymous(msg='You need to log-in to run a module'))
    @expose(content_type='text/xml')
    def execute(self, **kw):
        log.info ('EXECUTE %s with %s' , str(self.module), str(kw))
        mex = (tg.request.method.lower() in ('put', 'post') and read_xml_body()) or None
        mex = create_mex(self.module.get ('uri'), self.name, mex=mex, **kw)
        etree.SubElement(mex, 'tag',
                         name="start-time",
                         value=time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime()))
        mex = data_service.new_resource (mex, view='deep')
        transaction.commit() # NO ACTIVE TRANSACTION

        self.remap_uri(mex)
        log.debug ("SCHEDULING_MEX %s %s", self.module.get ('uri'), mex.get ('uri'))
        req = WorkRequest (async_dbaction, [ POST_mex, [ self.service_url, mex, get_username() ]],
                           callback = POST_over, exc_callback = POST_over)
        req = tg.app_globals.pool.putRequest(req)
        #req = tg.app_globals.pool.putRequest(WorkRequest (POST_mex, [self.module, mex, get_username() ]))
        log.debug ("Scheduled %s exception(%s)" , str(req), str(req.exception))
        #req = tg.app_globals.pool.wait_for(req)

        return etree.tostring (mex)

    @expose(content_type='text/xml')
    def kill(self, *args, **kw):
        log.info ('KILL %s with %s %s' , str(self.module), str(args), str(kw))
        if tg.request.method.lower() not in ('put', 'post'):
            abort(405, 'Kill operation requires PUT or POST method')
        if len(args) != 1:
            abort(405, 'Kill operation requires mex id')

        mex_uniq = args[0]
        mex_token = "%(user)s:%(uniq)s" % dict(user=get_username(), uniq=mex_uniq)

        try:
            resp, content = http.xmlrequest(urlparse.urljoin(self.service_url, "kill/"+mex_uniq), "POST",
                                            headers = {'Mex': mex_uniq,
                                                       'Authorization' : "Mex %s" % mex_token})
        except socket.error:
            resp = {'status':'503', }
            content = ""
        status = resp.get('status')
        log.debug("DISPATCH: RESULT %s %s", status, content)
        return ''

    def remap_uri (self, mex):
        """
            sets the mex url to mex document

            @param: mex - etree mex document
        """
        host_url = request_host()
        mexid = mex.get('resource_uniq')
        log.debug ('delegate remap -> %s' % self.mexurl)
        bq=BQServer()
        if host_url:
            bq.root = host_url
        mexurl = bq.prepare_url('%s%s'%(self.mexurl,mexid)) #adds host url if no host if provided in mexurl
        mex.set ('uri', mexurl)

    # Example process
    #from lxml.html import builder as E
    #def add_title(self, html, title):
    #    head = html.xpath('./head')
    #    head = (len(head) and head[0]) or None
    #    if head is None:
    #        head = E.HEAD()
    #        html.insert (0, head)
    #    el = head.xpath('./title')
    #    el = (len(el) and el[0]) or None
    #    if el is  None:
    #        el = E.TITLE(title)
    #    else:
    #        el.text = title
    #    head.insert(0, el)


#############################################################################
# Module server

class ModuleServer(ServiceController):
    """Module server provides services for finding and executing modules
    """
    service_type = "module_service"

    def __init__(self, server_url = None):
        super(ModuleServer, self).__init__(uri = server_url)

        self.runner = None
        self.__class__.mex = self.mex = MexDelegate (self.fulluri + 'mex',
                                                     self.runner)
        self.__class__.modules = self.modules = resource_controller ("module" , cache=False )
        self.__class__.engine = self.engine = EngineResource (server_url,
                                                              self.modules)
        #self.load_services()
        self.service_list = {}

    def load_services_OLD(self):
        "(re)Load all registered service points "

        services = data_service.query('service')
        service_list = {}
        for service in services:
            log.debug ("FOUND SERVICE: %s" , etree.tostring(service))
            engine = service.get('value')
            module = service.get('type')
            name = service.get('name')
            service = ServiceDelegate(name, engine, module, self.mex.url)
            service_list[name] = service
            #setattr(self.__class__, name , )
            log.info ("SERVICE PROXY %s -> %s " , name, engine)

        return service_list
        #self.runner.start()


    def load_services(self, name=None, set_admin=False, **kw):
        """
            Access to registered services through the module service

            @param: name - if name is provided the name will be checked with the
            registered modules. If the module name is found to be registered
            the module xml document will be returned. If nothing is provided
            a list of registered modules will be returned including both public
            and private modules for the user that is requesting.

            @param: set_admin - allows the load service to check for private modules
            (WARNING: only allow for module registration to not allow the user
            to look up other users private moduels)

            @param: kw - data service query args pass through
        """
        log.debug ("LOADING SERVICES %s %s", name, kw)
        if set_admin: #give temporary all system access to search for all the names
            user = get_username()
            set_admin_mode()

        if name:
            #modules = data_service.query('module', name=name, wpublic='1', view='deep')
            modules = data_service.query('module', name=name, **kw)
        else:
            #modules = data_service.query('module', wpublic='1', view='deep')
            modules = data_service.query('module', **kw)

        service_list = OrderedDict()
        for module in modules.xpath('module'):
            log.debug ("FOUND module: %s" , (module.get('uri')))
            engine = module.get('value')
            name = module.get('name')
            uniq = module.get('resource_uniq')
            log.info ("SERVICE PROXY %s -> %s" , str(name), str(engine))
            if name and engine :
                if not name in service_list: #names are protected
                    service_list[name] = ServiceDelegate(name, engine, module, self.mex.fulluri)

        if set_admin: #remove all system access
            set_current_user(user)
        return service_list
        #self.runner.start()


    @expose()
    def _lookup(self, service, *rest):
        """
            Proxy an engine service registered to the local module service
        """
        log.info('service lookup for %s' , str( service))
        proxy = self.service_list.get(service)
        if proxy is None:
            self.service_list = self.load_services(wpublic='1')
            proxy = self.service_list.get(service)
        return proxy, rest


    #@expose(content_type='text/xml')
    #def default(self, *path, **kw):
    #    log.info ("default : %s" % str(path))
    #    kw['wpublic']='1'
    #    #kw['view'] = 'deep'
    #    return self.modules.default(*path, **kw)

    @expose(content_type='text/xml')
    def index (self, **kw):
        """
            Return the list of active modules as determined by the registered services
        """
        kw.setdefault('wpublic', '1')
        kw.setdefault ('view','short')
        if 'set_admin' in kw:
            kw.pop('set_admin') #protect from setting admin
        #xml= self.modules.default(**kw)
        #modules = etree.XML(xml)
        #log.debug ("all modules = %s " % xml)

        try:
            tg.app_globals.pool.poll(block=False)
        except NoResultsPending:
            pass

        resource = etree.Element('resource', uri = self.uri)
        services =  self.load_services(**kw)
        for service in services.values():
            resource.append(service.module)
        return etree.tostring (resource)


    @expose(template='bq.module_service.templates.register')
    @require(not_anonymous())
    def register(self,**kw):
        "Show module registration page for module writers"
        return dict()


    @expose(content_type='text/xml')
    @require(not_anonymous())
    def register_engine(self, **kw):
        """
            registers a module from an engine service by posting module definition to
            data service
            (requires: a post and a request.body)

            @return - posted module to data service
        """
        #set_admin_mode()
        log.info ("register_engine")

        http_method = request.method.upper()

        try:
            definition = etree.fromstring(request.body)
        except:
            log.debug("Defintion has malformed xml")
            abort(400)

        if definition.tag != 'module':
            abort(400)

        if http_method=='POST' and (definition is not None):

            #check to see if module has the same name with all modules registered
            if len(self.load_services(definition.attrib.get('name'), set_admin=True, wpublic=True))>0:
                log.info ("Engine is already registered by that name")
                abort(405, 'Engine is already registered by that name')
            module = data_service.new_resource(definition, **kw)


            #xml =  self.engine._default (**kw)
            #update service list
            self.service_list  = self.load_services(wpublic='1')
            return etree.tostring(module)
        abort(400)


#    @expose(content_type='text/xml')
#    @require(not_anonymous())
#    def unregister_engine(self, engine_uri, module_uri=None, **kw):
#        'Remove a service record'
#        #set_admin_mode()
#        log.info ("unregister_engine %s %s %s " , engine_uri, module_uri, str(kw))
#        engine_uri = engine_uri.rstrip ('/')
#        if module_uri is None:
#            modules = data_service.query('module', value=engine_uri)
#            if len(modules) == 0:
#                abort(403, 'No module found with engine %s' % (engine_uri))
#            elif len(modules)==1:
#                module_uri = modules[0].get ('uri')
#                name = modules[0].get('name')
#            else:
#                abort(403, "multiple modules with uri %s, please specify module_uri" % engine_uri)
#        log.debug ('unregister %s at %s', module_uri, engine_uri)
#        module = etree.Element ('module', uri=module_uri, value = '')
#        data_service.update (module)
#        log.info ('UNREGISTERed  %s (%s)' , name, module_uri)
#        self.load_services()
#        return "<resource/>"

    @expose(content_type='text/xml')
    @require(not_anonymous())
    def unregister_engine(self, resource_uniq, **kw):
        """
            Removes a registered service by its name by leaving its value
            blank

            @param: resource uniq - the resource uniq of the module one wants remove

            @return - returns updated module
        """
        'Remove a service record'
        #set_admin_mode()
        log.info ("unregister engine")
        try:
            module = data_service.resource_load(resource_uniq, action=RESOURCE_EDIT, view='short')
            #module = data_service.get_resource(resource_uniq)
        except IndexError:
            abort(400)

        if module is not None:
            if module.tag == 'module':
                module.attrib['value'] = '' #needs to be changed in .06
                module = data_service.update(module, **kw)
                return etree.tostring(module)
            else:
                log.info("Resource not a module")
                abort(400, "Resource not a module")
        else:
            log.info ("Engine Not found")
            abort(404, "Engine Not found")

        #update service list
        self.service_list  = self.load_services(wpublic='1')
        #module_list = self.load_services(module_name)

    def execute(self, module_uri, **kw):
        mex = etree.Element ('mex', module = module_uri)
        for k,v in kw.items():
            # KGK: Filter by module items?
            etree.SubElement(mex, 'tag', name=k, value=v)
        log.info ("EXECUTE %s" , etree.tostring (mex))
        return self.mex.create_mex(mex)

    @expose('bq.module_service.templates.register')
    def register_module(self, name=None, module=None):
        return dict ()

    @expose(content_type="text/xml")
    def services(self):
        log.info("service list")
        x = d2xml (self.servicelist())
        return etree.tostring(x)

    def begin_internal_mex(self, name='session', value='active', mex_type = "session"):
        mex = etree.Element('mex', name=name, value=value, hidden='true', type=mex_type)
        if name:
            mex.set('name',name)
        #etree.SubElement(mex, 'tag',
        #                 name="start-time",
        #                 value=time.strftime("%Y-%m-%d %H:%M:%S",
        #                                     time.localtime()))

        #kw.pop('view', None)
        #response =  self.delegate.new (factory, mex, view='deep',**kw)
        mex = data_service.new_resource (mex, view='deep')
        #return mex.get ('uri').rsplit('/', 1)[1]
        return mex

    def end_internal_mex(self, mexuri):
        mex = etree.Element('mex', value="FINISHED", uri=mexuri)
        #etree.SubElement(mex, 'tag',
        #                 name="end-time",
        #                 value=time.strftime("%Y-%m-%d %H:%M:%S",
        #                                     time.localtime()))

        mex = data_service.update (mex)
        return mex


#######################################
# ENGINE
class EngineResource (Resource):
    """Manage the Engine resources through the web

    Engines are WebAddressable modules
    Class allows engine to register and withdraw availability
    to execute module classes
    """
    def __init__(self, url, module_resource):
        super(EngineResource, self).__init__(uri = url)
        #self.url = url
        self.module_resource = module_resource

    @expose()
    def dir(self, resource, **kw):
        """Show all endpoint for modules
        """

        response = etree.Element ('resource', url=self.url)
        services = data_service.query('service')
        for service in services:
            response.append(service)

        tg.response.headers['Content-Type'] = 'text/xml'
        return etree.tostring (response)

    def load(self, token, **kw):
        """
        loads and returns a resource identified by the token.
        """
        #raise NotImplementedError #easier to find errors
        return ""

    def create(self, **kw):
        """
        returns a class or function which will be passed into the self.new
        method.
        """
        #raise NotImplementedError #easier to find errors
        return ""


    def register_module (self, module_def):
        """register a remote module"""
        log.debug('register_module : %s' , module_def.get('name'))
        name = module_def.get ('name')
        ts   = module_def.get ('ts')
        value= module_def.get ('value')
        version = module_def.xpath('./tag[@name="module_options"]/tag[@name="version"]')
        version = len(version) and version[0].get('value')

        found = False
        modules = data_service.query ('module', name=name, view="deep")

        #  RULES for updating a module
        #
        found_versions = []
        for m in modules:
            m_version = m.xpath('./tag[@name="module_options"]/tag[@name="version"]')
            m_version = len(m_version) and m_version[0].get('value')
            #m_version = m.xpath('//tag[@name="version"]')[0].get('value')

            log.info('module %s ts(version) : new=%s(%s) current=%s(%s)' , name, ts, version, m.get('ts'), m_version)
            if m_version in found_versions:
                log.error("module %s has multiple definitions with same version %s" ,name, m_version)
                data_service.del_resource(m)
                continue

            found_versions.append(m_version)
            if m_version == version:
                found = True
                if  ts > m.get('ts'):
                    module_def.set('uri', m.get('uri'))
                    module_def.set('ts', str(datetime.now()))
                    #module_def.set('permission', 'published')
                    m = data_service.update_resource(resource=m, new_resource=module_def, view='deep')
                    log.info("Updated new module definition with: %s" , etree.tostring(m))
                else:
                    log.debug ("Module on system is newer: remote %s < system %s " , ts, m.get('ts'))
            else:
                # We are examining a different version of the module.
                # Should it be disabled?
                log.debug ("Skipping and hidding old version %s", m_version)
                m.set ('hidden', 'true')
                data_service.update_resource (resource=m, new_resource=m, replace=False, flush=False)


        if not found:
            log.info ("CREATING NEW MODULE: %s " , name)
            m = data_service.new_resource(module_def)

        log.info("END:register_module using  module %s for %s version %s" , m.get('uri'), name, version)
        return m

    def new(self, resource, xml, **kw):
        """ Create a new endpoint or endpoint set
        Allows an engine to register a set of modules in a single
        request
        """
        self.invalidate ("/module_service/")
        log.debug ("engine_register:new %s" , xml)
        if isinstance (xml, etree._Element):
            resource = xml
        else:
            resource = etree.XML (xml)

        #if resource.tag != 'engine':
        #    log.error('non-engine communication %s'  % xml)
        #    abort(502)
        #engine_url = resource.get('uri')
        for module_def in resource.getiterator('module'):
            #codeurl = module_def.get ('codeurl')
            #engine_url = module_def.get ('engine_url', None)
            #if codeurl is None or not codeurl.startswith('http://'):
            #    if engine_url is not None:
            #        log.debug ("Engine_url is deprecated. please use codeurl ")
            #        codeurl = engine_url
            #        module_def.set('codeurl', engine_url)
            #if codeurl is None or not codeurl.startswith('http://'):
            #    log.error ("Could not determine module codeurl during registration")
            #    raise abort(400)

            engine_url = module_def.get('value').rstrip('/')
            module_def.set ('value', engine_url)
            module = self.register_module(module_def)
            log.info ('Registered %s at %s' , module.get('name') , engine_url)
            log.debug ('Registered %s' , etree.tostring (module))

            # log.debug ('loading services for %s ' % module.get('name'))
            # service = data_service.query('service', name=module.get('name'), view="deep")
            # service = (len(service) and service[0])
            # if  service == 0:
            #     service_def = etree.Element('service',
            #                                 permission = 'published',
            #                                 name = module.get('name'),
            #                                 type = module.get('uri'),
            #                                 value = engine_url)
            #     service = data_service.new_resource(service_def)
            #     log.info("service create %s" % etree.tostring(service))
            # else:
            #     service.set('type', module.get('uri'))
            #     service.set('value', engine_url)
            #     service = data_service.update(service)
            #     log.info("service update %s" % etree.tostring(service))

        return etree.tostring (module)

    def modify(self, resource, xml, **kw):
        """
        Modify the mex in place.  Use to update status
        """
        raise abort(501)


    def get(self, resource, **kw):
        """
        fetches the resource, and returns a representation of the resource.
        """
        if resource:
            return etree.tostring (resource)

    def append(self, resource, xml, **kw):
        """ Register a new engine resource
        """

    def delete(self, resource,  **kw):
        """ Delete the engine resource
        """
        log.info ('DELETE %s: %s' , resource, kw)


import pkg_resources
def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    #log.debug ("initialize " + uri)
    service =  ModuleServer(uri)
    return service


def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'module_service', 'public'))]

def get_model():
    from bq.module_service import model
    return model

__controller__ =  ModuleServer
