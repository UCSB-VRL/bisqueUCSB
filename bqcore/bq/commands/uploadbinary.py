#!/usr/bin/env python
# Script to upload external files to the binary server
#
import os, re, urllib2, hashlib, inspect, sys

BASE= "https://biodev.ece.ucsb.edu/binaries/upload/"

class Abort(Exception):
    pass

def _sha1hash(data):
    return hashlib.sha1(data).hexdigest().upper()



def upload_file(url, filename, user='', passwd='', opts=None):
    pm = urllib2.HTTPPasswordMgrWithDefaultRealm()
    pm.add_password(None, 'biodev.ece.ucsb.edu', user, passwd)
    print ('Uploading %s to %s (%s Kb)\n' % (filename, url, os.path.getsize(filename) / 1024))
    auth = urllib2.HTTPBasicAuthHandler(pm)
    try:
        if not opts.dryrun:
            handle = open(filename, 'rb')
            data = {'file': handle,
                    'package':opts.package,
                    'version': opts.version,
                    'architecture' : opts.arch }
            # XXX support proxies; look at httprepo.httprepository.__init__
            # or http://www.hackorama.com/python/upload.shtml
            resp = urllib2.build_opener(urllib2.HTTPRedirectHandler, MultipartPostHandler, auth).open(url, data).close()

            if resp is not None:
                print resp.read()
            #print str( resp.info())
            handle.close()

        handle = open(filename, 'rb')
        sha1 = _sha1hash(handle.read())
        handle.close()
        filename = os.path.basename(filename)

        return "%s-%s" % (sha1, filename)

    except IOError, err:
        raise Abort('Problem uploading %s to %s (try it manually using a web browser): %s\n' % (filename, url, err))


# --- FROM http://odin.himinbi.org/MultipartPostHandler.py ---
# (with some bug fixes!)
import urllib
import urllib2
import mimetools, mimetypes
import os, stat

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

# Controls how sequences are uncoded. If true, elements may be given multiple values by
#  assigning a sequence.
doseq = 1

class MultipartPostHandler(urllib2.BaseHandler):
    handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first

    def http_request(self, request):
        data = request.get_data()
        if data is not None and type(data) != str:
            v_files = []
            v_vars = []
            for(key, value) in data.items():
                try:
                    value.name
                    v_files.append((key, value))
                except AttributeError:
                    v_vars.append((key, value))

            if len(v_files) == 0:
                data = urllib.urlencode(v_vars, doseq)
            else:
                boundary, data = self.multipart_encode(v_vars, v_files)
                contenttype = 'multipart/form-data; boundary=%s' % boundary
                if(request.has_header('Content-Type')
                   and request.get_header('Content-Type').find('multipart/form-data') != 0):
                    print "Replacing %s with %s" % (request.get_header('content-type'), 'multipart/form-data')
                request.add_unredirected_header('Content-Type', contenttype)

            request.add_data(data)
        return request

    # For some reason this not a real method see re-assign of Callable after defition
    # maybe for urlib? rewrite using requests someday
    def multipart_encode(vars, files, boundary = None, buffer = None): # pylint: disable=no-self-argument
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buffer is None:
            buffer = ''
        for(key, value) in vars: # pylint: disable=not-an-iterable
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"' % key
            buffer += '\r\n\r\n' + value + '\r\n'
        for(key, fd) in files:
            filename = os.path.basename(fd.name)
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
            buffer += 'Content-Type: %s\r\n' % contenttype
            fd.seek(0)
            buffer += '\r\n' + fd.read() + '\r\n'
        buffer += '--%s--\r\n\r\n' % boundary
        return boundary, buffer
    multipart_encode = Callable(multipart_encode)

    https_request = http_request
# ------------------------------------------------------------

help = """
bq-upload-binary [-u user] [-p passwd] [-d http dest] file

This script is used for uploading binary dependencies and optional
files for bisque image repository and analysis system.

Files uploaded will be placed at %s unless changed.

Use --help for more info.
""" % BASE


def main():
    from optparse import OptionParser
    parser = OptionParser (usage=help)
    parser.add_option ('-u', '--user', action="store", default='')
    parser.add_option('-p', '--password', action="store", default='')
    parser.add_option('--package', action="store", default='')
    parser.add_option('--version', action="store", default='')
    parser.add_option('--arch', action="store", default='')
    parser.add_option('-d', '--destination', action="store", default=BASE)
    parser.add_option('-n','--dryrun', action="store", default=False)

    (opts, args) = parser.parse_args()

    if  len(args) < 1:
        parser.error ("You must upload at least one file")


    print "Uploading to %s" % opts.destination
    uploaded = []
    for filename in args:
        if os.path.exists(filename):
            #upload_file(BASE, filename)
            fname = upload_file(opts.destination, filename,
                                opts.user, opts.password,
                                opts)
            uploaded.append (fname)

    print "Please add the following files to EXTERNAL_FILES:"
    print "\n".join (uploaded)


if __name__ == "__main__":
    main()
