###############################################################################
##  Bisque                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009,2010,2011,2012,2013,2014                 ##
##     by the Regents of the University of California                        ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ''AS IS'' AND ANY         ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE         ##
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR        ##
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR           ##
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,     ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ##
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## The views and conclusions contained in the software and documentation     ##
## are those of the authors and should not be interpreted as representing    ##
## official policies, either expressed or implied, of <copyright holder>.    ##
###############################################################################
"""
SYNOPSIS
========

DESCRIPTION
===========

"""

import logging
import os
import pickle
import shlex
import optparse
#import tempfile

try:
    from lxml import etree as et
except Exception:
    from xml.etree import ElementTree as et

from tg import config
from bq.util.configfile import ConfigFile
from bq.util.paths import  find_config_path
from bqapi import BQSession

from .base_env import strtobool, strtolist
from .module_env import MODULE_ENVS, ModuleEnvironmentError
from .mexparser import MexParser
from .pool import ProcessManager
from .attrdict import AttrDict

ENV_MAP = dict ([ (env.name, env) for env in MODULE_ENVS ])
POOL_SIZE   = int(config.get('bisque.engine_service.poolsize', 4))

logging.basicConfig(level=logging.DEBUG, filename='module.log')
#log = logging.getLogger('bq.engine_service.command_run')

####################
# Helpers
def check_exec (path, fix = True):
    if os.access (path, os.X_OK):
        return
    if fix:
        os.chmod (path, 0744)

#def strtobool(x):
#    return {"true": True, "false": False}.get(x.lower(), False)

#def strtolist(x, sep=','):
#    return [ s.strip() for s in x.split(sep)]

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        p = os.environ["PATH"].split(os.pathsep)
        p.insert(0, '.')
        for path in p:
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
##########################################
# Local exception
class RunnerException(Exception):
    """Exception in the runners"""
    def __init__(self, msg =None, mex= None):
        super( RunnerException, self).__init__(msg)
        self.mex = mex or {}
    def __str__(self):
        #return "\n".join( [ str (super( RunnerException, self) ) ] +
        #                  [ "%s: %s" % (k, self.mex[k]) for k in sorted(self.mex.keys() )] )
        return "%s env=%s" % (super( RunnerException, self).__str__(), self.mex )




###############################
# BaseRunner
class BaseRunner(object):
    """Base runner for ways of running a module in some runtime evironment.

    Runtime environments include the command line, condor and hadoop

    Each runner basically prepares the module environment, runs or stops
    modules, and allows the status of a run to be queried

    Runners interact with module environments (see base_env)

    For each module it is expected that custom  launcher will be written.
    A simple example might be:
       from bisque.util.launcher import Launcher
       class MyModuleLauncher (Launcher):
           execute='myrealmodule'
            ...

       if __name__ == "__main__":
           MyModuleLauncher().main()


    The engine will launch a subprocess with the following template:

      launcher arg1 arg2 arg3 mex=http://somehost/ms/mex/1212 start

    The launcher code will strip off the last 2 arguments and
    pass the other arguments to the real module.

    The last argument is command it must be one of the following
       start, stop, status

    """
    name       = "Base"
    env = None # A mapping of environment variables (or Inherit)
    executable = [] # A command line list of the arguments
    environments = []
    launcher   = None  # Use Default launcher
    mexhandled = "true"

    def __init__(self, **kw):
        self.parser =  optparse.OptionParser()
        self.parser.add_option("-n","--dryrun", action="store_true",
                               default=False)
        self.parser.add_option('-v', '--verbose', action="store_true",
                               default=False)
        self.parser.add_option('-d', '--debug', action="store_true",
                               default=False)
        self.session = None
        self.process_environment = dict (os.environ)
        self.log = logging.getLogger ("bq.engine_service.BaseRunner")
        self.mexid = None
        self.mexes =[]
        self.prerun = None
        self.postrun = None
        self.entrypoint_executable = None
        self.iterables = None


    def debug (self, msg, *args):
        #if self.options.verbose:
        self.log.debug( msg , *args)
    def info (self, msg, *args):
        self.log.info (msg, *args)
    def error (self, msg, *args):
        self.log.error (msg, *args)

    ###########################################
    # Config
    def read_config (self, **kw):
        """Initial state of a runner.  The module-runtime.cfg is read
        and the relevent runner section is applied.  The environment
        list is created and setup in order to construct the
        environments next
        """
        self.config = AttrDict(executable="", environments="")
        self.sections = {}
        self.debug("BaseRunner: read_config")
        # Load any bisque related variable into this runner
        runtime_bisque_cfg = find_config_path ('runtime-bisque.cfg')
        if os.path.exists(runtime_bisque_cfg):
            self.bisque_cfg = ConfigFile(runtime_bisque_cfg)
            self.load_section(None, self.bisque_cfg)
            self.config['files'] = self.config.setdefault ('files', '') + ',' + runtime_bisque_cfg
        else:
            self.info("BaseRunner: missing runtime-bisque.cfg")

        module_dir = kw.get ('module_dir', os.getcwd())
        runtime_module_cfg = os.path.join(module_dir, 'runtime-module.cfg')
        if not os.path.exists(runtime_module_cfg):
            self.info ("BaseRunner: missing %s", runtime_module_cfg)
            return
        self.module_cfg = ConfigFile(runtime_module_cfg)
        # Process Command section
        self.load_section(None, self.module_cfg)      # Globals

    def load_section (self, name, cfg):
        name = name or "__GLOBAL__"
        section = self.sections.setdefault(name, {})
        section.update  ( cfg.get (name, asdict = True) )
        self.config.update (section)
        #for k,v in section.items():
        #    setattr(self,k,v)

    #########################################################
    # Helpers
    def create_environments(self,  **kw):
        """Build the set of environments listed by the module config"""
        self.environments = strtolist(self.config.environments)
        envs = []
        for name in self.environments:
            env = ENV_MAP.get (name, None)
            if env is not None:
                envs.append (env(runner = self))
                continue
            self.log.warn ('Unknown environment: %s ignoring' , name)
        self.environments = envs
        self.info ('created environments %s' , envs)


    def process_config(self, **kw):
        """Configuration occurs in several passes.
        1.  read config file and associated runtime section
             create environments
        2.   Process the config values converting types
        """
        self.mexhandled = strtobool(self.mexhandled)

        # Find any configuration parameters in the envs
        # and add them to the class
        for env in self.environments:
            env.process_config (self)

    def setup_environments(self, **kw):
        """Call setup_environment during "start" processing
           Prepares environment and returns defined environment variable to be passed to jobs
        """
        self.debug ("setup_environments: %s", kw)
        process_env = self.process_environment.copy ()
        for env in self.environments:
            env.setup_environment (self, **kw)
        self.process_environment= process_env

    # Run during finish
    def teardown_environments(self, **kw):
        'Call teardown_environment during "finish" processing'
        for env in reversed(self.environments):
            env.teardown_environment (self, **kw)

    ##########################################
    # Initialize run state
    def init_runstate(self, arguments, **kw):
        """Initialize mex and module and deal with other arguments.
        """
        mex_tree = kw.pop('mex_tree', None)
        module_tree = kw.pop('module_tree', None)
        bisque_token = kw.pop('bisque_token', None)
        module_dir =  kw.pop ('module_dir', os.getcwd())

        # ---- the next items are preserved across execution phases ----
        # list of dict representing each mex : variables and arguments
        self.mexes = []
        self.rundir = module_dir
        self.outputs = []
        self.entrypoint_executable = []
        self.prerun = None
        self.postrun = None
        #self.process_environment (pre-set)
        #self.options (pre-set)
        # ---- the previous items are preserved across execution phases ----

        # Add remaining arguments to the executable line
        # Ensure the loaded executable is a list
        if isinstance(self.config.executable, str):
            executable = shlex.split(self.config.executable)
        #self.executable.extend (arguments)

        topmex = AttrDict(self.config)
        topmex.update(dict(named_args={},
                           executable=list(executable),
#                           arguments = [],
                           mex_url = mex_tree is not None and mex_tree.get('uri') or None,
                           bisque_token = bisque_token,
                           staging_path = None,
                           rundir = self.rundir))
        topmex.mex_id = topmex.mex_url.rsplit('/', 1)[1] if topmex.mex_url else ''
        self.mexes.append(topmex)

        # Scan argument looking for named arguments (these are used by condor_dag to re-initialize mex vars)
        for arg in arguments:
            tag, sep, val = arg.partition('=')
            if sep == '=':
                topmex.named_args[tag] = val
                if tag in topmex:
                    topmex[tag] = val

        # Pull out arguments from mex
        if mex_tree is not None and module_tree is not None:
            mexparser = MexParser()
            mex_inputs  = mexparser.prepare_inputs(module_tree, mex_tree, bisque_token)
            module_options = mexparser.prepare_options(module_tree, mex_tree)
            self.outputs = mexparser.prepare_outputs(module_tree, mex_tree)

            argument_style = module_options.get('argument_style', 'positional')
            # see if we have pre/postrun option
            self.prerun = module_options.get('prerun_entrypoint', None)
            self.postrun = module_options.get('postrun_entrypoint', None)

            topmex.named_args.update ( mexparser.prepare_mex_params( mex_inputs ) )
            topmex.executable.extend(mexparser.prepare_mex_params (mex_inputs, argument_style))
            topmex.rundir = self.rundir
            #topmex.options = module_options
            # remember topmex executable for pre/post runs

            # Create a nested list of  arguments  (in case of submex)
            submexes = mex_tree.xpath('/mex/mex')
            for mex in submexes:
                sub_inputs = mexparser.prepare_inputs(module_tree, mex)
                submex = AttrDict(self.config)
                submex.update(dict(named_args=dict(topmex.named_args),
#                                   arguments =list(topmex.arguments),
                                   executable=list(executable), #+ topmex.arguments,
                                   mex_url = mex.get('uri'),
                                   mex_id  = mex.get('uri').rsplit('/', 1)[1],
                                   bisque_token = bisque_token,
                                   staging_path = None,
                                   rundir = self.rundir))
                #if argument_style == 'named':
                #    submex.named_args.update ( [x.split('=') for x in sub_inputs] )
                submex.named_args.update(mexparser.prepare_mex_params(sub_inputs))
                submex.executable.extend(mexparser.prepare_mex_params(sub_inputs, argument_style))
                self.mexes.append(submex)
            # Submex's imply that we are iterated.
            # We can set up some options here and remove any execution
            # for the top mex.
            topmex.iterables = len(self.mexes) > 1 and mexparser.process_iterables(module_tree, mex_tree)

        self.info("processing %d mexes -> %s" % (len(self.mexes), self.mexes))

    def store_runstate(self):
        staging_path = self.mexes[0].get('staging_path') or '.'
        state_file = "state%s.bq" % self.mexes[0].get('mex_id', '')
        # pickle the object variables
        with open(os.path.join(staging_path, state_file),'wb') as f:
            pickle.dump(self.mexes, f)
            pickle.dump(self.rundir, f)
            pickle.dump([et.tostring(tree) for tree in self.outputs if tree and tree.tag == 'tag'], f)
            pickle.dump(self.entrypoint_executable, f)
            pickle.dump(self.prerun, f)
            pickle.dump(self.postrun, f)
            pickle.dump(self.process_environment, f)
            pickle.dump(self.options, f)

    def load_runstate(self):
        staging_path = self.mexes[0].get('staging_path') or  '.'
        state_file = "state%s.bq" % self.mexes[0].get('mex_id', '')
        # entered in a later processing phase (e.g., Condor finish) => unpickle
        with open(os.path.join(staging_path, state_file),'rb') as f:
            #self.pool = None   # not preserved for now
            self.mexes = pickle.load(f)
            self.rundir = pickle.load(f)
            self.outputs = [et.fromstring(tree) for tree in pickle.load(f)]
            self.entrypoint_executable = pickle.load(f)
            self.prerun = pickle.load(f)
            self.postrun = pickle.load(f)
            self.process_environment = pickle.load(f)
            self.options = pickle.load(f)


    ##################################################
    # Command sections
    # A command is launched with last argument on the command line of the launcher
    # Each command must return the either the next fommand to run or None to stop
    # Derived classes should overload these functions

    def command_start(self, **kw):
        self.info("starting %d mexes -> %s" , len(self.mexes), self.mexes)
        if self.session is None:
            self.session = BQSession().init_mex(self.mexes[0].mex_url, self.mexes[0].bisque_token)
        status  = "starting"
        self.entrypoint_executable = self.mexes[0].executable
        if self.mexes[0].iterables:
            self.mexes[0].executable = None
            status = 'running parallel'
        # add empty "outputs" section in topmex
        #self.session.update_mex(status=status, tags=[{'name':'outputs'}])
        self.session.update_mex(status=status) # dima: modules add outputs section and the empty one complicates module UI
        # if there is a prerun, run it now
        if self.prerun:
            self.info("prerun starting")
            self.command_single_entrypoint(self.prerun, self.command_execute, **kw)
            return None

        return self.command_execute

    def command_execute(self, **kw):
        """Execute the internal executable"""
        return self.command_finish

    def command_finish(self, **kw):
        """Cleanup the environment and perform any needed actions
        after the module completion
        """
        self.info("finishing %d mexes -> %s" , len(self.mexes), self.mexes)

        # if there is a postrun (aka "reduce phase"), run it now
        if self.postrun:
            self.info("postrun starting")
            self.command_single_entrypoint(self.postrun, self.command_finish2, **kw)
            return None

        self.command_finish2(**kw)

    def command_finish2(self, **kw):
        self.teardown_environments()

        if self.mexes[0].iterables:
            if self.session is None:
                self.session = BQSession().init_mex(self.mexes[0].mex_url, self.mexes[0].bisque_token)
            # outputs
            #   mex_url
            #   dataset_url  (if present and no list/range iterable)
            #   multiparam   (if at least one list/range iterable)
            need_multiparam = False
            for iter_name, iter_val, iter_type in self.mexes[0].iterables:
                if iter_type in ['list', 'range']:
                    need_multiparam = True
                    break
            outtag = et.Element('tag', name='outputs')
            if need_multiparam:
                # some list/range params => add single multiparam element if allowed by module def
                multiparam_name = None
                for output in self.outputs:
                    if output.get('type','') == 'multiparam':
                        multiparam_name = output.get('name')
                        break
                if multiparam_name:
                    # get inputs section for some submex to read actual types later
                    # TODO: this can be simplified with xpath_query in 0.6
                    inputs_subtree = None
                    if len(self.mexes) > 1:
                        submextree = self.session.fetchxml(self.mexes[1].mex_url, view='full')  # get latest MEX doc
                        inputs_subtree = submextree.xpath('./tag[@name="inputs"]')
                        inputs_subtree = inputs_subtree and self.session.fetchxml(inputs_subtree[0].get('uri'), view='deep')
                    multitag = et.SubElement(outtag, 'tag', name=multiparam_name, type='multiparam')
                    colnames = et.SubElement(multitag, 'tag', name='title')
                    coltypes = et.SubElement(multitag, 'tag', name='xmap')
                    colxpaths = et.SubElement(multitag, 'tag', name='xpath')
                    et.SubElement(multitag, 'tag', name='xreduce', value='vector')
                    for iter_name, iter_val, iter_type in self.mexes[0].iterables:
                        actual_type = inputs_subtree and inputs_subtree.xpath('.//tag[@name="%s" and @type]/@type') # read actual types from any submex
                        actual_type = actual_type[0] if actual_type else 'string'
                        et.SubElement(colnames, 'value', value=iter_name)
                        et.SubElement(coltypes, 'value', value="tag-value-%s" % actual_type)
                        et.SubElement(colxpaths, 'value', value='./mex//tag[@name="%s"]' % iter_name)
                    # last column is the submex URI
                    et.SubElement(colnames, 'value', value="submex_uri")
                    et.SubElement(coltypes, 'value', value="resource-uri")
                    et.SubElement(colxpaths, 'value', value='./mex')
                else:
                    self.log.warn("List or range parameters in Mex but no multiparam output tag in Module")
            else:
                # no list/range params => add iterables as always
                for iter_name, iter_val, iter_type in self.mexes[0].iterables:
                    et.SubElement(outtag, 'tag', name=iter_name, value=iter_val, type=iter_type)
            et.SubElement(outtag, 'tag', name='mex_url', value=self.mexes[0].mex_url, type='mex')

            self.session.finish_mex(tags = [outtag])
        return None

    def command_single_entrypoint(self, entrypoint, callback, **kw):
        return None

    def command_kill(self, **kw):
        """Kill the running module if possible
        """
        return False

    def command_status(self, **kw):
        return None

    def check(self, module_tree=None, **kw):
        "check whether the module seems to be runnable"
        self.read_config(**kw)
        # check for a disabled module
        enabled = self.config.get('module_enabled', 'true').lower() == "true"
        if not enabled :
            self.info ('Module is disabled')
            return False
        # Add remaining arguments to the executable line
        # Ensure the loaded executable is a list
        if isinstance(self.config.executable, str):
            executable = shlex.split(self.config.executable)
        if os.name == 'nt':
            return True
        canrun = executable and which(executable[0]) is not None
        if not canrun:
            self.error ("Executable cannot be run %s" % executable)
        return canrun

    def main(self, **kw):
        # Find and read a config file for the module
        created_pool = False
        try:
            self.pool = kw.pop('pool', None)
            if self.pool is None:
                self.pool =  ProcessManager (POOL_SIZE)
                created_pool = True

            self.read_config(**kw)

            args  = kw.pop('arguments', None)
            # Pull out command line arguments
            self.options, arguments = self.parser.parse_args(args)
            command_str = arguments.pop()

            # the following always has to run first so that e.g., staging dirs are set up properly
            self.init_runstate(arguments, **kw)
            self.create_environments(**kw)
            self.process_config(**kw)

            if command_str == 'start':
                # new run => setup environments from scratch
                self.setup_environments()
            else:
                # continued run => load saved run state
                try:
                    self.load_runstate()
                except OSError:
                    # could not load state => OK if it was command that can run without previous 'start' (e.g., 'kill')
                    if command_str not in ['kill']:
                        raise

            self.mexes[0].arguments = arguments

            command = getattr (self, 'command_%s' % command_str, None)
            while command:
                self.info("COMMAND_RUNNER %s" % command)
                command = command(**kw)

            if command_str not in ['kill']:
                # store run state since we may come back (e.g., condor finish)
                self.store_runstate()

            if created_pool:
                self.pool.stop()

            return 0
        except ModuleEnvironmentError, e:
            self.log.exception( "Problem occured in module")
            raise RunnerException(str(e), self.mexes)
        except RunnerException, e:
            raise
        except Exception, e:
            self.log.exception ("Unknown exeception: %s" , str( e ))
            raise RunnerException(str(e), self.mexes)

        return 1

#import multiprocessing
#log = multiprocessing.log_to_stderr()
#log.setLevel(multiprocessing.SUBDEBUG)


class CommandRunner(BaseRunner):
    """Small extension to BaseRunner to actually execute the script.
    """
    name = "command"

    def __init__(self, **kw):
        super(CommandRunner, self).__init__(**kw)
        self.log = logging.getLogger ("bq.engine_service.command_run")

    def read_config (self, **kw):
        super(CommandRunner, self).read_config (**kw)
        self.debug("CommandRunner: read_config")
        self.load_section('command', self.module_cfg) # Runner's name


    def setup_environments(self, **kw):
        super(CommandRunner, self).setup_environments(**kw)
        for mex in self.mexes:
            if not mex.executable:
                mex.log_name = os.path.join(mex.rundir, "topmex.log")
            else:
                mex.log_name = os.path.join(mex.rundir, "%s.log" % mex.executable[0])

    def command_single_entrypoint(self, entrypoint, callback, **kw):
        "Execute specific entrypoint"
        mex = self.mexes[0]   # topmex
        command_line = list(self.entrypoint_executable)
        # add entrypoint to command_line
        command_line += [ '--entrypoint', entrypoint ]
        # enclose options that start with '-' in quotes to handle numbers properly (e.g., '-3.3')
        command_line = [ tok if tok.startswith('--') or not tok.startswith('-') else '"%s"'%tok for tok in command_line ]
        rundir = mex.get('rundir')
        if self.options.dryrun:
            self.info( "DryRunning '%s' in %s" % (' '.join(command_line), rundir))
        else:
            self.info( "running '%s' in %s" % (' '.join(command_line), rundir))
            proc = dict(command_line = command_line, logfile = mex.log_name, rundir = rundir, mex=mex, env=self.process_environment,
                        entrypoint_callback = callback,
                        entrypoint_kw = kw)

            #from bq.engine.controllers.execone import execone
            #retcode = execone (proc)
            #if retcode:
            #    self.command_failed(proc, retcode)
            self.pool.schedule (proc, success=self.entrypoint_success, fail = self.command_fail)
        return None

    def entrypoint_success (self, proc):
        self.info ("Entrypoint Success for %s", proc)
        if 'entrypoint_callback' in proc:
            proc['entrypoint_callback'] (**proc['entrypoint_kw'])


    def command_execute(self, **kw):
        "Execute the commands locally specified the mex list"
        self.execute_kw = kw
        self.processes = []
        for mex in self.mexes:
            if not mex.executable:
                self.info ('skipping mex %s ' % mex)
                continue
            command_line = list(mex.executable)
            #command_line.extend (mex.arguments)
            # enclose options that start with '-' in quotes to handle numbers properly (e.g., '-3.3')
            command_line = [ tok if tok.startswith('--') or not tok.startswith('-') else '"%s"'%tok for tok in command_line ]
            rundir = mex.get('rundir')
            if  self.options.dryrun:
                self.info( "DryRunning '%s' in %s" % (' '.join(command_line), rundir))
                continue

            self.info( "running '%s' in %s" % (' '.join(command_line), rundir))
            self.info ('mex %s ' % mex)

            self.processes.append(dict( command_line = command_line, logfile = mex.log_name, rundir = rundir, mex=mex,
                                        status = 'waiting', env=self.process_environment))



        for p in self.processes:
            self.pool.schedule (p, success=self.command_success, fail=self.command_fail)
        return None
        # # ****NOTE***
        # # execone must be in engine_service as otherwise multiprocessing is unable to find it
        # # I have no idea why not.
        # from bq.engine.controllers.execone import execone

        # if self.pool:
        #     log.debug ('Using async ppool %s with %s ' % (self.pool, self.processes))
        #     #self.pool.map_async(fun, [1,2], callback = self.command_return)
        #     self.pool.map_async(execone, self.processes, callback = self.command_return)
        # else:
        #     for p in self.processes:
        #         retcode = execone (p)
        #         if retcode:
        #             self.command_failed(p, retcode)
        #     return self.command_finish
        #return None

    def command_success(self, proc):
        "collect return values when mex was executed asynchronously "
        self.info ("SUCCESS Command %s with %s" , " ".join (proc.get ('command_line')), proc.get ('return_code'))
        self.check_pool_status(proc, 'finished')

    def command_fail(self, process):
        """Update the bisque server  with a failed command for a mex"""
        command = " ".join(process['command_line'])
        retcode = process['return_code']
        exc  = process.get ('with_exception', None)
        msg = "FAILED %s: returned %s" %(command, retcode)
        if exc is not None:
            msg = "%s: exception %s" % (msg, repr(exc))
        process['fail_message'] = msg
        self.check_pool_status (process, 'failed')

    def command_kill(self, **kw):
        """Kill the running module if possible
        """
        mex = kw.get('mex_tree')
        topmex = self.mexes[0]
        if mex is not None:
            mex_id = mex.get('resource_uniq')
            self.pool.kill(selector_fct=lambda task: '00-' + task['mex'].get('mex_url').split('/00-',1)[1].split('/',1)[0] == mex_id)
            if self.session is None:
                mex_url = topmex.named_args['mex_url']
                token   = topmex.named_args['bisque_token']
                self.session = BQSession().init_mex(mex_url, token)
            self.session.fail_mex(msg = 'job stopped by user')
        else:
            self.debug("No mex provided")

        return None

    def check_pool_status(self, p, status):
        # Check that all have finished or failed
        with self.pool.pool_lock:
            p['status'] = status
            all_status = [p['status'] for p in self.processes]
            for status in all_status:
                if status not in ('finished', 'failed'):
                    return
        self.info ("All processes have returned %s", all_status)
        # all are done.. so check if we finished correctly
        if 'failed' not in all_status:
            self.mexes[0].status = 'finished'
            self.command_finish(**self.execute_kw)
            return
        # there was a failue:
        msg = '\n'.join ( p.get('fail_message') for p in self.processes if p['status'] == 'fail' )
        self.mexes[0].status = 'failed'
        self.error(msg)
        if self.session is None:
            self.session = BQSession().init_mex(self.mexes[0].mex_url, self.mexes[0].bisque_token)
        if self.session.mex.value not in ('FAILED', 'FINISHED'):
            self.session.fail_mex (msg)


#if __name__ == "__main__":
#    CommandRunner().main()
#    sys.exit(0)
