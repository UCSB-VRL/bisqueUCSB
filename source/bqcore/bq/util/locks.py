# locks.py
# Authors: Kris Kvilekval and Dmitry Fedorov
# Updated: 2025-05 by Wahid Sadique Koly
# Center for BioImage Informatics, University California, Santa Barbara

"""Cross-platform read/write locks for BioImage file operations."""

import logging
import os
import threading
import time

import portalocker

from .read_write_locks import HashedReadWriteLock

rw = HashedReadWriteLock()
LOCK_SLEEP = 0.3
MAX_SLEEP = 8
TIMEOUT = 0


class FileLocked(Exception):
    pass


class Locks:
    log = logging.getLogger("bq.util.locks")

    def debug(self, msg):
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.debug(
                "%s (%s,%s): %s", threading.current_thread().name, self.ifnm, self.ofnm, msg
            )

    def exception(self, msg):
        if self.log.isEnabledFor(logging.DEBUG):
            self.log.exception(
                "%s (%s,%s): %s", threading.current_thread().name, self.ifnm, self.ofnm, msg
            )

    def __init__(self, ifnm, ofnm=None, failonexist=False, mode="wb", failonread=False):
        self.wf = self.rf = None
        self.ifnm = os.path.abspath(ifnm) if ifnm else None
        self.ofnm = os.path.abspath(ofnm) if ofnm else None
        self.mode = mode
        self.locked = False
        self.thread_r = self.thread_w = False
        self.failonexist = failonexist
        self.failonread = failonread

    def acquire(self, ifnm=None, ofnm=None):
        ifnm = ifnm or self.ifnm
        ofnm = ofnm or self.ofnm

        if ifnm:
            self.debug("Acquiring thread-level read lock")
            rtimeout = None if not self.failonread else TIMEOUT
            try:
                rw.acquire_read(ifnm, timeout=rtimeout)
                self.thread_r = True
            except Exception:
                self.debug("Failed to acquire thread-level read lock")
                return

            self.debug("Acquiring file-level shared lock (read)")
            lock_sleep = LOCK_SLEEP
            while True:
                try:
                    self.rf = open(ifnm, "rb")
                    portalocker.lock(self.rf, portalocker.LOCK_SH | portalocker.LOCK_NB)
                    self.debug("Acquired shared file lock")
                    break
                except portalocker.exceptions.LockException:
                    if self.failonread:
                        self.debug("Shared lock failed and 'failonread' is True")
                        return
                    time.sleep(lock_sleep)
                    lock_sleep = min(lock_sleep * 2, MAX_SLEEP)

        if ofnm:
            self.debug("Acquiring thread-level write lock")
            wtimeout = None if not self.failonexist else TIMEOUT
            try:
                rw.acquire_write(ofnm, timeout=wtimeout)
                self.thread_w = True
            except Exception:
                self.debug("Failed to acquire thread-level write lock")
                self.release()
                return

            if self.failonexist and os.path.exists(ofnm):
                self.debug("Output file exists, and 'failonexist' is True")
                self.release()
                return

            self.debug("Acquiring file-level exclusive lock (write)")
            try:
                self.wf = open(ofnm, self.mode)
                portalocker.lock(self.wf, portalocker.LOCK_EX | portalocker.LOCK_NB)
                self.debug("Acquired exclusive file lock")
            except portalocker.exceptions.LockException:
                self.debug("Exclusive file lock failed")
                self.wf.close()
                self.wf = None
                self.release()
                return

        self.locked = True

    def release(self):
        if self.wf:
            self.debug("Releasing write file lock")
            try:
                portalocker.unlock(self.wf)
                self.wf.close()
                if os.path.getsize(self.wf.name) == 0:
                    self.log.info("Removing zero-size file: %s", self.wf.name)
                    os.unlink(self.wf.name)
            except Exception:
                pass
            self.wf = None

        if self.ofnm and self.thread_w:
            self.debug("Releasing thread-level write lock")
            rw.release_write(self.ofnm)
            self.thread_w = False

        if self.rf:
            self.debug("Releasing read file lock")
            try:
                portalocker.unlock(self.rf)
                self.rf.close()
            except Exception:
                pass
            self.rf = None

        if self.ifnm and self.thread_r:
            self.debug("Releasing thread-level read lock")
            rw.release_read(self.ifnm)
            self.thread_r = False

        self.locked = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.log.info(f"Exiting lock context: {self.ifnm}, {self.ofnm}")
        self.release()
        self.log.info(f"Exited lock context: {self.ifnm}, {self.ofnm}")
