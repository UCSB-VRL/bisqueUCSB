import logging
from paste.httpheaders import AUTHORIZATION #pylint: disable=no-name-in-module
from paste.deploy.converters import asbool
from repoze.who.interfaces import IIdentifier
from zope.interface import implements
from tg import config

from bq.core.model import DBSession

log = logging.getLogger("bq.mex_auth")

class MexAuthenticatePlugin(object):

    implements(IIdentifier)

    def identify(self, environ):
        """Lookup the owner """
        # New way using standard Authencation header
        # Authentication: Mex user_id mex_token
        authorization = AUTHORIZATION(environ)
        try:
            auth = authorization.split(' ')
        except ValueError: # not enough values to unpack
            auth =  None

        if auth and auth[0].lower() == 'mex':
            log.debug ("MexIdentify %s" , auth)
            try:
                user, token = auth[1].split(':')
                return { 'bisque.mex_user': user, 'bisque.mex_token' : token}
            except ValueError:
                pass

        # OLD Way using custom header  (deprecated)
        mexheader = environ.get('HTTP_MEX', None)
        if  mexheader:
            try:
                # OLD code may ship a NEW token with the OLD header.
                user, token = mexheader.split(':')
                return { 'bisque.mex_user': user, 'bisque.mex_token' : token }
            except ValueError:
                return { 'bisque.mex_token' : mexheader }
        return None


    def remember(self, environ, identity):
        pass
    def forget(self, environ, identity):
        pass
    def authenticate(self, environ, identity):
        try:
            mex_token = identity['bisque.mex_token']
        except KeyError:
            return None

        if not asbool(config.get('bisque.has_database')):
            environ['repoze.what.credentials'] = { 'repoze.who.userid': mex_token }
            identity ['bisque.mex_auth'] = "%s:%s" % (identity.get('bisque.mex_user') , mex_token)
            log.debug ("NO DB mex_auth=%s", identity['bisque.mex_auth'])
            return mex_token

        from bq.data_service.model import ModuleExecution
        log.debug("MexAuthenticate:auth %s" , identity)
        try:
            mex_id = int(mex_token)
            mex = DBSession.query(ModuleExecution).get(mex_id)
        except ValueError:
            mex = DBSession.query(ModuleExecution).filter_by (resource_uniq = mex_token).first()


        # NOTE: Commented out during system debugging
        #
        #if  mex.closed():
        #    log.warn ('attempt with  closed mex %s' % mex_id)
        #    return None
        if mex:
            identity['bisque.mex'] = mex
            #owner = identity.get ('bisque.mex_user') or mex.owner.tguser.user_name
            owner =  mex.owner.tguser.user_name
            identity ['bisque.mex_auth'] = '%s:%s' % (owner, mex_token)
            request_owner = identity.get ('bisque.mex_user')
            if request_owner is not None and owner != request_owner:
                log.error ("Mex with bad owner reuqest %s != mex %s", request_owner, owner)
                return None

            log.info ("MEX_IDENTITY %s->%s"  ,mex_token, owner)
            return owner
        log.warn("Mex authentication failed due to invalid mex %s" , mex_token)
        return None

    #def challenge(self, environ, status, app_headers, forget_headers):
    #    pass


def make_plugin():
    return MexAuthenticatePlugin()
