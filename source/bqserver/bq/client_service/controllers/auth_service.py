###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007,2008                                               ##
##      by the Regents of the University of California                       ##
##                            All rights reserved                            ##
##                                                                           ##
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
from datetime import datetime, timedelta

from lxml import etree
import transaction

import tg
from tg import request, session, flash, require, response
from tg import  expose, redirect, url
from tg import config
from pylons.i18n import ugettext as  _
from repoze.what import predicates

from bq.core.service import ServiceController
from bq.core import identity
from bq.core.model import DBSession
from bq.data_service.model import   User
from bq import module_service
from bq.util.urlutil import update_url
from bq.util.xmldict import d2xml
from bq.exceptions import ConfigurationError


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
        return etree.tostring (d2xml ({ 'providers' : self.login_map()} ))

    @expose()
    def login_check(self, came_from='/', login='', **kw):
        log.debug ("login_check %s from=%s " , login, came_from)
        login_urls = self.login_map()
        default_login = login_urls.values()[-1]
        if login:
            # Look up user
            user = DBSession.query (User).filter_by(user_name=login).first()
            # REDIRECT to registration page?
            if user is None:
                redirect(update_url(default_login['url'], dict(username=login, came_from=came_from)))
            # Find a matching identifier
            login_identifiers = [ g.group_name for g in user.groups ]
            for identifier in login_urls.keys():
                if  identifier in login_identifiers:
                    login_url  = login_urls[identifier]['url']
                    log.debug ("redirecting to %s handler" , identifier)
                    redirect(update_url(login_url, dict(username=login, came_from=came_from)))

        log.debug ("using default login handler %s" , default_login)
        redirect(update_url(default_login, dict(username=login, came_from=came_from)))


    @expose('bq.client_service.templates.login')
    def login(self, came_from='/', username = '', **kw):
        """Start the user login."""
        login_counter = int (request.environ.get ('repoze.who.logins', 0))
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        # Check if we have only 1 provider that is not local and just redirect there.
        login_urls = self.login_map()
        if len(login_urls) == 1:
            provider, entries =  login_urls.items()[0]
            if provider != 'local':
                redirect (update_url(entries['url'], dict(username=username, came_from=came_from)))

        return dict(page='login', login_counter=str(login_counter), came_from=came_from, username=username,
                    providers_json = json.dumps (login_urls), providers = login_urls )

    #@expose ()
    #def login_handler(self, **kw):
    #    log.debug ("login_handler %s" % kw)
    #    return self.login(**kw)

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
        log.debug ('POST_LOGIN')
        if not request.identity:
            login_counter = int (request.environ.get('repoze.who.logins',0)) + 1
            redirect(url('/auth_service/login',params=dict(came_from=came_from, __logins=login_counter)))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        self._begin_mex_session()
        timeout = int (config.get ('bisque.login.timeout', '0').split('#')[0].strip())
        length = int (config.get ('bisque.login.session_length', '0').split('#')[0].strip())
        if timeout:
            session['timeout']  = timeout
        if length:
            session['expires']  = (datetime.utcnow() + timedelta(seconds=length))
            session['length'] = length

        session.save()
        log.debug ("Current session %s" , str( session))
        transaction.commit()
        redirect(came_from)


    # This function is never called but used as token to recognize the logout
    # @expose ()
    # def logout_handler(self, **kw):
    #     log.debug ("logout %s" % kw)
    #     #session = request.environ['beaker.session']
    #     #session.delete()
    #     try:
    #         self._end_mex_session()
    #         session.delete()
    #     except Exception:
    #         log.exception("logout")

    #     redirect ('/')

    #@expose ()
    #def logout_handler(self, **kw):
    #    log.debug ("logout_handler %s" % kw)


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
        return etree.tostring(response)



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
        return etree.tostring(sess)


    @expose(content_type="text/xml")
    @require(predicates.not_anonymous())
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
    @require(predicates.not_anonymous())
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




def initialize(url):
    service =  AuthenticationServer(url)
    return service


__controller__ = AuthenticationServer
__staticdir__ = None
__model__ = None
