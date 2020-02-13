"""mex owner index

Revision ID: 156205cd1d39
Revises: 4687c8254c92
Create Date: 2013-03-08 15:48:51.105457

"""

# revision identifiers, used by Alembic.
revision = '156205cd1d39'
down_revision = '4687c8254c92'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index ('mex_idx', 'taggable', [ 'mex_id' ])
    op.create_index ('owner_idx', 'taggable', [ 'owner_id' ])


def downgrade():
    op.drop_index('mex_idx', 'taggable')
    op.drop_index('owner_idx', 'taggable')
