from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata

    from migration.versions.env002 import metadata, DBSession
    #meta = MetaData()
    metadata.bind = migrate_engine
    DBSession.configure(bind=migrate_engine)
    from migration.versions.model002 import  taggable, values, vertices

    resource_created = Column('created', DateTime(timezone=False))
    resource_uniq = Column('resource_uniq', String(40) ) # will be used for sha1
    resource_parent_id = Column('resource_parent_id', Integer, ForeignKey('taggable.id'))
    resource_index = Column('resource_index', Integer)
    resource_hidden = Column('resource_hidden', Boolean)
    resource_type =  Column('resource_type',Unicode(255))  # will be same as tb_id UniqueName
    resource_name =  Column('resource_name', Unicode (1023) )
    resource_user_type =  Column('resource_user_type', Unicode(1023) )
    resource_value = Column('resource_value', UnicodeText )

    # New columns
    resource_created.create(taggable)
    resource_uniq.create(taggable)
    resource_parent_id.create(taggable)
    resource_index.create(taggable)
    resource_hidden.create(taggable)
    resource_type.create(taggable)
    resource_name.create(taggable)
    resource_user_type.create(taggable)
    resource_value.create(taggable)

    # Adding document_id
    document_id = Column('document_id', Integer, ForeignKey('taggable.id')) # Unique Element
    document_id.create(taggable)
    document_id = Column('document_id', Integer, ForeignKey('taggable.id')) # Unique Element
    document_id.create(values)
    document_id = Column('document_id', Integer, ForeignKey('taggable.id')) # Unique Element
    document_id.create(vertices)



def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pass
