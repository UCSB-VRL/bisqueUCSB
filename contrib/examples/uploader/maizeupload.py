#!/bin/env python
###############################################################################
##  Bisque                                                                   ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008,2009,2010,2011,2012,2013,2014                 ##
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


DESCRIPTION
===========
  Example data transformer from CSV output

  1.  Read CSV containing image references and metadata
  2.  Fetch images from external website
  3.  Post each image to Bisque with Metadata
  4.  Create a dataset of the entire set

"""
#
# Python 2 Dependencies:
#    pip install argparse
#    pip install six
# Python 3 Dependencies
#    pip install six

import os
import sys
import csv
import argparse
import posixpath
import requests
import six
import logging
import uuid
import datetime
from six.moves import input

BASE = "http://www.dirt.biology.gatech.edu/sites/default/files/data/alex"
BISQUE_ROOT = "https://loup.ece.ucsb.edu"

# Original fields ['Image ID', 'Image name', 'Failed', 'Experiment
#number', 'circle ratio', 'x pixel', 'y pixel', 'xScale', 'yScale',
#'stem diameter', 'avg. root density', '#RTP', 'TD median', 'TD avg.',
#'DD90 max.', 'median Width', 'max. Width', 'D10', 'D20', 'D30',
#'D40', 'D50', 'D60', 'D70', 'D80', 'D90', 'DS10', 'DS20', 'DS30',
#'DS40', 'DS50', 'DS60', 'DS70', 'DS80', 'DS90', 'rel. root mass X',
#'rel. root mass Y', 'avg. lateral length', 'nodal root length',
#'lateral branching freq.', 'avg. nodal root dia', 'lateral
#avg. angle', 'lateral angular range', 'lateral min. angle', 'lateral
#max. angle', 'dist. to 1st lateral', 'median lateral dia', 'mean
#lateral dia']


REMOVE_FIELDS = ( 'Image ID','Image name','Failed','Experiment number', 'circle ratio','x pixel','y pixel' )

from bqapi import BQSession, BQDataset, BQImage, BQFactory

def readcsv(session):
    """Open the CSV maizedata file and return the reader"""
    filename = session.args.csvfile

    if session.args.verbose:
        six.print_ ( "Reading ", filename )
    csvfile  = open (filename, 'rU')
    #dialect = csv.Sniffer().sniff(csvfile.read(1024))
    #dialect.lineterminator = '\r'
    #csvfile.seek(0)
    #reader = csv.reader(csvfile)
    reader = csv.DictReader(csvfile)
    if session.args.verbose:
        six.print_ ("#Column headers")
        six.print_ ("#", reader.fieldnames )
    return reader


def transform(session, reader):
    """ Transform  rows to BQ objects into ( ImageURL, BQImage) array
    @param reader:  a csv reader
    @return : array of tuples  ( origin URL of image, BQImage with tags initialized)
    """
    uploaddir = str(datetime.date.today())

    images = []
    for row in reader:
        image_name = row['Image name'] +'.JPG'
        image_url = posixpath.join(BASE, image_name)
        # We can store the image in a serverside directory by prepending to the name
        image = BQImage (name = posixpath.join(uploaddir, image_name))
        for field in reader.fieldnames:
            if field in REMOVE_FIELDS:
                continue
            image.add_tag (name=field, value=row[field])
        images.append ( (image_url, image) )
        if session.args.limit and session.args.limit <= len (images):
            break

    return images

def transfer_images (session, image_data):
    """Download images and send them to bisque with metadata
    @param session: a bqsession
    @param image_data :array of tuples  ( origin URL of image, BQImage with tags initialized)
    @return: list of uris of uploaded bisque image
    """
    bqimages = []
    for url, bqo in image_data:
        # This is usually reserver for bisque servers but is generic enought to work with any URL
        tmpfile = "/tmp/%s" % os.path.basename (bqo.name)
        if not session.args.dryrun:
            session.fetchblob (url, path = tmpfile)
            image = session.saveblob (filename = tmpfile, bqo = bqo)
            bqimages.append ( (image.name, image.uri) )
            if session.args.verbose:
                six.print_( "Uploaded %s" %image.name)
        else:
            # Make a fake vector of uploaded files to check
            six.print_ ("Fetching %s->%s" % ( url, tmpfile))
            six.print_ ("uploading %s -> %s " % (tmpfile, session.args.bisque_host))
            six.print_ ("with metdata %s" % session.factory.to_string (xml))
            bqimages.append ( ( xml.name, posixpath.join(session.args.bisque_host, tmpfile)))

    return bqimages

def upload_dataset (session, dataset_name, uri_list):
    """Save a dataset
    Create a data setup from the uploaded list
    @param session: a bqsession
    @param dataset_name : name the new dataset
    @param url_list : array of uris (strings)
    @return: None
    """

    dataset = BQDataset (name="%s-%s" % (dataset_name, str(uuid.uuid4())[:4] ))
    # force dataset values to be interpreted as object references
    dataset.value =  [ (url, 'object') for url in uri_list ]

    if session.args.verbose:
        six.print_ ("DATASET ",  BQFactory.to_string(dataset))

    if not session.args.dryrun:
        session.save (dataset)


def main():
    parser = argparse.ArgumentParser(description='Load maize images and metadata')
    parser.add_argument('--imagebase', default = BASE, help= 'Directory to fetch images from  (%(default)s)')
    parser.add_argument('--bisque_host', default = BISQUE_ROOT, help="Upload images to (%(default)s)")
    parser.add_argument('--cas', default=False, action='store_true', help="Use CAS for login ( %(default)s )")
    parser.add_argument('-n', '--dryrun', default=False, action='store_true', help="Print actions")
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help="Dump alot of info")
    parser.add_argument('-u', '--credentials', help = "A Bisuqe username:password")
    parser.add_argument('-l', '--limit', type=int, help = "Limit number of images ")
    parser.add_argument('csvfile', nargs='?', default = 'MaizeImaging.csv', help="A local .csv file")

    args  = parser.parse_args()
    if args.verbose:
        logging.basicConfig (level = logging.DEBUG)

    print "LIMIT", args.limit

    session = BQSession()
    session.args = args
    # Ensure we have a way to login
    if not args.dryrun:
        if not args.credentials:
            args.credentials = input("Please enter bisque credentials: ")
        if ':' not in args.credentials:
            password = input ("Please enter password: ")
            args.credentials = ":".join ([args.credentials, password])
        user, password = args.credentials.split (":")

        if args.cas:
            session.init_cas (user, password, bisque_root = args.bisque_host, create_mex=False)
        else:
            session.init_local (user, password, bisque_root = args.bisque_host, create_mex=False)
    #
    #
    reader = readcsv (session)
    image_data = transform (session, reader)
    image_map = transfer_images (session, image_data)
    upload_dataset (session, 'maize', [ x[1] for x in image_map] )



if __name__ == "__main__":
    main()
