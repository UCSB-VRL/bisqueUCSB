#!/usr/bin/python
#

# List and fix errors  in the database
#   Fix image src to point to proper (local)URI
#   Fix tag values to point to propper (local)URI
#   Fix Permission between database and Image server
#   Fix Tag permissions for public images
import os,sys
import urlparse
#from sqlalchemy import create_engine
#from sqlalchemy import Table, Column, Integer, String, Text, Index, MetaData, DateTime
#from sqlalchemy.orm import mapper, create_session, scoped_session, sessionmaker
import re
from paste.deploy import appconfig
import transaction

from bq.config.environment import load_environment
from bq.core.model import DBSession as session
from bq.data_service.model import Taggable, Image, Tag, Value




#database.get_engine()
#session = database.session
#metadata = database.metadata

# blobdbfile  = r'blobdb.sqlite'
# blobdb = create_engine('sqlite:///'+blobdbfile)
# blobmd = MetaData(blobdb)

# files = Table('files', blobmd,
#               Column('id', Integer, primary_key=True),
#               Column('sha1', String(40)), # new column v2
#               Column('uri', Text),
#               Column('owner', Text),
#               Column('perm', Integer),
#               Column('ts', DateTime(timezone=False)),
#               Column('original', Text),
#               Column('file_type', Text), # new column v2
#               Column('local', Text) # new column v3
#               )
# BlobSession = sessionmaker(bind=blobdb, autoflush=True, transactional=True)


# class FileEntry(object):

# #    def __init__(self):
# #        self.id = None

#     def _set_id(self, new_id):
#       #self._id_db = new_id+1
#       pass

#     def _get_id(self):
#       return self._id_db-1

#     id = property( _get_id, _set_id )

#     def __repr__(self):
#         return "FileEntry(%r, %r, %r, %r, %r)" % (self.id, self.sha1, self.uri, self.owner, self.perm, self.ts, self.original, self.file_type )


# mapper(FileEntry, files, properties = { '_id_db': files.c.id })


verbose = 0
dryrun = False
fixall = False

class Msg(object):
    def __init__(self):
        self.clear()
        self.counts = { }
        self.count_items = { }
    def log (self, m):
        self.messages.append(m)
    def clear(self):
        self.messages =[]
    def dump(self, head):
        if self.messages:
            print head + ":" + "\n".join (self.messages)
    def count (self, v, *params ):
        self.counts[v] = self.counts.get (v, 0) + 1
        self.count_items.setdefault(v, []).extend (params)
    def dump_counts(self):
        for k,v in self.counts.items():
            print "count of %s = %d" % (k, v)
            if verbose:
                print "items of %s = %s" % (k, str(self.count_items[k]))


msg = Msg()

def ask(question):
    msg.dump("")
    msg.clear()
    if  fixall:
        print question + "fixing"
        return True

    a = raw_input( question + "(Y/N)" )
    if a=="" or a=="Y":
        return True
    return False


def close_sessions():
    "Close any remaining"
    #blob_session.commit()
    #blob_session.close()
    transaction.commit()

def flush():
    if verbose:
        msg.log ('bisque modifyed : new (%d), dirty (%d), deleted(%d)' %
                 (len(session.new), len(session.dirty), len(session.deleted)))
    if  not dryrun:
        msg.log ("Flush");
        session.flush()

def visit_all_files (callbacks, *l, **kw):
    print "VISIT BLOBS"
    count = 0
    for blob in session.query(Taggable).filter_by(resource_type = 'file'):
        msg.clear()
        for cb in callbacks:
            cb (blob, *l, **kw)
            count = count + 1
        count = count + 1
        if count % 2048 == 0:
            flush()
            msg.dump ("in blob %d" % blob.id)
        msg.dump ("in blob %d" % blob.id)
    flush()
    return True


def find_misreferenced_blob(blob, host, fix):
    host_tuple = urlparse.urlparse (host)
    blob_tuple = urlparse.urlparse (blob.value)
    if host_tuple[1] != blob_tuple[1]:
        msg.log ("blob %d has incorrect host '%s' != '%s'" % (blob.id , blob_tuple[1],host_tuple[1]))
        if fix and ask ("replace host"):
            b = list(blob_tuple)
            b[1] = host_tuple[1]
            blob.value = urlparse.urlunparse (b)


def move_blob_image_service(blob, host, **kw):
    "Change the old imgsrv address to image_service"
    #host_tuple = urlparse.urlparse (host)
    b_tuple = urlparse.urlparse (blob.value)
    if b_tuple[2].startswith("/imgsrv"):
        msg.log("blob %d has old image_service" % blob.id)
        if  ask("imgsrv->image_service"):
            b = list(b_tuple)
            b[2] = b_tuple[2].replace("/imgsrv", "/image_service")
            blob.value = urlparse.urlunparse (b)





def find_unattached_bix_files(blob, host, fix):
    pass



#################################################################

def visit_all_images (callbacks, start=0, **kw):
    """Visit all images and list and fix possible errors"""
    print "VISIT IMAGES"
    count = 0
    for image in session.query(Image).order_by(Image.id)[start:]:
        msg.clear()
        #blob = session.query(FileEntry).filter_by(uri=image.src).first()
        #if  blob is None:
        #    msg.log ("Database has image while with no blob ID %s %s"%(image.id , image.src))
        #    if image.src is None:
        #       msg.count("Image with no src:handfix", image.id )
        #       print ("image with no src")
        #       continue
        #    imagesrc = urlparse.urlparse(image.src)[2] # PATH
        #    blob = session.query(FileEntry).filter(FileEntry.uri.like("%%"+imagesrc)).first()
        #    if blob is not None:
        #        msg.log("Found blob w/ID but wrong host%s" % blob.uri)
        #    else:
        #        print ("No blob for %s" %image.src)
        #        continue
        #
        msg.count('images')
        for cb in callbacks:
            cb (image=image, **kw)
            count = count + 1
        count = count + 1
        if count % 2048 == 0:
            flush()
        msg.dump ("in image %d (%s),  " % (image.id, count))
    flush()
    msg.dump_counts()
    return True

def fix_image_value(image,  host, old_host=None, **kw):
    host_t = urlparse.urlparse(host)
    image_t = list (urlparse.urlparse (image.value))
    if old_host:
        oldhost_t = urlparse.urlparse(old_host)

    # Check if we have old_host and the src is old_host
    # otherwise check
    if (old_host and  image_t[1] == oldhost_t[1]) and  ask("image %d host %s -> %s" % (image.id, image_t[1], host_t[1]) ):
    #if or image_t[1] != host_t[1]:
        image_t [1] = host_t[1]
        image.value = urlparse.urlunparse (image_t)
        msg.count ('image.src modified', image.id)
        #blob.uri = urlparse.urlunparse (image_t)


def move_image_service(image,  host, old_host=None, **kw):
    "Change the old imgsrv address to image_service"
    #host_tuple = urlparse.urlparse (host)
    image_tuple = urlparse.urlparse (image.resource_value)
    if image_tuple[2].startswith("/imgsrv"):
        msg.log("image %d has old image_service" % image.id)
        if  ask("imgsrv->image_service"):
            b = list(image_tuple)
            b[2] = image_tuple[2].replace("/imgsrv", "/image_service")
            image.resource_value = urlparse.urlunparse (b)


def fix_tag_value(image, host, old_host=None, **kw):
    if old_host is None:
        return
    for tg in image.docnodes:
        if tg.resource_type == 'tag' and tg.value:
            S=tg.value
            if S and S.startswith(old_host) and ask ('Tag value %s -> %s' %(S, host)):
                #newhost = re.sub(r'http://[^/]*', host, S)
                newhost = host + S[len(old_host):]
                print "%s becomes  %s " %(S, newhost)
                tg.value=newhost
                msg.count ('replaced tag value', image.id)




def fix_tag_permission(image, blob, **kw):
    if image.perm != 0: return
    for t in image.tags:
        if image.owner_id == t.owner_id and t.perm != 0:
            msg.count ("public image w/private tag")
            t.perm=0
    for g in image.gobjects:
        if image.owner_id == g.owner_id and g.perm != 0:
            msg.count ("public image w/private gobject")
            g.perm=0





help = """
BSCK Bisquik System Check  [options] HOST

 List and fix errors in the database
   Fix image src/blob ur to point to proper (local)URI
   Fix tag values to point to propper (local)URI
   Fix Permission between database and Image server
   Fix Tag permissions for public images

   HOST : a web address like http://bisque.org:8080


   Can also be used to move an OLD database to a new address
   if --oldhost is used
"""

if __name__ == "__main__":
    quiet = False
    import getopt

    from optparse import OptionParser
    parser = OptionParser (usage=help)

    parser.add_option ('-v', '--verbose', action="count", default=0)
    parser.add_option('-f', '--fixall', action="store_true",
                      help = "(fix all) Don't ask for confirmation")
    parser.add_option('-n', '--dryrun', action="store_true",
                      help="dry run.. show actions without actually moving")
    parser.add_option('-s', '--start', action="store", type="int",
                      default = 0,
                      help="Start processing at this image ID")
    parser.add_option('--oldhost', action="store", default = None,
                      help="Replace tagvalues that match this host i.e. http://dough.ece.ucsb.edu")
    parser.add_option ('-c', '--config', action="store", default='shell.ini',
                       help="Provide an alternate config default=site.cfg")
    parser.add_option('--blobonly', action="store_true", default=False)


    (opts, args) = parser.parse_args()
    if  len(args) < 1:
        parser.error ("You must supply the correct host URL")


    conf = appconfig('config:' + os.path.abspath(opts.config))
    load_environment(conf.global_conf, conf.local_conf)

    host = args[0]

    print """YOU ARE ABOUT TO CHANGE %s
    ENSURE A Backup is available
    """ % conf.get ('sqlalchemy.url')
    if not ask("Continue"):
        sys.exit(0)


    start = opts.start
    verbose = opts.verbose
    fixall = opts.fixall
    old_host = opts.oldhost

    if host.find ("://") < 0:
        host = "http://" + host

    if host[-1] == '/':
        host = host[:-1]

    if verbose>0:
        print "Fixing bisquik database %s" % conf.get('sqlalchemy.url')



    ### CALLBACK for taggable objects in database
    callbacks = [
        fix_image_value,
        move_image_service,
        fix_tag_value,
#        fix_blob_permission,
        #fix_filename_tag,
        #fix_tag_permission,
        ]
    ### BLOBCALSS for all blobs
    blobcalls = [
#        find_misreferenced_blob,
#        move_blob_image_service,
        # find_unreferenced_blobs
        ]
    try:
        ok = True
        if not opts.blobonly:
            ok = visit_all_images(callbacks, host=host, start=start, old_host=old_host)
        # Most BLOBS are fixed during visiting images..
        #  Look for stragglers
        ok = ok and visit_all_files(blobcalls, host, fix=True)

        close_sessions()

    except Exception, e:
        print "EXception %s" % e
        raise
    finally:
        msg.dump("Finishing")
        msg.dump_counts()




