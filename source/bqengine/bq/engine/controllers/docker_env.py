""" Setup the environment for a docker execution.
"""

from __future__ import with_statement

import os
import string
import logging


from bq.util.converters import asbool
from .base_env import strtolist
from .module_env import BaseEnvironment, ModuleEnvironmentError
from .attrdict import AttrDict

log = logging.getLogger('bq.engine_service.docker_env')

DOCKER_RUN="""#!/bin/bash
set -x

mex=$(echo "$MEX_ID" | tr '[:upper:]' '[:lower:]')

echo "image: ${DOCKER_IMAGE}" | tee params.yaml
echo "args: ${@}" | tee -a params.yaml
argo submit --log --from workflowtemplate/bqflow-module-template --parameter-file params.yaml --token $ARGO_TOKEN --generate-name ${mex}- 
"""

DOCKER_RUN_GPU="""#!/bin/bash 
set -x 
 
mex=$(echo "$MEX_ID" | tr '[:upper:]' '[:lower:]') 
 
echo "image: ${DOCKER_IMAGE}" | tee params.yaml 
echo "args: ${@}" | tee -a params.yaml 
argo submit --log --from workflowtemplate/bqflow-module-gpu-template --parameter-file params.yaml --token $ARGO_TOKEN --generate-name ${mex}-  
"""

class DockerEnvironment(BaseEnvironment):
    '''Docker Environment

    This Docker environment prepares an execution script to run docker


    Enable  the Docker environment by adding to your module.cfg::
       environments = ..., Docker, ...

    The output file "docker.run" will be placed in the staging directory
    and used as the executable for any processing and will be called with
    matlab_launch executable argument argument argument

    The script will be generated based on internal template which can
    be overriden with (in runtime-module.cfg)::
       matlab_launcher = mymatlab_launcher.txt

    '''

    name = "Docker"
    config = { }
    matlab_launcher = ""
    docker_keys = [ 'docker.hub', 'docker.image', 'docker.hub.user', 'docker.hub.user', 'docker.hub.email',
                      'docker.login_tmpl', 'docker.default_tag' ]


    def process_config (self, runner, **kw):
        runner.load_section ('docker', runner.bisque_cfg)
        runner.load_section ('docker', runner.module_cfg)
        self.enabled = asbool(runner.config.get ('docker.enabled', False))
        self.module_exec_env = runner.config.get('exec_env', '')
        log.debug('module exection environment %s', self.module_exec_env)

        #self.docker_hub = runner.config.get('docker.hub', '')
        #self.docker_image = runner.config.get('docker.image', '')
        #self.docker_user = runner.config.get ('docker.hub.user', '')
        #self.docker_pass = runner.config.get('docker.hub.password', '')
        #self.docker_email = runner.config.get('docker.hub.email', '')
        #self.docker_login_tmpl = runner.config.get ('docker.login_tmpl', self.docker_login_tmpl)
        self.docker_params = AttrDict()
        for k in self.docker_keys:
            self.docker_params[ k.replace('.', '_') ] = runner.config.get (k, '')


        #self.matlab_launcher = runner.config.get('runtime.matlab_launcher', None)
        #if self.matlab_launcher is not None and not os.path.exists(self.matlab_launcher):
        #    raise ModuleEnvironmentError("Can't find matlab script %s" % self.matlab_launcher)
        #if runner.named_args.has_key('matlab_home'):
        #    self.matlab_home = runner.named_args['matlab_home']

    def setup_environment(self, runner, build=False):
        # Construct a special environment script
        runner.info ("docker environment setup")
        if not self.enabled:
            runner.info ("docker disabled")
            return

        if build:
            #docker_outputs = [ "." ]
            #module_vars =  runner.module_cfg.get ('command', asdict=True)
            #docker_inputs = [x.strip () for x in module_vars.get ('files', '').split (',') ]
            runner.mexes[0].files = strtolist (runner.mexes[0].files)
            runner.mexes[0].outputs = []
            return


        p = self.docker_params # pylint: disable=invalid-name
        docker_pull = ""
        docker_login= ""
        docker_image = "/".join ([x for x in  [ p.docker_hub, p.docker_hub_user, p.docker_image ] if x ])
        if p.docker_default_tag and ':' not in docker_image:
            docker_image = "{}:{}".format (docker_image, p.docker_default_tag)
        # always pull an image
        if p.docker_hub:
            docker_login = p.docker_login_tmpl.format ( p )
            docker_pull = "docker pull %s" % docker_image

        for mex in runner.mexes:
            docker_outputs = [ ]
            docker_inputs  = []
            #module_vars =  runner.module_cfg.get ('command', asdict=True)
            #docker_inputs = [x.strip () for x in module_vars.get ('files', '').split (',') ]

            #runner.log ("docker files setup %s" % mex.get ('files') )

            # Static files will already be inside container (created during build)

            # if there are additional executable wrappers needed in the environment, add them to copylist
            # (e.g., "matlab_run python mymodule")
            if  mex.executable:
                for p in mex.executable:
                    pexec = os.path.join(mex.rundir, p)
                    #runner.debug ("Checking exec %s->%s" % (pexec, os.path.exists (pexec)))
                    #if os.path.exists (pexec) and p not in docker_inputs:
                    if os.path.exists (pexec) and p not in mex.files:
                        docker_inputs.append (p)

            docker = self.create_docker_launcher(mex.rundir, mex.mex_id,
                                                 docker_image, docker_login, docker_pull, docker_inputs, docker_outputs, self.module_exec_env)
            if mex.executable:
                mex.executable.insert(0, docker)
                #mex.files = ",".join (docker_inputs)
                #mex.output_files = ",".join (docker_outputs)
                mex.files = docker_inputs
                mex.output_files = docker_outputs +  ['output_files/']

                runner.debug ("mex files %s outputs %s", mex.files, mex.output_files)

    def create_docker_launcher(self, dest, mex_id,
                               docker_image,
                               docker_login,
                               docker_pull,
                               docker_inputs,
                               docker_outputs,
                               module_exec_env):
        if module_exec_env=='use_gpu':
            log.info('executing module on gpu %s', module_exec_env)
            docker_run = DOCKER_RUN_GPU
        else:
            docker_run = DOCKER_RUN
        #if self.matlab_launcher and os.path.exists(self.matlab_launcher):
        #    matlab_launcher = open(self.matlab_launcher).read()
        content = string.Template(docker_run)
        content = content.safe_substitute(
            MEX_ID = mex_id,
            DOCKER_IMAGE = docker_image,
            DOCKER_LOGIN = docker_login,
            DOCKER_PULL  = docker_pull,
            DOCKER_INPUTS="\n".join("docker cp %s %s:/module/%s" % (f, "$CONTAINER", f) for f in docker_inputs),
            DOCKER_OUTPUTS="\n".join("docker cp %s:/module/%s %s" % ("$CONTAINER", f,f) for f in docker_outputs),
        )
        if os.name == 'nt':
            path = os.path.join(dest, 'docker_run.bat' )
        else:
            path = os.path.join(dest, 'docker_run' )
        with open(path, 'w') as f:
            f.write (content)
        os.chmod (path, 0744)
        return path
