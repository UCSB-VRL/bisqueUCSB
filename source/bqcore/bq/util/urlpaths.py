###############################################################################
##  Bisque                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009,2010,2011,2012                           ##
##     by the Regents of the University of California                        ##
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
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> ''AS IS'' AND ANY         ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE         ##
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR        ##
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> OR           ##
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,     ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ##
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## The views and conclusions contained in the software and documentation     ##
## are those of the authors and should not be interpreted as representing    ##
## official policies, either expressed or implied, of <copyright holder>.    ##
###############################################################################
"""
SYNOPSIS
========
blob_service


DESCRIPTION
===========
Store resource all special clients to simulate a filesystem view of resources.
"""
import os
import string
import urllib
import urlparse
import shutil
import posixpath

from bq.util.paths import data_path

if os.name == 'nt':
    def move_file (fp, newpath):
        with open(newpath, 'wb') as trg:
            shutil.copyfileobj(fp, trg)

    def data_url_path (*names):
        path = data_path(*names)
        #if len(path)>1 and path[1]==':': #file:// url requires / for drive lettered path like c: -> file:///c:/path
        #    path = '/%s'%path
        return path

    def localpath2url(path):
        # posixpath.normpath will not work well with smb mounts //share/dir/file.ext
        path = path.replace('\\', '/')
        try:
            path = path.encode('utf-8')
        except UnicodeDecodeError:
            pass # was encoded before
        url = urllib.quote(path)
        # KGK:would be better to add regexp matcher here
        if len(path)>3 and path[0] != '/' and path[1] == ':':
            # path starts with a drive letter: c:/ and is not a valid file like /:myfile/
            url = 'file:///%s'%url
        else:
            # path is a relative path
            url = 'file://%s'%url
        return url

    def url2localpath(url):
        "url should be utf8 encoded (but may actually be unicode from db)"
        if url.startswith('file://'):
            url = url[7:]
        path = posixpath.normpath(urlparse.urlparse(url).path)
        path = urllib.unquote(path)
        if len(path)>3 and path[0] == '/' and path[2] == ':':
            path = path[1:]
        path = force_filesys(path)
        return path

    def force_filesys(s):
        """Force s to be a unicode string
        """
        try:
            return s.decode('utf-8')
        except UnicodeEncodeError:
            # dima: safeguard measure for old non-encoded unicode paths
            return s
else:
    def move_file (fp, newpath):
        if hasattr(fp, 'name') and os.path.exists(fp.name):
            oldpath = os.path.abspath(fp.name)
            shutil.move (oldpath, newpath)
        else:
            with open(newpath, 'wb') as trg:
                shutil.copyfileobj(fp, trg)

    data_url_path = data_path

    def localpath2url(path):
        "convert a filespec to a utf8 %-encoded url"
        try:
            path = path.encode('utf-8')
        except UnicodeDecodeError:
            pass # was already encoded
        url = urllib.quote(path)
        url = 'file://%s'%url
        return url

    def force_filesys(s):
        """Force s to be a utf8 encode string no matter what
        """
        # Some unicode is actually UTF8, but the database doesn't know it.  Convert it to
        # a bytestring
        # http://stackoverflow.com/questions/14539807/convert-unicode-with-utf-8-string-as-content-to-str
        try:
            if isinstance(s, unicode):
                s = s.encode('latin1')
            # if we get here then we are  a bytestring (either ascii or utf8 encoded)
        except UnicodeEncodeError:
            # will be here if it *really* was unicode 16 (should still be unicode)
            if isinstance(s, unicode):
                s =  s.encode('utf8')
        # We should have an 8bit utf8 string or  a unciode that we can encode as utf8
        return s

    def url2localpath(url):
        "url should be utf8 encoded (but may actually be unicode from db)"
        if url.startswith('file://'):
            url = url[7:]
        path = posixpath.normpath(urlparse.urlparse(url).path)
        path = urllib.unquote(path)
        path = force_filesys(path)
        return path

def config2url(conf):
    "Make entries read from config with corrent encoding.. check for things that look like path urls"
    if conf.startswith('file://'):
        #return localpath2url( posixpath.normpath (urlparse.urlparse(conf).path))
        # Above breaks for dotted paths e.g. ./data .. simply returns /data
        return localpath2url( posixpath.normpath (conf[7:]))
    elif os.name == 'nt':
        return localpath2url(conf)
    else:
        return conf


def url2unicode(url):
    "Unquote and try to decode"
    url = urllib.unquote (url)
    try:
        return url.decode('utf-8')
    except UnicodeEncodeError:
        pass
    return url
