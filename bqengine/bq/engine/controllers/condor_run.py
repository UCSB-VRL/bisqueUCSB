# condor_run.py
#
import os
#import logging
#import string
import subprocess
#import StringIO
import platform

#from bq.util.configfile import ConfigFile
from bq.util.paths import config_path
from bqapi import BQSession

#from .attrdict import AttrDict
from .command_run import CommandRunner, strtolist, check_exec
from .condor_templates import CondorTemplates

class CondorRunner (CommandRunner):
    """A Runtime to execute a module on a condor enabled system


    """
    name     = "condor"

    transfers= []  # Condor transfers (see condor docs)
    requirements = ""  #  Condor "&& (Memory > 3000) && IsWholeMachineSlot"
    dag_template = ""
    submit_template = ""


    def __init__(self, **kw):
        super(CondorRunner, self).__init__(**kw)

    def read_config(self, **kw):
        super(CondorRunner, self).read_config(**kw)
        self.debug("CondorRunner: read_config")
        self.load_section ('condor', self.bisque_cfg)
        self.load_section ('condor', self.module_cfg)
        self.load_section ('condor_submit', self.bisque_cfg)
        self.load_section ('condor_submit', self.module_cfg)

    def process_config(self, **kw):
        super(CondorRunner, self).process_config(**kw)
        self.info ("process_config condor")

        # any listed file will be a transfer
        for mex in self.mexes:
            mex.files = strtolist(mex.get('files', []))
            mex.output_files = strtolist(mex.get('output_files', []))
            mex.files.append('runtime-module.cfg')
            mex.files.append(os.path.abspath (config_path ('runtime-bisque.cfg')))

    def setup_environments(self, **kw):
        super(CondorRunner, self).setup_environments(**kw)

        self.info ("setup_environments condor")
        for mex in self.mexes:
            mex.transfers = list(mex.files)
            mex.transfers_out = list (mex.output_files)

    def command_start(self, **kw):
        super(CondorRunner, self).command_start(**kw)

        self.helper = CondorTemplates(self.sections['condor'])
        # Condor requires a real Launcher (executable) in order
        # to post process. If it does not exist we create a small stub
        topmex = self.mexes[0]
        executable = topmex.executable
        if len(self.mexes)>1:
            # multimex
            executable = self.mexes[1].executable

        postargs=[]
        if self.options.verbose:
            postargs.append('-v')
        if self.options.debug:
            postargs.append('-d')
        if self.options.dryrun:
            postargs.append('-n')
        postargs.append ('mex_id=%s' % topmex.mex_id)
        postargs.append ('staging_path=%s' % topmex.staging_path)
        postargs.extend ([ '%s=%s' % (k,v) for k,v in topmex.named_args.items()
                           if k!='mex_id' and k!='staging_path'])
        postargs.append('mex_url=%s' % topmex.mex_url)
        postargs.append('bisque_token=%s' % topmex.bisque_token)
        postargs.append('condor_job_return=$RETURN')
        #postargs.append('$RETURN')
        postargs.append ('finish')

        for mex in self.mexes:
            mex_vars = dict(mex)
            mex_vars.update(mex.named_args)
            mex_vars.update(self.sections['condor'])
            mex_vars.update(self.sections['condor_submit'])
            if mex.get('launcher') is None:
                mex.launcher = self.helper.construct_launcher(mex_vars)
                check_exec (mex.launcher) # Esnure this launcher is executable
            mex.launcher = os.path.basename(mex.launcher)

        self.debug("Creating submit file")

        top_vars = dict(topmex)
        top_vars.update(topmex.named_args)
        top_vars.update(self.sections['condor'])
        top_vars.update(self.sections['condor_submit'])
        top_vars.update(
            executable   = executable[0],
            #arguments   = ' '.join (self.executable[1:]),
            #transfers   = ",".join(self.transfers),
            mexes        = self.mexes,
            post_exec    = topmex.launcher,
            post_args    = " ".join (postargs),
            condor_submit= "\n".join(["%s=%s"%(k,v)
                                      for k,v in self.sections['condor_submit'].items()])
            )
        self.helper.prepare_submit(top_vars)

        # Immediately go to execute
        return self.command_execute

    def command_execute(self, **kw):
        #self.info ("condor_execute: On %s",  platform.node())

        cmd = ['condor_submit_dag', self.helper.dag_path]
        process = dict(command_line = cmd, mex = self.mexes[0])
        self.info("SUBMIT %s in %s", cmd, self.mexes[0].get('staging_path'))
        if not self.options.dryrun:
            submit =  subprocess.Popen (cmd, cwd=self.mexes[0].get('staging_path'),
                                         stdout = subprocess.PIPE)
            out, err = submit.communicate()

            if submit.returncode != 0:
                self.command_failed(process, submit.returncode)

#             # get ID of dag runner cluster and store in runner_ids
#             runner_id = None
#             for line in out.split('\n'):
#                 toks = line.split('job(s) submitted to cluster')
#                 if len(toks) == 2:
#                     runner_id = toks[1].strip().rstrip('.')
#                     break
#             if runner_id is not None:
#                 self.runner_ids[self.mexes[0].mex_id] = runner_id

        # Don't do anything after execute
        return None

    def command_finish(self, **kw):
        # Cleanup condor stuff and look for error files.

        topmex = self.mexes[0]
        job_return = int(topmex.named_args.get ('condor_job_return', 0))
        #job_return = int(topmex.arguments.pop())
        self.info ("condor_finish %s: return=%s", topmex.executable, job_return)
        if job_return != 0:
            if self.session is None:
                mex_url = topmex.named_args['mex_url']
                token   = topmex.named_args['bisque_token']
                self.session = BQSession().init_mex(mex_url, token)
            # Possible look for log files and append to message here
            #if os.path.exists(''):
            #    pass
            self.session.fail_mex(msg = 'job failed with return code %s' % job_return)
            return None
        topmex.status = "finished"
        return super(CondorRunner, self).command_finish(**kw)

    def command_failed(self, process, retcode):
        """Update the bisque server  with a failed command for a mex"""
        mex = process['mex']
        mex.status = "failed"
        command = " ".join(process['command_line'])
        msg = "%s: returned (non-zero) %s" % (command, retcode)
        self.error("condor_failed: " + msg)
        # update process mex
        if self.session is None:
            self.session = BQSession().init_mex(self.mexes[0].mex_url, self.mexes[0].bisque_token)
        if self.session.mex.value not in ('FAILED', 'FINISHED'):
            self.session.fail_mex (msg)

    def command_kill(self, **kw):
        """Kill the running module if possible
        """
        self.info ("Kill On %s",  platform.node())
        mex = kw.get('mex_tree')
        topmex = self.mexes[0]
        if mex is not None:
            mex_id = mex.get('resource_uniq')

            # get all condor schedds
            schedd_names = []
            cmd = ['condor_status', '-long', '-schedd']
            pk = subprocess.Popen(cmd, stdout = subprocess.PIPE)
            for line in pk.stdout:
                toks = line.split('=', 1)
                if len(toks) == 2:
                    if toks[0].strip().lower() == 'name':
                        schedd_names.append(toks[1].strip().strip('"').strip("'"))
            self.debug("schedds found: %s" % schedd_names)
            pk.communicate()
            if pk.returncode != 0:
                self.debug("condor_status failed")
                process = dict(command_line = cmd, mex = topmex)
                self.command_failed(process, pk.returncode)
                return None

            # for each one: condor_rm with condition "mexid == <mexid>"
            for schedd_name in schedd_names:
                cmd = ['condor_rm', '-name', schedd_name, '-constraint', 'MexID =?= "%s"' % mex_id]
                self.debug("running %s", cmd)
                pk = subprocess.Popen (cmd,
                                       cwd=topmex.get('staging_path'),
                                       stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                message, err = pk.communicate()
                self.info("condor_rm %s status = %s message = %s err = %s" % (schedd_name, pk.returncode, message, err))
                if pk.returncode != 0:
                    self.debug("condor_rm failed")
                    process = dict(command_line = cmd, mex = topmex)
                    self.command_failed(process, pk.returncode)
                    return None

            if self.session is None:
                mex_url = topmex.named_args['mex_url']
                token   = topmex.named_args['bisque_token']
                self.session = BQSession().init_mex(mex_url, token)
            self.session.fail_mex(msg = 'job stopped by user')
        else:
            self.debug("No mex provided")

        return None

    def command_status(self, **kw):
        message =  subprocess.Popen (['condor_q', ],
                          cwd=self.mexes[0].get('staging_path'),
                          stdout = subprocess.PIPE).communicate()[0]
        self.info ("status = %s " , message)
        return None



class CondorMatlabRunner(CondorRunner):

   def process_config(self, **kw):
        super(CondorMatlabRunner, self).process_config(**kw)
