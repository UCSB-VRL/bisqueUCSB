"""hidden preferences in images

Revision ID: 2cbd9f4d11af
Revises: 1653e79bb48b
Create Date: 2017-10-17 14:51:22.747207

"""

# revision identifiers, used by Alembic.
revision = '2cbd9f4d11af'
down_revision = '1653e79bb48b'

from alembic import op
import sqlalchemy as sa


from alembic import op
from alembic import context
import sqlalchemy as sa

from sqlalchemy import Table, MetaData, and_
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.ext.declarative import declarative_base

from bq.util.fakerequestenv import create_fake_env

def upgrade():

    from bq.data_service.model.tag_model import Taggable

    cntxt = context.get_context()
    SessionMaker = sessionmaker(bind=cntxt.bind)
    session, request = create_fake_env()

    DBSession = SessionMaker()
    Pref = aliased(Taggable)
    prefs = DBSession.query(Pref).filter(
        and_(Pref.resource_type=='preference',
             Taggable.resource_type=='image',
             Pref.resource_parent_id == Taggable.id)
    )
    for pref in prefs:
        pref.hidden = True
        print "updating %s "   % (pref.uri)
    DBSession.commit()
    DBSession.close()



def downgrade():
    pass
