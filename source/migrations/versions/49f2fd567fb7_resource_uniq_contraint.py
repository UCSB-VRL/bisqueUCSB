"""resource uniq contraint

Revision ID: 49f2fd567fb7
Revises: 9c13d7f2587
Create Date: 2016-03-08 13:26:00.807476

"""

# revision identifiers, used by Alembic.
revision = '49f2fd567fb7'
down_revision = '9c13d7f2587'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint("cnst_resource_uniq", "taggable", ["resource_uniq"])


def downgrade():
    op.create_unique_constraint("cnst_resource_uniq", "taggable")
