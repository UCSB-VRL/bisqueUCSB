"""user_unid

Revision ID: 265a09af6b4f
Revises: 40992cd9aa78
Create Date: 2014-04-25 12:04:16.481357

"""

# revision identifiers, used by Alembic.
revision = '265a09af6b4f'
down_revision = '879bff686dd'

import sqlalchemy as sa
from alembic import op, context
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, UnicodeText
from bq.data_service.model.tag_model import Taggable
from bq.core.identity import set_current_user
from bq.util.fakerequestenv import create_fake_env

def upgrade():
    op.add_column('taggable', Column('resource_unid', UnicodeText))
    op.create_index('idx_taggable_unid', 'taggable',
                    ['owner_id', 'resource_parent_id', 'resource_unid'],
                    unique=True, mysql_length = {'resource_unid' : 255})

    from bq.data_service.model.tag_model import Taggable, ModuleExecution

    cntxt = context.get_context()
    SessionMaker = sessionmaker(bind=cntxt.bind)
    DBSession = SessionMaker()

    session, request = create_fake_env()

    initial_mex = DBSession.query(ModuleExecution).filter_by(resource_name='initialization').first()
    if initial_mex is None:
        initial_mex = ModuleExecution(owner_id = False, mex_id = False)
        initial_mex.mex = initial_mex
        initial_mex.name = "initialization"
        initial_mex.type = "initialization"
        initial_mex.hidden = True
        DBSession.add(initial_mex)
        DBSession.flush()
    request.identity['bisque.mex_id'] = initial_mex.id

    users = DBSession.query(Taggable).filter_by(resource_parent_id = None, resource_type='user')
    for user in users:
        #set_current_user (user.resource_name)
        root_store  = Taggable(resource_type = 'store', owner_id = user.id, mex_id = initial_mex.id)
        root_store.resource_name = '(root)'
        root_store.resource_unid = '(root)'

        DBSession.add(root_store)
    DBSession.flush()


def downgrade():

    from bq.data_service.model.tag_model import Taggable

    cntxt = context.get_context()
    SessionMaker = sessionmaker(bind=cntxt.bind)
    DBSession = SessionMaker()

    stores = DBSession.query(Taggable).filter_by(resource_parent_id = None, resource_type='store', resource_name="(root)")
    for store in stores:
        DBSession.delete(store)
    DBSession.flush()


    #op.drop_constraint('uq_user_unid', 'taggable')
    op.drop_index('idx_taggable_unid', 'taggable')
    op.drop_column('taggable', 'resource_unid')
