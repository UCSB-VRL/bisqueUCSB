import os,sys
import shutil
import logging

from .mkdir import _mkdir
from .io_misc import dolink

log = logging.getLogger('bq.util.copylink')



def copy_link (*largs):
    "Copy or make a hard link"
    largs = list (largs)
    d = largs.pop()

    for f in largs:
        if not os.path.exists(f):
            log.error("can't copy %s to %s: missing file", f, d)
            continue
        try:
            if os.path.isdir (f):
                f = f.rstrip ('/')
            dest = d
            if os.path.isdir (dest):
                dest = os.path.join (d, os.path.basename(f))
            if os.path.abspath(f) == os.path.abspath(dest):
                continue
            log.debug ("linking %s to %s", f,dest)
            if os.path.exists(dest):
                log.debug ("Found existing file %s: removing .." , dest)
                os.unlink (dest)

            #os.link(f, dest)
            dolink(f, dest)

        except (OSError, AttributeError) as e:
            log.debug ("Problem in link %s... trying copy" , e)
            if os.path.isdir(f):
                shutil.copytree(f, dest)
            else:
                shutil.copy2(f, dest)

if os.name != 'nt':
    def copy_symlink (source, dest):
        "Copy or make a symlink"
        try:
            os.symlink(source, dest)
        except (OSError, AttributeError), e:
            log.debug ("Problem in link %s... trying copy" , e)
            if os.path.isdir(source):
                shutil.copytree(source, dest)
            else:
                shutil.copy2(source, dest)
else:
    def copy_symlink (source, dest):
        #source = os.path.abspath(source)
        #dest = os.path.abspath(dest)

        "Copy or make a symlink"
        if not os.path.exists(source):
            log.debug('copy_symlink: source path does not exist "%s", skipping...', source)
            return

        #log.info('copy_symlink: "%s" -> "%s"'%(source, dest))

        if os.path.isdir(source):
            _mkdir(dest)
            # walk directory and call copy_symlink recursively on its children
            fs = os.listdir(source)
            for f in fs:
                copy_symlink ( os.path.join(source, f), os.path.join(dest, f))
        else:
            # try linking
            try:
                dolink(source, dest)
            except (OSError, AttributeError), e:
                log.debug ("Problem in link %s... trying copy" , e)
                shutil.copy2(source, dest)
