# Install script for MTTracker

import sys
from bq.util.module_setup import matlab_setup, matlab, require, read_config

def setup(params, *args, **kw):
    # Compile boost graphics library
    if not require (['matlab_home'], params):
        print "Skipping.. no matlab_home", params
        return 1

    print """MTTracker matlab compilation can fail due to the mex options
    not being set up.  This is an issue with mcc.  Please review any error
    and correctly configure the mex compiler

    IF BLOCKED AT ANY POINT TYPE 'quit'
    """
    
    matlab('bisque_compile', 'private', params)
    matlab('compile', params)

    return matlab_setup('MTTracker')
    
if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params.update  ( eval (sys.argv[1]) )

    sys.exit(setup(params))



