import os
#import urllib
#import urlparse

import random
import string
import logging
import tempfile
import json
import shutil

from six.moves import urllib

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

try:
    import tables
except ImportError:
    logging.warn ("pytables services not available")

from requests_toolbelt import MultipartEncoder
from .util import  normalize_unicode
from .exception import BQCommError



#DEFAULT_TIMEOUT=None
DEFAULT_TIMEOUT=60*60 # 1 hour

####
#### KGK
#### Still working on filling this out
#### would be cool to have service definition language to make these.
#### TODO more service, renders etc.

class BaseServiceProxy(object):

    def __init__(self, session, service_name, timeout=DEFAULT_TIMEOUT):
        self.session = session
        self.service_url = session.service_map [service_name]
        self.service_name = service_name
        self.timeout = timeout

    def construct(self, path, params=None):
        url = self.service_url
        if params:
            path = "%s?%s" % (path, urllib.parse.urlencode(params))
        if path:
            url = urllib.parse.urljoin (url, path)
        return url

    def request (self, path=None, params=None, method='get', render=None, **kw):
        """
        @param path: a path on the service
        @param params: a diction of value to encode as params
        @return a reuqest.response
        """
        if path and path[0] == "/":
            path = path[1:]
        if path:
            path = urllib.parse.urljoin (self.service_url, path)
        else:
            path = self.service_url

        # no longer in session https://github.com/requests/requests/issues/3341
        timeout = kw.pop('timeout', self.timeout)
        headers = kw.pop('headers', self.session.c.headers)
        if render in ("xml", 'etree'):
            headers.update ({'Content-Type':'text/xml', 'Accept': 'text/xml'})

        try:
            response = self.session.c.request (url=path, params=params, method=method, timeout=timeout, headers=headers, **kw)
            if render  in ("xml", 'etree'):
                return etree.fromstring (response.content)
            return response
        except etree.ParseError:
            #self.session.log.error ("xml parse error in %s", response.content)
            raise BQCommError(response)

    def fetch(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, **kw)
    def get(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, **kw)
    def post(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, method='post', **kw)
    def put(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, method='put', **kw)
    def delete(self, path=None, params=None, render=None, **kw):
        return self.request(path=path, params=params, render=render, method='delete', **kw)


class AdminProxy (BaseServiceProxy):
    def login_as (self, user_name):
        data = self.session.service ('data_service')
        userxml = data.fetch ("user", params = { 'wpublic' :'1', 'resource_name':  user_name}, render="xml")
        user_uniq = userxml.find ("user").get ('resource_uniq')
        self.fetch ('/user/{}/login'.format(user_uniq))


class AuthProxy (BaseServiceProxy):
    def login_providers (self, **kw):
        return self.request ('login_providers', **kw)

    def credentials (self, **kw):
        return self.request ('credentials', **kw)

    def get_session (self, **kw): # hides session
        return self.request ('session', **kw)

class BlobProxy (BaseServiceProxy):
    def _resource_element (self, args_tag_file=None, args_resource_type=None, args_srcpath=None, **kw):
        """Check the args and create a compatible resource element  for posting or linking
        """
        if args_tag_file:
            # Load file into resource
            try:
                resource = etree.parse (args_tag_file).getroot()
            except etree.ParseError as pe:
                raise BQCommError('Parse failure: aborting: ')
        else:
            resource = etree.Element (args_resource_type or 'resource')

        for fld in ('permission', 'hidden'):
            if fld in kw:
                resource.set (fld, kw.get(fld))
        if args_srcpath:
            resource.set('value', args_srcpath)
            resource.set('name', os.path.basename (args_srcpath))
        return resource

    def path_link(self, srcpath, alias=None, resource_type=None, tag_file=None):
        url = urllib.parse.urljoin( self.session.service_map['blob_service'], 'paths/insert' )
        params = {}
        resource = self._resource_element(args_srcpath=srcpath, args_resource_type=resource_type, args_tag_file=tag_file)
        payload = etree.tostring (resource)
        if alias:
            params['user'] = alias
        r = self.post(url, data=payload, params=params, headers={'content-type': 'application/xml'})
        return r

    def path_delete(self, srcpath, alias=None):
        url = urllib.parse.urljoin( self.session.service_map['blob_service'], 'paths/remove' )
        params = {'path': srcpath}
        if alias:
            params['user'] = alias
        r = self.get(url, params=params)
        return r

    def path_rename(self, srcpath, dstpath, alias=None):
        url = urllib.parse.urljoin( self.session.service_map['blob_service'], 'paths/move' )
        params = {'path': srcpath, 'destination': dstpath}
        if alias:
            params['user'] = alias
        r = self.get(url, params=params)
        return r

    def path_list(self, srcpath, alias=None):
        url = urllib.parse.urljoin( self.session.service_map['blob_service'], 'paths/list' )
        params = { 'path' : srcpath }
        if alias:
            params['user'] = alias
        r = self.get(url, params=params)
        return r

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class ImportProxy(BaseServiceProxy):
    def transfer (self, filename, fileobj=None, xml=None):
        fields = {}
        if fileobj is None and filename is None:
            raise BQCommError('Filename or fileobj are required for transfer')
        if fileobj is None and os.path.exists (filename):
            fileobj = open (filename, 'rb')
        if fileobj is not None and filename is None:
            filename = fileobj.name

        if fileobj is not None:
            filename = normalize_unicode(filename)
            fields['file'] = (os.path.basename(filename), fileobj, 'application/octet-stream')
        if xml is not None:
            fields['file_resource'] = xml
        if fields:
            # https://github.com/requests/toolbelt/issues/75
            m = MultipartEncoder(fields = fields )
            m._read = m.read #pylint: disable=protected-access
            m.read = lambda size: m._read (8129*1024) # 8MB
            # ID generator is used to force load balancing operations
            response = self.post("transfer_"+id_generator(),
                                 data=m,
                                 headers={'Accept': 'text/xml', 'Content-Type':m.content_type})
            return response

class DatasetProxy (BaseServiceProxy):

    def delete (self, dataset_uniq,  members=False, **kw):
        if members:
            params = kw.pop('params', {})
            params['duri'] = dataset_uniq
            return self.fetch("delete", params=params, **kw)
        data = self.session.service('data_service')
        return data.delete (dataset_uniq)

    def append_member (self, dataset_uniq, resource_uniq, **kw):
        """Append an element
        """
        data = self.session.service('data_service')
        member = etree.Element('value', type='object')
        member.text = data.contruct (resource_uniq)
        self.post (dataset_uniq, data=etree.tostring(member), render='etree')

    def delete_member (self, dataset_uniq, resource_uniq, **kw):
        """Delete a member..
        @return new dataset if success or None
        """
        data = self.session.service('data_service')
        dataset = data.fetch ( dataset_uniq,  params = {'view':'full'}, render='etree')
        members = dataset.xpath ('value[text()="%s"]' % data.construct (resource_uniq))
        for member in members:
            dataset.remove (member)
        if len (members):
            for val in dataset.iter ('value'):
                _ = val.attrib.pop ('index', 0)
            return data.put (dataset_uniq, data = etree.tostring (dataset), render='etree')
        return None


class ModuleProxy (BaseServiceProxy):
    def execute (self, module_name, **module_parms):
        pass
    def register(self, engine_url):
        return self.request (path='register_engine', params = { 'engine_url':engine_url })
    def unregister (self, engine_url):
        return self.request (path='unregister_engine', params = { 'engine_url':engine_url })




class TableProxy (BaseServiceProxy):
    def load_array(self, table_uniq, path, slices=[]):
        """
        Load array from BisQue.
        """
        if table_uniq.startswith('http'):
            table_uniq = table_uniq.split('/')[-1]
        slice_list = []
        for single_slice in slices:
            if isinstance(single_slice, slice):
                slice_list.append("%s;%s" % (single_slice.start or '', '' if single_slice.stop is None else single_slice.stop-1))
            elif isinstance(single_slice, int):
                slice_list.append("%s;%s" % (single_slice, single_slice))
            else:
                raise BQCommError("malformed slice parameter")
        path = '/'.join([table_uniq.strip('/'), path.strip('/')])
        info_url = '/'.join([path, 'info', 'format:json'])
        response = self.get(info_url)
        try:
            num_dims = len(json.loads(response.content).get('sizes'))
        except ValueError:
            raise BQCommError('array could not be read')
        # fill slices with missing dims
        for _ in range(num_dims-len(slice_list)):
            slice_list.append(';')
        data_url = '/'.join([path, ','.join(slice_list), 'format:hdf'])
        response = self.get(data_url)
        # convert HDF5 to Numpy array (preserve indices??)
        with tables.open_file('array.h5', driver="H5FD_CORE", driver_core_image=response.content, driver_core_backing_store=0) as h5file:
            return h5file.root.array.read()

    def store_array(self, array, name):
        """
        Store numpy array in BisQue and return resource doc.
        """
        try:
            dirpath = tempfile.mkdtemp()
            # (1) store array as HDF5 file
            out_file = os.path.join(dirpath, "%s.h5" % name)   # importer needs extension .h5
            with tables.open_file(out_file, "w", filters = tables.Filters(complevel=5)) as h5file:  # compression level 5
                h5file.create_array(h5file.root, name, array)
            # (2) call bisque importer with file
            importer = self.session.service('import')
            response = importer.transfer(out_file)
            # (3) return resource xml
            res = etree.fromstring (response.content)
            if res.tag != 'resource' or res.get('type') != 'uploaded':
                raise BQCommError('array could not be stored')
            else:
                return res[0]
        finally:
            if os.path.isfile(out_file):
                os.remove(out_file)
            os.rmdir(dirpath)


class ImageProxy(BaseServiceProxy):
    def get_thumbnail (self, image_uniq, **kw):
        url = urllib.parse.urljoin( self.session.service_map['image_service'], image_uniq, 'thumbnail' )
        r = self.get(url)
        return r

class ExportProxy(BaseServiceProxy):
    valid_param = set (['files', 'datasets', 'dirs', 'urls', 'users'])
    def fetch_export(self, **kw):
        params = { key:val for key,val in list(kw.items()) if key in self.valid_param and val is not None }
        response = self.fetch ('stream', params = params, stream=kw.pop ('stream', True) )
        return response
    def fetch_export_local(self, localpath, stream=True, **kw):
        response = self.fetch_export (stream=stream, **kw )
        with open(localpath, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        return localpath

SERVICE_PROXIES = {
    'admin' : AdminProxy,
    'auth_service' : AuthProxy,
    'import' : ImportProxy,
    'blob_service': BlobProxy,
    'dataset_service': DatasetProxy,
    'table': TableProxy,
    'image_service' : ImageProxy,
    'export' : ExportProxy,
}

class ServiceFactory (object):
    @classmethod
    def make (cls, session, service_name):
        svc = SERVICE_PROXIES.get (service_name, BaseServiceProxy)
        if service_name in session.service_map:
            return svc (session, service_name )
        return None


def test_module():
    from bqapi import BQSession
    session = BQSession ().init_local ('admin', 'admin', 'http://localhost:8080')
    admin = session.service('admin')
    data = session.service('data_service')
    #admin.user(uniq).login().fetch ()
    xml = data.get ("user", params = {'wpublic':'1', 'resource_name' : 'admin'}, render='xml')
    user_uniq = xml.find ("user").get ('resource_uniq')
    admin.fetch ('/user/{}/login'.format( user_uniq))

if __name__ == "__main__":
    test_module()
