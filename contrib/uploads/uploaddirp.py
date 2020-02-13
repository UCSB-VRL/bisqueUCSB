#!/usr/bin/env python

import os
import sys
import argparse
import multiprocessing
import bqapi


ROOT = 'http://bisque_host/'
USER ='USER'
PASSWD = 'SECRET'

SESSION = None

def create_session (user, passwd, root):
    global SESSION
    SESSION = bqapi.BQSession ().init_local(user, passwd, bisque_root=root, create_mex=False)


def sendimage_to_bisque(image_path, meta_path=None):
    "Send one image to bisque"
    if meta_path:
        meta_path = open (meta_path).read()
    resource = SESSION.postblob (image_path, xml = meta_path)
    return resource

def sendimage_helper (arg_tuple):
    "Expand tuple args"
    return sendimage_to_bisque (*arg_tuple)


def create_dataset (name, images):
    pass




def main(argv):
    parser = argpase.ArgumentParser("Upload files to bisque")
    parser.add_argument('-r','--root', help='set bisque server', default=ROOT)
    parser.add_argument('-U','--user', help='set user:passwd', )
    parser.add_argument('-D','--dataset', help='add to dataset', default=None)
    parser.add_argument('--cas', help='use cas login', action="store_true", default=False)
    parser.add_argument('directory', help='directory to upload', default='.')

    args = parser.parse_args()

    pool = multiprocessing.Pool(6, create_session, (user, passwd, root))
    files = os.listdir (direct)
    print "Uploading ", files
    resource_list = pool.map (sendimage_helper, [ (root, user, passwd, f) for f in os.listdir (direct) ])





if __name__ == "__main__":
    main(sys.argv)
