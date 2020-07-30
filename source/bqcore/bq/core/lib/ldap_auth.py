import logging
import re
from base64 import b64decode #b64encode


from repoze.who.plugins.ldap import LDAPSearchAuthenticatorPlugin #pylint: disable=no-name-in-module


# Optional dependency
import ldap #pylint: disable=import-error

bqlog = logging.getLogger('bq.ldap')


def retry(fn, args = (), kw = {}, count=2, exc=Exception, recover = int):
    for tries in range(count):
        try:
            return fn (*args, **kw)
        except exc as e:
            if tries == count:
                raise
            recover(*args, **kw)

class LDAPAuthenticatorPluginExt(LDAPSearchAuthenticatorPlugin):
    """ Special Bisque LDAP authenticator:

    - Authenticates against LDAP.
    - Combined Authenticator and metadata
    - Refreshes connection if stale.
    - Denies anonymously-authenticated users
    - will register (add user) if autoregister is set

    """
    dnrx = re.compile('<dn:(?P<b64dn>[A-Za-z0-9+/]+=*)>')



    def __init__(self, ldap_connection, base_dn,
                 auto_register = None,
                 attributes=None,
                 filterstr='(objectClass=*)',
                 **kw):
        self.uri = ldap_connection
        if hasattr(attributes, 'split'):
            attributes = attributes.split(',')
        elif hasattr(attributes, '__iter__'):
            # Converted to list, just in case...
            attributes = list(attributes)
        elif attributes is not None:
            raise ValueError('The needed LDAP attributes are not valid')
        self.attributes = attributes
        self.filterstr = filterstr
        self.auto_register = auto_register

        # The following option was need to login to certain ldaps servers
        # http://stackoverflow.com/questions/7716562/pythonldapssl
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)  #pylint: disable=no-member
        super(LDAPAuthenticatorPluginExt, self).__init__( ldap_connection, base_dn, **kw)


    def _add_metadata(self, environ, identity):
        """
        Add metadata about the authenticated user to the identity.

        It modifies the C{identity} dictionary to add the metadata.

        @param environ: The WSGI environment.
        @param identity: The repoze.who's identity dictionary.

        """
        # Search arguments:
        dnmatch = self.dnrx.match(identity.get('userdata',''))
        if dnmatch:
            dn = b64decode(dnmatch.group('b64dn'))
        else:
            dn = identity.get('repoze.who.userid')
        args = (
            dn,
            ldap.SCOPE_BASE, #pylint: disable=no-member
            self.filterstr,
            self.attributes
        )
        if self.bind_dn:
            try:
                self.ldap_connection.bind_s(self.bind_dn, self.bind_pass)
            except ldap.LDAPError: #pylint: disable=no-member
                raise ValueError("Couldn't bind with supplied credentials")
        try:
            attributes = self.ldap_connection.search_s(*args)
        except ldap.LDAPError, msg: #pylint: disable=no-member
            environ['repoze.who.logger'].warn('Cannot add metadata: %s' % msg)
            raise Exception("Cannot fetch metatdata %s" % msg)
        else:
            identity.update(attributes[0][1])
            return attributes[0][1]



    def _auto_register(self, environ, identity):
        """ Autoregister the user by passing looking up user metadata
        and passing to the autoregister plugin if available.
        """
        log  = environ.get('repoze.who.logger', bqlog)
        register = environ['repoze.who.plugins'].get(self.auto_register)
        log.debug('looking for %s found %s ' % (self.auto_register, register))

        userdata = identity.get('userdata', '')
        dnmatch = self.dnrx.match(userdata)
        if dnmatch:
            dn = b64decode(dnmatch.group('b64dn'))
            log.debug ('LDAP: found DN %s' % dn)
        else:
            log.error ('Could not parse userdata  %s' % userdata)
            return

        log.debug ('LDAP:add_metadata userdata %s' % userdata)
        r = identity['login']
        if register and userdata:
            log.debug('metadata identity=%s' % userdata)
            retry (self._add_metadata, args = (environ, identity),
                   recover=self.reconnect,
                   exc = ldap.LDAPError) #pylint: disable=no-member
            log.debug ('LDAP metadata %s' % r)
            info = dict((attr, identity[attr]) for attr in self.attributes)
            info .update ( { 'display_name' : info.get('cn', [r])[0],
                             'email_address' : info.get('mail', [None])[0],
                             'identifier'    : 'ldap' } )

            r = register.register_user (r, info)
            #identity['repoze.who.userid'] = r
        return r

    def reconnect(self,environ, identity):
        log  = environ.get('repoze.who.logger', bqlog)
        log.warn( "FAILED TO CONNECT TO LDAP 1 : " )
        log.warn( "Retrying...")
        self.ldap_connection = ldap.initialize(self.uri)

    def _authenticate (self, environ, identity):
        return super(LDAPAuthenticatorPluginExt, self).authenticate(
            environ, identity)

    def authenticate(self, environ, identity):
        """ Authenticate the user and password against the LDAP
        server if available

        Extending the repoze.who.plugins.ldap plugin to make it much
        more secure.
        """
        log  = environ.get('repoze.who.logger', bqlog)
        log.debug ("LDAP:authenticate %s" % identity)
        res = None
        # This is unbelievable.  Without this, ldap will
        # let you bind anonymously
        if not identity.get('password', None):
            return None
        #try:
        #    dn = self._get_dn(environ, identity)
        #except (KeyError, TypeError, ValueError):
        #    return None

        res = retry(self._authenticate, args = (environ, identity),
                    recover = self.reconnect,
                    exc = ldap.LDAPError) #pylint: disable=no-member

        if self.auto_register is not None and res is not None:
            res = self._auto_register (environ, identity)
            log.debug ('LDAP:authenticated user=%s' % res)

        return res
