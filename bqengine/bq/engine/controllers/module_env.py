#
#
#
from base_env import ModuleEnvironmentError, ModuleEnvironment, BaseEnvironment
from staged_env import StagedEnvironment
from matlab_env import MatlabEnvironment, MatlabDebugEnvironment
from script_env import ScriptEnvironment
from docker_env import DockerEnvironment
MODULE_ENVS = [ BaseEnvironment,
                StagedEnvironment,
                MatlabEnvironment,
                MatlabDebugEnvironment,
                DockerEnvironment, 
                ScriptEnvironment ]

