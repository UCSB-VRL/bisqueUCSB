import os
import subprocess
from threading import Thread, Lock
import logging
from time import sleep

try: 
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty # Python 2.x

logger = logging.getLogger('bq.engine_service.pool')


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
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


def worker(queue, thread_tasks, worker_id):
    """Worker waits forever command requests and executes one command at a time

    @param queue: is a queue of command requests
    @param thread_tasks: mapping worker_id -> (task, subprocess) (or None)
    @param worker_id: integer identifying this worker
     
    requests  = {
      command_line : ['processs', 'arg1', 'arg1']
      rundir       : 'directory to run in ',
      logfile      :  'file to  write stderr and stdout',
      on_success   : callback with (request) when success,
      on_fail      : callback with (request) when fail,
      env          : dict of environment
    }

    This routine will add the following fields:
    {
       return_code : return code of the command
       with_exception : an exception when exited with excepttion
    }
    """
    for request in iter(queue.get, None):
        if request is None:
            return
        
        rundir = request['rundir']
        env    = request['env']
        callme = request.get ('on_fail') # Default to fail
        request.setdefault('return_code',1)

        current_dir = os.getcwd()
        command_line = request['command_line']
        #os.chdir(rundir)
        if os.name=='nt':
            exe = which(command_line[0])
            exe = exe or which(command_line[0] + '.exe')
            exe = exe or which(command_line[0] + '.bat')
            if exe is None:
                logger.debug('command_line: %s', command_line)
                #raise RunnerException ("Executable was not found: %s" % command_line[0])
                return -1
            command_line[0] = exe
        logger.debug( 'CALLing %s in %s' , command_line,  rundir)
        #os.chdir(current_dir)
        try:
            subproc = subprocess.Popen(command_line,
                                       stdout = open(request['logfile'], 'a'),
                                       stderr = subprocess.STDOUT,
                                       shell  = (os.name == "nt"),
                                       cwd    = rundir,
                                       env    = env,)
            # remember which request this thread is working on
            thread_tasks[worker_id] = (request, subproc)
            # wait for termination
            retcode = subproc.wait()
            logger.debug ("RET %s with %s", command_line, retcode)
            request ['return_code'] =retcode
            if retcode == 0:
                callme = request.get('on_success')
        except Exception, e:
            request['with_exception'] = e
        finally:
            thread_tasks[worker_id] = None
            if callable(callme):
                callme(request)


class ProcessManager(object):
    "Manage a set of threads to execute limited subprocess"
    def __init__(self, limit=4):
        self.pool = Queue()
        self.pool_lock = Lock()
        self.thread_tasks = [None for _ in range(limit)]
        self.threads = [Thread(target=worker, args=(self.pool, self.thread_tasks, tid)) for tid in range(limit)]
        for t in self.threads: # start workers
            t.daemon = True
            t.start()


    def schedule  (self, process, success=None, fail=None):
        """Schedule  a process to be run when a worker thread is available

        @param process: a request see "worker"
        @param success:  a callable to call on success
        @param fail:  a callable to call on failure
        """
        process.setdefault ('on_success', success)
        process.setdefault ('on_fail', fail)
        self.pool.put_nowait (process)

    def stop (self):
        for _ in self.threads: self.pool.put(None) # signal no more commands
        for t in self.threads: t.join()    # wait for completion

    def kill(self, selector_fct):
        """Remove queue entries and kill workers for specific task
        
        @param selector_fct: fct to identify processes to kill fct(process)->boolean
        """
        # first, remove any queue entries for task
        qsize = self.pool.qsize()
        try:
            for _ in range(qsize):   # upper bound on number of iterations necessary (queue can only shrink while we iterate)
                task = self.pool.get_nowait()
                if task is None or not selector_fct(task):
                    # not to be deleted => put it back into queue
                    self.pool.put_nowait(task)
                else:
                    logger.debug("task removed from queue: %s" % task['command_line'])
        except Empty:
            pass
        # kill all threads associated with task
        for tid in range(len(self.thread_tasks)):
            if self.thread_tasks[tid] is None:
                continue
            task, subproc = self.thread_tasks[tid]
            if selector_fct(task):
                # found matching task => interrupt associated thread
                logger.debug("interrupting subprocess %s" % subproc)
                subproc.terminate()
                # wait for thread to terminate
                # (following will not always work: thread may pick another task while we wait...) 
                #while self.thread_tasks[tid] is not None:
                #    sleep(0.2)
                logger.debug("task interrupted")
