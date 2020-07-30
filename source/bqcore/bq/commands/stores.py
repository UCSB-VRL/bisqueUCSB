# Store services
#
from __future__ import print_function
import os
import logging

from tg import config
from lxml import etree

from bq.util.paths import data_path
from bq.util.compat import OrderedDict

__all__  = [ "list_stores", "init_stores", "fill_stores", "delete_stores" ]


log = logging.getLogger('bq.commands.store')


from bq import data_service
from bq.core import  identity
from bq.util.urlpaths import *

#  Load store parameters
OLDPARMS = dict (date='',
                 dirhash='',
                 filehash='',
                 filename='',
                 filebase='',
                 fileext='')


def get_tag(elem, tag_name):
    els = elem.xpath ('./tag[@name="%s"]' % tag_name)
    if len(els) == 0:
        return None
    return els

def load_default_drivers():
    stores = OrderedDict()
    store_list = [ x.strip() for x in config.get('bisque.blob_service.stores','').split(',') ]
    log.debug ('requested stores = %s' , store_list)
    for store in store_list:
        # pull out store related params from config
        params = dict ( (x[0].replace('bisque.stores.%s.' % store, ''), x[1])
                        for x in  config.items() if x[0].startswith('bisque.stores.%s.' % store))
        if 'mounturl' not in params:
            if 'path' in params:
                path = params.pop ('path')
                params['mounturl'] = string.Template(path).safe_substitute(OLDPARMS)
                log.warn ("Use of deprecated path (%s) in  %s driver . Please change to mounturl and remove any from %s", path, store, OLDPARMS.keys())
            else:
                log.error ('cannot configure %s without the mounturl parameter' , store)
                continue
        log.debug("params = %s" , params)
        #driver = make_storage_driver(params.pop('path'), **params)
        #if driver is None:
        #    log.error ("failed to configure %s.  Please check log for errors " , str(store))
        #    continue
        stores[store] = params
    return stores



def init_stores(username=None):
    """Esnure stores are initialized with correct values and tag order
    """
    if username is not None:
        users = [ username ]
    else:
        users  = [ x.get ('name') for x in data_service.query('user', wpublic=1) ]

    drivers = load_default_drivers()

    for user in users:
        with identity.as_user(user):
            _create_root_mount(drivers)


def _create_root_mount(drivers):
    'create/find hidden root store for each user'

    root = data_service.query('store', resource_unid='(root)', view='full')
    if len(root) == 0:
        return  _create_default_mounts(drivers)
    if len(root) == 1:
        return _create_default_mounts(drivers, root[0])
    elif len(root) > 1:
        log.error("Root store created more than once: %s ", etree.tostring(root))
        return None

    return root[0]

def _create_default_mounts(drivers, root=None):
    'translate system stores into mount (store) resources'

    #for x in range(subtrans_attempts):
    #    with optional_cm(subtrans):
    update = False
    user_name  = identity.current.user_name
    if root is None:
        update  = True
        root = etree.Element('store', name="(root)", resource_unid="(root)")
        etree.SubElement(root, 'tag', name='order', value = ','.join (drivers.keys()))
        for store_name,driver in drivers.items():
            mount_path = string.Template(driver['mounturl']).safe_substitute(datadir = data_url_path(), user = user_name)
            etree.SubElement(root, 'store', name = store_name, resource_unid=store_name, value=config2url(mount_path))
    else:
        storeorder = get_tag(root, 'order')
        if storeorder is None:
            log.warn ("order tag missing from root store adding")
            storeorder = etree.SubElement(root, 'tag', name='order', value = ','.join (drivers.keys()))
            update = True
        elif len(storeorder) == 1:
            storeorder = storeorder[0]
        else:
            log.warn("Multible order tags on root store")

        # Check for store not already initialized
        user_stores   = dict ((x.get ('name'), x)  for x in root.xpath('store'))
        for store_name, driver in drivers.items():
            if store_name not in user_stores:
                store = etree.SubElement (root, 'store', name = store_name, resource_unid = store_name)
                # If there is a new store defined, better just to reset it to the default

                #ordervalue = [ x.strip() for x in storeorder.get ('value', '').split(',') ]
                #if store_name not in ordervalue:
                #    ordervalue.append(store_name)
                #    storeorder.set ('value', ','.join(ordervalue))
                storeorder.set ('value', ','.join (drivers.keys()))
            else:
                store = user_stores[store_name]

            if store.get ('value') is None:
                mounturl = driver.get ('mounturl')
                mounturl = string.Template(mounturl).safe_substitute(datadir = data_url_path(), user = user_name)
                # ensure no $ are left
                mounturl = mounturl.split('$', 1)[0]
                store.set ('value', config2url(mounturl))
                log.debug ("setting store %s value to %s", store_name, mounturl)
                update = True

    if update:
        log.debug ("updating %s", etree.tostring(root))
        return data_service.update(root, new_resource=root, replace=False, view='full')
    return root


def list_stores(username = None):
    if username is not None:
        users = [ username ]
    else:
        users  = [ x.get ('name') for x in data_service.query('user', wpublic=1) ]

    drivers = load_default_drivers()
    print ("\n\nDrivers:\n")
    for n,d in drivers.iteritems():
        print ("%s: %s"%(n, d))

    # print ("\nStores:")
    # for user in users:
    #     with identity.as_user(user):
    #         user_root = data_service.query('store', resource_unid='(root)', view='full')
    #         user_stores = dict ((x.get ('name'), x)  for x in user_root.xpath('store'))
    #         print ("%s: %s"%(user, user_stores))

def fill_stores(username = None):
    "Clean unreferenced images/files from bisque storage"

    raise NotImplementedError ("fill stores not yet implemented")


def delete_stores(username = None):
    "Delete stores"

    raise NotImplementedError ("delete stores not yet implemented")

def update_stores(username = None):
    """ Update stores to use current datadir specifications """
    if username is not None:
        users = [ username ]
    else:
        users  = [ x.get ('name') for x in data_service.query('user', wpublic=1) ]

    drivers = load_default_drivers()
    for user in users:
        with identity.as_user(user):
            _update_mounts(drivers)

def _update_mounts(drivers):
    update = False
    user_name  = identity.current.user_name
    user_root = data_service.query('store', resource_unid='(root)', view='full')
    if len(user_root) == 0:
        log.warn ("No store found")
    elif len(user_root) == 1:
        user_root =  user_root[0]
    elif len(user_root) > 1:
        log.error("Root store created more than once for %s: %s please check DB", user_name, etree.tostring(user_root))
        return None

    user_stores = dict ((x.get ('name'), x)  for x in user_root.xpath('store'))

    storeorder = get_tag(user_root, 'order')
    if storeorder is None:
        log.warn ("order tag missing from root store adding")
        storeorder = etree.SubElement(user_root, 'tag', name='order', value = ','.join (drivers.keys()))
        update = True
    elif len(storeorder) == 1:
        storeorder = storeorder[0]
        storelist = ','.join (drivers.keys())
        if storeorder.get('value') != storelist:
            storeorder.set ('value', storelist)
            update = True

    for store_name, driver in drivers.items():
        if store_name not in user_stores:
            print ("Need to create new store : %s" % store_name)
            mount_path = string.Template(driver['mounturl']).safe_substitute(datadir = data_url_path(), user = user_name)
            etree.SubElement(user_root, 'store', name = store_name, resource_unid=store_name, value=config2url(mount_path))
            update = True
            continue

        store = user_stores[store_name]
        mounturl = driver.get ('mounturl')
        mounturl = string.Template(mounturl).safe_substitute(datadir = data_url_path(), user = user_name)
        # ensure no $ are left
        mounturl = mounturl.split('$', 1)[0]
        mounturl = config2url(mounturl)

        store_value =  store.get ('value')

        print ("examining store %s with %s" % (store_name, store_value))


        if store_value is None or store_value != mounturl:
            print ("Updating store with value %s to %s" % (store_value, mounturl))
            store.set ('value', mounturl)
            update = True

    if update:
        return data_service.update(user_root, new_resource=user_root, replace=False, view='full')



def move_stores(from_store, to_store, username = None):
    """ Update stores to use current datadir specifications """
    if username is not None:
        users = [ username ]
    else:
        users  = [ x.get ('name') for x in data_service.query('user', wpublic=1) ]


    from bq.core.service import service_registry
    file_service = service_registry.find_service ("mnt")
    drivers = load_default_drivers()
    for user in users:
        print ("MOVING %s -> %s for %s ", from_store, to_store, user)
        with identity.as_user(user):
            file_service.move (from_store, to_store)
