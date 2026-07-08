"""Setup the environment for a docker execution."""

from __future__ import with_statement

import logging
import os
import sys

from bq.util.converters import asbool

from .attrdict import AttrDict
from .base_env import strtolist
from .module_env import BaseEnvironment, ModuleEnvironmentError

log = logging.getLogger("bq.engine_service.docker_env")

DOCKER_LAUNCHER = """import os
import platform
import shlex
import subprocess
import sys


DOCKER_IMAGE = {docker_image}
DOCKER_LOGIN = {docker_login}
DOCKER_PULL = {docker_pull}
DOCKER_CALLBACK_URL = {docker_callback_url}
DOCKER_INTERNAL_URLS = {docker_internal_urls}
GPU_COUNT = {gpu_count}
HOST_SYSTEM = platform.system().lower()
MODULE_LOG_FILES = ("PythonScript.log", "scriptrun.log")
STAGING_DIR = os.path.dirname(os.path.abspath(__file__))


def run(command):
    print("+ " + " ".join(shlex.quote(str(part)) for part in command), flush=True)
    return subprocess.call(command)


def run_output(command):
    print("+ " + " ".join(shlex.quote(str(part)) for part in command), flush=True)
    return subprocess.check_output(command, universal_newlines=True).strip()


def run_shell_config(command):
    if not command:
        return 0
    return run(shlex.split(command))


def module_argument(argument):
    if DOCKER_CALLBACK_URL:
        for internal_url in DOCKER_INTERNAL_URLS:
            if internal_url and argument.startswith(internal_url):
                return DOCKER_CALLBACK_URL.rstrip("/") + argument[len(internal_url) :]
    if HOST_SYSTEM in ("darwin", "windows"):
        return (
            argument.replace("http://localhost:", "http://host.docker.internal:")
            .replace("https://localhost:", "https://host.docker.internal:")
            .replace("http://127.0.0.1:", "http://host.docker.internal:")
            .replace("https://127.0.0.1:", "https://host.docker.internal:")
        )
    return argument


def copy_module_logs(container):
    for log_file in MODULE_LOG_FILES:
        container_path = "%s:/module/%s" % (container, log_file)
        host_path = os.path.join(STAGING_DIR, log_file)
        code = run(["docker", "cp", container_path, host_path])
        if code:
            print("warning: could not copy %s from container" % log_file, flush=True)


code = run_shell_config(DOCKER_LOGIN)
if code:
    sys.exit(code)

code = run_shell_config(DOCKER_PULL)
if code:
    sys.exit(code)

container = None
module_return = 1
docker_command = ["docker", "create"]
if GPU_COUNT:
    docker_command.extend(["--gpus", str(GPU_COUNT)])
if HOST_SYSTEM == "linux":
    docker_command.extend(["--network=host", "--add-host=host.docker.internal:host-gateway"])
docker_command.append(DOCKER_IMAGE)
docker_command.extend(module_argument(arg) for arg in sys.argv[1:])
try:
    container = run_output(docker_command)
    if not container:
        sys.exit(1)

    code = run(["docker", "start", container])
    if code:
        sys.exit(code)

    wait_output = run_output(["docker", "wait", container])
    module_return = int(wait_output.splitlines()[-1])
    run(["docker", "logs", container])
    copy_module_logs(container)
    sys.exit(module_return)
except subprocess.CalledProcessError as exc:
    sys.exit(exc.returncode)
finally:
    if container:
        run(["docker", "rm", container])
"""

ARGO_LAUNCHER = """import json
import os
import platform
import re
import shlex
import subprocess
import sys
import tempfile


DOCKER_IMAGE = {docker_image}
DOCKER_CALLBACK_URL = {docker_callback_url}
DOCKER_INTERNAL_URLS = {docker_internal_urls}
MEX_ID = {mex_id}
GPU_COUNT = {gpu_count}
CPU = {cpu}
MEMORY = {memory}
EPHEMERAL_STORAGE = {ephemeral_storage}
ARGO_WORKFLOW_TEMPLATE = {argo_workflow_template}
ARGO_GPU_WORKFLOW_TEMPLATE = {argo_gpu_workflow_template}
HOST_SYSTEM = platform.system().lower()


def run(command):
    print("+ " + " ".join(shlex.quote(str(part)) for part in command), flush=True)
    return subprocess.call(command)


def module_argument(argument):
    if DOCKER_CALLBACK_URL:
        for internal_url in DOCKER_INTERNAL_URLS:
            if internal_url and argument.startswith(internal_url):
                return DOCKER_CALLBACK_URL.rstrip("/") + argument[len(internal_url) :]
    if HOST_SYSTEM in ("darwin", "windows"):
        return (
            argument.replace("http://localhost:", "http://host.docker.internal:")
            .replace("https://localhost:", "https://host.docker.internal:")
            .replace("http://127.0.0.1:", "http://host.docker.internal:")
            .replace("https://127.0.0.1:", "https://host.docker.internal:")
        )
    return argument


def workflow_generate_name(mex_id):
    name = re.sub(r"[^a-z0-9-]+", "-", mex_id.lower()).strip("-")
    name = name or "mex"
    return name[:52].rstrip("-") + "-"


template = ARGO_GPU_WORKFLOW_TEMPLATE if GPU_COUNT else ARGO_WORKFLOW_TEMPLATE
module_command = shlex.join(module_argument(arg) for arg in sys.argv[1:])
params = {{
    "image": DOCKER_IMAGE,
    "args": module_command,
    "cpu": CPU,
    "memory": MEMORY,
    "ephemeral_storage": EPHEMERAL_STORAGE,
    "gpu_count": str(GPU_COUNT or ""),
}}
parameter_path = None

try:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as parameter_file:
        json.dump(params, parameter_file)
        parameter_file.write("\\n")
        parameter_path = parameter_file.name

    argo_command = [
        "argo",
        "submit",
        "--log",
        "--from",
        "workflowtemplate/%s" % template,
        "--parameter-file",
        parameter_path,
        "--generate-name",
        workflow_generate_name(MEX_ID),
    ]

    namespace = os.environ.get("ARGO_NAMESPACE") or os.environ.get("POD_NAMESPACE")
    if namespace:
        argo_command.extend(["--namespace", namespace])

    token = os.environ.get("ARGO_TOKEN")
    if token:
        argo_command.extend(["--token", token])

    sys.exit(run(argo_command))
finally:
    if parameter_path:
        try:
            os.unlink(parameter_path)
        except OSError:
            pass
"""

# DOCKER_RUN="""#!/bin/bash
# set -x

# #mkdir -p ./output_files
# ${DOCKER_LOGIN}
# ${DOCKER_PULL}
# CONTAINER=$$(docker create --network=host ${DOCKER_IMAGE}  $@)
# ${DOCKER_INPUTS}
# docker start $CONTAINER
# MODULE_RETURN=$$(docker wait  $CONTAINER)
# docker logs $CONTAINER
# ${DOCKER_OUTPUTS}
# # docker will not copy to existing directory .. so create a new one and copy from that
# docker cp $CONTAINER:/module/ output_files
# mv -fuv ./output_files/* .
# #rsync -av ./output_files/ .
# rm -rf ./output_files/*/
# docker rm $CONTAINER
# exit $MODULE_RETURN
# """

# !!! Can use `CONTAINER=$$(docker create --network=host ${DOCKER_IMAGE}  $@)` to enable host networking if needed
# !!! instead of `CONTAINER=$$(docker create ${DOCKER_IMAGE}  $@)`


class DockerEnvironment(BaseEnvironment):
    """Docker Environment

    This Docker environment prepares an execution script to run docker


    Enable  the Docker environment by adding to your module.cfg::
       environments = ..., Docker, ...

    The output file "docker.run" will be placed in the staging directory
    and used as the executable for any processing and will be called with
    matlab_launch executable argument argument argument

    The script will be generated based on internal template which can
    be overriden with (in runtime-module.cfg)::
       matlab_launcher = mymatlab_launcher.txt

    """

    name = "Docker"
    config = {}
    matlab_launcher = ""
    docker_keys = [
        "docker.backend",
        "docker.hub",
        "docker.image",
        "docker.hub.user",
        "docker.hub.user",
        "docker.hub.email",
        "docker.login_tmpl",
        "docker.default_tag",
        "docker.callback_url",
        "docker.argo.workflow_template",
        "docker.argo.gpu_workflow_template",
    ]
    requirement_defaults = {
        "gpu": "false",
        "gpu.count": "",
        "cpu": "500m",
        "memory": "512Mi",
        "ephemeral_storage": "1Gi",
    }

    def process_config(self, runner, **kw):
        log.debug("=== PROCESS_CONFIG START ===")
        log.debug("Input kwargs: %s", kw)
        if hasattr(runner, "bisque_cfg"):
            runner.load_section("docker", runner.bisque_cfg)
        runner.load_section("docker", runner.module_cfg)
        self.enabled = asbool(runner.config.get("docker.enabled", False))
        self.backend = (runner.config.get("docker.backend", "docker") or "docker").strip().lower()
        if self.backend not in ("docker", "argo"):
            raise ModuleEnvironmentError(
                "Unsupported docker.backend %r. Expected 'docker' or 'argo'." % self.backend
            )
        self.module_exec_env = runner.config.get("exec_env", "")
        self.requirements = self.module_requirements(runner)
        log.debug("Docker enabled: %s", self.enabled)

        self.docker_params = AttrDict()
        for k in self.docker_keys:
            key_normalized = k.replace(".", "_")
            value = runner.config.get(k, "")
            self.docker_params[key_normalized] = value
            log.debug("Docker param - %s: %s", key_normalized, value)

        log.debug("Final Docker config: %s", self.docker_params)
        log.debug("=== PROCESS_CONFIG END ===")

    def setup_environment(self, runner, build=False):
        # Construct a special environment script
        log.debug("=== SETUP_ENVIRONMENT START ===")
        log.debug("Build mode: %s", build)
        runner.info("docker environment setup")

        if not self.enabled:
            log.debug("Docker is disabled, returning early")
            runner.info("docker disabled")
            return

        if build:
            log.debug("Build mode detected")
            log.debug("Number of mexes: %d", len(runner.mexes))
            log.debug("First mex files before strtolist: %s", runner.mexes[0].files)
            runner.mexes[0].files = strtolist(runner.mexes[0].files)
            log.debug("First mex files after strtolist: %s", runner.mexes[0].files)
            runner.mexes[0].outputs = []
            log.debug("First mex outputs set to: %s", runner.mexes[0].outputs)
            return

        p = self.docker_params  # pylint: disable=invalid-name
        log.debug("Docker params object: %s", p)

        docker_pull = ""
        docker_login = ""

        # Build docker image name
        image_parts = [x for x in [p.docker_hub, p.docker_hub_user, p.docker_image] if x]
        log.debug("Docker image parts (hub, user, image): %s", image_parts)

        docker_image = "/".join(image_parts)
        log.debug("Docker image (before tag): %s", docker_image)

        if p.docker_default_tag and ":" not in docker_image:
            docker_image = "{}:{}".format(docker_image, p.docker_default_tag)
            log.debug("Docker image (after adding tag): %s", docker_image)

        # always pull an image
        if p.docker_hub:
            log.debug("Docker hub configured, setting up login and pull")
            docker_login = p.docker_login_tmpl.format(p)
            docker_pull = "docker pull %s" % docker_image
            log.debug("Docker login command: %s", docker_login)
            log.debug("Docker pull command: %s", docker_pull)
        else:
            log.debug("Docker hub not configured, skipping login/pull setup")

        log.debug("Total mexes to process: %d", len(runner.mexes))
        runner_config = getattr(runner, "config", {})
        bisque_server = runner_config.get("bisque.server", "").rstrip("/")
        docker_callback_url = p.get("docker_callback_url", "").rstrip("/")
        docker_internal_urls = [
            url for url in [bisque_server, "http://127.0.0.1:8080", "http://localhost:8080"] if url
        ]

        for mex_index, mex in enumerate(runner.mexes):
            log.debug("--- Processing mex %d ---", mex_index)
            log.debug("Mex ID: %s", mex.mex_id)
            log.debug("Mex rundir: %s", mex.rundir)
            log.debug("Mex executable: %s", mex.executable)
            log.debug("Mex files: %s", mex.files)

            docker_outputs = []
            docker_inputs = []

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
                    is_argument = "://" in str(item) or (
                        str(item).startswith("admin:") or str(item).startswith("http")
                    )
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
                    log.debug(
                        "Executable %d - Part: %s, Path: %s, Exists: %s, In files: %s",
                        exec_index,
                        p,
                        pexec,
                        exists,
                        in_files,
                    )

                    if exists and not in_files:
                        docker_inputs.append(p)
                        log.debug("Added to docker_inputs: %s", p)
            else:
                log.debug("Mex has no executables")

            log.debug("Final docker_inputs for this mex: %s", docker_inputs)
            log.debug("Final docker_outputs for this mex: %s", docker_outputs)

            docker = self.create_docker_launcher(
                mex.rundir,
                mex.mex_id,
                docker_image,
                docker_login,
                docker_pull,
                docker_inputs,
                docker_outputs,
                self.module_exec_env,
                getattr(self, "requirements", self.module_requirements(runner)),
                docker_callback_url,
                docker_internal_urls,
                getattr(self, "backend", "docker"),
                self.docker_params.get("docker_argo_workflow_template", "")
                or "bqflow-module-template",
                self.docker_params.get("docker_argo_gpu_workflow_template", "")
                or "bqflow-module-gpu-template",
            )
            log.debug("Created docker launcher at: %s", docker)

            if mex.executable:
                # Keep the original executable list intact for the docker script
                original_executable = list(mex.executable)
                log.debug("Original executable before replacement: %s", original_executable)

                # Replace entire executable with docker script + original command
                # This way: docker_run python PythonScriptWrapper.py url1 url2 token
                mex.executable = [sys.executable, docker] + original_executable
                mex.files = docker_inputs
                mex.output_files = docker_outputs + ["output_files/"]

                log.debug(
                    "Updated mex executable (docker script + original command): %s",
                    mex.executable,
                )
                log.debug("Updated mex files: %s", mex.files)
                log.debug("Updated mex output_files: %s", mex.output_files)

                # Verify the docker launcher exists. It is invoked by Python, so it is
                # intentionally not executable.
                if os.path.exists(docker):
                    script_stat = os.stat(docker)
                    log.debug(
                        "Docker script exists: %s, size: %d bytes, mode: %o",
                        docker,
                        script_stat.st_size,
                        script_stat.st_mode,
                    )
                else:
                    log.error("Docker script does NOT exist: %s", docker)

                # Log the complete command that will be executed
                log.info("FINAL COMMAND TO EXECUTE: %s", " ".join(mex.executable))
                log.info("Working directory will be: %s", mex.rundir)
                log.info("Output files will be: %s", mex.output_files)

                runner.debug("mex files %s outputs %s", mex.files, mex.output_files)
            else:
                log.debug("Warning: mex has no executables to update")

        log.debug("=== SETUP_ENVIRONMENT END ===")

    def module_requirements(self, runner):
        requirements = dict(self.requirement_defaults)
        module_requirements = {}
        if hasattr(runner, "module_cfg"):
            module_requirements = runner.module_cfg.get("requirements", asdict=True)
            requirements.update(module_requirements)

        if "gpu" not in module_requirements:
            runner_config = getattr(runner, "config", {})
            if (runner_config.get("exec_env", "") or "").strip().lower() == "use_gpu":
                requirements["gpu"] = "true"
                requirements["gpu.count"] = requirements.get("gpu.count") or "1"

        if asbool(requirements.get("gpu", "false")) and not requirements.get("gpu.count"):
            requirements["gpu.count"] = "1"
        if not asbool(requirements.get("gpu", "false")):
            requirements["gpu.count"] = ""

        return AttrDict(
            gpu=asbool(requirements.get("gpu", "false")),
            gpu_count=requirements.get("gpu.count", ""),
            cpu=requirements.get("cpu", self.requirement_defaults["cpu"]),
            memory=requirements.get("memory", self.requirement_defaults["memory"]),
            ephemeral_storage=requirements.get(
                "ephemeral_storage", self.requirement_defaults["ephemeral_storage"]
            ),
        )

    def create_docker_launcher(
        self,
        dest,
        mex_id,
        docker_image,
        docker_login,
        docker_pull,
        docker_inputs,
        docker_outputs,
        module_exec_env,
        requirements=None,
        docker_callback_url="",
        docker_internal_urls=None,
        backend="docker",
        argo_workflow_template="bqflow-module-template",
        argo_gpu_workflow_template="bqflow-module-gpu-template",
    ):
        log.debug("=== CREATE_DOCKER_LAUNCHER START ===")
        log.debug("Destination: %s", dest)
        log.debug("Mex ID: %s", mex_id)
        log.debug("Docker image: %s", docker_image)
        log.debug("Docker inputs: %s", docker_inputs)
        log.debug("Docker outputs: %s", docker_outputs)
        requirements = requirements or AttrDict(
            gpu=False,
            gpu_count="",
            cpu=self.requirement_defaults["cpu"],
            memory=self.requirement_defaults["memory"],
            ephemeral_storage=self.requirement_defaults["ephemeral_storage"],
        )
        gpu_count = requirements.gpu_count if requirements.gpu else ""

        if backend == "docker":
            inputs_str = "\n".join(
                "docker cp %s %s:/module/%s" % (f, "$CONTAINER", f) for f in docker_inputs
            )
            outputs_str = "\n".join(
                "docker cp %s:/module/%s %s" % ("$CONTAINER", f, f) for f in docker_outputs
            )

            log.debug("Generated docker inputs commands:\n%s", inputs_str)
            log.debug("Generated docker outputs commands:\n%s", outputs_str)

            content = DOCKER_LAUNCHER.format(
                docker_image=repr(docker_image),
                docker_login=repr(docker_login),
                docker_pull=repr(docker_pull),
                docker_callback_url=repr(docker_callback_url),
                docker_internal_urls=repr(docker_internal_urls or []),
                gpu_count=repr(gpu_count),
            )
        elif backend == "argo":
            content = ARGO_LAUNCHER.format(
                docker_image=repr(docker_image),
                docker_callback_url=repr(docker_callback_url),
                docker_internal_urls=repr(docker_internal_urls or []),
                mex_id=repr(mex_id),
                gpu_count=repr(gpu_count),
                cpu=repr(requirements.cpu),
                memory=repr(requirements.memory),
                ephemeral_storage=repr(requirements.ephemeral_storage),
                argo_workflow_template=repr(argo_workflow_template),
                argo_gpu_workflow_template=repr(argo_gpu_workflow_template),
            )
        else:
            raise ModuleEnvironmentError(
                "Unsupported docker.backend %r. Expected 'docker' or 'argo'." % backend
            )

        path = os.path.join(dest, "docker_run.py")

        log.debug("Writing docker launcher script to: %s", path)

        try:
            with open(path, "w") as f:
                f.write(content)
            log.debug("Successfully wrote %d bytes to launcher script", len(content))
        except Exception as e:
            log.error("Failed to write launcher script: %s", e, exc_info=True)
            raise

        try:
            os.chmod(path, 0o644)
            log.debug("Set permissions to 0o644 on: %s", path)
        except Exception as e:
            log.error("Failed to set permissions: %s", e, exc_info=True)
            raise

        log.debug("=== CREATE_DOCKER_LAUNCHER END ===")
        return path
