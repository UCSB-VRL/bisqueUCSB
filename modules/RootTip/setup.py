# Install script for RootTip
import sys
from bq.setup.module_setup import matlab_setup, read_config, python_setup, docker_setup

def setup(*args, **kw):
    python_setup('RootTip.py', params=params)
    matlab_setup('matlab/araGT.m', bisque_deps = False, params=params)
    docker_setup('roottip', "RootTip", "matlab_runtime", params=params)

if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
