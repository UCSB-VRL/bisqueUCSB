# -*- coding: utf-8 -*-
"""Setup the bqcore application"""

import os
from tg import config, session, request
from paste.registry import Registry
from beaker.session import  SessionObject
from pylons.controllers.util import Request
from bq.release import __VERSION__
from bq.core import model
from bq.util.paths import config_path, defaults_path
from bq.util.bisquik2db import bisquik2db

import transaction
import logging

log = logging.getLogger('bq.boostrap')

def bootstrap(command, conf, vars):
    """Place any commands to setup bq here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    from  bq.data_service.model import Taggable, Tag, BQUser, ModuleExecution

    registry = Registry()
    registry.prepare()
    registry.register(session, SessionObject({}))
    registry.register(request, Request.blank('/bootstrap'))
    request.identity = {}

    log.info('BEGIN boostrap')
    try:
        initial_mex = ModuleExecution(mex_id = False, owner_id = False)
        initial_mex.mex = initial_mex
        initial_mex.name = "initialization"
        initial_mex.type = "initialization"
        initial_mex.hidden = True
        model.DBSession.add(initial_mex)
        model.DBSession.flush()

        admin = model.User(
            user_name = u"admin",
            display_name = config.get('bisque.admin_display_name', u'Bisque admin'))
        admin._email_address = config.get('bisque.admin_email', u'manager@somedomain.com')
        admin.password = u'admin'
        #    password = u'admin')
        #admin.password = u'admin'
        model.DBSession.add(admin)

        for g in [ u'admins', u'managers' ] :
            group = model.Group()
            group.group_name = g
            group.display_name = u'Administrators Group'
            group.users.append(admin)
            model.DBSession.add(group)

        permission = model.Permission()
        permission.permission_name = u'root'
        permission.description = u'This permission give an administrative right to the bearer'
        permission.groups.append(group)
        model.DBSession.add(permission)
        #model.DBSession.flush()
        # This commit will setup the BQUser also
        transaction.commit()

    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        #import traceback
        #print traceback.format_exc()
        transaction.abort()
        print 'Continuing with bootstrapping...'


    try:
        ######
        #
        #from bq.data_service.model import UniqueName
        initial_mex = model.DBSession.query(ModuleExecution).first()
        session['mex_id'] = initial_mex.id
        #request.identity['bisque.mex_id'] = initial_mex.id


        admin = model.DBSession.query(BQUser).filter_by(resource_name = 'admin').first()
        admin.mex_id = initial_mex.id
        initial_mex.owner = admin
        session['user'] = admin


        system = model.DBSession.query(Taggable).filter_by (resource_type='system').first()
        if system is None:
            system_prefs = defaults_path('preferences.xml.default')
            if os.path.exists(system_prefs):
                with open (system_prefs) as f:
                    system = bisquik2db (f)
                    system.permission = 'published'
            else:
                print( "Couldn't find %s: using minimal default preferences" % system_prefs)
                system = Taggable(resource_type = 'system')
                version = Tag(parent = system)
                version.name ='version'
                version.value  = __VERSION__
                prefs = Tag(parent = system)
                prefs.name = 'Preferences'
            model.DBSession.add(system)
            transaction.commit()



    except IntegrityError:
        log.exception ( 'Warning, there was a problem adding your system object, it may have already been added:')
        #import traceback
        #print traceback.format_exc()
        transaction.abort()
        log.warning ( 'Continuing with bootstrapping...' )

    log.info('END boostrap')


    # <websetup.bootstrap.after.auth>
