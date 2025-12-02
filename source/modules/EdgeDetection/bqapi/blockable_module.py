import sys
import collections

from bqapi import BQSession


import logging



#logging.basicConfig(filename='BlockableModule.log',level=logging.DEBUG)   #!!!
log = logging.getLogger('bqapi.blockable_module')

class BlockableModule(object):
    """Base class for module that can run over blocks of parameters"""
    
    def main(self, mex_url=None, auth_token=None, bq=None, **kw):        
        #  Allow for testing by passing an alreay initialized session
        if bq is None:
            bq = BQSession().init_mex(mex_url, auth_token)
            
        # check for list parameters
        params = bq.get_mex_inputs()
        if isinstance(params, dict) or not isinstance(params, collections.Iterable):
            params = [params]
        # pass values directly as args
        for single_params in params:
            for param_name in single_params:
                if 'value' in single_params[param_name]:
                    single_params[param_name] = single_params[param_name].get('value')
        
        # TODO: measure block startup time
        self.start_block(bq, params)
                    
        for kw in params:
            # TODO: measure single item time
            # TODO: run in parallel
            if 'mex_url' in kw:
                # set (innermost) single item mex
                sub_bq = BQSession().init_mex(kw['mex_url'], auth_token)
            else:
                sub_bq = bq
            self.process_single(sub_bq, **kw)
            if 'mex_url' in kw:
                sub_bq.close()
        
        # TODO: measure block teardown time
        self.end_block(bq)
        
        sys.exit(0)
        #bq.close()
    
    def start_block(self, bq, all_kw):
        pass
    
    def end_block(self, bq):
        pass
            
    def process_single(self, bq, **kw):
        pass
