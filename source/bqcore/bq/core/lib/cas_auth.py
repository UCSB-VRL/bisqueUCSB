from urllib import quote_plus  #, urlencode
import logging

import requests
from webob import Request, Response
from webob.exc import HTTPFound  #, HTTPUnauthorized

from zope.interface import implements
from repoze.who.interfaces import IChallenger, IIdentifier, IAuthenticator
#from repoze.who.interfaces import IRequestClassifier, IChallengeDecider

log = logging.getLogger('bq.auth.cas')

def make_plugin(cas_base_url,
                saml_validate = None,
                login_path="/login_handler",
                logout_path="/logout_handler",
                post_logout = "/post_logout",
                remember_name="auth_tkt",
                validate_plugin = None,
                registration_url = None,
                ):
    return CASPlugin (cas_base_url,  saml_validate, login_path, logout_path, post_logout,
                      remember_name, validate_plugin, registration_url)


class CASPlugin(object):
    implements(IChallenger, IIdentifier, IAuthenticator)

    def __init__(self,
                 cas_base_url,
                 saml_validate,
                 login_path,
                 logout_path,
                 post_logout,
                 rememberer_name,
                 validate_plugin,
                 registration_url,):
        """

        @param cas_base_url : a cas provider url
        @param saml_validate : saml endpoint or None (will be cas_base_ur/samlValidate
        @param login_path : filter to redirect to cas login
        @param logout_path : filter to redirect to cas on logout
        @param post_logout : an application path to visit after logout
        @param rememberer_name: who plugin name for the remember (auth_tk)
        @param validate_plugin : A pluginname : method i.e. autoreg:validate or autoreg:register
        """
        if cas_base_url[-1] == '/':
            cas_base_url = cas_base_url[0:-1]
        self.cas_login_url = "%s/login" % cas_base_url
        self.cas_logout_url = "%s/logout" % cas_base_url
        self.cas_validate_url = "%s/validate" % cas_base_url
        self.cas_saml_validate = saml_validate or ("%s/samlValidate" % cas_base_url)
        self.logout_path = logout_path
        self.login_path = login_path
        self.post_logout = post_logout
        self.registration_url = registration_url or self.cas_login_url
        # rememberer_name is the name of another configured plugin which
        # implements IIdentifier, to handle remember and forget duties
        # (ala a cookie plugin or a session plugin)
        self.rememberer_name = rememberer_name
        # validate_plugin is atring "pluginname:[register:validate]"
        if validate_plugin:
            self.validate_plugin, self.validate_method  = validate_plugin.split (':')
        self.http = requests.Session()
        self.http.verify = False


    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        log.debug ('cas:challenge')
        request = Request(environ, charset="utf8")
        service_url = request.url

        #login_type = request.params.get ('login_type', '')
        # if environ['PATH_INFO'] == self.logout_path:
        #     # Let's log the user out without challenging.
        #     came_from = environ.get('came_from', '')
        #     if self.post_logout:
        #         # Redirect to a predefined "post logout" URL.
        #         destination = self.post_logout
        #     else:
        #         # Redirect to the referrer URL.
        #         script_name = environ.get('SCRIPT_NAME', '')
        #         destination = came_from or script_name or '/'
        # else:
        #if login_type == 'cas':
        if request.path == self.login_path and environ.get('repoze.who.plugins.cas'): #  and request.params.get('login_type', None)=='cas':
            log.debug ('CAS challenge redirect to %s', self.cas_login_url)
            destination =  "%s?service=%s" % (self.cas_login_url, quote_plus(service_url))
            return HTTPFound(location=destination)

        return None

    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    # IIdentifier
    def remember(self, environ, identity):
        """remember the openid in the session we have anyway"""
        log.debug("cas:remember")
        rememberer = self._get_rememberer(environ)
        r = rememberer.remember(environ, identity)
        return r

    # IIdentifier
    def forget(self, environ, identity):
        """forget about the authentication again"""
        log.debug("cas:forget")
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

    # IIdentifier
    def identify(self, environ):
        request = Request(environ)
        identity = {}

        # first test for logout as we then don't need the rest
        if request.path == self.logout_path:
            #log.debug ("cas logout:  %s " , environ)
            tokens = environ.get('REMOTE_USER_TOKENS', '')
            cas_ticket = None
            for token in tokens:
                cas_ticket = token.startswith('cas:') and token[4:]
                break
            log.debug ("logout cas ticket %s" , cas_ticket)
            if cas_ticket:
                res = Response()
                # set forget headers
                #headers = self.forget(environ, {})
                #destination = 'http://%s%s' % (environ['HTTP_HOST'], self.post_logout)
                #destination = self.post_logout
                #app = HTTPFound(location = destination, headers=headers)
                #environ['repoze.who.application'] = app
                # The above doesn't work

                for a,v in self.forget(environ,{}):
                    res.headers.add(a,v)
                res.status = 302
                logout_url = '%s%s' % (request.host_url, self.post_logout)
                res.location = "%s?service=%s" % (self.cas_logout_url, logout_url)
                environ['repoze.who.application'] = res
            return identity


        # first we check we are actually on the URL which is supposed to be the
        # url to return to (login_handler_path in configuration)
        # this URL is used for both: the answer for the login form and
        # when the openid provider redirects the user back.
        if request.path == self.login_path: #  and request.params.get('login_type', None)=='cas':
            ticket = request.params.get('ticket', None)
            log.debug ("login_path ticket=%s" , ticket)
            if ticket is None:
                res = Response()
                log.debug ('CAS challenge redirect to %s', self.cas_login_url)
                res.location =  "%s?service=%s" % (self.cas_login_url, quote_plus(request.url))
                res.status = 302
                environ['repoze.who.application'] = res
            else:
                # we are returning with a ticket set
                ticket = ticket.encode('utf-8')
                identity['tokens'] =  "cas:%s" % ticket
                identity['repoze.who.plugins.cas.ticket' ] = ticket

            #identity.update(self._validate(environ, identity))
        return identity


    def _redirect_to_loggedin (self,environ):
        request = Request(environ)
        came_from = request.params.get('came_from', '/')
        res = Response()
        res.status = 302
        res.location = came_from
        environ['repoze.who.application'] = res

    def _redirect_invalid (self,environ):

        BODY = """
<h1>Invalid User</h1>
<b>The user is invalid or not recognized for this service. Please check your authorizations or credentials </b>
<br> <a href="%s">Logout</a>
<br><a href="%s">Registration management</a>
"""  % (self.cas_logout_url, self.registration_url)

        res = Response(BODY)
        res.status = 200
        environ['repoze.who.application'] = res


    def _validate_simple(self, environ, identity):
        request = Request(environ)

        if identity.has_key('repoze.who.plugins.cas.ticket'):
            service_url = request.url
            validate_url = '%s?service=%s&ticket=%s' % (
                self.cas_validate_url,
                service_url,
                identity['repoze.who.plugins.cas.ticket'])
            #headers, response = self.http.request(validate_url)
            response = self.http.get (validate_url)
            if response.status_code == requests.codes.ok: #pylint: disable=no-member
                okayed, username = response.content.split("\n")[:2]
                log.debug ('validate got %s user %s' ,  okayed, username)
                if okayed == 'yes':
                    return username
        return None


    def _validate_saml(self, environ, identity):
        from .cas_saml import create_soap_saml, parse_soap_saml

        request = Request(environ)
        if identity.has_key('repoze.who.plugins.cas.ticket'):
            service_url = request.url
            ticket = identity['repoze.who.plugins.cas.ticket']
            url = "%s?TARGET=%s" % (self.cas_saml_validate, service_url)
            body = create_soap_saml(ticket)
            headers = { 'content-type': 'text/xml',
                        'accept' : 'text/xml',
                        'connection': 'keep-alive',
                        'cache-control': 'no-cache',
                        'soapaction' :'http://www.oasis-open.org/committees/security'}
            log.debug ("SENDING %s %s %s" , url, headers, body)
            #headers, content = self.http.request(url, method="POST", headers=headers, body=body)
            response = self.http.post (url, headers=headers, data=body)
            log.debug ("RECEIVED %s %s" , response.headers, response.content)
            found = parse_soap_saml(response.content)
            if response.status_code == requests.codes.ok and found:  #pylint: disable=no-member
                for k,v in found.items():
                    identity['repoze.who.plugins.cas.%s' % k] = v
                return found['user_id']

        return None

    #IAuthenticator
    def authenticate(self, environ, identity):
        """ Authenticate the identified user.
        """
        user_id = None
        if identity.get ('repoze.who.plugins.cas.ticket'):
            if self.cas_saml_validate:
                user_id =  self._validate_saml(environ, identity)
                log.debug ('CAS authenticate : %s' , user_id)
            # CAS validate the ticket and found the user so check if there is a local user.
            if self.validate_plugin and user_id:
                log.debug ('CAS autoregister')
                user_id = self._validate_register(environ, identity, user_id)
            del identity['repoze.who.plugins.cas.ticket']
            if user_id :
                self._redirect_to_loggedin(environ)
            else:
                self._redirect_invalid(environ)

        return user_id


    def _validate_register(self, environ, identity, user_id):
        plugin = environ['repoze.who.plugins'].get(self.validate_plugin)
        log.debug('looking for plugin %s found %s '  , self.validate_plugin, plugin)

        if plugin:
            user_name = identity["repoze.who.plugins.cas.user_id"]
            name  = user_name
            email = '%s@nowhere.org' % name

            if identity.has_key('repoze.who.plugins.cas.firstName'):
                name = identity["repoze.who.plugins.cas.firstName"]

            if identity.has_key('repoze.who.plugins.cas.lastName'):
                name = "%s %s" % (name, identity["repoze.who.plugins.cas.lastName"])

            if identity.has_key('repoze.who.plugins.cas.email'):
                email =  identity["repoze.who.plugins.cas.email"]

            validate_method = getattr (plugin, self.validate_method)
            if validate_method is None or not callable(validate_method):
                log.error ("%s is not a callable method on plugin %s", self.validate_method, self.validate_plugin)
                return None

            return validate_method(user_name, values = {
                    'display_name' : name,
                    'email_address' : email,
                    'identifier'    : 'cas',
                    #password =  illegal password so all authentication goes through openid
                    })

        log.debug('%s not found in %s. Ensure autoreg is enabled in who.ini',
                  self.validate_plugin, environ['repoze.who.plugins'])
        return None
