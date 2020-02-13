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

 Base engine adaptor for common code

"""
import os
import copy
import logging
import tempfile
from lxml import etree
from bq.core import identity

log = logging.getLogger('bq.engine_service.mexparser')

def local_xml_copy(root):
    b, id = root.get ('uri').rsplit ('/', 1)
    #path = '/tmp/%s%s' % (root.tag, id)
    path = os.path.join(tempfile.gettempdir(), "%s%s" % (root.tag, id))
    f = open (path, 'w')
    f.write (etree.tostring (root))
    f.close()
    return path

class MexParser(object):

    def prepare_inputs (self, module, mex, token = None):
        '''Scan the module definition and the mex and match input
        formal parameters creating a list of actual parameters in the
        proper order (sorted by index)

        '''

        # ? dima - client_server, look at any find_service('client_service') in any api file
        mex_specials = { 'mex_url'      : mex.get('uri'),
                         'bisque_token' : token or identity.mex_authorization_token(),
                         'module_url'   : module.get ('uri'),
                         #'bisque_root'  : '',
                         #'client_server': '',
                         }

        # Pass through module definition looking for inputs
        # for each input find the corresponding tag in the mex
        # Warn about missing inputs
        input_nodes = []
        formal_inputs = module.xpath('./tag[@name="inputs"]')
        formal_inputs = formal_inputs and formal_inputs[0]
        actual_inputs = mex.xpath('./tag[@name="inputs"]')
        if len( actual_inputs )==0:
            # maybe this is a blocked mex => look one level deeper
            actual_inputs = mex.xpath('./mex/tag[@name="inputs"]')
            if len( actual_inputs )==0:
                # no inputs in mex
                return []
        actual_inputs = actual_inputs and actual_inputs[0]


        for mi in formal_inputs:
            # pull type off and markers off
            found = None
            #param_name = mi.get('value').split(':')[0].strip('$')
            param_name = mi.get('name')
            #log.debug ("PARAM %s" % param_name)
            if param_name in mex_specials:
                log.debug ("PARAM special %s=%s" % ( param_name, mex_specials[param_name]))
                found = etree.Element('tag',
                                      name=param_name,
                                      value = mex_specials[param_name])
                input_nodes.append (found)
            else:
                found = actual_inputs.xpath ('./tag[@name="%s"]'%param_name)
                if len(found ):
                    if found[0].get('type') == 'range' or (len(found[0])>0 and all([kid.tag == 'value' and kid.get('type') == 'object' for kid in found[0]])):
                        # special multi-param case => keep entire subtree
                        addtl_input = [ copy.deepcopy(found[0]) ]
                    else:
                        # found parameter but it may be a subtree (tree of parameters)
                        # => traverse the tree and collect all parameters at the leaves
                        addtl_input = [ copy.deepcopy(kid) for kid in found[0].iter() if not len(kid) and kid.tag=='tag' ]
                    log.debug ("PARAM %s=%s" % (param_name, str(addtl_input)))
                    input_nodes.extend(addtl_input)
                else:
                    log.warn ('missing input for parameter %s' % mi.get('value'))

        # Add the index
        for i, node in enumerate(input_nodes):
            if 'index' in node.keys():
                continue
            node.set ('index', str(i))

        input_nodes.sort (lambda n1,n2: cmp(int(n1.get('index')), int(n2.get('index'))))
        return input_nodes


    def prepare_outputs (self, module, mex):
        '''Scan the module definition and the mex and match output
        parameters creating a list in the proper order
        '''
        outputs = module.xpath ('./tag[@name="outputs"]')
        outputs = outputs and outputs[0]
        return [ copy.deepcopy(kid) for kid in outputs ]


    def prepare_options (self, module, mex):
        """Find the module options on the module definition and make
        available as a dict
        """
        options = {}
        for x in (module, mex):
            execute = x.xpath ('./tag[@name="execute_options"]')
            execute = execute  and execute[0]
            log.debug ("options %s" % execute )
            for opt in execute:

                options[opt.get('name')] = opt.get('value')

        log.debug("options=%s" % options)
        return options


    def prepare_mex_params(self, input_nodes,  style = None ):
        """Create list of params based on execution : named or positional, or tuples (None)
        @param inputs:  a etree document of formal_param, actual_param
        @param style: 'named' return a list formal=actual, None return (formal, actual), else actual
        """
        if style is None:
            params = [ (i.get('name'), i.get('value') if i.get('value', None) else i.get('uri')) for i in input_nodes if i.get('value', None) or len(i)>0 ]
        elif style == 'named':
            params = ['%s=%s'%(i.get('name'), i.get('value') if i.get('value', None) else i.get('uri')) for i in input_nodes if i.get('value', None) or len(i)>0 ]
        else:
            params = [ i.get('value') if i.get('value', None) else i.get('uri') for i in input_nodes if i.get('value', None) or len(i)>0 ]
        log.debug('\n\nPARAMS : %s'%params)
        return params

    def process_iterables(self, module, mex):
        """extract iterables from the mex as tuple i.e.  iterable_tag_name, dataset_url
         (input tagname, value, type)
        ('resource_url', 'http://host/dataservice/image/121',  'image')
        """

        #log.debug ('iteraable module = %s' % etree.tostring(module))
        iterables = []
        mod_iterables = mex.xpath('./tag[@name="execute_options"]/tag[@name="iterable"]')

        iters = {}
        for itr in mod_iterables:
            resource_tag = itr.get('value')
            resource_type = itr.get('type')
            iters.setdefault(resource_tag, {})[resource_type] =  None
        log.debug ('iterables in module %s' % iters)

        for iter_tag, iter_d in iters.items():
            for iter_type in iter_d.keys():
                log.debug ("checking name=%s type=%s" % (iter_tag, iter_type))
                resource_tag = mex.xpath('./tag[@name="inputs"]//tag[@name="%s" and @type="%s" and @value]' % (iter_tag, iter_type))
                if len(resource_tag):
                    # Hmm assert len(resource_tag) == 1
                    iterables.append( (iter_tag, resource_tag[0].get('value'), resource_tag[0].get('type') ))
        log.debug('iterables  %s' % iterables)
        return iterables
