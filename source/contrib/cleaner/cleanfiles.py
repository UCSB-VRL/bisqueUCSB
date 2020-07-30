#!/usr/bin/python
import os
import sys
import math
import time
import fnmatch
import argparse
import logging
import logging.config
import subprocess

from bq.util.locks import Locks

def iter_files(dirname, include_pattern=None, exclude_pattern=None):
    for dirname, _, filenames in os.walk(dirname):
        for filename in filenames:
            if (include_pattern is not None and not any([fnmatch.fnmatch(filename, patt) for patt in include_pattern])) or \
               (exclude_pattern is not None and any([fnmatch.fnmatch(filename, patt) for patt in exclude_pattern])):
                continue
            fullpath = os.path.join(dirname, filename)
            try:
                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(fullpath)
                yield (fullpath, atime, size)
            except OSError:
                pass  # skip this file (probably a symbolic link?)

def iter_files_by_atime(dirname, include_pattern=None, exclude_pattern=None):
    return sorted(iter_files(dirname, include_pattern, exclude_pattern), key = lambda tup: (tup[1], -tup[2]))   # sort by increasing atime and decreasing size (delete larger files first)


def scandir(dirname, options, logger):
    """Scan a directory freeing oldest files until free target is achieved
    """
    stats = os.statvfs(dirname)
    f_bavail = stats.f_bavail
    f_blocks = stats.f_blocks
    f_bfree = stats.f_bfree
    percent_free = percent_free_last = 100.0 - ((f_blocks-f_bfree) * 100.0 / (f_blocks-f_bfree+f_bavail))
    files_removed = 0
    logger.info("Filesystem %s before cleaning %s%% free" ,  dirname, int(percent_free))
    if percent_free < float(options.capacity):
        for filename, _, size in iter_files_by_atime(dirname, include_pattern=options.include_pattern, exclude_pattern=options.exclude_pattern):
            try:
                with Locks(None, filename, failonexist=False, mode='ab') as bq_lock:
                    if bq_lock.locked:
                        # we have exclusive lock => OK to delete
                        if options.dryrun:
                            logger.info("(simulated) delete %s (%s bytes)" ,  filename, size)
                            f_bavail += math.ceil(float(size) / float(stats.f_frsize))
                            f_bfree += math.ceil(float(size) / float(stats.f_frsize))
                        else:
                            logger.debug("delete %s (%s bytes)" ,  filename, size)
                            os.remove(filename)
                            files_removed += 1
                            if percent_free_last < percent_free-0.1:
                                # time to refresh stats
                                stats = os.statvfs(dirname)
                                f_bavail = stats.f_bavail
                                f_bfree = stats.f_bfree
                                percent_free_last = percent_free
                            else:
                                f_bavail += math.ceil(float(size) / float(stats.f_frsize))
                                f_bfree += math.ceil(float(size) / float(stats.f_frsize))
                        percent_free = percent_free_last = 100.0 - ((f_blocks-f_bfree) * 100.0 / (f_blocks-f_bfree+f_bavail))
                        logger.debug("now %s%% free" ,  percent_free)
                    else:
                        logger.info("lock on %s failed, skipping" , filename)
            except IOError:
                logger.info("IO error accessing %s, skipping", filename)
            if percent_free >= float(options.capacity):
                break
    logger.info("Filesystem %s after cleaning %s%% free, removed %s files" , dirname, int(percent_free), files_removed)


def main():
    parser = argparse.ArgumentParser(description='Clean specific files from directory trees.')
    parser.add_argument('paths', nargs='+', help='directory to clean')
    parser.add_argument('-c', '--free', dest="capacity", default='80', help="target free capacity (in percent of drive), default: 80" )
    parser.add_argument('-l','--loop', dest="loop", help="wait time between cleaning cycles (in s), default: no cycle" )
    parser.add_argument('-r','--dryrun', action="store_true", default=False, help='simulate what would happen')
    parser.add_argument('-d','--debug',  action="store_true", default=False, help='print debug log')
    parser.add_argument('-i','--include',  dest="include_pattern",  action='append', help='filename pattern to include')
    parser.add_argument('-e','--exclude',  dest="exclude_pattern", action='append', help='filename pattern to exclude')
    parser.add_argument('--log-ini', dest='logini', default=None, help='logging config ini')
    parser.add_argument('--prerun', default = None, help="Run script before processing")
    parser.add_argument('--postrun', default = None, help="Run script after processing")
    parser.add_argument('--lockdir', default = None , help="Directory for locks (deafult is dir path). Ensures 1 cleanrer ")

    options = parser.parse_args()
    args = options.paths
    dirnames = [arg.rstrip('/') for arg in args]

    if options.dryrun:
        print options

    if options.logini:
        logging.config.fileConfig (options.logini)
    else:
        logging.basicConfig(stream=sys.stdout, level = logging.INFO)

    logger = logging.getLogger ('bq.file_cleaner')

    if options.debug:
        logger.setLevel(logging.DEBUG)

    while True:
        if options.prerun:
            status = subprocess.call (options.prerun, shell=True)
            if status != 0:
                logger.error ("Prerun %s failed with status %s", options.prerun, status)
            else:
                logger.info ("PRERUN %s: OK", options.prerun)

        for dirname in dirnames:
            skipped = False
            lockname = os.path.join (options.lockdir or dirname, 'xCLEANERx')
            with Locks (None, lockname, failonexist=True) as fl:
                if not fl.locked:
                    # Somebody
                    skipped = True
                    logger.info ("%s was locked .. skipping ", lockname)
                    break
                with open(lockname, 'wb') as fl:
                    scandir (dirname, options, logger)
                    os.remove (lockname)

        if not skipped and options.postrun:
            status = subprocess.call (options.postrun, shell=True)
            if status != 0:
                logger.error ("Postrun %s failed with status %s", options.postrun, status)
            else:
                logger.info ("POSTRUN %s: OK", options.postrun)

        if options.loop:
            time.sleep(float(options.loop))
        else:
            break


if __name__=="__main__":
    main()
