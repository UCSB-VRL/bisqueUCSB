# Install script for Metalab
import sys
from bq.setup.module_setup import matlab_setup, python_setup, read_config

def setup(params, *args, **kw):
    python_setup('MyData.py',  params=params )

if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
    
