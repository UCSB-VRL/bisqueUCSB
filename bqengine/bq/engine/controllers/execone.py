
import os
import subprocess

import multiprocessing, logging
#logger = multiprocessing.log_to_stderr()
#logger.setLevel(multiprocessing.SUBDEBUG)
logger = logging.getLogger('bq.engine_service.execone')

def which(program):
    import os
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

def execone(params):
    """ Execute a single process locally """
    #command_line, stdout = None, stderr=None, cwd = None):
    #print "Exec", params
    command_line = params['command_line']
    rundir = params['rundir']
    env    = params['env']

    current_dir = os.getcwd()
    os.chdir(rundir)
    if os.name=='nt':
        exe = which(command_line[0])
        exe = exe or which(command_line[0] + '.exe')
        exe = exe or which(command_line[0] + '.bat')
        if exe is None:
            logger.debug('command_line: %s'%command_line)
            #raise RunnerException ("Executable was not found: %s" % command_line[0])
            return -1
        command_line[0] = exe
    logger.debug( 'CALLing %s in %s' % (command_line,  rundir))
    os.chdir(current_dir)
    try:
        return subprocess.call(params['command_line'],
                               stdout = open(params['logfile'], 'a'),
                               stderr = subprocess.STDOUT,
                               shell  = (os.name == "nt"),
                               cwd    = rundir,
                               env    = env,
                               )
    except Exception, e:
        return 1
