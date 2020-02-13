from sqlalchemy import *
from migrate import *
from sqlalchemy.orm import relation, class_mapper, object_mapper, validates, backref, synonym
from sqlalchemy.orm import scoped_session, sessionmaker, mapper as sa_mapper, make_transient
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
import logging



logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
def session_mapper (scoped_session):
    def mapper (cls, *arg, **kw):
        cls.query = scoped_session.query_property ()
        return sa_mapper (cls, *arg, **kw)
    return mapper
DBSession = scoped_session(maker)
mapper = session_mapper (DBSession)

class Taggable(object):
    def findtag (self, nm, create=False):
        for t in self.tags:
            if t.resource_name == nm:
                return t
        return None
class Value(object):
    pass
class Vertex(object):
    pass
class TaggableAcl(object):
    pass

def maptables(meta):
    taggable = Table('taggable', meta, autoload=True)
    values = Table('values', meta, autoload=True)
    vertices = Table('vertices', meta, autoload=True)
    taggable_acl = Table('taggable_acl', meta, autoload=True)
    mapper( Value, values)
    mapper( Vertex, vertices)
    mapper(TaggableAcl, taggable_acl)
    mapper( Taggable, taggable,
            properties = {
    'tags' : relation(Taggable, lazy=True, viewonly=True, cascade="all, delete-orphan",
                         primaryjoin= and_(taggable.c.resource_parent_id==taggable.c.id,
                                           taggable.c.resource_type == 'tag')),
    'gobjects' : relation(Taggable, lazy=True, viewonly=True, cascade="all, delete-orphan",
                         primaryjoin= and_(taggable.c.resource_parent_id==taggable.c.id,
                                           taggable.c.resource_type == 'gobject')),
    'acl'  : relation(TaggableAcl, lazy=True, cascade="all, delete-orphan",
                      primaryjoin = (TaggableAcl.taggable_id == taggable.c.document_id),
                      foreign_keys=[TaggableAcl.taggable_id],
                      backref = backref('resource', enable_typechecks=False, remote_side=[taggable.c.document_id])),

    'children' : relation(Taggable, lazy=True, cascade="all, delete-orphan",
                          enable_typechecks = False,
                          backref = backref('parent', enable_typechecks=False, remote_side = [ taggable.c.id]),
                          primaryjoin = (taggable.c.id == taggable.c.resource_parent_id)),
    'values' : relation(Value,  lazy=True, cascade="all, delete-orphan",
                        order_by=[values.c.indx],
                        primaryjoin =(taggable.c.id == values.c.resource_parent_id),
                        backref = backref('parent', enable_typechecks = False, remote_side=[taggable.c.id])
                        #foreign_keys=[values.c.parent_id]
                        ),
    'vertices':relation(Vertex, lazy=True, cascade="all, delete-orphan",
                        order_by=[vertices.c.indx],
                        primaryjoin =(taggable.c.id == vertices.c.resource_parent_id),
                        backref = backref('parent', enable_typechecks=False, remote_side=[taggable.c.id]),
                        #foreign_keys=[vertices.c.resource_parent_id]
                        ),

    'tagq' : relation(Taggable, lazy='dynamic',
                      primaryjoin= and_(taggable.c.resource_parent_id==taggable.c.id,
                                        taggable.c.resource_type == 'tag')),


    'docnodes': relation(Taggable, lazy=True,
                         cascade = "all, delete-orphan",
                         enable_typechecks = False,
                         post_update=True,
                         primaryjoin = (taggable.c.id == taggable.c.document_id),
                         backref = backref('document', post_update=True,
                                           enable_typechecks=False, remote_side=[taggable.c.id]),
                         )
    }
        )


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine

    maptables(meta)
    DBSession.configure(bind=migrate_engine)

    print "Mapping dataset members to values"

    for ds in DBSession.query(Taggable).filter(Taggable.resource_type == 'dataset'):
        values = []
        members = ds.findtag('members')
        if members:
            for x in members.values:
                make_transient(x)
                values.append(x)

        ds.values = values
        for x in ds.values:
            DBSession.add(x)

        if ds.resource_user_type == 'datasets':
            ds.resource_user_type  = None
    transaction.commit()
    for ds in DBSession.query(Taggable).filter(Taggable.resource_type == 'dataset'):
        members = ds.findtag('members')
        if members:
            ds.children.remove(members)
            print "removed tags"
    transaction.commit()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pass
