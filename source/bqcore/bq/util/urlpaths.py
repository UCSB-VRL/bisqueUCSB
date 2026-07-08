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

import logging
import os
import posixpath
import shutil
import string
import urllib.error
import urllib.parse
import urllib.request

from bq.util.paths import data_path

log = logging.getLogger(__name__)


def move_file(fp, newpath):
    if hasattr(fp, "name") and isinstance(fp.name, str) and os.path.exists(fp.name):
        oldpath = os.path.abspath(fp.name)
        shutil.move(oldpath, newpath)
    else:
        newdir = os.path.dirname(newpath)
        if not os.path.exists(newdir):
            os.makedirs(newdir, exist_ok=True)
        with open(newpath, "wb") as trg:
            shutil.copyfileobj(fp, trg)


data_url_path = data_path


def localpath2url(path):
    "convert a filespec to a utf8 %-encoded url"
    if isinstance(path, bytes):
        try:
            path = path.decode("utf-8")
        except Exception:
            path = f"{path}"
    url = urllib.parse.quote(path)
    return f"file://{url}"


def force_filesys(s):
    """Force s to be a utf8 encode string no matter what"""
    try:
        if isinstance(s, str):
            if all(ord(c) < 256 for c in s):
                s = s.encode("latin1")
            else:
                return s
    except UnicodeEncodeError:
        if isinstance(s, str):
            s = s.encode("utf8")
    return s


def url2localpath(url):
    "url should be utf8 encoded (but may actually be unicode from db)"
    url = f"{url}"
    if url.startswith("file://"):
        url = url[7:]
    path = os.path.normpath(urllib.parse.urlparse(url).path)
    path = urllib.parse.unquote(path)
    path = force_filesys(path)
    return f"{path}"


def config2url(conf):
    "Make entries read from config with corrent encoding.. check for things that look like path urls"
    if conf.startswith("file://"):
        # return localpath2url( posixpath.normpath (urlparse.urlparse(conf).path))
        # Above breaks for dotted paths e.g. ./data .. simply returns /data
        return localpath2url(posixpath.normpath(conf[7:]))
    return conf


# def url2unicode(url):
#     "Unquote and try to decode"
#     url = urllib.parse.unquote (url)
#     try:
#         return url.decode('utf-8')
#     except UnicodeEncodeError:
#         pass
#     return url


# !!! alternative approach
def url2unicode(url):
    "Unquote and try to decode with better Unicode support for Cyrillic characters"
    # Handle different encoding scenarios for Unicode filenames
    try:
        # First try regular URL unquoting
        url = urllib.parse.unquote(url)

        if isinstance(url, bytes):
            # Try UTF-8 first (most common)
            try:
                return url.decode("utf-8")
            except UnicodeDecodeError:
                # Try latin-1 as fallback (preserves bytes)
                try:
                    return url.decode("latin-1")
                except UnicodeDecodeError:
                    # Last resort: replace invalid characters
                    return url.decode("ascii", "replace")
        else:
            # Already a string, but might be percent-encoded twice
            if "%" in url:
                try:
                    # Try unquoting again in case of double encoding
                    decoded_again = urllib.parse.unquote(url)
                    if decoded_again != url:
                        return decoded_again
                except Exception:
                    pass
            return url
    except Exception as e:
        # log.exception("Error decoding url %s: %s", url, e)
        # Return as-is if nothing works
        return f"{url}"
