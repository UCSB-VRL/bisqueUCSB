"""setup ordering

Revision ID: 1653e79bb48b
Revises: 2f38b45d9ba5
Create Date: 2017-06-30 15:29:07.484740

"""

# revision identifiers, used by Alembic.

import sys
from alembic import context

from sqlalchemy import Table, MetaData, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

revision = '1653e79bb48b'
down_revision = '2f38b45d9ba5'

def upgrade():
    cntxt = context.get_context()
    SessionMaker = sessionmaker(bind=cntxt.bind)

    Base = declarative_base()
    metadata = MetaData(bind=cntxt.bind)
    class Taggable(Base):
        __table__ = Table('taggable', metadata, autoload=True)

    DBSession = SessionMaker()
    converted_docs = 0
    commits = 0
    for rv in DBSession.query(Taggable).filter(Taggable.resource_uniq != None).yield_per(10000):

        current_parent = -1
        converted_docs += 1
        for tv in DBSession.query(Taggable).\
            filter(and_(Taggable.document_id == rv.document_id, Taggable.resource_parent_id != None)).\
            order_by(Taggable.resource_parent_id, Taggable.id):
            if current_parent != tv.resource_parent_id:
                count = 0
                current_parent = tv.resource_parent_id
            if tv.resource_index is None:
                tv.resource_index = count
            count+=1

        if converted_docs % 1024 ==0:
            DBSession.commit ()
            commits += 1
            print >>sys.stderr, ".",
            if commits % 10 :
                print >> sys.stderr

    DBSession.commit ()
    DBSession.close()




def downgrade():
    pass
