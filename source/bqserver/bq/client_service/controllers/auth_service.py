###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##                            Copyright (c) 2007,2008                       ##
##                        The Regents of the University of California       ##
##                            All rights reserved                             ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##                                                                           ##
##     1. Redistributions of source code must retain the above copyright     ##
##        notice, this list of conditions, and the following disclaimer.     ##
##                                                                           ##
##     2. Redistributions in binary form must reproduce the above copyright  ##
##        notice, this list of conditions, and the following disclaimer in   ##
##        the documentation and/or other materials provided with the         ##
##        distribution.                                                      ##
##                                                                           ##
##     3. All advertising materials mentioning features or use of this       ##
##        software must display the following acknowledgement: This product  ##
##        includes software developed by the Center for Bio-Image Informatics##
##        University of California at Santa Barbara, and its contributors.   ##
##                                                                           ##
##     4. Neither the name of the University nor the names of its            ##
##        contributors may be used to endorse or promote products derived    ##
##        from this software without specific prior written permission.      ##
##                                                                           ##
## THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS "AS IS" AND ANY ##
## EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED ##
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ARE   ##
## DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR  ##
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL    ##
## DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS   ##
## OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)     ##
## HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       ##
## STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN  ##
## ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE           ##
## POSSIBILITY OF SUCH DAMAGE.                                               ##
##                                                                           ##
###############################################################################
"""
SYNOPSIS
========

DESCRIPTION
===========
  Authorization for web requests

"""
import logging
#import cherrypy
#import base64
import json
import posixpath
from datetime import datetime, timedelta, timezone

from lxml import etree
import transaction

import tg
from tg import request, session, flash, require, response
from tg import  expose, redirect, url
from tg import config
# from pylons.i18n import ugettext as  _
from tg.i18n import ugettext as _ # !!! modern replacement for pylons.i18n
# from repoze.what import predicates # !!! deprecated following is the replacement
from tg.predicates import not_anonymous, has_permission

from bq.core.service import ServiceController
from bq.core import identity
from bq.core.model import DBSession
from bq.data_service.model import   User
from bq import module_service
from bq.util.urlutil import update_url
from bq.util.xmldict import d2xml
from bq.exceptions import ConfigurationError
from bq.data_service.model.tag_model import Tag


from bq import data_service
log = logging.getLogger("bq.auth")


try:
    # python 2.6 import
    from ordereddict import OrderedDict
except ImportError:
    try:
        # python 2.7 import
        from collections import OrderedDict
    except ImportError:
        log.error("can't import OrderedDict")



class AuthenticationServer(ServiceController):
    service_type = "auth_service"
    providers = {}

    def _is_domain_authorized(self, email):
        """Check if email domain is in authorized domains list for social login"""
        log.error("Checking domain authorization for email: %s", email)
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[1].lower()
        
        try:
            # Ensure domain tables exist
            from bq.admin_service.controllers.service import ensure_domain_tables
            if not ensure_domain_tables():
                # If tables can't be created (e.g., during setup), allow all access
                log.warning("Domain tables not available, allowing all access")
                return True
            
            from bq.data_service.model.domain_model import is_domain_authorized
            return is_domain_authorized(email)
            
        except Exception as e:
            # If domain model doesn't exist or there's an error, default to allow all
            # This maintains backward compatibility
            log.warning(f"Domain authorization check failed, allowing access: {e}")
            return True

    def _is_approved(self, bq_user):
        """Check if user has been approved by admin for login"""
        approved_tag = (
            DBSession.query(Tag)
            .filter(
                Tag.parent == bq_user,
                Tag.resource_name == "is_approved",
                Tag.resource_value == "true",
            )
            .first()
        )
        return True if approved_tag else False
    
    def _is_email_verified(self, bq_user):
        """Check if user has verified their email address"""
        verified_tag = (
            DBSession.query(Tag)
            .filter(
                Tag.parent == bq_user,
                Tag.resource_name == "email_verified",
                Tag.resource_value == "true",
            )
            .first()
        )
        return True if verified_tag else False

    @classmethod
    def login_map(cls):
        if cls.providers:
            return cls.providers
        identifiers = OrderedDict()
        for key in (x.strip() for x in config.get('bisque.login.providers').split(',')):
            entries = {}
            for kent in ('url', 'text', 'icon', 'type'):
                kval = config.get('bisque.login.%s.%s' % (key, kent))
                if kval is not None:
                    entries[kent] = kval
            identifiers[key] =  entries
            if 'url' not in entries:
                raise ConfigurationError ('Missing url for bisque login provider %s' % key)
        cls.providers = identifiers
        return identifiers

    @expose(content_type="text/xml")
    def login_providers (self):
        log.debug ("providers")
        return etree.tostring (d2xml ({ 'providers' : self.login_map()} ), encoding='unicode')

    @expose()
    def login_check(self, came_from='/', login='', **kw):
        log.debug ("login_check %s from=%s " , login, came_from)
        login_urls = self.login_map()
        default_login = list(login_urls.values())[-1]
        if login:
            # Look up user
            user = DBSession.query (User).filter_by(user_name=login).first()
            # REDIRECT to registration page?
            if user is None:
                redirect(update_url(default_login['url'], dict(username=login, came_from=came_from)))
            # Find a matching identifier
            login_identifiers = [ g.group_name for g in user.groups ]
            for identifier in list(login_urls.keys()):
                if  identifier in login_identifiers:
                    login_url  = login_urls[identifier]['url']
                    log.debug ("redirecting to %s handler" , identifier)
                    redirect(update_url(login_url, dict(username=login, came_from=came_from)))

        log.debug ("using default login handler %s" , default_login)
        redirect(update_url(default_login, dict(username=login, came_from=came_from)))


    @expose('bq.client_service.templates.login')
    def login(self, came_from='/', username = '', **kw):
        """Start the user login."""
        if 'failure' in kw:
            log.info("------ login failure %s" % kw['failure'])
            flash(_(kw['failure']), 'warning')
        login_counter = int (request.environ.get ('repoze.who.logins', 0))
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        # Check if we have only 1 provider that is not local and just redirect there.
        login_urls = self.login_map()
        if len(login_urls) == 1:
            provider, entries =  list(login_urls.items())[0]
            if provider != 'local':
                redirect (update_url(entries['url'], dict(username=username, came_from=came_from)))

        return dict(page='login', login_counter=str(login_counter), came_from=came_from, username=username,
                    providers_json = json.dumps (login_urls), providers = login_urls )
    
    
    @expose ()
    def login_handler(self, came_from='/', **kw):
        """Handle login form submission and redirect appropriately."""
        log.debug ("login_handler %s" % kw)
        # Redirect to post_login to handle the actual authentication logic
        return self.post_login(came_from=came_from, **kw)

    @expose()
    def openid_login_handler(self, **kw):
        log.error("openid_login_handler %s" % kw)
        redirect(update_url("https://bisque-md.ece.ucsb.edu/", dict(redirect_uri="https://bisque2.ece.ucsb.edu/")))
       # log.debug ("openid_login_handler %s" % kw)
       # return self.login(**kw)



    @expose()
    def post_login(self, came_from='/', **kw):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = int (request.environ.get('repoze.who.logins',0)) + 1
            redirect(url('/auth_service/login',params=dict(came_from=came_from, __logins=login_counter)))
        
        userid = request.identity['repoze.who.userid']
        
        # Check email verification status FIRST before proceeding with login
        try:
            # Skip email verification for admin users
            is_admin_user = (userid == 'admin' or 
                           userid == 'administrator' or 
                           'admin' in userid.lower())
            
            if is_admin_user:
                log.debug(f"Skipping email verification for admin user: {userid}")
            else:
                from bq.registration.email_verification import get_email_verification_service
                from bq.data_service.model import BQUser
                from bq.data_service.model.tag_model import DBSession
                
                email_service = get_email_verification_service()
                if email_service and email_service.is_available():
                    # Find the user by username
                    bq_user = DBSession.query(BQUser).filter(BQUser.resource_name == userid).first()
                    if bq_user:
                        # Check if user is verified
                        is_verified = email_service.is_user_verified(bq_user)
                        is_approved = self._is_approved(bq_user)
                        if not is_verified:
                            # User is not verified - deny login completely
                            log.warning(f"Login denied for unverified user: {userid}")
                            
                            # Force logout by redirecting to logout handler first
                            flash(_('Your email address must be verified before you can sign in. Please check your email for the verification link or request a new one.'), 'error')
                            redirect('/auth_service/logout_handler?came_from=/registration/resend_verification')
                            return  # This should never be reached due to redirect
                        if not is_approved:
                            # User is not approved by admin - deny login
                            log.warning(f"Login denied for unapproved user: {userid}")
                            
                            # Force logout by redirecting to logout handler first
                            flash(_('Your account requires administrator approval before you can sign in. Please contact an administrator.'), 'error')
                            redirect('/auth_service/logout_handler?came_from=/client_service/')
                            return  # This should never be reached due to redirect
                        log.info(f"Email verified user logged in: {userid}")
                    else:
                        log.warning(f"User not found in database during email verification check: {userid}")
                else:
                    # Email verification not available - check if user is manually verified by admin
                    log.debug(f"Email verification not available - checking manual verification for: {userid}")
                    bq_user = DBSession.query(BQUser).filter(BQUser.resource_name == userid).first()
                    if bq_user:                        
                        verified_tag = self._is_email_verified(bq_user)
                        approved_tag = self._is_approved(bq_user)
                        
                        log.error(f"Unified approval check for user {userid}, verified_tag: {verified_tag}, approved_tag: {approved_tag}")
                        
                        if not verified_tag or not approved_tag:
                            # User is not fully approved - deny login
                            log.warning(f"Login denied for unapproved user (no SMTP): {userid}")
                            flash(_('Your account requires administrator approval before you can sign in. Please contact an administrator.'), 'error')
                            redirect('/auth_service/logout_handler?came_from=/client_service/')
                            return
                        else:
                            log.info(f"Manually verified user logged in: {userid}")
                    else:
                        log.warning(f"User not found during manual verification check: {userid}")
                        flash(_('Account not found. Please contact an administrator.'), 'error')
                        redirect('/auth_service/logout_handler?came_from=/client_service/')
                        return
                
        except (ImportError, AttributeError, NameError) as import_error:
            # Only catch import/attribute errors, not redirects
            log.error(f"Error importing email verification modules for {userid}: {import_error}")
            # Allow login to continue if email verification modules can't be imported
        except Exception as e:
            # Check if this is a redirect exception (which is normal)
            import tg.exceptions
            if isinstance(e, (tg.exceptions.HTTPFound, tg.exceptions.HTTPRedirection)):
                # This is a redirect, let it propagate normally
                raise
            else:
                # This is a real error
                log.error(f"Error checking email verification status for {userid}: {e}")
                # If there's an error checking verification, allow login to avoid breaking the system
                # but log it for investigation
                import traceback
                log.error(f"Email verification check error traceback: {traceback.format_exc()}")
        
        # Original login logic continues only if user is verified or verification is disabled
        flash(_('Welcome back, %s!') % userid)
        self._begin_mex_session()
        timeout = int (config.get ('bisque.login.timeout', '0').split('#')[0].strip())
        length = int (config.get ('bisque.login.session_length', '0').split('#')[0].strip())
        if timeout:
            session['timeout']  = timeout
        if length:
            session['expires']  = (datetime.now(timezone.utc) + timedelta(seconds=length))
            session['length'] = length

        session.save()
        transaction.commit()
        redirect(came_from)


    # This function is used to handle logout requests
    @expose ()
    def logout_handler(self, **kw):
        log.debug ("logout_handler %s" % kw)
        try:
            self._end_mex_session()
            session.delete()
        except Exception:
            log.exception("logout")
        redirect ('/')


    @expose()
    def post_logout(self, came_from='/', **kw):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        #self._end_mex_session()
        #flash(_('We hope to see you soon!'))
        log.debug("post_logout")
        try:
            self._end_mex_session()
            session.delete()
            transaction.commit()
        except Exception:
            log.exception("post_logout")
        #redirect(came_from)
        log.debug ("POST_LOGOUT")

        redirect(tg.url ('/'))

    @expose(content_type="text/xml")
    def credentials(self, **kw):
        response = etree.Element('resource', type='credentials')
        username = identity.get_username()
        if username:
            etree.SubElement(response,'tag', name='user', value=username)
            #OLD way of sending credential
            #if cred[1]:
            #    etree.SubElement(response,'tag', name='pass', value=cred[1])
            #    etree.SubElement(response,'tag',
            #                     name="basic-authorization",
            #                     value=base64.encodestring("%s:%s" % cred))
        #tg.response.content_type = "text/xml"
        return etree.tostring(response, encoding='unicode')

    @expose(content_type="text/xml")
    def whoami(self, **kw):
        """Return information about the current authenticated user"""
        response = etree.Element('user')
        
        username = identity.get_username()
        if username:
            etree.SubElement(response, 'tag', name='name', value=username)
            
            # Add user ID if available
            current_user = identity.get_user()
            if current_user:
                etree.SubElement(response, 'tag', name='uri', value=data_service.uri() + current_user.uri)
                etree.SubElement(response, 'tag', name='resource_uniq', value=current_user.resource_uniq)
                
                # Add groups
                groups = [g.group_name for g in current_user.get_groups()]
                if groups:
                    etree.SubElement(response, 'tag', name='groups', value=",".join(groups))
        else:
            # Not authenticated
            etree.SubElement(response, 'tag', name='name', value='anonymous')
            
        return etree.tostring(response, encoding='unicode')


    @expose(content_type="text/xml")
    def session(self):
        sess = etree.Element ('session', uri = posixpath.join(self.uri, "session") )
        if identity.not_anonymous():
            #vk = tgidentity.current.visit_link.visit_key
            #log.debug ("session_timout for visit %s" % str(vk))
            #visit = Visit.lookup_visit (vk)
            #expire =  (visit.expiry - datetime.now()).seconds
            #KGKif 'mex_auth' not in session:
            #KGKlog.warn ("INVALID Session or session deleted: forcing logout on client")
            #KGK    return etree.tostring (sess)
            #KGK    #redirect ('/auth_service/logout_handler')

            timeout = int(session.get ('timeout', 0 ))
            length  = int(session.get ('length', 0 ))
            expires = session.get ('expires', datetime(2100, 1,1))
            current_user = identity.get_user()
            if current_user:
                # Pylint misses type of current_user
                # pylint: disable=no-member
                etree.SubElement(sess,'tag',
                                 name='user', value=data_service.uri() + current_user.uri)
                etree.SubElement(sess, 'tag', name='group', value=",".join([ g.group_name for g in  current_user.get_groups()]))

            # https://stackoverflow.com/questions/19654578/python-utc-datetime-objects-iso-format-doesnt-include-z-zulu-or-zero-offset
            etree.SubElement (sess, 'tag', name='expires', value= expires.isoformat()+'Z' )
            etree.SubElement (sess, 'tag', name='timeout', value= str(timeout) )
            etree.SubElement (sess, 'tag', name='length', value= str(length) )
        return etree.tostring(sess, encoding='unicode')


    @expose(content_type="text/xml")
    # @require(predicates.not_anonymous()) # !!! deprecated following is the replacement
    @require(not_anonymous())
    def newmex (self, module_url=None):
        mexurl  = self._begin_mex_session()
        return mexurl

    def _begin_mex_session(self):
        """Begin a mex associated with the visit to record changes"""

        #
        #log.debug('begin_session '+ str(tgidentity.current.visit_link ))
        #log.debug ( str(tgidentity.current.visit_link.users))
        mex = module_service.begin_internal_mex()
        mex_uri = mex.get('uri')
        mex_uniq  = mex.get('resource_uniq')
        session['mex_uniq']  = mex_uniq
        session['mex_uri'] =  mex_uri
        session['mex_auth'] = "%s:%s" % (identity.get_username(), mex_uniq)
        log.info ("MEX Session %s ( %s ) " , mex_uri, mex_uniq)
        #v = Visit.lookup_visit (tgidentity.current.visit_link.visit_key)
        #v.mexid = mexid
        #session.flush()
        return mex

    def _end_mex_session(self):
        """Close a mex associated with the visit to record changes"""
        try:
            mexuri = session.get('mex_uri')
            if mexuri:
                module_service.end_internal_mex (mexuri)
        except AttributeError:
            pass
        return ""


    @expose(content_type="text/xml")
    # @require(predicates.not_anonymous()) # !!! deprecated following is the replacement
    @require(not_anonymous())
    def setbasicauth(self,  username, passwd, **kw):
        log.debug ("Set basic auth %s", kw)
        if not identity.is_admin() and username != identity.get_username() :
            return "<error msg='failed: not allowed to change password of others' />"
        user = tg.request.identity.get('user')
        log.debug ("Got user %s", user)
        if user and user.user_name == username:  # sanity check
            user = DBSession.merge(user)
            user.password = passwd
            log.info ("Setting new basicauth password for %s", username)
            #transaction.commit()
            return "<success/>"
        log.error ("Could not set basicauth password for %s", username)
        return "<error msg='Failed to set password'/>"


    @expose()
    def login_app(self):
        """Allow  json/xml logins.. core functionality in bq/core/lib/app_auth.py
        This is to a place holder
        """
        if identity.not_anonymous():
            response.body = "{'status':'OK'}"
            return
        response.status = 401
        response.body = "{'status':'FAIL'}"


    @expose()
    # @require(predicates.not_anonymous())
    def logout_app(self):
        """Allow  json/xml logins.. core functionality in bq/core/lib/app_auth.py
        This is to a place holder
        """
        pass

    # Firebase Authentication Endpoints
    @expose('bq.client_service.templates.firebase_auth')
    def firebase_auth(self, provider='google', came_from='/', **kw):
        """Firebase authentication page with provider selection"""
        log.debug(f"Firebase auth requested for provider: {provider}")
        
        # Get Firebase configuration from TurboGears config
        firebase_config = {
            'project_id': config.get('bisque.firebase.project_id', ''),
            'web_api_key': config.get('bisque.firebase.web_api_key', ''),
        }
        
        # Check if Firebase is properly configured
        if not firebase_config.get('project_id') or not firebase_config.get('web_api_key'):
            log.error("Firebase not properly configured")
            redirect('/auth_service/login?error=firebase_config')
        
        # Supported providers
        providers_config = {
            'google': {'name': 'Google', 'color': '#4285f4'},
            'facebook': {'name': 'Facebook', 'color': '#1877f2'},
            'github': {'name': 'GitHub', 'color': '#24292e'},
            'twitter': {'name': 'Twitter', 'color': '#1da1f2'}
        }
        
        # Validate provider
        if provider not in providers_config:
            log.error(f"Invalid Firebase provider: {provider}")
            redirect('/auth_service/login?error=invalid_provider')
        
        # Get the available providers (same as login method)
        providers = self.login_map()
        
        return {
            'provider': provider,
            'came_from': came_from,
            'firebase_config': firebase_config,
            'providers_config': providers_config,
            'providers': providers  # Add this so template can check 'firebase_facebook' in providers
        }

    @expose('json')
    def firebase_token_verify(self, id_token=None, **kw):
        """Verify Firebase ID token and create BisQue session"""
        from urllib.parse import quote_plus
        
        came_from = kw.get('came_from', '/')
        
        if not id_token:
            return {'status': 'error', 'message': 'No ID token provided'}
            
        try:
            # Import Firebase Admin SDK directly
            import firebase_admin
            from firebase_admin import auth, credentials
            
            # Get Firebase configuration
            service_account_path = config.get('bisque.firebase.service_account_key')
            project_id = config.get('bisque.firebase.project_id')
            
            log.info(f"Firebase config - project_id: {project_id}, service_account: {service_account_path}")
            
            # Initialize Firebase app if not already done
            firebase_app = None
            try:
                # Try to delete any existing app first to avoid conflicts
                try:
                    existing_app = firebase_admin.get_app()
                    firebase_admin.delete_app(existing_app)
                    log.info("Deleted existing Firebase app")
                except ValueError:
                    pass  # No existing app
                
                # Initialize Firebase with explicit project ID
                if service_account_path and project_id:
                    cred = credentials.Certificate(service_account_path)
                    firebase_app = firebase_admin.initialize_app(cred, {
                        'projectId': project_id
                    })
                    log.info(f"Initialized Firebase app with project ID: {project_id}")
                else:
                    return {'status': 'error', 'message': 'Firebase configuration missing'}
            except Exception as e:
                log.error(f"Failed to initialize Firebase: {e}")
                return {'status': 'error', 'message': f'Firebase initialization failed: {e}'}
            
            # Verify the ID token directly with Firebase Admin SDK
            decoded_token = auth.verify_id_token(id_token, app=firebase_app)
            
            # Extract user information from the decoded token
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', '')
            uid = decoded_token.get('uid', '')
            provider_info = decoded_token.get('firebase', {}).get('sign_in_provider', 'unknown')
            
            log.info(f"Firebase token verified for {email} (provider: {provider_info})")
            
            # Check if email domain is authorized for social login
            if not self._is_domain_authorized(email):
                domain = email.split('@')[1] if '@' in email else 'unknown'
                log.warning(f"Social login attempt from unauthorized domain: {domain}")
                return {
                    'status': 'error',
                    'message': f'Social login is not authorized for domain: {domain}. Please contact an administrator.'
                }
            
            # Check if user exists in BisQue
            from bq.data_service.model import BQUser
            from bq.data_service.model.tag_model import DBSession, Tag
            
            # Simple email-based user lookup (Firebase guarantees unique emails)
            bq_user = None
            username = None
            user_id = None
            
            if email:
                bq_user = DBSession.query(BQUser).filter(BQUser.resource_value == email).first()
                if bq_user:
                    # Extract attributes while still in session context to avoid DetachedInstanceError
                    username = bq_user.resource_name
                    user_id = bq_user.resource_uniq
                    log.info(f"Found existing user by email: {email}")
                else:
                    log.info(f"No existing user found for email: {email}")
            
            if not bq_user and email:
                # Auto-register the user (first-time Firebase login)
                try:
                    user_data = self._register_firebase_user(email, name, uid, provider_info)
                    # Extract attributes from returned data
                    if user_data:
                        bq_user = user_data['bq_user']
                        username = user_data['resource_name']
                        user_id = user_data['resource_uniq']
                    
                    # Note: _register_firebase_user already marks user as verified, no need to do it again
                    log.info(f"Auto-registered Firebase user: {email}")
                except Exception as e:
                    log.error(f"Failed to auto-register Firebase user {email}: {e}")
                    return {'status': 'error', 'message': 'Failed to register user'}
            
            if bq_user and username:
                if not self._is_approved(bq_user):
                    log.warning(f"Login denied for unapproved Firebase user: {username}")
                    return {
                        'status': 'error',
                        'message': 'Your account requires administrator approval before you can sign in. Please contact an administrator.'
                    }
                # Store Firebase credentials temporarily in session for authentication
                session['firebase_pending_auth'] = {
                    'username': username,
                    'user_id': user_id,
                    'firebase_uid': uid,
                    'email': email,
                    'name': name,
                    'provider': provider_info,
                    'came_from': came_from
                }
                session.save()
                
                log.info(f"Firebase user authenticated, redirecting for session creation: {username}")
                
                return {
                    'status': 'success', 
                    'message': 'Authentication successful',
                    'redirect_url': f'/auth_service/firebase_session_create?came_from={quote_plus(came_from)}',
                    'user': {
                        'email': email,
                        'name': name,
                        'provider': provider_info,
                        'username': username
                    }
                }
            else:
                return {'status': 'error', 'message': 'User registration failed'}
                
        except Exception as e:
            log.error(f"Firebase token verification failed: {e}")
            import traceback
            log.error(f"Full traceback: {traceback.format_exc()}")
            return {'status': 'error', 'message': 'Token verification failed'}

    def _register_firebase_user(self, email, name, uid, provider):
        """Register a new Firebase user in BisQue"""
        from bq.core.model.auth import User
        from bq.data_service.model import BQUser
        from bq.data_service.model.tag_model import Tag
        from sqlalchemy.exc import IntegrityError
        
        # First, check if a user with this email already exists (race condition safety)
        existing_bq_user = DBSession.query(BQUser).filter(BQUser.resource_value == email).first()
        if existing_bq_user:
            log.info(f"User with email {email} already exists, returning existing user data")
            return {
                'resource_name': existing_bq_user.resource_name,
                'resource_uniq': existing_bq_user.resource_uniq,
                'bq_user': existing_bq_user
            }
        
        # Create unique username to prevent conflicts
        base_username = email.split('@')[0] if email else f"firebase_{uid[:8]}"
        username = base_username
        
        # Check if username already exists and make it unique
        counter = 1
        while DBSession.query(User).filter_by(user_name=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
        
        
        try:
            # Create TurboGears User (this will trigger bquser_callback which creates BQUser automatically)
            tg_user = User(
                user_name=username,
                email_address=email,
                display_name=name or username,
                password=f'firebase_auth_{uid}'  # Random password since auth is via Firebase
            )
            DBSession.add(tg_user)
            DBSession.flush()  # This triggers bquser_callback which creates BQUser automatically
            
            # Find the BQUser that was created by the callback (same as manual registration)
            bq_user = DBSession.query(BQUser).filter_by(resource_name=username).first()
            if not bq_user:
                # Fallback: create BQUser manually if callback didn't work (should be rare)
                log.warning(f"bquser_callback didn't create BQUser for {username}, creating manually")
                bq_user = BQUser(tg_user=tg_user, create_tg=False, create_store=True)
                DBSession.add(bq_user)
                DBSession.flush()
                bq_user.owner_id = bq_user.id
            
            # Add Firebase-specific tags
            firebase_uid_tag = Tag(parent=bq_user)
            firebase_uid_tag.name = "firebase_uid"
            firebase_uid_tag.value = uid
            firebase_uid_tag.owner = bq_user
            DBSession.add(firebase_uid_tag)
            
            firebase_provider_tag = Tag(parent=bq_user)
            firebase_provider_tag.name = "firebase_provider" 
            firebase_provider_tag.value = provider
            firebase_provider_tag.owner = bq_user
            DBSession.add(firebase_provider_tag)
            
            # Add standard user profile tags (similar to manual registration)
            if name:
                # Update the display_name tag that was created by BQUser constructor
                display_name_tag = bq_user.findtag('display_name')
                if display_name_tag:
                    display_name_tag.value = name
                else:
                    # Create display_name tag if not found
                    display_name_tag = Tag(parent=bq_user)
                    display_name_tag.name = "display_name"
                    display_name_tag.value = name
                    display_name_tag.owner = bq_user
                    DBSession.add(display_name_tag)
                
                # Add fullname tag (used by registration form)
                fullname_tag = Tag(parent=bq_user)
                fullname_tag.name = "fullname"
                fullname_tag.value = name
                fullname_tag.owner = bq_user
                DBSession.add(fullname_tag)
            
            # Add username tag (for compatibility with manual registration)
            username_tag = Tag(parent=bq_user)
            username_tag.name = "username"
            username_tag.value = username
            username_tag.owner = bq_user
            DBSession.add(username_tag)
            
            # Mark email as verified since Firebase handles email verification
            from datetime import datetime, timezone
            
            email_verified_tag = Tag(parent=bq_user)
            email_verified_tag.name = "email_verified"
            email_verified_tag.value = "true"
            email_verified_tag.owner = bq_user
            DBSession.add(email_verified_tag)
            
            email_verified_time_tag = Tag(parent=bq_user)
            email_verified_time_tag.name = "email_verified_at"
            email_verified_time_tag.value = datetime.now(timezone.utc).isoformat()
            email_verified_time_tag.owner = bq_user
            DBSession.add(email_verified_time_tag)
            
            # Add default values for research area and institution (can be updated later)
            research_area_tag = Tag(parent=bq_user)
            research_area_tag.name = "research_area"
            research_area_tag.value = "Other"  # Default value
            research_area_tag.owner = bq_user
            DBSession.add(research_area_tag)
            
            institution_tag = Tag(parent=bq_user)
            institution_tag.name = "institution_affiliation"
            institution_tag.value = ""  # Empty default, user can fill in later
            institution_tag.owner = bq_user
            DBSession.add(institution_tag)
            
            DBSession.flush()
            
            # Extract attributes before committing to avoid DetachedInstanceError
            user_data = {
                'resource_name': bq_user.resource_name,
                'resource_uniq': bq_user.resource_uniq,
                'bq_user': bq_user
            }
            
            transaction.commit()
            return user_data
            
        except IntegrityError as e:
            # Handle race condition - another thread/request created the user
            log.warning(f"IntegrityError creating user {email}, likely due to race condition: {e}")
            transaction.abort()
            
            # Re-query for the user that was created by the other request
            existing_bq_user = DBSession.query(BQUser).filter(BQUser.resource_value == email).first()
            if existing_bq_user:
                log.info(f"Found existing user after IntegrityError: {email}")
                return {
                    'resource_name': existing_bq_user.resource_name,
                    'resource_uniq': existing_bq_user.resource_uniq,
                    'bq_user': existing_bq_user
                }
            else:
                log.error(f"Failed to find user after IntegrityError: {email}")
                raise Exception(f"Failed to create or find user {email}")
        
        except Exception as e:
            log.error(f"Unexpected error creating Firebase user {email}: {e}")
            transaction.abort()
            raise

    def _ensure_firebase_user_tags(self, tg_user, email, name, uid, provider):
        """Ensure existing Firebase user has all required tags"""
        from bq.data_service.model import BQUser
        from bq.data_service.model.tag_model import Tag
        from datetime import datetime, timezone
        
        # Get the BQUser for this TurboGears user
        bq_user = DBSession.query(BQUser).filter(BQUser.resource_name == tg_user.user_name).first()
        if not bq_user:
            log.warning(f"No BQUser found for TG user: {tg_user.user_name}")
            return
        
        log.info(f"Checking/updating tags for existing Firebase user: {tg_user.user_name}")
        
        # Define required tags and their values
        required_tags = {
            'firebase_uid': uid,
            'firebase_provider': provider,
            'fullname': name or tg_user.display_name,
            'username': tg_user.user_name,
            'research_area': 'Other',
            'institution_affiliation': ''
        }
        
        # Only add email verification tags if they don't already exist
        existing_email_verified = DBSession.query(Tag).filter(
            Tag.parent == bq_user,
            Tag.resource_name == "email_verified"
        ).first()
        
        if not existing_email_verified:
            required_tags['email_verified'] = 'true'
            required_tags['email_verified_at'] = datetime.now(timezone.utc).isoformat()
        
        # Check and add missing tags
        tags_added = []
        for tag_name, tag_value in required_tags.items():
            # Check if tag already exists
            existing_tag = DBSession.query(Tag).filter(
                Tag.parent == bq_user,
                Tag.resource_name == tag_name
            ).first()
            
            if not existing_tag:
                # Create the missing tag
                new_tag = Tag(parent=bq_user)
                new_tag.name = tag_name
                new_tag.value = tag_value
                new_tag.owner = bq_user
                DBSession.add(new_tag)
                tags_added.append(tag_name)
                log.info(f"Added missing tag for {tg_user.user_name}: {tag_name} = {tag_value}")
            else:
                # Update Firebase-specific tags in case they changed
                if tag_name in ['firebase_uid', 'firebase_provider'] and existing_tag.value != tag_value:
                    existing_tag.value = tag_value
                    log.info(f"Updated tag for {tg_user.user_name}: {tag_name} = {tag_value}")
        
        # Update display_name tag if needed
        if name and name != tg_user.display_name:
            display_name_tag = bq_user.findtag('display_name')
            if display_name_tag:
                display_name_tag.value = name
                log.info(f"Updated display_name for {tg_user.user_name}: {name}")
            else:
                # Create display_name tag if not found
                display_name_tag = Tag(parent=bq_user)
                display_name_tag.name = "display_name"
                display_name_tag.value = name
                display_name_tag.owner = bq_user
                DBSession.add(display_name_tag)
                tags_added.append('display_name')
        
        if tags_added:
            DBSession.flush()
            # Don't commit here - let the main flow handle the commit
            log.info(f"Successfully added/updated {len(tags_added)} tags for existing user {tg_user.user_name}: {tags_added}")
        else:
            log.info(f"No tag updates needed for existing user {tg_user.user_name}")

    @expose('json')
    def firebase_session_create(self, came_from='/', **kw):
        """Create a session from Firebase authentication - following the exact manual login flow"""
        # Import Firebase Admin SDK
        import firebase_admin
        from firebase_admin import auth as admin_auth, credentials
        import json
        
        # Get the POST data
        try:
            request_data = json.loads(request.body.decode('utf-8'))
        except:
            request_data = kw
        
        id_token = request_data.get('idToken')
        provider = request_data.get('provider')  # This might be None, we'll get it from token
        came_from = request_data.get('came_from', '/')
        
        log.info(f"Firebase session creation request - token present: {bool(id_token)}, provider: {provider}")
        
        if not id_token:
            log.error("No Firebase ID token provided")
            redirect('/auth_service/login?error=no_token')
        
        # Step 1: Initialize Firebase if needed and verify the token
        try:
            # Try to get existing app first
            try:
                firebase_app = firebase_admin.get_app()
                log.info("Using existing Firebase app")
            except ValueError:
                # Initialize Firebase with explicit project ID
                service_account_path = config.get('bisque.firebase.service_account_key')
                project_id = config.get('bisque.firebase.project_id')
                
                if service_account_path and project_id:
                    cred = credentials.Certificate(service_account_path)
                    firebase_app = firebase_admin.initialize_app(cred, {
                        'projectId': project_id
                    })
                    log.info(f"Initialized new Firebase app with project ID: {project_id}")
                else:
                    log.error("Firebase configuration missing")
                    redirect('/auth_service/login?error=firebase_config_missing')
            
            # Verify the ID token
            decoded_token = admin_auth.verify_id_token(id_token)
            firebase_uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name', email.split('@')[0] if email else 'Unknown')
            
            # Get the provider from the token if not provided
            if not provider:
                firebase_info = decoded_token.get('firebase', {})
                if 'sign_in_provider' in firebase_info:
                    provider = firebase_info['sign_in_provider']
                else:
                    provider = 'firebase'  # fallback
            
            log.info(f"Firebase token verified for session creation: {email} (provider: {provider})")
            
        except Exception as e:
            log.error(f"Firebase token verification failed: {e}")
            redirect('/auth_service/login?error=invalid_token')
        
        if not email:
            log.error("No email found in Firebase token")
            redirect('/auth_service/login?error=no_email')
        
        # Step 2: Find or create the local user account
        from bq.data_service.model import User, BQUser
        from bq.data_service.model.tag_model import DBSession
        
        # Ensure we see any recently committed data from firebase_token_verify
        DBSession.expire_all()
        
        # Use the same lookup method as firebase_token_verify to avoid duplicates
        # First try to find existing user by email using BQUser table (more reliable)
        bq_user = DBSession.query(BQUser).filter(BQUser.resource_value == email).first()
        tg_user = None
        username = None
        
        if bq_user:
            # Found existing user, get the TurboGears user by username
            tg_user = DBSession.query(User).filter_by(user_name=bq_user.resource_name).first()
            username = bq_user.resource_name
            log.info(f"Found existing BQUser by email: {email}, username: {username}")
            
            # For existing users, ensure they have all required Firebase tags
            try:
                self._ensure_firebase_user_tags(tg_user, email, name, firebase_uid, provider)
            except Exception as e:
                log.warning(f"Failed to update existing user tags for {email}: {e}")
        else:
            # Fallback: try TurboGears User table lookup
            tg_user = User.by_email_address(email) if email else None
            
            if tg_user:
                username = tg_user.user_name
                log.info(f"Found existing TG User by email: {email}, username: {username}")
                # For existing users, ensure they have all required Firebase tags
                try:
                    self._ensure_firebase_user_tags(tg_user, email, name, firebase_uid, provider)
                except Exception as e:
                    log.warning(f"Failed to update existing user tags for {email}: {e}")
            else:
                # User doesn't exist, create new one using the existing Firebase registration method
                try:
                    user_data = self._register_firebase_user(email, name, firebase_uid, provider)
                    # Extract username from the returned data since the tg_user object will be detached
                    username = user_data['resource_name']
                    # Get the tg_user by username since BQUser doesn't have tg_user attribute
                    tg_user = DBSession.query(User).filter_by(user_name=username).first()
                    log.info(f"Created new Firebase user: {username}")
                except Exception as e:
                    log.error(f"Failed to create user for email {email}: {e}")
                    redirect('/auth_service/login?error=user_creation_failed')
        
        if not tg_user:
            log.error(f"Failed to find or create user for email: {email}")
            redirect('/auth_service/login?error=user_creation_failed')
            
        # Step 3: Authenticate user using TurboGears authentication system
        # For new users, extract username from the returned data
        if 'username' not in locals():
            username = tg_user.user_name
        log.info(f"Firebase authentication successful for user: {username}")
        
        # Use TurboGears authentication system to remember the user
        from tg import config
        
        # Manually call TurboGears login to set proper authentication cookies
        from bq.core.model import DBSession
        
        # Create identity dict that TurboGears expects
        identity = {
            'repoze.who.userid': username,
            'user': tg_user,
            'userdata': {}
        }
        
        # Set identity in request for immediate use
        request.environ['repoze.who.identity'] = identity
        request.identity = identity
        
        # Most importantly, set the authentication cookie using TurboGears mechanism
        from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
        
        # Create auth_tkt plugin to set authentication cookie
        auth_tkt = AuthTktCookiePlugin(
            secret=config.get('sa_auth.cookie_secret', 'images'),
            cookie_name='authtkt',  # TurboGears default cookie name
            secure=config.get('sa_auth.cookie_secure', False),
            include_ip=config.get('sa_auth.cookie_include_ip', False)
        )
        
        # Remember the user (sets authentication cookie)
        headers = auth_tkt.remember(request.environ, identity)
        
        log.info(f"Identity set for user: {username} with auth cookie")
        
        # Now redirect to post_login (TurboGears will handle the HTTPFound exception)
        redirect_url = f'/auth_service/post_login'
        if came_from and came_from != '/':
            redirect_url += f'?came_from={came_from}'
        
        log.info(f"Redirecting to: {redirect_url}")
        
        # Create HTTPFound with authentication headers
        from tg.exceptions import HTTPFound
        response = HTTPFound(location=redirect_url)
        if headers:
            for header_name, header_value in headers:
                response.headers[header_name] = header_value
        
        # Raise the response to redirect with proper authentication
        raise response




def initialize(url):
    service =  AuthenticationServer(url)
    return service


__controller__ = AuthenticationServer
__staticdir__ = None
__model__ = None
