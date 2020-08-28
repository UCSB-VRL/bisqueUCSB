"""init_stores

Revision ID: 33b00e22cb16
Revises: 265a09af6b4f
Create Date: 2014-09-26 10:36:00.985512
"""
#36b17eaadc9a
# revision identifiers, used by Alembic.
revision = '33b00e22cb16'
down_revision = '265a09af6b4f'

from alembic import op
import sqlalchemy as sa
import subprocess

def upgrade():

    print "initializing authenticated stores"
    r = subprocess.call (['bq-admin', 'stores', 'init'])
    if r!=0:
        print "encountered an error during store initialization"


def downgrade():
    pass
