import os
import stat
import subprocess
import sys
from threading import Lock

import pytest
from bq.engine.controllers import command_run, module_run
from bq.engine.controllers.attrdict import AttrDict
from bq.engine.controllers.command_run import CommandRunner
from bq.engine.controllers.docker_env import DockerEnvironment
from bq.engine.controllers.module_env import ModuleEnvironmentError
from bq.engine.controllers.module_run import ModuleRunner
from lxml import etree

pytestmark = pytest.mark.unit


def test_choose_runner_uses_site_runtime_platforms(tmp_path, monkeypatch):
    (tmp_path / "runtime-module.cfg").write_text("runtime.platforms = command\n")
    monkeypatch.setattr(module_run, "find_config_path", lambda _name: None)
    monkeypatch.setitem(module_run.config, "runtime.platforms", "command")

    runner_class = ModuleRunner().choose_runner(module_dir=str(tmp_path))

    assert runner_class is CommandRunner


def test_choose_runner_requires_system_runtime_platforms(tmp_path, monkeypatch):
    (tmp_path / "runtime-module.cfg").write_text("runtime.platforms = command\n")
    monkeypatch.setattr(module_run, "find_config_path", lambda _name: None)
    monkeypatch.delitem(module_run.config, "runtime.platforms", raising=False)
    monkeypatch.delitem(module_run.config, "runtime.mode", raising=False)

    with pytest.raises(ModuleEnvironmentError, match="runtime.platforms"):
        ModuleRunner().choose_runner(module_dir=str(tmp_path))


def test_choose_runner_rejects_unsupported_site_runtime_platform(tmp_path, monkeypatch):
    (tmp_path / "runtime-module.cfg").write_text("runtime.platforms = command\n")
    monkeypatch.setattr(module_run, "find_config_path", lambda _name: None)
    monkeypatch.setitem(module_run.config, "runtime.platforms", "unsupported")

    with pytest.raises(ModuleEnvironmentError, match="No compatible runtime platform"):
        ModuleRunner().choose_runner(module_dir=str(tmp_path))


def test_command_runner_read_config_uses_site_runtime_settings(tmp_path, monkeypatch):
    (tmp_path / "runtime-module.cfg").write_text(
        """runtime.platforms = command

[command]
executable = python PythonScriptWrapper.py
environments = Staged,Docker
        """
    )
    monkeypatch.setattr(command_run, "find_config_path", lambda _name: None)
    monkeypatch.setitem(command_run.config, "runtime.staging_base", "/tmp/bisque-staging")
    monkeypatch.setitem(command_run.config, "docker.enabled", "True")

    runner = CommandRunner()
    runner.read_config(module_dir=str(tmp_path))

    assert runner.config.executable == "python PythonScriptWrapper.py"
    assert runner.config["runtime.staging_base"] == "/tmp/bisque-staging"
    assert runner.config["docker.enabled"] == "True"


def test_command_runner_keeps_module_docker_environment(tmp_path, monkeypatch):
    (tmp_path / "runtime-module.cfg").write_text(
        """runtime.platforms = command

[command]
executable = python PythonScriptWrapper.py
environments = Staged,Docker
        """
    )
    monkeypatch.setattr(command_run, "find_config_path", lambda _name: None)

    runner = CommandRunner()
    runner.read_config(module_dir=str(tmp_path))

    assert runner.config.executable == "python PythonScriptWrapper.py"
    assert "Docker" in runner.config.environments.split(",")


def test_docker_launcher_uses_python_instead_of_os_shell(tmp_path):
    launcher = DockerEnvironment(object()).create_docker_launcher(
        str(tmp_path),
        "00-test",
        "edgedetection:v1.0.0",
        "",
        "",
        [],
        [],
        "",
        None,
    )

    mode = stat.S_IMODE((tmp_path / "docker_run.py").stat().st_mode)
    content = (tmp_path / "docker_run.py").read_text()

    assert launcher == str(tmp_path / "docker_run.py")
    assert mode == 0o644
    assert not content.startswith("#!")
    assert 'docker_command = ["docker", "create"]' in content
    assert 'run(["docker", "start", container])' in content
    assert 'run_output(["docker", "wait", container])' in content
    assert 'run(["docker", "logs", container])' in content
    assert 'run(["docker", "cp", container_path, host_path])' in content
    assert 'MODULE_LOG_FILES = ("PythonScript.log", "scriptrun.log")' in content
    assert 'run(["docker", "rm", container])' in content
    assert "host.docker.internal" in content
    assert (
        'docker_command.extend(["--network=host", "--add-host=host.docker.internal:host-gateway"])'
        in content
    )


def test_docker_launcher_keeps_gpu_flags_for_local_docker(tmp_path):
    DockerEnvironment(object()).create_docker_launcher(
        str(tmp_path),
        "00-test",
        "gpu-module:v1",
        "",
        "",
        [],
        [],
        "",
        AttrDict(
            gpu=True,
            gpu_count="2",
            cpu="2",
            memory="8Gi",
            ephemeral_storage="10Gi",
        ),
    )

    content = (tmp_path / "docker_run.py").read_text()

    assert "GPU_COUNT = '2'" in content
    assert 'docker_command.extend(["--gpus", str(GPU_COUNT)])' in content


def test_argo_launcher_submits_workflow_template(tmp_path):
    launcher = DockerEnvironment(object()).create_docker_launcher(
        str(tmp_path),
        "00-Test_Mex",
        "edgedetection:v1.0.0",
        "",
        "",
        [],
        [],
        "",
        None,
        "http://bisque:8080",
        ["http://127.0.0.1:8080"],
        "argo",
        "bqflow-module-template",
        "bqflow-module-gpu-template",
    )

    content = (tmp_path / "docker_run.py").read_text()

    assert launcher == str(tmp_path / "docker_run.py")
    assert '"argo",' in content
    assert '"submit",' in content
    assert '"--log",' in content
    assert '"workflowtemplate/%s" % template' in content
    assert "json.dump(params, parameter_file)" in content
    assert "shlex.join(module_argument(arg) for arg in sys.argv[1:])" in content
    assert "DOCKER_CALLBACK_URL = 'http://bisque:8080'" in content
    assert '"cpu": CPU' in content
    assert '"memory": MEMORY' in content
    assert '"gpu_count": str(GPU_COUNT or "")' in content
    assert "docker_command" not in content


def test_argo_launcher_uses_gpu_template_when_requirements_request_gpu(tmp_path):
    DockerEnvironment(object()).create_docker_launcher(
        str(tmp_path),
        "00-test",
        "gpu-module:v1",
        "",
        "",
        [],
        [],
        "",
        AttrDict(
            gpu=True,
            gpu_count="1",
            cpu="2",
            memory="8Gi",
            ephemeral_storage="10Gi",
        ),
        "",
        [],
        "argo",
        "cpu-template",
        "gpu-template",
    )

    content = (tmp_path / "docker_run.py").read_text()

    assert "GPU_COUNT = '1'" in content
    assert "CPU = '2'" in content
    assert "MEMORY = '8Gi'" in content
    assert "EPHEMERAL_STORAGE = '10Gi'" in content
    assert "ARGO_WORKFLOW_TEMPLATE = 'cpu-template'" in content
    assert "ARGO_GPU_WORKFLOW_TEMPLATE = 'gpu-template'" in content


def test_module_requirements_uses_legacy_exec_env_gpu_fallback(tmp_path):
    (tmp_path / "runtime-module.cfg").write_text(
        """runtime.platforms = command

[command]
docker.image = gpu-module:v1
environments = Staged,Docker
executable = python PythonScriptWrapper.py
exec_env = use_gpu
        """
    )
    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(command_run, "find_config_path", lambda _name: None)
        runner = CommandRunner()
        runner.read_config(module_dir=str(tmp_path))

        requirements = DockerEnvironment(object()).module_requirements(runner)

        assert requirements.gpu is True
        assert requirements.gpu_count == "1"
    finally:
        monkeypatch.undo()


def test_module_requirements_prefers_requirements_section(tmp_path, monkeypatch):
    (tmp_path / "runtime-module.cfg").write_text(
        """runtime.platforms = command

[command]
docker.image = cpu-module:v1
environments = Staged,Docker
executable = python PythonScriptWrapper.py
exec_env = use_gpu

[requirements]
gpu = false
cpu = 4
memory = 16Gi
ephemeral_storage = 20Gi
        """
    )
    monkeypatch.setattr(command_run, "find_config_path", lambda _name: None)
    runner = CommandRunner()
    runner.read_config(module_dir=str(tmp_path))

    requirements = DockerEnvironment(object()).module_requirements(runner)

    assert requirements.gpu is False
    assert requirements.gpu_count == ""
    assert requirements.cpu == "4"
    assert requirements.memory == "16Gi"
    assert requirements.ephemeral_storage == "20Gi"


def test_command_runner_uses_callback_url_for_internal_bisque_urls_k3s():
    module_tree = etree.XML(
        """
        <module name="EdgeDetection">
          <tag name="inputs">
            <tag name="Input Image" type="resource"/>
            <tag name="mex_url" type="system-input_resource"/>
            <tag name="bisque_token" type="system-input_resource"/>
          </tag>
          <tag name="outputs"/>
        </module>
        """
    )
    mex_tree = etree.XML(
        """
        <mex uri="http://bisque.localhost:8080/module_service/mex/00-mex">
          <tag name="inputs">
            <tag name="Input Image" type="resource"
                 value="http://bisque.localhost:8080/data_service/00-image"/>
          </tag>
        </mex>
        """
    )

    runner = CommandRunner()
    runner.config = AttrDict(
        executable="python PythonScriptWrapper.py",
        **{
            "bisque.server": "http://bisque.localhost:8080",
            "docker.callback_url": "http://bisque:8080",
        },
    )

    runner.init_runstate([], mex_tree=mex_tree, module_tree=module_tree, bisque_token="admin:token")

    assert mex_tree.get("uri") == "http://bisque:8080/module_service/mex/00-mex"
    assert (
        mex_tree.xpath('string(./tag[@name="inputs"]/tag[@name="Input Image"]/@value)')
        == "http://bisque:8080/data_service/00-image"
    )
    assert runner.mexes[0].mex_url == "http://bisque:8080/module_service/mex/00-mex"
    assert runner.mexes[0].named_args["Input Image"] == "http://bisque:8080/data_service/00-image"
    assert runner.mexes[0].named_args["mex_url"] == "http://bisque:8080/module_service/mex/00-mex"
    assert "http://bisque:8080/data_service/00-image" in runner.mexes[0].executable


def test_command_runner_uses_callback_url_for_k3s_public_url_without_port():
    module_tree = etree.XML(
        """
        <module name="EdgeDetection">
          <tag name="inputs">
            <tag name="Input Image" type="resource"/>
            <tag name="mex_url" type="system-input_resource"/>
          </tag>
          <tag name="outputs"/>
        </module>
        """
    )
    mex_tree = etree.XML(
        """
        <mex uri="http://bisque.localhost:8080/module_service/mex/00-mex">
          <tag name="inputs">
            <tag name="Input Image" type="resource"
                 value="http://bisque.localhost:8080/data_service/00-image"/>
          </tag>
        </mex>
        """
    )

    runner = CommandRunner()
    runner.config = AttrDict(
        executable="python PythonScriptWrapper.py",
        **{
            "bisque.server": "http://bisque.localhost",
            "docker.callback_url": "http://bisque:8080",
        },
    )

    runner.init_runstate([], mex_tree=mex_tree, module_tree=module_tree, bisque_token="admin:token")

    assert runner.mexes[0].mex_url == "http://bisque:8080/module_service/mex/00-mex"
    assert runner.mexes[0].named_args["Input Image"] == "http://bisque:8080/data_service/00-image"
    assert runner.mexes[0].named_args["mex_url"] == "http://bisque:8080/module_service/mex/00-mex"
    assert "http://bisque:8080/data_service/00-image" in runner.mexes[0].executable


def test_command_runner_uses_callback_url_for_internal_bisque_urls_compose():
    module_tree = etree.XML(
        """
        <module name="EdgeDetection">
          <tag name="inputs">
            <tag name="Input Image" type="resource"/>
            <tag name="mex_url" type="system-input_resource"/>
          </tag>
          <tag name="outputs"/>
        </module>
        """
    )
    mex_tree = etree.XML(
        """
        <mex uri="http://127.0.0.1:8080/module_service/mex/00-mex">
          <tag name="inputs">
            <tag name="Input Image" type="resource"
                 value="http://127.0.0.1:8080/data_service/00-image"/>
          </tag>
        </mex>
        """
    )

    runner = CommandRunner()
    runner.config = AttrDict(
        executable="python PythonScriptWrapper.py",
        **{
            "bisque.server": "http://127.0.0.1:8080",
            "docker.callback_url": "http://host.docker.internal:8080",
        },
    )

    runner.init_runstate([], mex_tree=mex_tree, module_tree=module_tree, bisque_token="admin:token")

    assert runner.mexes[0].mex_url == "http://host.docker.internal:8080/module_service/mex/00-mex"
    assert (
        runner.mexes[0].named_args["Input Image"]
        == "http://host.docker.internal:8080/data_service/00-image"
    )
    assert (
        runner.mexes[0].named_args["mex_url"]
        == "http://host.docker.internal:8080/module_service/mex/00-mex"
    )
    assert "http://host.docker.internal:8080/data_service/00-image" in runner.mexes[0].executable


def test_command_runner_leaves_external_urls_unchanged():
    runner = CommandRunner()
    runner.config = AttrDict(
        **{
            "bisque.server": "http://bisque.localhost:8080",
            "docker.callback_url": "http://bisque:8080",
        }
    )

    assert (
        runner.internal_bisque_url("https://external-engine.example.org/engine_service/MyModule")
        == "https://external-engine.example.org/engine_service/MyModule"
    )
    assert (
        runner.internal_bisque_url("https://example.org/data/file.tif")
        == "https://example.org/data/file.tif"
    )


def test_docker_environment_runs_launcher_with_current_python(tmp_path):
    class Mex:
        mex_id = "00-test"
        rundir = str(tmp_path)
        executable = [
            "python",
            "PythonScriptWrapper.py",
            "http://localhost:8080/data_service/00-image",
        ]
        files = []

    class Runner:
        mexes = [Mex()]

        def info(self, *args):
            pass

        def debug(self, *args):
            pass

    runner = Runner()
    environment = DockerEnvironment(object())
    environment.enabled = True
    environment.module_exec_env = ""
    environment.docker_params = AttrDict(
        docker_hub="",
        docker_hub_user="",
        docker_image="edgedetection:v1.0.0",
        docker_default_tag="",
        docker_login_tmpl="",
        docker_backend="docker",
    )

    environment.setup_environment(runner)

    assert runner.mexes[0].executable[:2] == [
        sys.executable,
        str(tmp_path / "docker_run.py"),
    ]


def test_docker_launcher_rewrites_internal_urls_to_callback_url(tmp_path):
    DockerEnvironment(object()).create_docker_launcher(
        str(tmp_path),
        "00-test",
        "edgedetection:v1.0.0",
        "",
        "",
        [],
        [],
        "",
        None,
        "http://host.docker.internal:8080",
        ["http://127.0.0.1:8080"],
    )

    launcher = tmp_path / "docker_run.py"
    content = launcher.read_text()

    assert "DOCKER_CALLBACK_URL = 'http://host.docker.internal:8080'" in content
    assert "DOCKER_INTERNAL_URLS = ['http://127.0.0.1:8080']" in content
    assert 'return DOCKER_CALLBACK_URL.rstrip("/") + argument[len(internal_url) :]' in content


def test_docker_launcher_copies_logs_ignores_missing_logs_and_preserves_exit_code(
    tmp_path, monkeypatch
):
    launcher = DockerEnvironment(object()).create_docker_launcher(
        str(tmp_path),
        "00-test",
        "edgedetection:v1.0.0",
        "",
        "",
        [],
        [],
        "",
        None,
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    command_log = tmp_path / "docker_commands.txt"
    fake_docker = bin_dir / "docker"
    fake_docker.write_text(
        """#!/usr/bin/env python3
import os
import sys

command = sys.argv[1]
with open(os.environ["FAKE_DOCKER_COMMAND_LOG"], "a") as handle:
    handle.write(" ".join(sys.argv[1:]) + "\\n")

if command == "create":
    print("container-123")
elif command == "start":
    sys.exit(0)
elif command == "wait":
    print(os.environ.get("FAKE_MODULE_EXIT", "7"))
elif command == "logs":
    print("module stdout")
elif command == "cp":
    source = sys.argv[2]
    destination = sys.argv[3]
    if source.endswith("/PythonScript.log"):
        with open(destination, "w") as handle:
            handle.write("python log\\n")
        sys.exit(0)
    sys.exit(1)
elif command == "rm":
    sys.exit(0)
else:
    sys.exit(99)
"""
    )
    fake_docker.chmod(0o755)
    monkeypatch.setenv("PATH", os.pathsep.join([str(bin_dir), os.environ.get("PATH", "")]))
    monkeypatch.setenv("FAKE_DOCKER_COMMAND_LOG", str(command_log))
    monkeypatch.setenv("FAKE_MODULE_EXIT", "7")

    result = subprocess.run(
        [sys.executable, launcher, "python", "PythonScriptWrapper.py"],
        cwd=tmp_path,
        check=False,
    )

    commands = command_log.read_text().splitlines()
    assert result.returncode == 7
    assert (tmp_path / "PythonScript.log").read_text() == "python log\n"
    assert not (tmp_path / "scriptrun.log").exists()
    assert any(
        command.startswith("cp container-123:/module/PythonScript.log") for command in commands
    )
    assert any(command.startswith("cp container-123:/module/scriptrun.log") for command in commands)
    assert commands[-1] == "rm container-123"


def test_command_runner_reports_failed_process_message():
    class Pool:
        pool_lock = Lock()

    class Mex:
        status = None
        mex_url = "http://example.invalid/mex/00-test"
        bisque_token = "token"

    class Session:
        class mex:
            value = "RUNNING"

        def __init__(self):
            self.failed_message = None

        def fail_mex(self, msg):
            self.failed_message = msg

    runner = CommandRunner()
    runner.pool = Pool()
    runner.mexes = [Mex()]
    runner.session = Session()
    runner.processes = [
        {"status": "finished"},
        {"status": "waiting", "fail_message": "docker_run permission denied"},
    ]
    errors = []
    runner.error = errors.append

    runner.check_pool_status(runner.processes[1], "failed")

    assert runner.mexes[0].status == "failed"
    assert errors == ["docker_run permission denied"]
    assert runner.session.failed_message == "docker_run permission denied"
