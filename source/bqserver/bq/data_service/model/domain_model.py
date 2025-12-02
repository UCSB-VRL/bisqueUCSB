###############################################################################
# Authored by Wahid Sadique Koly at 2025-09-21
# These models and code are created for managing authorized email domains for user registration.
# The code is inspired by BisQue's user management models and follows its classical SQLAlchemy pattern.
# The code includes functions for adding, deleting, and checking authorized domains.
# The database migration script to create the necessary table is also provided.
# The models are designed to work seamlessly with BisQue's existing infrastructure.
###############################################################################
"""
Domain management models for BisQue

DESCRIPTION
===========

Models for managing authorized email domains using BisQue's classical SQLAlchemy pattern.
"""

import logging
from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, Text, Boolean, DateTime
from bq.core.model import mapper, metadata, DBSession

log = logging.getLogger("bq.domain_model")

# Only define the table if it doesn't already exist
if 'authorized_email_domains' not in metadata.tables:
    authorized_email_domains = Table('authorized_email_domains', metadata,
        Column('id', Integer, primary_key=True),
        Column('domain', String(255), unique=True, nullable=False, index=True),
        Column('description', Text),
        Column('is_active', Boolean, default=True, nullable=False),
        Column('created_date', DateTime, nullable=False),
    )
else:
    authorized_email_domains = metadata.tables['authorized_email_domains']

class AuthorizedEmailDomain(object):
    """Model for authorized email domains"""
    
    def __init__(self, domain=None, description=None, is_active=True):
        self.domain = domain.lower().strip() if domain else None
        self.description = description
        self.is_active = is_active
        self.created_date = datetime.utcnow()
    
    def __repr__(self):
        return f"<AuthorizedEmailDomain(id={getattr(self, 'id', None)}, domain='{self.domain}', active={self.is_active})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': getattr(self, 'id', None),
            'domain': self.domain,
            'description': self.description,
            'is_active': self.is_active,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

# Use BisQue's mapper from bq.core.model
mapper(AuthorizedEmailDomain, authorized_email_domains)

# Helper functions for database operations
def get_authorized_domains():
    """Get all authorized domains from database"""
    try:
        session = DBSession()
        domains = session.query(AuthorizedEmailDomain).order_by(AuthorizedEmailDomain.domain).all()
        return domains
    except Exception as e:
        log.error(f"Error getting authorized domains: {e}")
        return []

def add_authorized_domain(domain, description=None):
    """Add a new authorized domain"""
    try:
        session = DBSession()
        
        # Check if domain already exists
        existing = session.query(AuthorizedEmailDomain).filter_by(domain=domain.lower().strip()).first()
        if existing:
            log.warning(f"Domain {domain} already exists")
            return existing  # Return existing domain instead of False
            
        # Create new domain
        new_domain = AuthorizedEmailDomain(domain=domain, description=description)
        session.add(new_domain)
        session.flush()  # Get the ID but let transaction manager handle commit
        log.info(f"Added domain: {domain}")
        return new_domain
    except Exception as e:
        log.error(f"Error adding domain {domain}: {e}")
        # Don't rollback - let transaction manager handle it
        return None

def delete_authorized_domain(domain_id):
    """Delete an authorized domain"""
    try:
        session = DBSession()
        domain = session.query(AuthorizedEmailDomain).filter_by(id=domain_id).first()
        if domain:
            session.delete(domain)
            session.flush()  # Let transaction manager handle commit
            log.info(f"Deleted domain: {domain.domain}")
            return True
        else:
            log.warning(f"Domain with ID {domain_id} not found")
            return False
    except Exception as e:
        log.error(f"Error deleting domain {domain_id}: {e}")
        # Don't rollback - let transaction manager handle it
        return False

def is_domain_authorized(email):
    """Check if an email domain is authorized"""
    try:
        if not email or '@' not in email:
            return False
            
        domain = email.split('@')[1].lower()
        session = DBSession()
        authorized_domain = session.query(AuthorizedEmailDomain).filter_by(
            domain=domain, 
            is_active=True
        ).first()
        
        return authorized_domain is not None
        
    except Exception as e:
        log.error(f"Error checking domain authorization for {email}: {e}")
        return False  # Default to deny if error