# Install script for Dream3D UCSB
import sys
import tempfile
import shutil
import re
from subprocess import Popen, PIPE
from bq.setup.module_setup import python_setup, read_config, docker_setup
from bq.util.converters import asbool


def setup(params, *args, **kw):
    docker_params = read_config('runtime-bisque.cfg', "docker")
    if not asbool(docker_params.get('docker.enabled', False)):
        print "No Docker available... cannot set up module."
        return 1
    
    try:
        # clone Dream.3D UCSB repo and build Docker image
        tmp_dir = tempfile.mkdtemp()
        print "Cloning code into %s..." % tmp_dir
        p = Popen(['git', 'clone', 'git@github.com:wlenthe/UCSB_DREAM3D', '%s/source' % tmp_dir],
                  stdout=PIPE)
        if p.wait() != 0:
            print "Dream.3D repo could not be cloned... cannot set up module."
            return 1
     
        # build Docker image
        print "Building Dream.3D docker image..."
        p = Popen(['timeout', '-s', 'SIGKILL', '120m',
                   'docker', 'build', '--tag', 'dream3d_ucsb', '%s/source' % tmp_dir],
                  stdout=PIPE)
        while True:    
            line = p.stdout.readline()
            if line == '':
                break
            m = re.search('\[[ ]*[0-9]+%\]', line)
            if m:
                print '\r\r\r\r\r\r',
                print m.group(0),
                sys.stdout.flush()            
        print
        if p.wait() != 0:
            print "Dream.3D image could not be built... cannot set up module."
            return 1
        
        python_setup('Dream3D.py',  params=params )            
        docker_setup('bisque_dream3d_ucsb', 'Dream3D', 'dream3d_ucsb', params=params)    

    finally:    
        # delete tmp_dir
        shutil.rmtree(tmp_dir)
    
if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])
    sys.exit(setup(params))
    
