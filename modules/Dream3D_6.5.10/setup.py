# Install script for Dream3D
import sys
from bq.setup.module_setup import python_setup, require, read_config, docker_setup


def setup(params, *args, **kw):
    python_setup('Dream3D.py',  params=params )
    docker_setup('bisque_dream3d_6_5_10', 'Dream3D', 'dream3d', params=params)
    
if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
    
