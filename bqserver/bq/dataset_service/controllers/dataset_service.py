import os
import logging
import pkg_resources
from lxml import etree
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, flash, require, request
from repoze.what import predicates
from bq.core.service import ServiceController
from bq.dataset_service import model


from bq import data_service
from bq import module_service
from bq.data_service.controllers.resource_auth import  append_share_handler


log = logging.getLogger('bq.dataset')


class DatasetOp(object):
    def __init__(self, duri, dataset, members):
        self.duri = duri
        self.dataset = dataset
        self.members = members

    def __call__(self, **kw):
        return self.action(**kw)

    def action(self, member, **kw):
        'Null Op'
        return None


class IdemOp(DatasetOp):
    'An idempotent operation'
    def action(self, member, **kw):
        'return the members'
        log.debug ('idem action %s' % member.text)
        return member

# Not the correct way to run a module on dataset.
#class ModuleOp(DatasetOp):
#    'Run a module on each member'
#    def action(self, member, module, **kw):
#        log.debug ('module action %s' % member)
#        member = member.text
#        mex = module_service.execute (module_uri = module,
#                                image_url = member,
#                                **kw)
#        return mex

class PermissionOp(DatasetOp):
    'change permission on member'
    def action(self, member, permission):
        member = member.text
        log.debug('permission action %s' % member)
        resource = data_service.get_resource(member, view='short')
        log.debug('GOT %s' % etree.tostring (resource))
        resource.set('permission',  permission)
        data_service.update(resource)
        return None

class DeleteOp(DatasetOp):
    'Delete each member'
    def action(self, member, **kw):
        log.debug ('Delete action %s' % member)
        data_service.del_resource (member.text)
        return None

class TagEditOp (DatasetOp):
    'Add/Remove/Modify Tags on each member'
    def action(self, member, action, tagdoc, **kw):
        """Modify the tags of the member
        @param member: the memeber of the dataset
        @param action: a string :append, delete, edit_value, edit_name, change_name
        @poarag tagdoc
        """
        member = member.text
        if isinstance(tagdoc, basestring):
            tagdoc = etree.XML(tagdoc)

        log.debug ('TagEdit (%s) %s with %s' % (action, member, etree.tostring(tagdoc)))
        # These update operation should be done in the database
        # However, I don't want to think about it now
        # so here's the brute-force way
        if action=="append":
            resource = data_service.get_resource(member, view='short')
            resource.append(tagdoc)
            data_service.update(resource)
        elif action=='delete':
            resource = data_service.get_resource(member, view='full')
            for tag in tagdoc.xpath('./tag'):
                resource_tags = resource.xpath('./tag[@name="%s"]' % tag.get('name'))
                for killtag in resource_tags:
                    data_service.del_resource(killtag.get('uri'))
        elif action=='edit_value':
            resource = data_service.get_resource(member, view='full')
            for tag in tagdoc.xpath('./tag'):
                resource_tags = resource.xpath('./tag[@name="%s"]' % tag.get('name'))
                for mtag in resource_tags:
                    mtag.set('value', tag.get('value'))
            data_service.update(resource)
        elif action=='edit_name':
            resource = data_service.get_resource(member, view='full')
            for tag in tagdoc.xpath('./tag'):
                resource_tags = resource.xpath('./tag[@value="%s"]' % tag.get('value'))
                for mtag in resource_tags:
                    mtag.set('name', tag.get('name'))
            data_service.update(resource)
        elif action=='change_name':
            resource = data_service.get_resource(member, view='full')
            for tag in tagdoc.xpath('./tag'):
                resource_tags = resource.xpath('./tag[@name="%s"]' % tag.get('name'))
                for mtag in resource_tags:
                    mtag.set('name', tag.get('value'))
            data_service.update(resource)

        return None

class ShareOp (DatasetOp):
    'Apply sharing options to  each member'
    def action(self, member, auth, action, last=False, **kw):
        member = member.text
        data_service.auth_resource(member,  auth=auth, invalidate=last, action=action)
        return None

def dataset_share_handler (resource_uniq, user_uniq, auth, action):
    """Apply share to all members

    resource dataset
    auth   xml auth record
    acl    acl of dataset
    """
    dataset = data_service.resource_load (uniq = resource_uniq, view='full')
    iterate(dataset=dataset, operation='share', auth=auth, action=action, last=True)


append_share_handler ('dataset', dataset_share_handler)




#---------------------------------------------------------------------------------------
# controller
#---------------------------------------------------------------------------------------


def iterate(duri=None, operation='idem', dataset=None, members = None, last= False, **kw):
    """Iterate over a dataset executing an operation on each member

    @param  duri: dataset uri
    @param operation: an operation name (i.e. module, permisssion)
    @param kw : operation parameters by name
    """

    log.info('iterate op %s on  %s' , operation, duri or dataset.get('uri'))
    if dataset is None:
        dataset = data_service.get_resource(duri, view='full')
    if members is None:
        members = dataset.xpath('/dataset/value')

    op_klass  = DatasetServer.operations.get(operation, IdemOp)
    op = op_klass(duri, dataset=dataset, members = members)

    #mex = module_service.begin_internal_mex ("dataset_iterate")

    log.debug ("%s on  members %s" , str( op ),  [ x.text for x in members ] )
    results = etree.Element('resource', uri=request.url)
    if last:
        last_member = members[-1]
        members = members[:-1]

    for val in members:
        result =  op(member = val, **kw)
        log.debug ("%s on %s -> %s" , operation, val.text, result )
        if result is not None:
            results.append (result)

    if last:
        result =  op(member = last_member, last = True, **kw)
        log.debug ("%s on %s -> %s" , operation, last_member.text, result )
        if result is not None:
            results.append (result)

    return etree.tostring(results)



class DatasetServer(ServiceController):
    """Server side actions on datasets
    """
    service_type = "dataset_service"

    operations = {
        'idem' : IdemOp,
#        'module' : ModuleOp,
        'permission' : PermissionOp,
        'delete' : DeleteOp,
        'tagedit' : TagEditOp,
        'share' : ShareOp,
        }

    def __init__(self, server_url):
        super(DatasetServer, self).__init__(server_url)

    def iterate(self, duri=None, operation='idem', dataset=None, members = None, last= False, **kw):
        return iterate(duri,operation,dataset, members, last, **kw)

    #############################################
    # visible
    @expose('bq.dataset_service.templates.datasets')
    @require(predicates.not_anonymous())
    def index(self, **kw):
        'list operations of dataset service'
        return dict(operations = self.operations, )

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def add_query(self, duri, resource_tag, tag_query, **kw):
        """Append query results to a dataset

        @param duri: dataset uri of an existing dataset
        @param resource_tag:resource type tag i.e. images
        @param tag_query:  expression of tag search
        """
        log.info ("dataset: addquery members of %s tag %s query %s " , duri, resource_tag, tag_query)

        dataset = data_service.get_resource(duri, view='deep')
        members = dataset.xpath('./value')
        for n, val in enumerate(members):
            val.set('index', str(n))

        items = data_service.query (resource_tag, tag_query=tag_query, **kw)
        count = len(members)
        for resource in items:
            # check  if already there:
            found = dataset.xpath('./value[text()="%s"]' % resource.get('uri'))
            if len(found) == 0:
                val = etree.SubElement(dataset, 'value', type='object', index = str(count))
                val.text =resource.get('uri')
                count += 1


        log.debug ("members = %s" % etree.tostring (dataset))
        r = data_service.update(dataset)
        return etree.tostring(r)

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def delete(self, duri, **kw):
        # remove all member
        log.info ("dataset: delete members of %s to " , duri)
        dataset = data_service.get_resource(duri, view='full')
        members = dataset.xpath('./value')
        data_service.del_resource(dataset)
        return self.iterate (operation='delete', dataset=dataset, members=members, **kw)

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def permission(self, duri, **kw):
        log.info ("dataset: permission members of %s to %s" , duri, kw.get ('permission'))
        ds = etree.Element ('dataset', uri = duri, permission= kw["permission"])
        data_service.update(ds)
        return self.iterate(duri, operation='permission', **kw)

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def tagedit(self, duri, **kw):
        return self.iterate(duri, operation='tagedit', **kw)

    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
    def share(self, duri, **kw):
        'Apply share settings of dataset to all members'

        #dataset_auth = data_service.auth_resource(duri)
        #log.info ("dataset: auth setting members of %s to %s" , duri, etree.tostring(dataset_auth))
        #values =  self.iterate(duri, operation='share', auth=dataset_auth, last=True, **kw)
        #return values
        return "<resource/>"




#---------------------------------------------------------------------------------------
# bisque init stuff
#---------------------------------------------------------------------------------------

def initialize(uri):
    """ Initialize the top level server for this microapp"""
    # Add you checks and database initialize
    log.debug ("initialize " + uri)
    service =  DatasetServer(uri)
    return service

def get_static_dirs():
    """Return the static directories for this server"""
    package = pkg_resources.Requirement.parse ("bqserver")
    package_path = pkg_resources.resource_filename(package,'bq')
    return [(package_path, os.path.join(package_path, 'dataset_service', 'public'))]

__controller__ =  DatasetServer
