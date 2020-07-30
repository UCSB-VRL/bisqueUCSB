"""index_ts

Revision ID: 2f38b45d9ba5
Revises: 49f2fd567fb7
Create Date: 2016-11-30 15:54:58.084655

"""

# revision identifiers, used by Alembic.
revision = '2f38b45d9ba5'
down_revision = '49f2fd567fb7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index ('ix_taggable_ts', 'taggable', [ 'ts' ])


def downgrade():
    op.drop_index('ix_taggable_ts', 'taggable')
