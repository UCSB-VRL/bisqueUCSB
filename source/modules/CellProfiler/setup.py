# Install script for CellProfiler
import sys
from bq.setup.module_setup import python_setup, require, read_config, docker_setup


def setup(params, *args, **kw):
    #python_setup('CellProfiler.py', params=params)
    docker_setup('bisque_cellprofiler', 'CellProfiler', 'cellprofiler', params=params)

if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
