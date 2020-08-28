import os
import time

if os.name == 'nt':
    def walltime():
        return time.clock()
else:
    def walltime():
        return time.time()


class Timer(object):#pylint disable-msg=R0903
    """
    Time a set of statement or a function
    with Timer() as t:
      somefun()
      somemorefun()
    log.info ("fun took %.03f seconds" % t.interval)

    """
    def __init__(self):
        self.start = self.end = self.interval = 0
    def __enter__(self):
        self.start = walltime()
        return self
    def __exit__(self, *args):
        self.end = walltime()
        self.interval = self.end - self.start

    def start_timer(self):
        self.start = walltime()
        return self

    def stop_timer(self, *args):
        self.end = walltime()
        self.interval = self.end - self.start
        return self
#    def __str__(self):
#        return str (self.interval)
