import logging
import transaction
from sqlalchemy.exc import SQLAlchemyError, DatabaseError
from zope.interface import implements
from repoze.who.interfaces import IMetadataProvider #, IAuthenticator

from bq.core import model

log = logging.getLogger('auth.autoreg')

class AutoRegister (object):
    """This plugin attempts to register users that are so far unknown
    to the system.  During the metadata phase it looks to see if the user
    name is currently known and if  not so will create a local user structure
    """
    implements(IMetadataProvider)

    def __init__( self ):
        """Create autoregister metadata provider to create local users
        structures.

        """

    def login_group (self, login_identifier):
        log.debug ('login_group')
        g = model.DBSession.query(model.Group).filter_by(group_name = login_identifier).first()
        if g is None:
            g = model.Group()
            g.group_name = login_identifier
            g.display_name = u'%s Group' % login_identifier
            model.DBSession.add(g)
        return g

    def validate_user(self, user_name, values ):
        name_match = model.User.by_user_name( user_name )
        if name_match is not None:
            log.info("found existing user: name %s by user %s " ,  user_name, str(name_match))
            return user_name
        return None

    def register_user( self, user_name, values ):
        """Attempt to register the user locally"""
        name_match = model.User.by_user_name( user_name )
        if name_match is not None:
            log.info("found existing user: name %s by user %s " , user_name, str(name_match))
            return user_name

        email_match=  values.get('email_address') and model.User.by_email_address(values['email_address'])
        if email_match is not None:
            log.info("found existing user: name %s (%s) by email %s " ,  user_name, email_match.user_name, str(email_match))
            return email_match.user_name

        identifier = values.pop('identifier', None)
        try:
            log.info("adding user %s with %s" ,  user_name, values )

            u = model.User(user_name = user_name,
                           display_name = values.get('display_name'),
                           email_address = values.get('email_address'))

            model.DBSession.add(u)
            if identifier:
                g = self.login_group(identifier)
                g.users.append(u)
            transaction.commit()
            return user_name
        except (SQLAlchemyError, DatabaseError) as e:
            log.exception('problem with autoreg %s', e)
        return None

    def add_metadata( self, environ, identity ):
        """Add our stored metadata to given identity if available"""
        user = identity.get('repoze.who.userid', None)
        log.debug ("metadata with user: %s" ,  user)
        try:
            from bq.data_service.model import BQUser
            if user:
                bquser =  model.DBSession.query (BQUser).filter_by(resource_name = user).first()
                identity['bisque.bquser'] = bquser
                #log.debug ("adding %s to identity %s" ,  bquser, identity)
        except ImportError:
            pass
        return identity
