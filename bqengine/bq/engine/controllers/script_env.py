#
"""
Use a script specified by the user to run setup, run, and teardown


"""
import os,sys
import shlex
import string
import subprocess
import re
from module_env import BaseEnvironment, ModuleEnvironmentError

class ScriptEnvironment(BaseEnvironment):
    """Run an external script for environment prep
    """
    name       = "Script"
    config    = {'script':""}

    def __init__(self, runner, **kw):
        super(ScriptEnvironment, self).__init__(runner, **kw)

    def process_config(self, runner):
        for mex in runner.mexes:
            if not hasattr(mex, 'script'):
                raise ModuleEnvironmentError('Missing script tag in configuration')


    def create_script(self, mex):
        """Runs before the normal command but after read the config"""

        _find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

        def quote(s):
            if not s:
                return "''"
            if _find_unsafe(s) is None:
                return s
            return "'" + s.replace("'", "'\"'\"'") + "'"

        quoted = dict ([(k, quote(v)) for (k, v) in mex.named_args.items()])
        quoted.update (dict ((k, quote(v)) for (k, v) in mex.items() if isinstance(v, basestring)))
        script = string.Template(mex.script).safe_substitute(quoted)

        script = shlex.split(script)
        mex.executable=list(script) + ['start']

        return script

    def setup_environment(self, runner):
        for mex in runner.mexes:
            if mex.executable:
                script = self.create_script(mex)
                rundir = mex.get('rundir')
                runner.debug ("Execute setup '%s' in %s" % (" ".join (script + ['setup']), rundir))
                runner.debug ("logging to  %s " % mex.log_name)
                r =  subprocess.call(script + ['setup'],
                                     stdout=open(mex.log_name, 'a'),
                                     stderr = subprocess.STDOUT,
                                     cwd = rundir)
                if r != 0:
                    raise ModuleEnvironmentError("setup returned %s"  % r)

    def teardown_environment(self, runner):
        for mex in runner.mexes:
            if mex.executable:
                script = self.create_script(mex)
                rundir = mex.get('rundir')
                runner.debug ("Execute teardown '%s' in %s" % (" ".join(script+['teardown']), rundir))
                r = subprocess.call(script + ['teardown'],
                                    stdout=open(mex.log_name, 'a'),
                                    stderr = subprocess.STDOUT,
                                    cwd = rundir)
                if r != 0:
                    raise ModuleEnvironmentError("teardown returned %s"  % r)
