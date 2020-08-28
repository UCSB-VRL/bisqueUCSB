from __future__ import print_function
import sys
import os
import argparse
import urlparse
import requests
from lxml import etree
import contextlib

CLEAN_URL = "/image_service/image/{resource_uniq}?cleancache"
SERVICE_URL = "/image_service/image/{resource_uniq}?thumbnail"

if os.name != 'nt':
    WLOG="httperf --rate=8 --hog --wlog=Y,reqs.txt --num-conn=100 {options}"
    WSESS="httperf --rate=8 --hog --wsesslog=10,1,reqs.txt --num-conn=100 {options}"
else:
    # --hog would hang httperf on cygwin, removing it for windows
    WLOG="httperf --rate=8 --wlog=Y,reqs.txt --num-conn=100 {options}"
    WSESS="httperf --rate=8 --wsesslog=10,1,reqs.txt --num-conn=100 {options}"
    
PRE_SCRIPT="""
import requests
import subprocess

"""

@contextlib.contextmanager
def special_open(filename=None, mode="w"):
   if filename and filename != '-':
       fh = open(filename, mode)
   else:
       fh = sys.stdout

   try:
       yield fh
   finally:
       if fh is not sys.stdout:
           fh.close()


def gen_wlog(args, options, els):
    urls = []
    with open(args.request_file, 'wb') as req:
        for attrs in els:
            print (SERVICE_URL.format (**attrs), '\0', sep='', end='', file=req)
            urls.append (urlparse.urljoin(args.url, CLEAN_URL.format(**attrs)))

    with special_open(args.script) as out:
        print (PRE_SCRIPT, file=out)
        for arg in urls:
            print ("requests.get('{0}', verify=False)".format(arg), file=out)
        print ("subprocess.call('{0}', shell=True)".format(WLOG.format(options=' '.join(options))),
               file=out)


def gen_session(args, options, els):
    with open(args.request_file, 'wb') as req:
        for attrs in els:
            print (CLEAN_URL.format(**attrs), file=req)
        for attrs in els:
            print (' '*4, SERVICE_URL.format (**attrs), file=req)

    with special_open(args.script) as out:
        print (PRE_SCRIPT, file=out)
        print ("subprocess.call('{0}', shell=True)".format(WSESS.format(options=' '.join(options))),
               file=out)


DESCR="Generate a httperf request file and python script to exercise a bisque server"
def main():
    parser = argparse.ArgumentParser(DESCR)
    parser.add_argument("url", help="A place to grap resource i.e. http://host/data_service/image?limit=10")
    parser.add_argument("-r", "--request_file", default="reqs.txt",  help="place reqs in this file: default reqs.txt")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--script", default=None, help="Write script to SCRIPT or default to stdout")
    parser.add_argument("--gensession", default=False, action="store_true", help="Generate a session file: see httperf docs")

    options=[]
    args = parser.parse_args()
    url = urlparse.urlparse (args.url)
    if url.scheme == 'https':
        options.append('--ssl')
    options.append ('--server={0}'.format(url.hostname))
    if url.port:
        options.append ('--port={0}'.format(url.port))


    r = requests.get (args.url, verify=False)
    els = []
    if  r.status_code == 200:
        response = etree.XML( r.text)
        for image in response:
            els.append ( dict (image.attrib) )

    if len(els)==0:
        print ("NOTHING to generate no images found")
        return

    if args.gensession:
        gen_session(args, options, els)
    else:
        gen_wlog (args, options, els)


if __name__ == "__main__":
    main()



