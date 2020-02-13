from urllib import quote_plus  #, urlencode
import logging

from webob import Request, Response
from webob.exc import HTTPFound  , HTTPUnauthorized
import simplejson as json
from lxml import etree

from paste.httpheaders import CONTENT_TYPE   #pylint: disable=no-name-in-module

from zope.interface import implements
from repoze.who.interfaces import IChallenger, IIdentifier, IAuthenticator
#from repoze.who.interfaces import IRequestClassifier, IChallengeDecider
log = logging.getLogger('bq.auth.app')

def make_plugin(
                login_path="/login_app",
                logout_path="/logout_app",
                post_logout = "/post_logout",
                rememberer_name="auth_tkt",
                ):
    return AppAuthPlugin(login_path, logout_path, post_logout, rememberer_name)


class AppAuthPlugin(object):
    implements(IChallenger, IIdentifier, IAuthenticator)

    def __init__(self, login_path, logout_path, post_logout, rememberer_name):
        """
        @param login_path : filter to redirect to cas login
        @param logout_path : filter to redirect to cas on logout
        @param post_logout : an application path to visit after logout
        @param rememberer_name: who plugin name for the remember (auth_tk)
        """
        self.login_path = login_path
        self.logout_path = logout_path
        self.post_logout = post_logout
        self.rememberer_name = rememberer_name


    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        log.debug ("APP CHALLENGE %s %s %s %s", environ.keys(), status, app_headers, forget_headers)
        content_type = CONTENT_TYPE(environ)
        log.debug ("APP CONTENT %s", content_type)
        if any (content_type.startswith(v) for v in ('application/json', 'application/xml')):
            return  Response(status=401, content_type=content_type, body="")
        return None

    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    # IIdentifier
    def remember(self, environ, identity):
        """remember the openid in the session we have anyway"""
        #log.debug("app_auth:remember")
        rememberer = self._get_rememberer(environ)
        r = rememberer.remember(environ, identity)
        return r

    # IIdentifier
    def forget(self, environ, identity):
        """forget about the authentication again"""
        #log.debug("app_auth:forget")
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

    # IIdentifier
    def identify(self, environ):
        request = Request(environ)

        # first test for logout as we then don't need the rest
        if request.path == self.logout_path:
            headers = self.forget(environ, {})
            raise HTTPFound (location="/", headers = headers)

        if request.path == self.login_path:
            content_type = CONTENT_TYPE(environ)
            if content_type.startswith('application/json'):
                login_data = json.load (request.body_file)
            elif content_type.startswith('application/xml'):
                xml = etree.parse (request.body_file).getroot()
                login_data = dict (username = xml.find ("tag[@name='username']").get('value'),
                                   password = xml.find ("tag[@name='password']").get('value'))
            else:
                return None
            log.debug ("found user %s", login_data.get('username', None))
            return { 'login': login_data.get('username', None), 'password': login_data.get('password', None) }
        return None
