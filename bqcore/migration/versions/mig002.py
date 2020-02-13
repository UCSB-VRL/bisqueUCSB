#!/usr/bin/env python
"""
Resource rationalization script

Move data from  bisque04 database to bisque05 style
"""


import sys
from sqlalchemy import *
from sqlalchemy.sql import *

import transaction
import os
import logging

import bq
from bq.util.hash import make_uniq_hash

from migration.versions.env002 import *
## Build database connection BEFORE model002 import
if __name__ == '__main__':
    if len(sys.argv)>1:
        url = sys.argv[1]
        print "using %s" % url
        engine = create_engine(url, echo = False)
        metadata.bind = engine
        DBSession.configure(bind=engine)
        print "attached to", engine
##
from migration.versions.model002 import *


def new_tag(r, name, val, ty_=None):
    t= Taggable('tag')
    t.table = 'tag'
    t.mex = r.mex
    t.owner_id = r.owner_id
    t.resource_name = name
    t.resource_value = val
    t.resouce_user_type = ty_
    t.document  = r.document
    r.children.append(t)
    return t

def move_files_to_resources():
    print "MOVING FILE TABLE TO RESOURCE"
    DBSession.autoflush = False
    for count, fi in enumerate(DBSession.query(FileEntry)):
        image = DBSession.query (Image).filter_by(src = fi.uri).first()
        hash_id = make_uniq_hash(fi.original or '', fi.ts)
        if image is None:
            print "processing file", fi.local
            #resource = DBSession.query(Taggable).filter_by(resource_uniq = fi.sha1).first()
            #if resource is None:
            owner = DBSession.query(BQUser).filter_by(user_name = fi.owner).first()
            resource = Taggable(resource_type='file')
            resource.perm = fi.perm
            resource.resource_type = 'file'
            resource.ts = fi.ts
            resource.table = 'file'
            resource.document = resource
            if owner:
                resource.owner_id = owner.id
            else:
                print "file with no owner"
                resource.owner_id = 1
            DBSession.add(resource)
        else:
            resource = image
            print "processing image", fi.local
            #image.src = "/image_service/images/%s" % hash_id
            resource.resource_type   = 'image'

        resource.resource_name   = fi.original
        resource.resource_uniq   = hash_id
        resource.resource_value  = fi.local
        new_tag(resource, 'sha1', fi.sha1).resource_hidden=True
        if count % 1024 == 0:
            DBSession.flush()

    transaction.commit()

def nunicode (v):
    #return v is not None and unicode(v)
    return (v is not None and unicode(v)) or None

def move_all_to_resource():
    print "MOVING Images, etc to RESOURCE"
    alltypes_ =  [ Taggable, Image, Tag, GObject, Dataset, Module, ModuleExecution, Service,
                   Template, BQUser ]

    def map_(r, ty):
        r.resource_type = ty.xmltag
        r.resource_name = nunicode(getattr(r, 'name', None))
        r.resource_user_type = nunicode(getattr(r, 'type', None))
        if r.resource_type == 'tag' and r.resource_user_type=='tag':
            r.resource_user_type = None
        r.resource_parent_id = getattr(r, 'parent_id', None)

    for ty_ in [ Tag, GObject, Dataset,  Template,  ]:
        print "processing ", ty_.xmltag
        for r in DBSession.query (ty_):
            map_(r, ty_)
        DBSession.flush()

    # Special type here
    print "processing ", BQUser.xmltag
    for r in DBSession.query(BQUser):
        #map_(r, BQUser)
        r.resource_type = u'user'
        r.resource_name = nunicode(r.user_name)
        r.resource_value = nunicode(r.email_address)
        new_tag(r, 'display_name', r.display_name)
    DBSession.flush()

    print "processing ", Module.xmltag
    for r in DBSession.query(Module):
        #map_(r, Module)
        r.resource_type = u'module'
        r.resource_name  = nunicode(r.name)
        r.resource_user_type = nunicode(r.type)
        r.resource_value = nunicode(r.codeurl)
    DBSession.flush()

    print "processing ", ModuleExecution.xmltag
    for r in DBSession.query(ModuleExecution):
        #map_(r, ModuleExecution)
        r.resource_type = u'mex'
        r.resource_name = nunicode(r.module)
        r.resource_value = nunicode(r.status)
    DBSession.flush()

    # Don't bother as they must reregister
    print "processing ", Service.xmltag
    for r in DBSession.query(Service):
        DBSession.delete(r)
    #    #map_(r, Service)
    #    r.resource_name = r.type
    #    r.resource_user_type = u'app'
    #    r.resource_value = r.uri

    print "processing ", Image.xmltag
    for r in DBSession.query(Image):
        #r.resource_type = u'image'
        #map_(r, Image)
        new_tag(r, 'geometry',
                "%s,%s,%s,%s,%s" % (r.x or '', r.y or '',r.z or '',r.t or '',r.ch or '')
                ).resource_hidden = True

    transaction.commit()


def move_values():
    print "ADDING DOCUMENT POINTERS TO VALUES"
    print "processing values:", Tag.xmltag
    for count, r in enumerate(DBSession.query(Tag)):
        for v in r.values:
            v.document_id = r.document_id
        if len(r.values) == 1:
            v = r.values[0]
            if v.valstr is not None:
                r.resource_value = unicode(v.valstr)
            elif v.valnum is not None:
                r.resource_value = v.valnum
                r.resource_user_type = 'numeric'
            elif v.valobj is not None:
                r.resource_value = v.objref.uri
                r.resource_user_type = 'resource'

            #DBSession.delete (r.values[0])
        if count % 1024 == 0:
            DBSession.flush()

    transaction.commit()

    for r in DBSession.query(GObject):
        for v in r.vertices:
            v.document_id = r.document_id
    #print "processing ", GObject.xmltag
    #for r in DBSession.query(GObject):
    #    if len(r.vertices) == 1:
    #        v = r.vertices[0]
    #        v = "%s,%s,%s,%s,%s" % (v.x or '', v.y or '',v.z or '',v.t or '',v.ch or '')
    #        r.resource_value = v
            #DBSession.delete (r.vertices[0])
        #else:
        #    x=';'.join(["%s,%s,%s,%s,%s" % (v.x or '', v.y or '',v.z or '',v.t or '',v.ch or '')
        #                for v in r.vertices])
        #    r.resource_value = x


    transaction.commit()


def apply_to_all(resource, parent_id, document_id):
    resource.document_id = document_id
    resource.resource_parent_id = parent_id
    #fn (resource, parent, document)
    #for kid in resource.children:
    #    apply_to_all(kid, resource, document)
    for tag in resource.tags:
        apply_to_all(tag, resource.id, document_id)
    for gob in resource.gobjects:
        apply_to_all(gob, resource.id,  document_id)

def build_document_pointers():
    """Visit all top level resource and apply a document_id (root) to
    all children: tags and gobjects
    """
    DBSession.autoflush = False
    types_ =  [ Image, Dataset, Module, ModuleExecution, Service, Template, BQUser ]
    print "ADDING DOCUMENT POINTERS"
    visited = {}
    for ty_ in types_:
        print "processing %s" % ty_.xmltag
        for count, resource in  enumerate(DBSession.query(ty_)):
            print >>sys.stderr, "doc %s(%s) %s" % (resource.table, count, resource.id )
            resource.resource_type = unicode(resource.xmltag)

            #if resource.id in visited:
            #    print "VISTED %s before when visiting %s" % (resource, visited[resource.id][1])
            #else:
            #    visited[resource.id] = (resource, ty_)

            # Given a top level resource create a document
            #document = Document()
            #document.uniq = resource.resource_uniq
            #document.owner_id = resource.owner_id
            #document.perm     =  resource.perm
            apply_to_all(resource , parent_id=None, document_id=resource.id)
            DBSession.flush()
    transaction.commit()

    # Taggable
    user_types = [ (nm, ty) for nm, ty in [ dbtype_from_name(str(y)) for y in all_resources() ]
                    if ty == Taggable ]
    for table, ty_ in user_types:
        print "processing %s" % table
        for resource in  DBSession.query(ty_).filter(ty_.tb_id == UniqueName(table).id):
            print "doc %s %s" % (resource.table, resource.id)

            #if resource.id in visited:
            #    print "VISTED %s before when visiting %s" % (resource, visited[resource.id][1])
            #else:
            #    visited[resource.id] = ( resource, ty_)

            resource.resource_type = table
            apply_to_all(resource , parent_id=None, document_id=resource.id)

    transaction.commit()


def main():
    try:
        build_document_pointers()
        move_all_to_resource()
        move_values()
        move_files_to_resources()
    except Exception, e:
        logging.exception("")
        raise e


if __name__ == '__main__':
    main()
