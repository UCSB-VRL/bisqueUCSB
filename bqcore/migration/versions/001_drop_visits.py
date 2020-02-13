import sqlalchemy as sa
from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    meta = MetaData()
    meta.bind = migrate_engine


    tables = ('visits', 'visit_identity', 'visit_statistics')
    for name in tables:
        try:
            table = Table(name, meta, autoload=True)
            table.drop()
        except sa.exc.NoSuchTableError:
            pass

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pass
