# Install script for Botanicam
import sys
from bqapi.comm import BQSession
from bq.setup.module_setup import python_setup, read_config
from bq.setup.bisque_setup import getanswer


def setup(params, *args, **kw):
    return python_setup('Botanicam.py', params=params)
    
    
if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
