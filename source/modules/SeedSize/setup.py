# Install script for SeedSize
import sys
from bq.setup.module_setup import matlab_setup, python_setup, docker_setup, read_config

def setup(params, *args, **kw):
    python_setup('SeedSize.py', params=params)
    matlab_setup('matlab/seedSize', bisque_deps=False, params=params)
    docker_setup ('seedsize', 'SeedSize', 'matlab_runtime',  params=params)


if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
