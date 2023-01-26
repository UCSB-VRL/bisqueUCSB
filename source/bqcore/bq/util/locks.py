# locks.py
# Authors: Kris Kvilekval and Dmitry Fedorov
# Center for BioImage Informatics, University California, Santa Barbara

""" Functions to call BioImageConvert command line tools.
"""

__module__    = "locks"
__author__    = "Kris Kvilekval and Dmitry Fedorov"
__version__   = "1.1"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"


import os
import time
import logging
import threading

from .read_write_locks import HashedReadWriteLock
from . import XFile


rw = HashedReadWriteLock()
LOCK_SLEEP = 0.3
MAX_SLEEP  = 8
TIMEOUT = 0

class FileLocked(Exception):
    pass

class Locks (object):
    log = logging.getLogger('bq.util.locks')

    def debug(self, msg):
        """Log detailed info about the locking of threads and files"""
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug ("%s (%s,%s): %s" %
                            (threading.currentThread().getName(),
                             self.ifnm, self.ofnm, msg))

    def exception(self, msg):
        """Log detailed info about the locking of threads and files"""
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.exception ("%s (%s,%s): %s" %
                            (threading.currentThread().getName(),
                             self.ifnm, self.ofnm, msg))


    def __init__(self, ifnm, ofnm=None, failonexist=False, mode="wb", failonread=False):
        self.wf = self.rf = None
        self.ifnm = ifnm
        self.ofnm = ofnm
        self.mode = mode
        self.locked = False
        self.thread_r = self.thread_w = False
        self.failonexist = failonexist
        self.failonread = failonread

        if self.ifnm:
            if not os.path.isabs(self.ifnm):
                self.ifnm = os.path.abspath(ifnm)

        if self.ofnm:
            if not os.path.isabs(self.ofnm):
                self.ofnm = os.path.abspath(ofnm)

    def acquire (self, ifnm=None, ofnm=None):
        if ifnm:
            self.debug ("acquire thread-r")
            ##self.log.info("acquire thread-r %s", ifnm)
            rtimeout = None if self.failonread is False else TIMEOUT
            try:
                rw.acquire_read(ifnm, timeout=rtimeout)
            except Exception:
                self.debug ("Failed to acquire READ lock and asked to bail...")
                #self.log.info("Failed to acquire READ lock and asked to bail...")
                return
            self.thread_r = True
        self.debug("yes acquired thread-r")
        #self.log.info("yes acquired thread-r %s", ifnm)

        if ifnm and os.name != "nt":
            self.debug ("->RL")
            lock_sleep=LOCK_SLEEP
            while True:
                try:
                    self.rf = XFile.XFile(ifnm, 'rb')
                    self.rf.lock(XFile.LOCK_SH|XFile.LOCK_NB)
                    self.debug ("GOT RL")
                    break
                except XFile.LockError:
                    if self.failonread:
                        self.debug ("Failed to acquire READ lock and asked to bail...")
                        return
                    self.debug ("RL sleep %s" % lock_sleep)
                    time.sleep(lock_sleep)
                    lock_sleep *= 2
                    if lock_sleep > MAX_SLEEP:
                        lock_sleep = MAX_SLEEP


        if ofnm:
            self.debug ("acquire thread-w")
            #self.log.info("acquire thread-w %s", ofnm)
            wtimeout = None if self.failonexist is False else TIMEOUT
            try:
                rw.acquire_write(ofnm, timeout=wtimeout)
            except Exception:
                self.debug ("Failed to acquire WRITE lock and asked to bail...")
                #self.log.info("Failed to acquire WRITE lock and asked to bail...")
                self.release()
                return
            self.thread_w = True
            if self.failonexist and os.path.exists (ofnm):
                self.debug ("out file exists: bailing")
                #self.log.info("out file exists: bailing")
                self.release()
                return

        if ofnm and os.name != "nt":
            self.debug ("->WL")
            #open (ofnm, 'w').close()
            self.wf = XFile.XFile(ofnm, self.mode)
            try:
                self.wf.lock(XFile.LOCK_EX|XFile.LOCK_NB)
                self.debug ("GOT WL")
                #self.log.info("GOT WL %s", ofnm)
            except XFile.LockError:
                self.debug ("WL failed")
                #self.log.info("WL failed")
                self.wf.close()
                self.wf = None
                self.release()
                return

        self.locked = True


    def release(self):
        if self.wf:
            self.debug ("RELEASE WF")
            ##self.log.info("RELEASE WF, %s", self.ofnm)
            self.wf.unlock()
            self.wf.close()
            try:
                stats = os.stat (self.wf.name)
                if stats.st_size == 0:
                    self.debug ('release: unlink 0 length file %s' % stats)
                    os.unlink (self.wf.name)
            except OSError:
                pass
            self.wf = None

        if self.ofnm and self.thread_w:
            self.debug ("release thread-w")
            #self.log.info("release thread-w %s", self.ofnm)
            rw.release_write(self.ofnm)
            self.thread_w = False

        if self.rf:
            self.debug ("RELEASE RF")
            #self.log.info("RELEASE RF")
            try:
                self.rf.unlock()
            except XFile.LockError:
                pass

            self.rf.close()
            self.rf = None

        if self.ifnm and self.thread_r:
            self.debug ("release thread-r")
            #self.log.info("release thread-r, %s", self.ifnm)
            rw.release_read(self.ifnm)
            self.thread_r = False

        self.locked = False

    def __enter__(self):
        self.acquire(self.ifnm, self.ofnm)
        return self
    def __exit__(self, type, value, traceback):
        self.release()
