import hashlib
import datetime
import random
import shortuuid

def make_uniq_hash(filename, dt = None):
    rand_str = str(random.randint(1, 1000000))
    rand_str = filename.encode('utf-8') + rand_str + str( (dt or datetime.datetime.now()).isoformat())
    rand_hash = hashlib.sha1(rand_str).hexdigest()
    return rand_hash



def make_short_uuid (filename=None, dt=None):
    return "00-%s" % shortuuid.uuid()



def make_uniq_code (version = 0, length=40):
    return "00-%s" % shortuuid.uuid()


def is_uniq_code(uniq, version = None):
    """Check that the code is a bisque uniq code

    @param uniq: The uniq code
    @param version: Test for a particular version:
    @return:  The version of the code or None
    """
    return uniq.startswith('00-') or None



###########################################################################
# Hashing Utils
###########################################################################


def file_hash_SHA1( filename ):
    '''Takes a file path and returns a SHA-1 hash of its bits'''
    f = file(filename, 'rb')
    m = hashlib.sha1()
    readBytes = 1024 # use 1024 byte buffer
    while readBytes:
        readString = f.read(readBytes)
        m.update(readString)
        readBytes = len(readString)
    f.close()
    return m.hexdigest()

def file_hash_MD5( filename ):
    '''Takes a file path and returns a MD5 hash of its bits'''
    f = file(filename, 'rb')
    m = hashlib.md5()
    readBytes = 1024 # use 1024 byte buffer
    while readBytes:
        readString = f.read(readBytes)
        m.update(readString)
        readBytes = len(readString)
    f.close()
    return m.hexdigest()

