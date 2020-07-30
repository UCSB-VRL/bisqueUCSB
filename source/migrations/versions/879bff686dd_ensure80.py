"""ensure80

Revision ID: 879bff686dd
Revises: 306c5eb91bac
Create Date: 2014-03-07 17:05:42.924802

"""

# revision identifiers, used by Alembic.
revision = '879bff686dd'
down_revision = '306c5eb91bac'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Unicode


def upgrade():
    op.alter_column('tg_user', 'password',
                    type_ = Unicode(80))


def downgrade():
    pass
