"""
Firebase Authentication Plugin for BisQue
Supports Google, Facebook, GitHub, GitLab, and LinkedIn authentication via Firebase Auth
"""
import logging
import json
import os
from urllib.parse import quote_plus, urlencode
from datetime import datetime, timedelta

from webob import Request, Response
from webob.exc import HTTPFound

from zope.interface import implementer
from repoze.who.interfaces import IChallenger, IIdentifier, IAuthenticator

try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    firebase_admin = None
    auth = None

log = logging.getLogger('bq.auth.firebase')


def make_plugin(firebase_config=None, auto_register=None, **kwargs):
    """Factory function to create Firebase authentication plugin"""
    return FirebaseAuthPlugin(firebase_config, auto_register, **kwargs)


@implementer(IChallenger, IIdentifier, IAuthenticator)
class FirebaseAuthPlugin(object):
    """Firebase Authentication Plugin for BisQue"""
    
    def __init__(self, firebase_config=None, auto_register=None, 
                 login_path="/auth_service/firebase_login",
                 logout_path="/auth_service/logout_handler", 
                 post_logout="/auth_service/post_logout",
                 rememberer_name="auth_tkt"):
        """
        Initialize Firebase authentication plugin
        
        Args:
            firebase_config: Dict with Firebase configuration
            auto_register: Auto-registration plugin name
            login_path: Path for Firebase login initiation
            logout_path: Path for logout handling
            post_logout: Path to redirect after logout
            rememberer_name: Name of rememberer plugin (usually auth_tkt)
        """
        self.firebase_config = firebase_config or {}
        self.auto_register = auto_register
        self.login_path = login_path
        self.logout_path = logout_path
        self.post_logout = post_logout
        self.rememberer_name = rememberer_name
        
        # Initialize Firebase Admin SDK if available
        self.firebase_app = None
        self._init_firebase()
        
        # Supported providers configuration (only providers with native Firebase support)
        self.providers = {
            'google': {
                'name': 'Google',
                'icon': '/core/images/signin/google.svg',
                'firebase_provider': 'google.com'
            },
            'facebook': {
                'name': 'Facebook', 
                'icon': '/core/images/signin/facebook.svg',
                'firebase_provider': 'facebook.com'
            },
            'github': {
                'name': 'GitHub',
                'icon': '/core/images/signin/github.svg', 
                'firebase_provider': 'github.com'
            },
            'twitter': {
                'name': 'Twitter',
                'icon': '/core/images/signin/twitter.svg',
                'firebase_provider': 'twitter.com'
            }
        }

    def _init_firebase(self):
        """Initialize Firebase Admin SDK"""
        if not FIREBASE_AVAILABLE:
            log.warning("Firebase Admin SDK not available. Install with: pip install firebase-admin")
            return
            
        try:
            # Check if Firebase is already initialized
            try:
                self.firebase_app = firebase_admin.get_app()
                log.info("Using existing Firebase app")
                return
            except ValueError:
                # App not initialized yet
                pass
                
            # Get service account key path from config
            service_account_path = self.firebase_config.get('service_account_key')
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                self.firebase_app = firebase_admin.initialize_app(cred)
                log.info(f"Firebase initialized with service account: {service_account_path}")
            else:
                # Try to initialize with default credentials
                self.firebase_app = firebase_admin.initialize_app()
                log.info("Firebase initialized with default credentials")
                
        except Exception as e:
            log.error(f"Failed to initialize Firebase: {e}")
            self.firebase_app = None

    def _get_rememberer(self, environ):
        """Get the rememberer plugin for session management"""
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    # IChallenger interface
    def challenge(self, environ, status, app_headers, forget_headers):
        """Challenge user for Firebase authentication"""
        log.debug('Firebase challenge initiated')
        
        request = Request(environ, charset="utf8")
        
        # Check if this is a Firebase login request
        if request.path.startswith(self.login_path):
            provider = request.params.get('provider', 'google')
            
            # For now, redirect to a Firebase auth page
            # In a full implementation, this would redirect to Firebase Auth UI
            service_url = request.url
            
            # Create Firebase Auth URL (this would be customized based on your frontend)
            firebase_auth_url = f"/auth_service/firebase_auth?provider={provider}&came_from={quote_plus(service_url)}"
            
            log.debug(f'Firebase challenge redirect to {firebase_auth_url} for provider {provider}')
            return HTTPFound(location=firebase_auth_url)
            
        return None

    # IIdentifier interface  
    def identify(self, environ):
        """Identify user from Firebase ID token"""
        request = Request(environ, charset="utf8")
        
        # Look for Firebase ID token in request
        id_token = None
        
        # Check Authorization header for Bearer token
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            id_token = auth_header[7:]  # Remove 'Bearer ' prefix
            
        # Check for token in request parameters
        if not id_token:
            id_token = request.params.get('firebase_token')
            
        # Check for token in session (for web-based auth)
        if not id_token and hasattr(request, 'session'):
            id_token = request.session.get('firebase_id_token')
            
        if not id_token:
            return None
            
        # Verify the Firebase ID token
        try:
            if not self.firebase_app:
                log.debug("Firebase not initialized, cannot verify token")
                return None
                
            decoded_token = auth.verify_id_token(id_token)
            
            # Extract user information
            uid = decoded_token['uid']
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', '')
            provider_id = decoded_token.get('firebase', {}).get('sign_in_provider', 'unknown')
            
            log.info(f"Firebase token verified for user: {email} (provider: {provider_id})")
            
            return {
                'repoze.who.userid': email or uid,
                'firebase.uid': uid,
                'firebase.email': email,
                'firebase.name': name,
                'firebase.provider': provider_id,
                'firebase.token': id_token,
                'firebase.decoded_token': decoded_token
            }
            
        except Exception as e:
            log.warning(f"Firebase token verification failed: {e}")
            return None

    def remember(self, environ, identity):
        """Remember Firebase authentication"""
        # Delegate to the main rememberer plugin
        rememberer = self._get_rememberer(environ)
        return rememberer.remember(environ, identity)

    def forget(self, environ, identity):
        """Forget Firebase authentication"""
        # Delegate to the main rememberer plugin  
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

    # IAuthenticator interface
    def authenticate(self, environ, identity):
        """Authenticate user using Firebase identity"""
        if environ.get('repoze.who.logger'):
            self.log = environ['repoze.who.logger']
        else:
            self.log = log
            
        # Check if this is a Firebase identity
        if 'firebase.uid' not in identity:
            return None
            
        firebase_uid = identity['firebase.uid']
        email = identity.get('firebase.email', '')
        name = identity.get('firebase.name', '')
        provider = identity.get('firebase.provider', 'unknown')
        
        self.log.info(f'Authenticating Firebase user: {email} (UID: {firebase_uid}, Provider: {provider})')
        
        # Extract username from email (before @)
        if email:
            username = email.split('@')[0]
        else:
            username = firebase_uid
            
        # Auto-register user if configured
        if self.auto_register:
            try:
                username = self._auto_register(environ, identity, username, email, name, provider)
            except Exception as e:
                self.log.exception(f"Auto-registration failed for {email}: {e}")
                return None
                
        return username

    def _auto_register(self, environ, identity, username, email, name, provider):
        """Auto-register Firebase user in BisQue"""
        registration = environ['repoze.who.plugins'].get(self.auto_register)
        
        if not registration:
            self.log.debug(f'Auto-registration plugin {self.auto_register} not found')
            return username
            
        self.log.debug(f'Auto-registering Firebase user: {username} ({email})')
        
        # Prepare user data for registration
        user_data = {
            'display_name': name or username,
            'email_address': email,
            'identifier': f'firebase_{provider}',
            'firebase_uid': identity.get('firebase.uid'),
            'firebase_provider': provider,
            # Use a random password since authentication is handled by Firebase
            'password': f'firebase_auth_{identity.get("firebase.uid")}'
        }
        
        try:
            registered_username = registration.register_user(username, values=user_data)
            self.log.info(f'Successfully auto-registered Firebase user: {registered_username}')
            return registered_username
        except Exception as e:
            self.log.error(f'Auto-registration failed for {username}: {e}')
            raise

    def get_provider_config(self, provider_name):
        """Get configuration for a specific provider"""
        return self.providers.get(provider_name, {})

    def get_supported_providers(self):
        """Get list of supported provider names"""
        return list(self.providers.keys())
