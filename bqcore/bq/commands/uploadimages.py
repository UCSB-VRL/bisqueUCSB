#!/usr/bin/python
import os
import sys
import urlparse
import logging
import argparse
#from StringIO import StringIO

from ConfigParser import SafeConfigParser
import requests
import requests_toolbelt


logging.basicConfig(level = logging.WARN)



try:
    from lxml import etree as et
except Exception:
    from xml.etree import ElementTree as et

try:
    import magic # pylint: disable=import-error
    ms = magic.open(magic.MAGIC_NONE)
    ms.load()
    def isimagefile(fname):
        ftype = ms.file(fname)
        return ftype.lower().find ('image') >= 0
except Exception:
    def isimagefile(fname):
        return True

DESTINATION = "/import/transfer"

def upload(dest, filename, userpass, tags=None):
    files = []
    if tags:
        files.append( ('file_resource', (None, tags, "text/xml")  ) )
    files.append( ("file",  (os.path.basename (filename), open(filename, "rb"), 'application/octet-stream') ))

    fields  = dict (files)
    # Crazy way to speed up read speed.
    # https://github.com/requests/toolbelt/issues/75
    m  = requests_toolbelt.MultipartEncoder (fields = dict (files) )
    m._read = m.read
    m.read = lambda size: m._read (1024*1024)

    response = requests.post (dest, data=m, auth = requests.auth.HTTPBasicAuth(*userpass),verify=False,
                              headers={'Content-Type': m.content_type})
    if response.status_code != 200:
        print "error while copying %s: Server response %s" % (filename, response.headers)
        print "saving error information to ", filename , "-transfer.err"
        open(filename + "-transfer.err",'wb').write(response.content)
        return
    return response.content


def walk_deep(path):
    """Splits sub path that follows # sign if present
    """
    for root, _, filenames in os.walk(path):
        for f in filenames:
            yield os.path.join(root, f).replace('\\', '/')

DEFAULTS  = dict(
    logfile    = '/tmp/bisque_insert.log',
    bisque_host='https://loup.ece.ucsb.edu',
    bisque_user='admin',
    bisque_pass='admin',
    irods_host='irods://mokie.iplantcollaborative.org',
    )


SPECIAL_TYPES=[
    'zip-bisque',
    'zip-multi-file',
    'zip-time-series',
    'zip-z-stack',
    'zip-5d-image',
    'zip-proprietary',
    'zip-dicom',
    'image/proprietary',
    'image-part-5D',
    ]


def main():
    #usage="usage [options] f1 [f2 f2 d1 ] bisque-url"
    parser = argparse.ArgumentParser()

    config = SafeConfigParser()
    config.add_section('main')
    for k,v in DEFAULTS.items():
        config.set('main', k,v)

    config.read (['.bisque', os.path.expanduser('~/.bisque'), '/etc/bisque/bisque_config'])
    defaults =  dict(config.items('main'))


    parser.add_argument('-u','--user', dest="user",
                        default="%s:%s" % (defaults['bisque_user'], defaults["bisque_pass"]),
                        help="Credentials in  user:pass form" )
    parser.add_argument('-r','--recursive', action="store_true", default=False, help='recurse into dirs')
    parser.add_argument('-v','--verbose',  action="store_true", default=False, help="print actions")
    parser.add_argument('-d','--debug',  action="store_true", default=False, help='print debug log')
    parser.add_argument('-t','--tag', action="append", dest="tags", help="-t name:value")
    parser.add_argument('--resource', action="store", default=None, help="XML resource record for the file")
    parser.add_argument('--dest', default=defaults['bisque_host'], help="Bisque server root")
    parser.add_argument('--ingest-type', default=None, help="Upload special type of image .. %s " % ",".join (SPECIAL_TYPES))
    parser.add_argument('paths', nargs='+', help="List for files or dirs")


    args = parser.parse_args()

    print args

    if  DESTINATION not in args.dest: # and not dest.endswith(DESTINATION):
        args.dest = urlparse.urljoin (args.dest, DESTINATION)

    dest_tuple = list(urlparse.urlsplit(args.dest))
    args.dest =  urlparse.urlunsplit(dest_tuple)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)


    # Prepare username
    if args.user is None:
        parser.error ("Need username:password")
    userpass = tuple(args.user.split (':'))

    # Prepare tags
    tags = None
    if args.resource or args.tags or args.ingest_type:
        resource = None
        if args.resource:
            if args.resource == '-':
                fresource = sys.stdin
            else:
                fresource = open(args.resource, 'r')
            resource = et.parse (fresource).getroot()
        if resource is None:
            resource = et.Element('resource', uri = "/tags")
        if args.tags:
            for t,v in [ x.split(':') for x in args.tags]:
                et.SubElement (resource, 'tag', name=t, value=v)
        if args.ingest_type:
            ingest = et.SubElement (resource, 'tag', name='ingest')
            et.SubElement (ingest, 'tag', name='type', value=args.ingest_type)
        if resource is not None:
            #tags = StringIO(et.tostring(resource))
            #tags.name = "stringio"
            tags = et.tostring(resource)


    #Upload copied files
    for p in args.paths:
        path = os.path.abspath(os.path.expanduser(p))
        if os.path.isdir (path):
            for root, dirs, files in os.walk(path):
                for name in files:
                    filename = os.path.join(root, name)
                    if isimagefile (filename):
                        if args.verbose:
                            print "transfering %s" % (filename)
                        upload(args.dest, filename, userpass, tags)
        elif os.path.isfile(path):
            if isimagefile (path):
                response = upload(args.dest, path, userpass, tags)
                if args.verbose:
                    print response
    sys.exit(0)



if __name__=="__main__":
    main()
