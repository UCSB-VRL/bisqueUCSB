from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData()
    meta.bind = migrate_engine
    taggable = Table('taggable', meta, autoload=True)
    uniq_index = Index('resource_uniq_idx', taggable.c.resource_uniq)
    uniq_index.create()




def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pass
