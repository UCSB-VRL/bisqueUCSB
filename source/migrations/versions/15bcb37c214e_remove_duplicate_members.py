"""remove duplicate members

Revision ID: 15bcb37c214e
Revises: 138f50ba7665
Create Date: 2018-07-23 15:46:07.545732

"""

# revision identifiers, used by Alembic.
revision = '15bcb37c214e'
down_revision = '138f50ba7665'

from alembic import op
from alembic import context
import sqlalchemy as sa

from sqlalchemy import Table, MetaData, and_
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.ext.declarative import declarative_base
from bq.util.fakerequestenv import create_fake_env
from orderedset import OrderedSet

def upgrade():

    from bq.data_service.model.tag_model import Taggable, Value

    cntxt = context.get_context()
    SessionMaker = sessionmaker(bind=cntxt.bind)
    session, request = create_fake_env()
    DBSession = SessionMaker(autoflush=False)
    Dataset = aliased(Taggable)
    datasets = DBSession.query(Dataset).filter(Dataset.resource_type == 'dataset')
    for dataset in datasets:
        objs = OrderedSet (  val.valobj for val  in dataset.values )
        if len (objs) != len (dataset.values):
            print "Replacing  ", dataset.resource_uniq
            dataset.values[:] = [ Value (o = obj)  for obj in objs ]
            #dataset.values.reorder()
            DBSession.flush()


def downgrade():
    pass
