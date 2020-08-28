#
"""



"""
import os
import shutil

from bq.util.copylink import copy_link

from .base_env import strtolist
from .module_env import BaseEnvironment, ModuleEnvironmentError

STAGING_BASE="~/staging"

#def strtolist(x, sep=','):
#    return [ s.strip() for s in x.split(sep)]

class StagedEnvironment(BaseEnvironment):
    """A staged environment creates a temporary staging area
    for a module run.  This is usefull for launcher that need
    local files or simply shouldn't be run in source area
    """
    name       = "Staged"
    config    = {'files':[], 'staging_path':None, 'mex_id':None}

    def __init__(self, runner, **kw):
        super(StagedEnvironment, self).__init__(runner, **kw)
        self.mex = None
        self.initial_dir = None

    def process_config(self, runner):
        setup_dir = os.getcwd()
        for mex in runner.mexes:
            mex.initial_dir = mex.module_dir = setup_dir
            mex.files = mex.get('files', [])
            if isinstance(mex.files, basestring):
                mex.files =  strtolist(mex.files)
            mex.staging_path= mex.staging_path or mex.named_args.get ('staging_path')
            if mex.staging_path is None:
                self._set_staging_path(runner, mex)
            #mex.mex_id=mex.named_args.get ('mex_id')

    def _set_staging_path(self, runner, mex):
        runner.debug ( 'mex_id = %s' , mex.mex_id)
        if not mex.staging_path:
            staging_base = mex.get('runtime.staging_base', STAGING_BASE)
            mex.staging_path = os.path.abspath(os.path.expanduser(
                os.path.join (staging_base, mex.mex_id)))

        runner.debug ( 'staging_path = %s' % mex.staging_path)
        mex.rundir = mex.staging_path

    def _staging_setup(self, runner, mex, create=True, **kw):
        self._set_staging_path (runner, mex)
        if create and not os.path.exists (mex.staging_path) :
            runner.debug ( 'create dir staging_path = %s' % mex.staging_path)
            os.makedirs (mex.staging_path)

    def _filelist(self, runner, files, **kw):
        if os.name != 'nt':
            return [ os.path.join(runner.rundir, f) for f in files ]
        fs = []
        for f in files:
            mf = os.path.join (runner.rundir, f)
            if not os.path.exists(mf) and os.path.exists(mf + '.exe'):
                fs.append(mf+'.exe')
                continue
            if not os.path.exists(mf) and os.path.exists(mf + '.bat'):
                fs.append(mf+'.bat')
                continue
            fs.append(mf)
        return fs

    def setup_environment(self, runner, **kw):
        """Create the staging area and place the executable there
        """
        runner.info ("staged environment setup cwd=%s rundir=%s", os.getcwd(), runner.rundir)
        for mex in runner.mexes:
            self._staging_setup(runner, mex)
            if mex.get('files'):
                files = self._filelist(runner, mex.files)
                runner.debug ("copying %s: %s to %s" % (mex.initial_dir, files, mex.staging_path))
                copy_link(*(files + [ mex.staging_path ]))
        return {'HOME': mex.staging_path}

    def teardown_environment(self, runner, **lw):
        """Remove the staging area
        """
        for mex in runner.mexes:
            self._staging_setup(runner, mex, False)

            #if mex.initial_dir:
            #    os.chdir (mex.initial_dir)

            if  runner.options.dryrun or runner.options.debug:
                runner.info('not removing %s for debug or dryrun' , mex.staging_path)
                return


            status = getattr (mex, 'status', None)
            runner.debug( "Cleaning %s with status %s",  getattr (mex,'staging_path', None), status)
            if status == "finished":
                #shutil.rmtree (mex.staging_path)
                pass
