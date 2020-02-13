"""preference

Revision ID: 9c13d7f2587
Revises: 14bcc365e5d6
Create Date: 2015-05-06 12:12:16.043409

"""

# revision identifiers, used by Alembic.
revision = '9c13d7f2587'
down_revision = '14bcc365e5d6'

from alembic import op
from alembic import context
import sqlalchemy as sa

from sqlalchemy import Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def upgrade():
    cntxt = context.get_context()
    SessionMaker = sessionmaker(bind=cntxt.bind)

    Base = declarative_base()
    metadata = MetaData(bind=cntxt.bind)
    class Taggable(Base):
        __table__ = Table('taggable', metadata, autoload=True)

    DBSession = SessionMaker()
    prefs = DBSession.query(Taggable).filter_by(resource_name = 'Preferences', resource_type='tag')
    for resource in prefs:
        resource.resource_type = 'preference'
        print "updating %s -> %s" % (resource.id, resource.resource_uniq)
    DBSession.commit()
    DBSession.close()


def downgrade():
    pass
