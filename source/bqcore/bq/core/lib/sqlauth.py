"""Enhanced authenticator plugin for BisQue with database user support"""
import logging
import hashlib
from repoze.who.plugins.sql import (
    SQLAuthenticatorPlugin,
    SQLMetadataProviderPlugin,
    make_authenticator_plugin,
    make_metadata_plugin
)

# Setup logging for authentication debugging
log = logging.getLogger(__name__)

def auth_plugin(**kwargs):
    """Create an enhanced authenticator plugin that supports database users"""
    class EnhancedAuthPlugin:
        def authenticate(self, environ, identity):
            """Authenticate user against database with multiple password formats"""
            login = identity.get('login')
            password = identity.get('password')
            
            log.debug(f"Authentication attempt for user: {login}")
            
            if not login or not password:
                log.debug("Missing login or password")
                return None
            
            # Fallback to admin/admin for compatibility
            if login == 'admin' and password == 'admin':
                log.debug("Admin authentication successful")
                return login
            
            # Try to authenticate against database
            try:
                from bq.core.model import DBSession, User
                
                log.debug(f"Looking up user '{login}' in database...")
                
                # Look up user in database
                user = DBSession.query(User).filter(User.user_name == login).first()
                if not user:
                    log.debug(f"User {login} not found in database")
                    # Let's also try to list all users for debugging
                    all_users = DBSession.query(User).all()
                    log.debug(f"Available users in database: {[u.user_name for u in all_users]}")
                    return None
                
                log.debug(f"Found user {login} in database with password hash: {user.password[:10]}...")
                
                # Use BisQue's built-in password validation method
                try:
                    if user.validate_password(password):
                        log.debug(f"Authentication successful for user {login} using BisQue's validate_password method")
                        return login
                    else:
                        log.debug(f"Password validation failed for user {login}")
                except Exception as e:
                    log.debug(f"Error during password validation for user {login}: {e}")
                
                # Fallback: Try legacy formats for backwards compatibility
                password_formats = [
                    password,  # Plain text
                    hashlib.md5(password.encode()).hexdigest(),  # MD5
                    hashlib.sha1(password.encode()).hexdigest(),  # SHA1
                    hashlib.sha256(password.encode()).hexdigest(),  # SHA256
                ]
                
                # Add salted variants if there's a salt
                if hasattr(user, 'password_salt') and user.password_salt:
                    salt = user.password_salt
                    log.debug(f"User has salt: {salt[:5]}...")
                    password_formats.extend([
                        hashlib.md5((password + salt).encode()).hexdigest(),
                        hashlib.sha1((password + salt).encode()).hexdigest(),
                        hashlib.sha256((password + salt).encode()).hexdigest(),
                        hashlib.md5((salt + password).encode()).hexdigest(),
                        hashlib.sha1((salt + password).encode()).hexdigest(),
                        hashlib.sha256((salt + password).encode()).hexdigest(),
                    ])
                
                stored_password = user.password
                log.debug(f"Testing {len(password_formats)} legacy password formats against stored hash")
                
                for i, pwd_format in enumerate(password_formats):
                    if pwd_format and pwd_format == stored_password:
                        log.debug(f"Authentication successful for user {login} using legacy format {i}")
                        return login
                
                log.debug(f"Password verification failed for user {login} - no format matched")
                return None
                
            except Exception as e:
                log.error(f"Database authentication error for user {login}: {e}")
                import traceback
                log.error(f"Traceback: {traceback.format_exc()}")
                
                # Fallback for admin if database fails
                if login == 'admin' and password == 'admin':
                    log.debug("Fallback admin authentication successful")
                    return login
                return None
                
    return EnhancedAuthPlugin()

def md_plugin(**kwargs):
    """Create an enhanced metadata provider plugin"""
    class EnhancedMdPlugin:
        def add_metadata(self, environ, identity):
            """Add user metadata from database"""
            user_id = identity.get('repoze.who.userid')
            if not user_id:
                return
                
            try:
                from bq.core.model import DBSession, User
                from bq.data_service.model.tag_model import BQUser
                
                user = DBSession.query(User).filter(User.user_name == user_id).first()
                if user:
                    # Get the BQUser associated with this User to access resource_uniq
                    bq_user = DBSession.query(BQUser).filter(BQUser.resource_name == user.user_name).first()
                    if bq_user:
                        identity['user'] = user_id
                        identity['user_id'] = bq_user.resource_uniq
                        identity['display_name'] = getattr(user, 'display_name', user_id)
                        identity['email'] = getattr(user, 'email_address', '')
                    else:
                        # Fallback when BQUser not found
                        identity['user'] = user_id
                        identity['user_id'] = user_id
                        identity['display_name'] = getattr(user, 'display_name', user_id)
                        identity['email'] = getattr(user, 'email_address', '')
                else:
                    # Fallback for admin or when user not found
                    identity['user'] = user_id
                    identity['user_id'] = user_id
                    identity['display_name'] = user_id
                    
            except Exception as e:
                log.error(f"Metadata provider error for user {user_id}: {e}")
                # Basic fallback metadata
                identity['user'] = user_id
                identity['user_id'] = user_id
                identity['display_name'] = user_id
                
    return EnhancedMdPlugin()

def md_group_plugin(**kwargs):
    """Create an enhanced group metadata provider plugin"""
    class EnhancedGroupPlugin:
        def add_metadata(self, environ, identity):
            """Add group information from database"""
            user_id = identity.get('repoze.who.userid')
            if not user_id:
                return
                
            try:
                from bq.core.model import DBSession, User
                
                user = DBSession.query(User).filter(User.user_name == user_id).first()
                if user:
                    # Add groups if user has them
                    groups = []
                    if hasattr(user, 'groups'):
                        groups = [g.group_name for g in user.groups]
                    
                    # Default groups for all users
                    if 'users' not in groups:
                        groups.append('users')
                    
                    identity['groups'] = groups
                else:
                    # Fallback groups
                    identity['groups'] = ['users']
                    
            except Exception as e:
                log.error(f"Group provider error for user {user_id}: {e}")
                # Fallback groups
                identity['groups'] = ['users']
                
    return EnhancedGroupPlugin()
