# Install script for GraphcutSegmentation
import sys
from bq.setup.module_setup import matlab_setup, read_config, ensure_matlab, mex_compile, docker_setup

def setup(params, *args, **kw):
    ensure_matlab(params)
    #mex_compile(['vrl_gc.cpp'], where='vrl_tools/maxflow_kolmogorov')
    matlab_setup(['GraphcutSegmentation'], params=params)
    docker_setup('graphcut', 'GraphcutSegmentation', 'matlab_runtime', params=params)

if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])

    sys.exit(setup(params))
