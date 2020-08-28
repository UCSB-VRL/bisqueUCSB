"""indexes 4 deletes

Revision ID: 318381ec60ba
Revises: 2cbd9f4d11af
Create Date: 2018-01-18 10:18:29.846996

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '318381ec60ba'
down_revision = '2cbd9f4d11af'



def upgrade():
    #pylint: disable=no-member
    try:
        op.create_index('ix_taggableacl_taggable_id', 'taggable_acl', [ 'taggable_id'])
    except sa.exc.IntegrityError:
        pass
    try:
        op.create_index('ix_values_valobj', 'values', [ 'valobj'])
    except sa.exc.IntegrityError:
        pass
    try:
        inspector = sa.inspect (op.get_bind().engine )
        for idx in inspector.get_indexes ('taggable') :
            if idx['name'] == 'ix_taggable_resource_value':
                op.drop_index('ix_taggable_resource_value', 'taggable')
                break
        op.create_index('ix_taggable_resource_value', 'taggable', [ 'resource_value' ],
                        postgresql_ops = { 'resource_value': 'text_pattern_ops' } )
    except sa.exc.IntegrityError:
        pass


def downgrade():
    #pylint: disable=no-member
    op.drop_index('ix_taggableacl_taggable_id', 'taggable_acl')
    op.drop_index('ix_values_valobj', 'values')
    op.drop_index('ix_taggable_resource_value', 'taggable')
    op.create_index('ix_taggable_resource_value', 'taggable', [ 'resource_value' ])
