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

#mkdir -p ./output_files
${DOCKER_LOGIN}
${DOCKER_PULL}
CONTAINER=$$(docker create ${DOCKER_IMAGE}  $@)
${DOCKER_INPUTS}
docker start $CONTAINER
MODULE_RETURN=$$(docker wait  $CONTAINER)
docker logs $CONTAINER
${DOCKER_OUTPUTS}
# docker will not copy to existing directory .. so create a new one and copy from that
docker cp $CONTAINER:/module/ output_files
mv -fuv ./output_files/* .
#rsync -av ./output_files/ .
rm -rf ./output_files/*/
docker rm $CONTAINER
exit $MODULE_RETURN
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
        log.debug("=== PROCESS_CONFIG START ===")
        log.debug("Input kwargs: %s", kw)
        runner.load_section ('docker', runner.bisque_cfg)
        runner.load_section ('docker', runner.module_cfg)
        self.enabled = asbool(runner.config.get ('docker.enabled', False))
        log.debug("Docker enabled: %s", self.enabled)
        
        self.docker_params = AttrDict()
        for k in self.docker_keys:
            key_normalized = k.replace('.', '_')
            value = runner.config.get (k, '')
            self.docker_params[key_normalized] = value
            log.debug("Docker param - %s: %s", key_normalized, value)
        
        log.debug("Final Docker config: %s", self.docker_params)
        log.debug("=== PROCESS_CONFIG END ===")

    def setup_environment(self, runner, build=False):
        # Construct a special environment script
        log.debug("=== SETUP_ENVIRONMENT START ===")
        log.debug("Build mode: %s", build)
        runner.info ("docker environment setup")
       
        if not self.enabled:
            log.debug("Docker is disabled, returning early")
            runner.info ("docker disabled")
            return

        if build:
            log.debug("Build mode detected")
            log.debug("Number of mexes: %d", len(runner.mexes))
            log.debug("First mex files before strtolist: %s", runner.mexes[0].files)
            runner.mexes[0].files = strtolist (runner.mexes[0].files)
            log.debug("First mex files after strtolist: %s", runner.mexes[0].files)
            runner.mexes[0].outputs = []
            log.debug("First mex outputs set to: %s", runner.mexes[0].outputs)
            return

        p = self.docker_params # pylint: disable=invalid-name
        log.debug("Docker params object: %s", p)
        
        docker_pull = ""
        docker_login= ""
        
        # Build docker image name
        image_parts = [x for x in [p.docker_hub, p.docker_hub_user, p.docker_image] if x]
        log.debug("Docker image parts (hub, user, image): %s", image_parts)
        
        docker_image = "/".join(image_parts)
        log.debug("Docker image (before tag): %s", docker_image)
        
        if p.docker_default_tag and ':' not in docker_image:
            docker_image = "{}:{}".format (docker_image, p.docker_default_tag)
            log.debug("Docker image (after adding tag): %s", docker_image)
        
        # always pull an image
        if p.docker_hub:
            log.debug("Docker hub configured, setting up login and pull")
            docker_login = p.docker_login_tmpl.format ( p )
            docker_pull = "docker pull %s" % docker_image
            log.debug("Docker login command: %s", docker_login)
            log.debug("Docker pull command: %s", docker_pull)
        else:
            log.debug("Docker hub not configured, skipping login/pull setup")

        log.debug("Total mexes to process: %d", len(runner.mexes))
        
        for mex_index, mex in enumerate(runner.mexes):
            log.debug("--- Processing mex %d ---", mex_index)
            log.debug("Mex ID: %s", mex.mex_id)
            log.debug("Mex rundir: %s", mex.rundir)
            log.debug("Mex executable: %s", mex.executable)
            log.debug("Mex files: %s", mex.files)
            
            docker_outputs = [ ]
            docker_inputs  = []

            # Static files will already be inside container (created during build)

            # if there are additional executable wrappers needed in the environment, add them to copylist
            # (e.g., "matlab_run python mymodule")
            if mex.executable:
                log.debug("Mex has %d items in executable list", len(mex.executable))
                
                # Separate actual executables/files from arguments
                # Arguments typically contain URLs, tokens, etc. (have :// or : patterns)
                executable_parts = []
                argument_parts = []
                
                for item in mex.executable:
                    is_argument = ('://' in str(item) or (str(item).startswith('admin:') or str(item).startswith('http')))
                    if is_argument:
                        argument_parts.append(item)
                        log.debug("Identified as argument: %s", item)
                    else:
                        executable_parts.append(item)
                        log.debug("Identified as executable/command: %s", item)
                
                log.debug("Separated executable parts: %s", executable_parts)
                log.debug("Separated argument parts: %s", argument_parts)
                
                # Now process only the executable/file parts
                for exec_index, p in enumerate(executable_parts):
                    pexec = os.path.join(mex.rundir, p)
                    exists = os.path.exists(pexec)
                    in_files = p in mex.files
                    log.debug("Executable %d - Part: %s, Path: %s, Exists: %s, In files: %s", 
                             exec_index, p, pexec, exists, in_files)
                    
                    if exists and not in_files:
                        docker_inputs.append(p)
                        log.debug("Added to docker_inputs: %s", p)
            else:
                log.debug("Mex has no executables")

            log.debug("Final docker_inputs for this mex: %s", docker_inputs)
            log.debug("Final docker_outputs for this mex: %s", docker_outputs)
            
            docker = self.create_docker_launcher(mex.rundir, mex.mex_id,
                                                 docker_image, docker_login, docker_pull, docker_inputs, docker_outputs)
            log.debug("Created docker launcher at: %s", docker)
            
            if mex.executable:
                # Keep the original executable list intact for the docker script
                original_executable = list(mex.executable)
                log.debug("Original executable before replacement: %s", original_executable)
                
                # Replace entire executable with docker script + original command
                # This way: docker_run python PythonScriptWrapper.py url1 url2 token
                mex.executable = [docker] + original_executable
                mex.files = docker_inputs
                mex.output_files = docker_outputs +  ['output_files/']
                
                log.debug("Updated mex executable (docker script + original command): %s", mex.executable)
                log.debug("Updated mex files: %s", mex.files)
                log.debug("Updated mex output_files: %s", mex.output_files)
                
                # Verify the docker script exists and is executable
                if os.path.exists(docker):
                    script_stat = os.stat(docker)
                    log.debug("Docker script exists: %s, size: %d bytes, mode: %o", docker, script_stat.st_size, script_stat.st_mode)
                    is_executable = os.access(docker, os.X_OK)
                    log.debug("Docker script is executable: %s", is_executable)
                    if not is_executable:
                        log.error("Docker script is NOT executable! Need to fix permissions.")
                else:
                    log.error("Docker script does NOT exist: %s", docker)
                
                # Log the complete command that will be executed
                log.info("FINAL COMMAND TO EXECUTE: %s", " ".join(mex.executable))
                log.info("Working directory will be: %s", mex.rundir)
                log.info("Output files will be: %s", mex.output_files)
                
                runner.debug ("mex files %s outputs %s", mex.files, mex.output_files)
            else:
                log.debug("Warning: mex has no executables to update")

        log.debug("=== SETUP_ENVIRONMENT END ===")

    def create_docker_launcher(self, dest, mex_id,
                               docker_image,
                               docker_login,
                               docker_pull,
                               docker_inputs,
                               docker_outputs,):
        log.debug("=== CREATE_DOCKER_LAUNCHER START ===")
        log.debug("Destination: %s", dest)
        log.debug("Mex ID: %s", mex_id)
        log.debug("Docker image: %s", docker_image)
        log.debug("Docker inputs: %s", docker_inputs)
        log.debug("Docker outputs: %s", docker_outputs)
        
        docker_run = DOCKER_RUN
        content = string.Template(docker_run)
        
        inputs_str = "\n".join("docker cp %s %s:/module/%s" % (f, "$CONTAINER", f) for f in docker_inputs)
        outputs_str = "\n".join("docker cp %s:/module/%s %s" % ("$CONTAINER", f, f) for f in docker_outputs)
        
        log.debug("Generated docker inputs commands:\n%s", inputs_str)
        log.debug("Generated docker outputs commands:\n%s", outputs_str)
        
        content = content.safe_substitute(
            MEX_ID = mex_id,
            DOCKER_IMAGE = docker_image,
            DOCKER_LOGIN = docker_login,
            DOCKER_PULL  = docker_pull,
            DOCKER_INPUTS = inputs_str,
            DOCKER_OUTPUTS = outputs_str,
        )
        
        if os.name == 'nt':
            path = os.path.join(dest, 'docker_run.bat')
            log.debug("Windows environment detected")
        else:
            path = os.path.join(dest, 'docker_run')
            log.debug("Unix environment detected")
        
        log.debug("Writing docker launcher script to: %s", path)
        
        try:
            with open(path, 'w') as f:
                f.write(content)
            log.debug("Successfully wrote %d bytes to launcher script", len(content))
        except Exception as e:
            log.error("Failed to write launcher script: %s", e, exc_info=True)
            raise
        
        try:
            os.chmod(path, 0o744)
            log.debug("Set permissions to 0o744 on: %s", path)
        except Exception as e:
            log.error("Failed to set permissions: %s", e, exc_info=True)
            raise
        
        log.debug("=== CREATE_DOCKER_LAUNCHER END ===")
        return path
