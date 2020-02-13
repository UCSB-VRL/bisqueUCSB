from zope.interface import implements
from repoze.who.interfaces import IAuthenticator

class OpenIDAuth(object):
    implements(IAuthenticator)

    key_map = {
        # maps identity : sreg keys
        'display_name': 'fullname',
        'user_name': 'nickname',
        'email_address': 'email',
    }

    def __init__(self, auto_register=None):
        self.auto_register = auto_register

    def _auto_register(self, environ, identity, user_name):
        registration = environ['repoze.who.plugins'].get(self.auto_register)
        self.log.debug('looking for %s found %s ' % (self.auto_register, registration))

        if registration:
            name = user_name
            if identity.has_key('repoze.who.plugins.openid.firstname'):
                name = identity["repoze.who.plugins.openid.firstname"][0]

            if identity.has_key('repoze.who.plugins.openid.lastname'):
                name = "%s %s" % (name, identity["repoze.who.plugins.openid.lastname"][0])

            email = 'unknown@nowhere.org'
            if identity.has_key('repoze.who.plugins.openid.email'):
                email =  identity["repoze.who.plugins.openid.email"][0]
            return registration.register_user(user_name, values = {
                    'display_name' : name,
                    'email_address' : email,
                    'identifier'    : 'openid',
                    #password =  illegal password so all authentication goes through openid
                    })
        else:
            self.log.debug('%s not found in %s' % (self.auto_register, environ['repoze.who.plugins']))
        return user_name

    def authenticate(self, environ, identity):
        if environ['repoze.who.logger'] is not None:
            self.log =  environ['repoze.who.logger']

        if identity.has_key("repoze.who.plugins.openid.email"):
            self.log.info('authenticated email: %s ' %identity['repoze.who.plugins.openid.email'])
            userid =  identity["repoze.who.plugins.openid.email"]
            name,address = userid[0].split('@')

            try:
                if self.auto_register:
                    name = self._auto_register(environ, identity, name)
            except Exception:
                self.log.exception("problem in autoreg")

            return name

        if identity.has_key("repoze.who.plugins.openid.userid"):
            self.log.info('authenticated : %s ' %identity['repoze.who.plugins.openid.userid'])
            return identity["repoze.who.plugins.openid.userid"]

    def as_user_values( self, values, identity ):
        """Given sreg values, convert to User properties"""
        for id_key,sreg_key in self.key_map.items():
            value = values.get( sreg_key )
            if value is not None:
                identity[id_key] = value
        return identity
    def add_metadata( self, environ, identity ):
        """Add our stored metadata to given identity if available"""
        key = identity.get('repoze.who.plugins.openid.userid')
        if key:
            values = self.key_map.get( key )
            if values:
                identity = self.as_user_values( values, identity )
        return identity



def make_plugin(auto_register=None):
    return OpenIDAuth(auto_register)
