import logging
import multiprocessing
import os
import subprocess

# logger = multiprocessing.log_to_stderr()
# logger.setLevel(multiprocessing.SUBDEBUG)
logger = logging.getLogger("bq.engine_service.execone")


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
        p.insert(0, ".")
        for path in p:
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def execone(params):
    """Execute a single process locally"""
    # command_line, stdout = None, stderr=None, cwd = None):
    # print "Exec", params
    command_line = params["command_line"]
    rundir = params["rundir"]
    env = params["env"]

    current_dir = os.getcwd()
    os.chdir(rundir)
    logger.debug("CALLing %s in %s" % (command_line, rundir))
    os.chdir(current_dir)
    try:
        return subprocess.call(
            params["command_line"],
            stdout=open(params["logfile"], "a"),
            stderr=subprocess.STDOUT,
            cwd=rundir,
            env=env,
        )
    except Exception as e:
        return 1
