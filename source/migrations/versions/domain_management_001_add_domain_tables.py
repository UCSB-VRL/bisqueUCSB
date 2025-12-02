"""add domain management tables

Revision ID: domain_management_001
Revises: 15bcb37c214e  
Create Date: 2025-09-18 14:30:00.000000

"""

# revision identifiers, used by Alembic.
revision = 'domain_management_001'
down_revision = '15bcb37c214e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import String, Text, Boolean, DateTime, Integer


def upgrade():
    # Create authorized_email_domains table
    op.create_table(
        'authorized_email_domains',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('domain', String(255), unique=True, nullable=False, index=True),
        sa.Column('description', Text),
        sa.Column('is_active', Boolean, default=True, nullable=False),
        sa.Column('created_date', DateTime, nullable=False),
    )

    # Create index for better performance
    op.create_index('ix_authorized_domains_domain', 'authorized_email_domains', ['domain'])


def downgrade():
    # Drop table and index
    op.drop_index('ix_authorized_domains_domain', 'authorized_email_domains')
    op.drop_table('authorized_email_domains')