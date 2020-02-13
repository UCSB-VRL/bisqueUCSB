#!/usr/bin/python

# Convert a dataset resource of "partial" images (image references with "#<part>" suffix)
# into an image resource without "#<part>" references.

import sys
import os
import argparse
import logging
import copy
import re
import time

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

import bqapi


def find_image_datasets(sess, name_pattern=r'^.*\.czi$', bisque_root=None):
    # find all datasets that should be converted to images
    logging.info("===== finding datasets to convert =====")
    res = []
    data = sess.service ('data_service')

    datasets = None
    try:
        #datasets = sess.fetchxml(url=bisque_root+'/data_service/dataset', view='short,clean', wpublic='1')
        #datasets = sess.fetchxml(url=bisque_root+'/data_service/dataset', view='short,clean')
        datasets  = data.get ("dataset", params = {'view': 'short,clean' }, render='xml')
        logging.debug("got datasets")
    except bqapi.BQCommError:
        logging.error("could not fetch datasets")
        return []
    for dataset in datasets:
        if not re.match(name_pattern, dataset.get('name')):
            continue
        # matching name, now look inside to see if all references are to images with "#<part>" suffix
        logging.debug("inspecting dataset %s" % dataset.get('resource_uniq'))
        full_dataset = None
        try:
            #full_dataset = sess.fetchxml(url=bisque_root+'/data_service/'+dataset.get('resource_uniq')+'/value', view='short,clean')
            full_dataset = data.get(dataset.get('resource_uniq')+"/value", params = {'view': 'short,clean'}, render='xml')
        except bqapi.BQCommError:
            logging.error("could not fetch dataset")
            return []
        good_refs = True
        for ref_image in full_dataset.xpath("./image"):
            if not re.match('^.*#[0-9]+$', ref_image.get('name')) or not re.match('^.*#[0-9]+$', ref_image.get('value')):
            # local testing !!!!!!!!!! if not any([ref_image.get('name').lower().endswith(ext) for ext in ['jpg', 'tif']]) or not any([ref_image.get('value').lower().endswith(ext) for ext in ['jpg', 'tif']]):
                logging.debug("malformatted image name/value found, skipping dataset")
                good_refs = False
                break
        if good_refs:
            res.append(dataset.get('resource_uniq'))
    logging.debug("found datasets to convert: %s" % res)
    return res

def convert_dataset(sess, dataset_uniq, want_delete=False, bisque_root=None, dryrun=False, as_user=None):
    dataset = None
    data = sess.service('data_service')
    blobs= sess.service('blob_service')
    try:
        #dataset = sess.fetchxml(url=bisque_root+'/data_service/'+dataset_uniq, view='deep,clean')
        dataset = data.fetch(dataset_uniq, params = {'view': 'deep,clean'}, render='xml')
        dataset_created=data.fetch (dataset_uniq, render='xml').get ('created')
        logging.debug("got dataset")
    except bqapi.BQCommError:
        logging.error("could not fetch dataset")
        return None
    # read one of the items to get filename
    matches = dataset.xpath("./value[@type='object']")
    if len(matches)<1:
        logging.error("dataset is empty")
        return None
    image = None
    try:
        #image = sess.fetchxml(url=matches[0].text, view='full,clean')
        image = data.fetch (matches[0].text, params = {'view': 'full,clean'}, render='xml')
        #links  = data.fetch ('link', params = {'noparent':1, 'value': image.get('resource_uniq')}, render='xml')
        logging.debug("got one of the images in dataset")
    except bqapi.BQCommError:
        logging.error("could not fetch image in dataset")
        return None
    image_filename = image.xpath("./tag[@name='filename']")[0].get('value')
    # create image resource with filename without '#' and with all tags from dataset
    new_image = etree.Element('image', created=dataset_created, name=image.get('name').split('#')[0], value=image.get('value').split('#')[0])
    etree.SubElement(new_image, 'tag', name='filename', value=image_filename.split('#')[0])
    for match in dataset.xpath("./tag"):
        match_copy = copy.deepcopy(match)
        new_image.append(match_copy)

    # write new image back
    res = None
    try:
        extra = {}
        if not dryrun:
            #extra = {'user':as_user} if as_user is not None else {}
            #res = sess.postxml(url=bisque_root+'/data_service', xml=new_image, **extra)
            res = data.post (data=etree.tostring(new_image), render="xml")
        else:
            res = etree.Element('image', name="dryrun" , resource_uniq='00-dryrun')
        logging.debug("new image posted back")
    except bqapi.BQCommError:
        logging.error("could not post new image back")
        return None
    # update link
    try:
        dirname = dataset_created.split('T')[0]
        linkpath="/mounts/s3/{}/{}?resource_uniq={}".format (dirname, new_image.get ('name'), res.get('resource_uniq'))
        if not dryrun:
            blob = blobs.post (linkpath)
            #data.post (dir_uri, data=etree.tostring (link_xml), render='xml')
        logging.debug ("new link at %s", linkpath)
    except bqapi.BQCommError:
        logging.error("could not post new image link")

    # delete old dataset if requested
    if want_delete:
        try:
            if not dryrun:
                #sess.deletexml(url=bisque_root+'/data_service/'+dataset_uniq)
                data.delete (dataset_uniq, render="xml")
            logging.debug("old dataset deleted")
        except bqapi.BQCommError:
            logging.error("could not delete dataset")
            return None
    return res.get('resource_uniq')

def update_references(sess, dataset_map, bisque_root=None, update_mexes=False, update_datasets=False, dryrun=False, as_user=None):
    # find any reference to the converted dataset and switch it to the new image
    data = sess.service("data_service")
    if update_datasets:
        logging.info("===== updating references in datasets =====")
        # (1) search in datasets
        datasets = []
        try:
            #datasets = sess.fetchxml(url=bisque_root+'/data_service/dataset', view='short', wpublic='1')
            #datasets = sess.fetchxml(url=bisque_root+'/data_service/dataset', view='short')
            datasets = data.fetch ("dataset", render="xml")
        except bqapi.BQCommError:
            logging.error("could not fetch datasets")
            return
        for dataset in datasets:
            deep_dataset = None
            was_updated = False
            try:
                #deep_dataset = sess.fetchxml(url=dataset.get('uri'), view='deep')  # TODO: avoid deep fetch
                deep_dataset = data.fetch(dataset.get ('resource_uniq'), params={'view':'deep'}, render="xml")
            except bqapi.BQCommError:
                logging.error("could not fetch dataset %s" % dataset.get('resource_uniq'))
                continue
            refs = deep_dataset.xpath("./value[@type='object']")
            for ref in refs:
                val = ref.text
                for dataset_uniq, img_uniq in dataset_map.iteritems():
                    if val.startswith('http') and val.endswith(dataset_uniq):
                        # found pointer to dataset => convert it
                        ref.text = val.replace(dataset_uniq, img_uniq)
                        was_updated = True
                        break
            if was_updated:
                try:
                    extra = {}
                    if not dryrun:
                        #extra = {'user':as_user} if as_user is not None else {}
                        #sess.postxml(url=dataset.get('uri'), xml=deep_dataset, **extra)
                        data.post(data=etree.tostring(deep_dataset)) # no check?
                    logging.debug("dataset %s updated" % dataset.get('resource_uniq'))
                except bqapi.BQCommError:
                    logging.error("could not update dataset %s" % dataset.get('resource_uniq'))
    if update_mexes:
        logging.info("===== updating references in mexes =====")
        # (2) search in mexes
        mexes = []
        try:
            #mexes = sess.fetchxml(url=bisque_root+'/data_service/mex', view='short')
            mexes = data.fetch ("mex", render='xml')
        except bqapi.BQCommError:
            logging.error("could not fetch mexes")
            return
        for mex in mexes:
            deep_mex = None
            was_updated = False
            try:
                #deep_mex = sess.fetchxml(url=mex.get('uri'), view='deep')  # TODO: avoid deep fetch
                deep_mex = data.fetch (mex.get('resource_uniq'), params={'view':'deep'}, render='xml')
            except bqapi.BQCommError:
                logging.error("could not fetch mex %s" % mex.get('resource_uniq'))
                continue
            tags = deep_mex.xpath("./tag[@name='inputs' or @name='outputs']//tag")
            for tag in tags:
                val = tag.get("value")
                for dataset_uniq, img_uniq in dataset_map.iteritems():
                    if val.startswith('http') and val.endswith(dataset_uniq):
                        # found pointer to dataset => convert it
                        tag.set("value", val.replace(dataset_uniq, img_uniq))
                        was_updated = True
                        break
            if was_updated:
                try:
                    extra = {}
                    if not dryrun:
                        #extra = {'user':as_user} if as_user is not None else {}
                        #sess.postxml(url=mex.get('uri'), xml=deep_mex, **extra)
                        data.post (mex.get('resource_uniq'), data=etree.tostring(deep_mex))
                    logging.debug("mex %s updated" % mex.get('resource_uniq'))
                except bqapi.BQCommError:
                    logging.error("could not update mex %s" % mex.get('resource_uniq'))

def rerun_mexes(sess, dataset_map, bisque_root=None, dryrun=False, as_user=None):
    # find all mexes that have one of the converted datasets as input
    # and re-run them with the new image as input
    # after that, delete the old mex
    logging.info("===== re-running affected mexes =====")
    data = sess.service("data_service")
    #module = sess.service("module_service")
    # (1) find affected mexes
    mexes = []
    try:
        mexes = data.fetch ("mex", params={'view':'full'}, render="xml")
    except bqapi.BQCommError:
        logging.error("could not fetch mexes")
        return
    for mex in mexes:
        input_url = mex.xpath("./tag[@name='inputs']")
        if len(input_url) >= 1:
            mex_input = None
            try:
                mex_input = sess.fetchxml(url=input_url[0].get('uri'), view='deep,clean')
            except bqapi.BQCommError:
                logging.error("could not fetch mex %s input" % mex.get('resource_uniq'))
                continue
            in_links = mex_input.xpath("./tag[(@name='resource_url' or @name='image_url') and @type='dataset']")
            if len(in_links) >= 1 and in_links[0].get('value').startswith('http'):
                for dataset_uniq, img_uniq in dataset_map.iteritems():
                    if in_links[0].get('value').endswith(dataset_uniq):
                        # found a mex with converted input => create new mex for re-run
                        logging.debug("found mex to rerun: %s" % mex.get('resource_uniq'))
                        new_mex = etree.Element('mex')
                        new_mex.append(copy.deepcopy(mex_input))
                        new_link = new_mex.xpath("./tag[@name='inputs']/tag[(@name='resource_url' or @name='image_url') and @type='dataset']")[0]
                        new_link.set("value", in_links[0].get('value').replace(dataset_uniq, img_uniq))
                        new_link.set("type", "image")
                        # (2) re-run the MEX
                        if not dryrun:
                            extra = {'user':as_user} if as_user is not None else {}
                            sess.postxml(url=bisque_root+'/module_service/'+mex.get('name')+'/execute', xml=new_mex, **extra)
                        logging.debug("started module %s with mex %s" % (mex.get('name'), etree.tostring(new_mex)))
                        # (3) delete old MEX
                        if not dryrun:
                            data.delete(mex.get('resource_uniq'), render="xml")
                        logging.debug("old mex %s deleted" % mex.get('resource_uniq'))


def reload_images(sess, dataset_map, bisque_root=None, dryrun=False):
    logging.info("===== reloading images (ensure in s3 cache)  =====")
    data = sess.service('data_service')
    image = sess.service('image_service')
    
    for dataset_uniq, img_uniq in dataset_map.iteritems():
        logging.info ("prefetch %s", img_uniq)
        data.fetch (img_uniq)
        if dryrun :
            continue
        while True:
            try:
                # need to wait for image to become available
                response = image.fetch ("{}?thumbnail=280,280".format(img_uniq))
                if response.status_code == 200:
                    break
                logging.warning ("too long to fetch %s (looping)", img_uniq)
            except bqapi.BQCommError:
                logging.warning ("too long to fetch %s (looping)", img_uniq)
                

def delete_datasets(sess, dataset_uniqs, bisque_root=None, dryrun=False):
    logging.info("===== deleting old dataset =====")
    dataset= sess.service("dataset_service")
    for dataset_uniq in dataset_uniqs:
        try:
            if not dryrun:
                #sess.deletexml(url=bisque_root+'/data_service/'+dataset_uniq)
                #sess.fetchxml(url=bisque_root+'/dataset_service/delete', duri="{}/data_service/{}".format (bisque_root, dataset_uniq))
                dataset.delete (dataset_uniq, members=True)
            logging.info("old dataset %s deleted" , dataset_uniq)
        except bqapi.BQCommError:
            logging.error("could not delete dataset %s" % dataset_uniq)

USAGE="""
dataset2image: Convert a dataset resource of "partial" images (image references with "#<part>" suffix)
into an image resource without "#<part>" references.

Example:
dataset2image <dataset resource uniq>
converts the given dataset into an image resource.
"""

def main():
    parser = argparse.ArgumentParser(USAGE)
    parser.add_argument("dataset_uniq",  help = "resource uniq of dataset to convert (or ALL)" )
    parser.add_argument("--delete", '-d', default=False, action="store_true", help="delete dataset after conversion")
    parser.add_argument("--server", "-s", help="BisQue server", default='http://localhost')
    parser.add_argument("--auth", "-a", help="basic auth credentials (user:passwd)", default='admin:admin')
    parser.add_argument("--user", "-u", help="user name to run as", default=None)
    parser.add_argument("--verbose", '-v', default=False, action="store_true", help="verbose output")
    parser.add_argument("--dryrun", '-r', default=False, action="store_true", help="no updates")
    parser.add_argument("--mexrefs", default=False, action="store_true", help="update mex refs to converted images")
    parser.add_argument("--dsrefs", default=False, action="store_true", help="update dataset refs to converted images")
    parser.add_argument("--mexrerun", default=False, action="store_true", help="delete and rerun mexes with converted images")
    args = parser.parse_args()
    print (args)

    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    try:
        user, passwd = args.auth.split(':')
    except AttributeError:
        user, passwd = 'admin', 'admin'
    sess = bqapi.BQSession ().init_local(user, passwd, bisque_root=args.server, create_mex=False)
    if args.user:
        admin = sess.service ('admin')
        admin.login_as (args.user)

    if args.dataset_uniq.lower() == 'all':
        dataset_map = {}
        datasets = find_image_datasets(sess, bisque_root=args.server.rstrip('/'))
        logging.info("===== converting %s datasets to images =====" % len(datasets))
        for dataset_uniq in datasets:
            img_uniq = convert_dataset(sess, dataset_uniq, want_delete=False, bisque_root=args.server.rstrip('/'), dryrun=args.dryrun, as_user=args.user)  # will delete later
            if img_uniq is not None:
                dataset_map[dataset_uniq] = img_uniq
        update_references(sess, dataset_map, bisque_root=args.server.rstrip('/'), update_mexes=args.mexrefs, update_datasets=args.dsrefs, dryrun=args.dryrun, as_user=args.user)
        if args.delete:
            logging.info ("MAP %s", dataset_map)
            delete_datasets(sess, dataset_map.keys(), bisque_root=args.server.rstrip('/'), dryrun=args.dryrun)
        
        if args.mexrerun:
            reload_images (sess, dataset_map, bisque_root=args.server.rstrip('/'), dryrun=args.dryrun)
            rerun_mexes(sess, dataset_map, bisque_root=args.server.rstrip('/'), dryrun=args.dryrun, as_user=args.user)
    else:
        logging.info("===== converting dataset to image =====")
        convert_dataset(sess, args.dataset_uniq, want_delete=args.delete, bisque_root=args.server.rstrip('/'), dryrun=args.dryrun, as_user=args.user)

if __name__ == "__main__":
    main()
