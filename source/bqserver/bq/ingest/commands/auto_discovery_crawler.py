##############################################################################st
#
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2011 by the Regents of the University of California     ##
##                            All rights reserved                            ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========


DESCRIPTION
===========

"""
import glob
import logging
import logging.handlers
import os, sys, traceback
import time
from StringIO import StringIO
import ConfigParser
import getopt
import boto
from boto.s3 import Connection
import httplib, urllib2
import base64

LAST_POST = 0
NEXT_POST = 1
DEFAULT_POST_INTERVAL = 1
LOG_FILENAME = 'auto_discovery_crawler.log'
logger = None

def usage():
    print "Usage: auto_discovery_crawler -i <amazon_access_key_id> -k <amazon_secret_access_key> -u <bisque_username> -p <bisque_password> [ -b <s3_bucket> ] [-c <config_file] [-s <bisque_url>]"
    print "\n\tIf no bucket is specified, the crawler will scan all buckets to which it has access."
    print "\tDefault config file location is ~/.bisque_crawler.  Command-line args override any config file settings."
    sys.exit()

def read_config_file(config):
    parser = ConfigParser.ConfigParser()
    if parser.read(os.path.expanduser(config["config_file"])) == []:
        logger.info("Config file %s not found; using command-line params", config["config_file"])
        return config
    if not parser.has_section("bisque_crawler"):
        logger.info("No [bisque_crawler] section found in %s", config["config_file"])
        return config
    if "access_key_id" not in config:
        config["access_key_id"] = parser.get("bisque_crawler", "access_key_id")
    if "secret_access_key" not in config:
        config["secret_access_key"] = parser.get("bisque_crawler", "secret_access_key")
    if "bisque_user" not in config:
        config["bisque_user"] = parser.get("bisque_crawler", "bisque_user")
    if "bisque_pw" not in config:
        config["bisque_pw"] = parser.get("bisque_crawler", "bisque_pw")
    try: 
        if "bucket" not in config:
            config["bucket"] = parser.get("bisque_crawler", "bucket")
    except ConfigParser.NoOptionError:
        pass
    try:
        if "bisque_url" not in config:
            config["bisque_url"] = parser.get("bisque_crawler", "bisque_url")
    except ConfigParser.NoOptionError:
        pass

    return config

def scan_S3(config, local_url_cache):
    key_list = ""
    new_key_count = 0
    total_key_count = 0
    try: 
        connection = Connection(aws_access_key_id=config["access_key_id"], aws_secret_access_key=config["secret_access_key"])
        if "bucket" in config:
            buckets = connection.get_bucket(config["bucket"])
        else:
            buckets = connection.get_all_buckets()
        logger.info("Starting scan of %d S3 buckets", len(buckets))
        for b in buckets:
            rs = b.list()
            for key in rs:
                total_key_count += 1
                if((total_key_count % 1000) == 0):
                    logger.info("Scanned %d keys", total_key_count)
                if key.size == 0:
                    continue
                url = "https://%s.s3.amazonaws.com/%s %s" % (b.name, key.name, key.etag)
                if url not in local_url_cache: 
                    key_list = key_list + url + "\n"
                    local_url_cache[url] = key.etag
                    new_key_count += 1
        logger.info("Finished S3 scan: %d keys", total_key_count)
    except Exception as e:
        logger.warning("Failed to scan S3: %s", e)
        return "" 
    else:
        logger.info ("Successful scan of S3 buckets; found %d new keys", new_key_count)
        return key_list

def post_to_bisque(config, key_list):
    authstring = base64.b64encode(config["bisque_user"] + ":" + config["bisque_pw"])
    httplib.HTTPConnection.debuglevel = 1
    try:
        req = urllib2.Request(config['bisque_url'], urllib2.quote(key_list))
        req.add_header('User-Agent', 'BisqueCrawler/0.1 http://http://www.bioimage.ucsb.edu/')
        req.add_header('Authorization', "Basic " + authstring)
        opener = urllib2.build_opener()
        data = opener.open(req).read() 
    except Exception as e:
        r = False
        logger.warning('Failed to post data: %s' % (e))
    else:
        r = True
    httplib.HTTPConnection.debuglevel = 0
    return r

def post_to_bisque_if_due(config, new_url_list):
    r = False
    global NEXT_POST
    global LAST_POST
    if(len(new_url_list) <= 0):
        return r
    if(time.time() > NEXT_POST):
        r = post_to_bisque(config, new_url_list)
        NEXT_POST = next_post_schedule(r)
        LAST_POST = time.time()
    if not r:
        logger.warning("Failed to post %.2f KB to blob server; saving for later retry", len(new_url_list)/1024.0)
    else:
        logger.info("Posted %.2f KB to blob server", len(new_url_list)/1024.0)
    return r

def next_post_schedule(last_post_succeeded):
    if last_post_succeeded:
        return DEFAULT_POST_INTERVAL + time.time()
    return abs(NEXT_POST - LAST_POST) * 2 + time.time()

def config_logging(log_filename):
    global logger
    logger = logging.getLogger()
    jandler = logging.handlers.RotatingFileHandler(log_filename, maxBytes=20*1024*1024, backupCount=5)
    logger.addHandler(jandler)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(process)s - %(message)s")
    jandler.setFormatter(formatter)
    logger.setLevel(logging.INFO)




def main():
    config = {}
    local_url_cache = {}
    new_url_list = ""

    config_logging(LOG_FILENAME)
    logger.info("Auto_discovery_crawler started")
    try:                                
        opts, args = getopt.getopt(sys.argv[1:], "hi:k:b:u:p:c:s:", ["help", "access_key_id=", "secret_access_key=", "bucket=", "bisque_pw=", "bisque_user=", "config_file=", "bisque_url="]) 
    except getopt.GetoptError:           
        usage()                          
        sys.exit(2)                     
    for o, a in opts:
        if o in("-i", "--access_key_id"):
            config["access_key_id"] = a
        elif o in ("-k", "--secret_access_key"):
            config["secret_access_key"] = a
        elif o in ("-b", "--bucket"):
            config["bucket"] = a
        elif o in ("-p", "--bisque_pw"):
            config["bisque_pw"] = a
        elif o in ("-u", "--bisque_user"):
            config["bisque_user"] = a
        elif o in ("-c", "--config_file"):
            config["config_file"] = a
        elif o in ("-s", "--bisque_url"):
            config["bisque_url"] = a
        elif o in ("-h", "--help"):
           usage()
        else:
            usage()
    
    if "config_file" not in config:
        if os.path.exists('./.bisque_crawler'):
            config["config_file"] = "./.bisque_crawler"
        elif os.path.exists('~/.bisque_crawler'):
            config["config_file"] = "~/.bisque_crawler"
    config = read_config_file(config)

    if "bisque_url" not in config:
        config["bisque_url"] = "http://dough.ece.ucsb.edu"
    
    if "access_key_id" not in config or "secret_access_key" not in config or "bisque_user" not in config or "bisque_pw" not in config:
        usage()

    print config
    while True:
        new_url_list += scan_S3(config, local_url_cache)
        r = post_to_bisque_if_due(config, new_url_list)
        if(r):
            new_url_list = ""
        time.sleep(1)


if __name__ == "__main__":
    main()
sys.exit()



# What to do with logging?
# log = logging.getLogger('bisquik.db')
