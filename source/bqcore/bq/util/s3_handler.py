import os
import logging
import shutil
#import math
import time

import boto3
#from boto.s3.key import Key
import botocore
from tg import config

#from filechunkio import FileChunkIO

from bq.util.mkdir import _mkdir
from bq.util.paths import data_path
from bq.util.copylink import copy_link
from bq.util.locks import Locks, FileLocked
from bq.util.timer import Timer
from bq.util.sizeoffmt import sizeof_fmt
from bq.util.converters import asbool

class S3Error(Exception):
    pass

log = logging.getLogger('bq.blobs.storage.s3')

#def s3_parse_url(url):
#    "Read an s3 url, return a bucket and key"
#    pass

s3q=None
if asbool (config.get('bisque.s3queue')):
    from rq import Queue #pylint: disable=import-error
    from redis import Redis #pylint: disable=import-error
    s3q = Queue ("S3", connection = Redis())


def rate_str (cache_filename, t):
    size_bytes = os.path.getsize (cache_filename)
    return "%s %s in %s  (%s)/s" % ( cache_filename, sizeof_fmt(size_bytes), t.interval, sizeof_fmt (size_bytes/t.interval))

def s3_download(bucket, key, cache_filename, creds, blocking):
    s3_client = boto3.client ('s3', **creds)

    with Locks (None, cache_filename, failonexist=True) as l:
        if l.locked is True:
            with Timer () as t:
                s3_client.download_file (bucket, key, cache_filename)
            log.info("S3 Downloaded %s", rate_str (cache_filename, t))

    if cache_filename is not None and os.path.exists(cache_filename):
        with Locks (cache_filename, failonread = (not blocking)) as l:
            if l.locked is False:
                return None
            return cache_filename
    return None

def s3_upload (bucket, key, cache_filename, creds):
    s3_client = boto3.client('s3', **creds)
    with Locks (cache_filename):
        with Timer () as t:
            s3_client.upload_file(cache_filename, bucket, key)
    size_bytes = os.path.getsize (cache_filename)
    log.info("S3 Uploaded %s", rate_str(cache_filename, t))

def s3_cache_fetch(bucket, key, cache, creds, blocking):

    cache_filename = os.path.join(cache, key)
    if os.path.exists(cache_filename):
        return cache_filename
    _mkdir(os.path.dirname(cache_filename))
    if s3q and not blocking:
        log.debug ("Queuing download of %s", cache_filename)
        job = s3q.enqueue(s3_download, bucket, key, cache_filename, creds, blocking, timeout="6h")
        for ix in range (5):
            if job.result == None:
                time.sleep(1)
            else:
                return job.result # cache_filename
        # jobs wait has time out.
        log.debug ("download timedout")
        raise FileLocked
    else:
        cache_filename = s3_download( bucket, key, cache_filename, creds, blocking)
        if cache_filename is None and not blocking:
            raise FileLocked

    return cache_filename

def s3_cache_save(f, bucket, key, cache, creds):
    cache_filename = os.path.join(cache, key)
    _mkdir(os.path.dirname(cache_filename))

    #patch for no copy file uploads - check for regular file or file like object
    abs_path_src = os.path.abspath(f.name)
    if os.path.isfile(abs_path_src):
        #f.close() #patch to make file move possible on windows
        #shutil.move(abs_path_src, cache_filename)
        copy_link (abs_path_src, cache_filename)
    else:
        with open(cache_filename, 'wb') as fw:
            shutil.copyfileobj(f, fw)

    if s3q:
        s3q.enqueue (s3_upload  , bucket, key, cache_filename, creds, timeout="6h")
    else:
        s3_upload( bucket, key, cache_filename, creds)

    # file_size = os.path.getsize(cache_filename)
    # if file_size < 60 * 1e6:
    #     log.debug ("PUSH normal")
    #     k = Key(bucket)
    #     k.key = key
    #     k.set_contents_from_filename(cache_filename)
    # else:
    #     log.debug ("PUSH multi")
    #     chunk_size = 52428800 #50MB
    #     chunk_count = int(math.ceil(file_size / float(chunk_size)))
    #     mp = bucket.initiate_multipart_upload(key)
    #     for i in range(chunk_count):
    #         offset = chunk_size * i
    #         bytes = min(chunk_size, file_size - offset)
    #         with FileChunkIO(cache_filename, 'r', offset=offset, bytes=bytes) as fp:
    #             mp.upload_part_from_file(fp, part_num=i + 1)
    #     mp.complete_upload()

    return cache_filename

def s3_cache_delete(bucket, key, cache, creds):
    cache_filename = os.path.join(cache, key)
    if os.path.exists(cache_filename):
        os.remove (cache_filename)
    s3_client = boto3.client('s3', **creds)
    s3_client.delete_object (Bucket = bucket, Key=key)
    #k = Key(bucket)
    #k.key = key
    #k.delete()

def s3_fetch_file(bucket, key, cache, creds, blocking):
    if not os.path.exists(cache):
        _mkdir (cache)
    localname = s3_cache_fetch(bucket, key, cache=cache,creds=creds, blocking=blocking)
    return localname

def s3_isfile(bucket, key, creds):
    #key = bucket.get_key (key)
    #return key is not None
    s3_client = boto3.client('s3', **creds)
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except botocore.exceptions.ClientError:
        # Not found
        return False


def s3_push_file(fileobj, bucket , key, cache, creds):
    localname = s3_cache_save(fileobj, bucket, key, cache=cache, creds=creds)
    return localname

def s3_delete_file(bucket, key, cache, creds):
    s3_cache_delete(bucket, key, cache=cache, creds=creds)

def s3_list(bucket, key, creds):
    s3 = boto3.resource('s3', **creds)
    s3_bucket = s3.Bucket (bucket)
    return s3_bucket.objects.filter(Prefix=key)
