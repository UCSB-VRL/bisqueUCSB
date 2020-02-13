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
import logging
import copy
import tempfile
from lxml import etree
from bq.core import identity


log = logging.getLogger('bq.engine_service.adapters.base_adapter')

def local_xml_copy(root):
    b, id = root.get ('uri').rsplit ('/', 1)
    #path = '/tmp/%s%s' % (root.tag, id)
    path = os.path.join(tempfile.gettempdir(), "%s%s" % (root.tag, id))
    f = open (path, 'w')
    f.write (etree.tostring (root))
    f.close()
    return path

class BaseAdapter(object):

    def check(self, module):
        '''Check if the adaptor can be loaded and run. Check for
        missing libraries or try a trial run.  Used by the engine
        service to determine whether a module is valid
        '''
        return False

    def execute(self, module, mex, pool):
        '''Execute the module given by the mex context.  The module
        will be the module definition parameter, the mex will contain
        the current values of all input parameters
        '''
        pass


    def prepare_inputs (self, module, mex):
        '''Scan the module definition and the mex and match input
        formal parameters creating a list of actual parameters in the
        proper order (sorted by index)

        '''

        # ? dima - client_server, look at any find_service('client_service') in any api file
        mex_specials = { 'mex_url'      : mex.get('uri'),
                         'bisque_token' : identity.mex_authorization_token(),
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
        actual_inputs = actual_inputs and actual_inputs[0]
        #actual_inputs = mex

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
                log.debug ("PARAM %s=%s" % (param_name, found))
                input_nodes +=  found
            if found is None:
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
        """Find the module options on the module definition
        and make available as a dict
        """
        options = {}
        execute = module.xpath ('./tag[@name="execute_options"]')
        execute = execute and execute[0]
        log.debug ("options %s" % execute )
        for opt in execute:
            options[opt.get('name')]= opt

        log.debug("options=%s" % options)
        return options
