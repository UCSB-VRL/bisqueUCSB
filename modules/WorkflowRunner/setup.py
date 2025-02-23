# Install script for WorkflowRunner
import sys
from bq.setup.module_setup import python_setup, require, read_config


def setup(params, *args, **kw):
    python_setup('WorkflowRunner.py',  params=params )
    
if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
    
