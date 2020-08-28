#!/usr/bin/env python
## insert2bisque.py
## This file lives in IRODSHOME/server/bin/cmd/insert2bisque.py
##       
import os
import sys
import shlex
import urllib
import urllib2
import urlparse
import base64
import logging
from optparse import OptionParser

############################
# Config for local installation
LOGFILE='/tmp/bisque_insert.log'
BISQUE_HOST='http://bisque.ece.ucsb.edu'
BISQUE_ADMIN_PASS='guessme'
IRODS_HOST='irods://irods.ece.ucsb.edu'
# End Config 

logging.basicConfig(filename=LOGFILE, level=logging.INFO)

log = logging.getLogger('i2b')

def insert_bisque(path, user, host, credentials):
    try:
        opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(debuglevel=0),
            urllib2.HTTPSHandler(debuglevel=0))

        request = urllib2.Request(host)
        request.add_header('authorization',  'Basic ' + base64.encodestring(credentials).strip())
        resource = "<resource name='%s' value='%s' />" % (os.path.basename(path), path )
        resource = urllib.urlencode({ "user" : user, "irods_resource" : resource })
        request.add_data (resource)
        r = opener.open(request)
        response = r.read()
        log.info( 'insert %s -> %s' % (host, response))
    except Exception,e:
        log.exception( "exception occurred %s" % e )
        raise e


if __name__ == "__main__":
    parser = OptionParser (usage="usage: %prog [options] path user")
    parser.add_option('-d', '--debug', action="store_true", default=False, help="log debugging")
    parser.add_option('-t', '--target', default="%s/import/insert_inplace" % (BISQUE_HOST), help="bisque host entry url")
    parser.add_option('-c', '--credential', default="admin:%s" % BISQUE_ADMIN_PASS, help="user credentials")
    

    (options, args) = parser.parse_args ()
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    log.debug( "insert2bisque recevied %s" % (sys.argv) )
    if len(args) != 2:
        parser.error("need path and user")

    path, user = args 
    if not urlparse.urlparse (path).scheme:
        path = IRODS_HOST + path


    insert_bisque(path, user, options.target, options.credential)
    sys.exit(0)
