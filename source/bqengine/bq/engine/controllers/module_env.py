#
#
#
from .base_env import BaseEnvironment, ModuleEnvironment, ModuleEnvironmentError
from .docker_env import DockerEnvironment
from .matlab_env import MatlabDebugEnvironment, MatlabEnvironment
from .script_env import ScriptEnvironment
from .staged_env import StagedEnvironment

MODULE_ENVS = [
    BaseEnvironment,
    StagedEnvironment,
    MatlabEnvironment,
    MatlabDebugEnvironment,
    DockerEnvironment,
    ScriptEnvironment,
]
