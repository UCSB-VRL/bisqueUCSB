#!/usr/bin/env python
""" Script to register irods files with bisque
"""
__author__    = "Center for Bioimage Informatics"
__version__   = "1.0"
__revision__  = "$Rev$"
__date__      = "$Date$"
__copyright__ = "Center for BioImage Informatics, University California, Santa Barbara"

import httplib2
import urlparse
import base64
from optparse import OptionParser
from urllib import  urlencode
from bq.util import irods_handler

DEFAULT_URL = "irods://data.cyverse.org"
BISQUE_ADD_IMAGE = "/import/insert"

http = httplib2.Http(disable_ssl_certificate_validation=True)

def is_image(irods_url):
    return True

def irods_import(options, irods_url, bisque_url, auth):
    """Send an irods url to a bisque server

    @param irods_url:  The file or container to save
    @param bisque_url:  The bisqiue server
    @param auth      : Whatever auth header are needed to chat with the bisque server
    """
    if options.onefile:
        # Register one file an return
        url = bisque_url + '?url=' + irods_url
        if options.verbose:
            print  "POSTING ", url
        if not options.dryrun:
            http.request(url, headers = auth )
        return
    entries = irods_handler.irods_fetch_dir(irods_url)
    for irods_file in entries:
        if irods_file.endswith('/'):
            if options.verbose:
                print "Skipping directory", irods_file
            continue
        if is_image (irods_file ):
            url = bisque_url + '?url=' + irods_file 
            if options.verbose:
                print "POSTING ", url
            if not options.dryrun:
                http.request(url, headers = auth)
  
usage = """%prog [options] irods_url [bisque_url]

Register files from an irods repository with a bisque server.
"""
def main():
    irods_url = DEFAULT_URL
    bisque_url = None
    parser = OptionParser(usage=usage)
    parser.add_option('-u', '--user', help="bisque user id")
    parser.add_option('-p', '--password', help="bisque user password")
    parser.add_option('-l', '--list', action="store_true", default=False, 
                      help="list contents of irods url and exit")
    parser.add_option('-n', '--dryrun', action="store_true", default=False, 
                      help="print actions but do not execute.. sets verbose")
    parser.add_option('-1', '--onefile', action="store_true", default=False, 
                      help="irods url is a single file instead of container")
    parser.add_option('-v', '--verbose', action="store_true", default=False, 
                      help="be verbose")
    options, args = parser.parse_args()
    if len(args)>0:
        irods_url = args.pop(0)
    if len(args)>0:
        bisque_url = args.pop(0)

    # check arguments
    if not irods_url or not  irods_url.startswith('irods://'):
        parser.error ('must include a valid irods url i.e. %s' % DEFAULT_URL)
    if options.list:
        # If testing then just print the contents of the container
        entries = irods_handler.irods_fetch_dir(irods_url)
        print "\n".join(entries)
        return
    if not bisque_url:
        parser.error ('must have a destination bisque server')
    if not options.user or not options.password:
        parser.error('Username needs to be provided for uploads')
    if options.dryrun:
        options.verbose = True

    # setup auth
    user = options.user
    password = options.password
    if not bisque_url.endswith(BISQUE_ADD_IMAGE):
        bisque_url = urlparse.urljoin(bisque_url, BISQUE_ADD_IMAGE)
    auth = {'authorization' : 'Basic '+base64.encodestring("%s:%s" % (user,password)).strip()}

    # make request
    if bisque_url[-1] != '/':
        bisque_url += '/'
    irods_import(options, irods_url, bisque_url, auth)
        
if __name__ == "__main__":
    main()
