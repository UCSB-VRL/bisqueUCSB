
import os
import string
from tg import config
import posixpath
from sqlalchemy.sql import and_, or_
from bq.util.paths import data_path
from bq.util.sizeoffmt import sizeof_fmt
from bq.util.diskusage import disk_usage

__all__  = [ "clean_images" ]



def clean_store(stores, options):
    from bq.data_service.model import Taggable, Image, DBSession


    tops = []
    localfiles = set()

    for local in stores:
        if 'top' not in local:
            continue
        top =  local['top'][7:]
        top = string.Template(top).safe_substitute(datadir = data_path())
        tops.append  (top)
        print "Scanning ", top
       #for root, dirs, files in local.walk():
        for root, dirs, files in os.walk(top):
            for f in files:
                #if f.endswith('.info'):
                #    continue
                filepath =  os.path.join(root, f)
                localfiles.add(filepath)
    print "file count ", len(localfiles)

    dbfiles = []
    resources_missing = []
    locs = DBSession.query(Taggable).filter(or_(Taggable.resource_type=='image',
                                                Taggable.resource_type=='file',
                                                Taggable.resource_type=='table'))
    for f in locs:
        if f.resource_value is None:
            # check for sub values
            for ref in f.values:
                if ref.valstr and ref.valstr.startswith ('file://'):
                    relpath = ref.valstr[7:]
        elif f.resource_value.startswith ('irods')  or f.resource_value.startswith ('s3'):
            continue
        elif f.resource_value.startswith ('file://'):
            relpath  = f.resource_value[7:]
        else:
            relpath = f.resource_value

        for top in tops:
            filepath = posixpath.join (top, relpath)
            if os.path.exists (filepath):
                dbfiles.append(filepath)
                break
        if not dbfiles[-1].endswith (relpath):
            resources_missing.append ( ( f.resource_uniq, relpath) )

    dbfiles = set (dbfiles)
    print "DB count", len(dbfiles)
    missing = localfiles - dbfiles
    print "deleting %s files" % len(missing)
    before = disk_usage(top)
    if not options.dryrun:
        for f in missing:
            os.remove(f)
    else:
        print "would delete %s" % list(missing) [:20]
        print "DBFILES:", list(dbfiles)[:20]
        print "LOCALFILES", list(localfiles)[:20]
        print "resource_missing in DB", resources_missing
    after = disk_usage(top)
    print "Reclaimed %s space" % sizeof_fmt(before.used - after.used)


def clean_images(options):
    "Clean unreferenced images/files from bisque storage"

    #from bq.blob_service.controllers.blobsrv import load_stores
    #stores = load_stores()
    from bq.blob_service.controllers.mount_service import load_default_drivers
    drivers = load_default_drivers()


    # Collect ALL files in file stores
    clean_store([store for name, store in drivers.items() if store['mounturl'].startswith('file')], options)
