""" Setup the environment for a matlab execution.

This may require a help script which is constructed here
We also need to know which matlab to use and how to construct
the appropiate LD_LIBRARY_PATH
"""

from __future__ import with_statement

import os,sys
import string
from module_env import BaseEnvironment, ModuleEnvironmentError


MATLAB_LAUNCHER="""#!/bin/sh
#  This script is run in a clean environment (NO PATH, etc) on the remote
#  node.   All needed ENV vars must be set up before launching the script.
#
#
matlabroot=${MATLAB_HOME}

#
LD_LIBRARY_PATH=$matlabroot/runtime/glnxa64:\
$matlabroot/bin/glnxa64:\
$matlabroot/sys/os/glnxa64:\
$matlabroot/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:\
$matlabroot/sys/java/jre/glnxa64/jre/lib/amd64/server:\
$matlabroot/sys/java/jre/glnxa64/jre/lib/amd64:
XAPPLRESDIR=$matlabroot/X11/app-defaults

PATH=$PATH:$matlabroot/bin:.
HOME=.
DISPLAY=:0.0

export PATH LD_LIBRARY_PATH HOME DISPLAY  XAPPLRESDIR

SCRIPT=$1; shift;

echo "+++BEGIN"
date

echo "+++NODE"
hostname

echo "+++LOCAL DIR"
pwd
ls -l

echo "+++ENVIRONMENT"
printenv


echo "+++EXEC of ./$SCRIPT and $@"
exec ./$SCRIPT $@
"""



class MatlabEnvironment(BaseEnvironment):
    '''Matlable Environment

    This script environment prepares an execution script to run matlab
    or a matlab executable in any runtime


    Enable  the matlab environment by adding to your module.cfg::
       environments = ..., Matlab, ...

    The output file "matlab_launch" will be placed in the staging directory
    and used as the executable for any processing and will be called with
    matlab_launch executable argument argument argument

    The script will be generated based on internal template which can
    be overriden with (in runtime-module.cfg)::
       matlab_launcher = mymatlab_launcher.txt

    '''

    name = "Matlab"
    config = { }
    matlab_launcher = ""

    def process_config (self, runner, **kw):
        self.matlab_home = runner.config['runtime.matlab_home']
        self.matlab_launcher = runner.config.get('runtime.matlab_launcher', None)
        if self.matlab_launcher is not None and not os.path.exists(self.matlab_launcher):
            raise ModuleEnvironmentError("Can't find matlab script %s" % self.matlab_launcher)
        #if runner.named_args.has_key('matlab_home'):
        #    self.matlab_home = runner.named_args['matlab_home']

    def setup_environment(self, runner, **kw):
        # Construct a special environment script
        runner.info ("matlab_env setup")
        for mex in runner.mexes:
            #if mex.executable:
            condor_matlab = self.create_matlab_launcher(mex.rundir)
            condor_matlab = os.path.join('.', os.path.basename(condor_matlab))
            if mex.executable:
                mex.executable.insert(0, condor_matlab)
            mex.files.append (condor_matlab)

    def create_matlab_launcher(self, dest):
        matlab_launcher = MATLAB_LAUNCHER
        if self.matlab_launcher and os.path.exists(self.matlab_launcher):
            matlab_launcher = open(self.matlab_launcher).read()
        content = string.Template(matlab_launcher)
        content = content.safe_substitute(MATLAB_HOME=self.matlab_home)
        if os.name == 'nt':
            path = os.path.join(dest, 'matlab_launch.bat' )
        else:
            path = os.path.join(dest, 'matlab_launch' )
        with open(path, 'w') as f:
            f.write (content)
        os.chmod (path, 0744)
        return path

class MatlabDebugEnvironment(MatlabEnvironment):

    name = "MatlabDebug"

    def setup_environment(self, runner, **kw):
        # Construct a special environment script
        for mex in runner.mexes:
            #if mex.executable:
            condor_matlab = self.create_matlab_launcher(mex.rundir)
            condor_matlab = os.path.join('.', os.path.basename(condor_matlab))

            if mex.executable:
                function = mex.executable.pop(0)
                function = '%s(%s); exit;'%(function, ','.join("'%s'"%x for x in mex.executable))
                mex.executable = [condor_matlab, 'matlab', '-r', function]
