import sys
from bq.setup.module_setup import python_setup, docker_setup, require, read_config


def setup(params, *args, **kw):
    python_setup('PythonScriptWrapper.py', params=params)
    docker_setup('COVIDPredictor', params=params)
    
if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))

# docker run -itp 8080:8080 -p 27000:27000 --name bq-module-dev -v //var/run/docker.sock:/var/run/docker.sock --ipc=host --net=host amilworks/bisque-module-dev:git
