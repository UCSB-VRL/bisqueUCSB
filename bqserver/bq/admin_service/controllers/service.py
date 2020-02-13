###############################################################################
##  Bisquik                                                                  ##
##  Center for Bio-Image Informatics                                         ##
##  University of California at Santa Barbara                                ##
## ------------------------------------------------------------------------- ##
##                                                                           ##
##     Copyright (c) 2007 by the Regents of the University of California     ##
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

"""
import copy
import json
import logging
#import operator
import os
import string
#from datetime import datetime
from urllib import  unquote
#import io
#import itertools
#import mmap


import transaction
from lxml import etree
from pylons.controllers.util import abort, redirect
from repoze.what.predicates import Any, in_group
#from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from tg import (config,  expose,   request, response)

from bq import data_service
from bq.client_service.controllers import notify_service
from bq.core.identity import get_username, set_current_user
from bq.core.model import DBSession, Group, User  # , Visit
from bq.core.service import ServiceController
from bq.data_service.model import BQUser, Image, TaggableAcl
from bq.data_service.controllers.formats import find_inputer, find_formatter
#from bq.util.bisquik2db import bisquik2db, db2tree
from bq.util.paths import data_path
from bq.util import urlutil

#from bq.image_service.model import  FileAcl


log = logging.getLogger('bq.admin')

#from tgext.admin import AdminController
#class BisqueAdminController(AdminController):
#    'admin controller'
#    allow_only = Any (in_group("admin"), in_group('admins'))

# reading log file

if os.name != 'nt':
    def tail(fn, n=10):
        cmd = 'tail -n {1} {0}'.format(fn, n)
        return os.popen(cmd).readlines()

elif os.name == 'nt':
    def tail(fn, n=10, _buffer=4098):
        """Tail a file and get X lines from the end"""
        # place holder for the lines found
        lines_found = []

        with open(fn, 'rb') as f:
            # block counter will be multiplied by buffer
            # to get the block size from the end
            block_counter = -1

            # loop until we find X lines
            while len(lines_found) < n:
                try:
                    f.seek(block_counter * _buffer, os.SEEK_END)
                except IOError:  # either file is too small, or too many lines requested
                    f.seek(0)
                    lines_found = f.readlines()
                    break

                lines_found = f.readlines()

                # we found enough lines, get out
                if len(lines_found) > n:
                    break

                # decrement the block counter to get the
                # next X bytes
                block_counter -= 1

            return lines_found[-n:]

# Tags that used but not be stored as part of the BQUser record
REMOVE_TAGS = [ 'user_name', 'password', 'email', 'groups' ]

class AdminController(ServiceController):
    """
        The admin controller is a central point for
        adminstrative tasks such as monitoring, data, user management, etc.
    """
    service_type = "admin"

    allow_only = Any(in_group("admin"), in_group('admins'))
    #allow_only = is_user('admin')

    #admin = BisqueAdminController([User, Group], DBSession)
    @expose ("bq.admin_service.templates.manager")
    def manager(self):
        return dict()


    @expose(content_type='text/xml')
    def _default(self, *arg, **kw):
        """
            Returns some command information
        """
        log.info('admin/index')
        index_xml = etree.Element('resource', uri=str(request.url))
        users_xml = etree.SubElement(index_xml,'command', name='user', value='Lists all the users')
        users_xml = etree.SubElement(index_xml,'command', name='user/RESOURCE_UNIQ', value='Lists the particular user')
        users_xml = etree.SubElement(index_xml,'command', name='user/RESOURCE_UNIQ/login', value='Log in as user')

        etree.SubElement(index_xml,'command', name='notify_users', value='sends message to all users')
        etree.SubElement(index_xml,'command', name='message_variables', value='returns available message variables')
        return etree.tostring(index_xml)

    @expose(content_type='text/xml')
    def notify_users(self, *arg, **kw):
        """
          Sends message to all system users
        """
        log.info("notify_users")
        if request.method.upper() == 'POST' and request.body is not None:
            try:
                resource = etree.fromstring(request.body)
                message = resource.find('tag[@name="message"]').get ('value')
                userlist = resource.find('tag[@name="users"]').get('value')
                self.do_notify_users(userlist, message)
                return '<resource type="message" value="sent" />'
            except Exception:
                log.exception ("processing message")
                return abort(400, 'Malformed request document')

        abort(400, 'The request must contain message body')

    @expose(content_type='text/xml')
    def message_variables(self, **kw):
        """
          Sends message to all system users
        """
        log.info("message_variables")
        variables = self.get_variables()
        resp = etree.Element('resource', name='message_variables')
        for n,v in variables.iteritems():
            etree.SubElement(resp, 'tag', name=n, value=v)
        return etree.tostring(resp)

    def add_admin_info2node(self, user_node, view=None):
        """
            adds email and password tags and remove the email value
        """
        if view and 'short' not in view:
            tg_user = User.by_user_name (user_node.get('name'))
            email = user_node.attrib.get('value', '')
            etree.SubElement(user_node, 'tag', name='email', value=email)
            if tg_user is None:
                log.error ("No tg_user was found for %s", user_node.get ('name'))
            else:
                if 'password' in view:
                    password = tg_user.password
                else:
                    password ='******'
                etree.SubElement(user_node, 'tag', name='password', value=password)
                etree.SubElement(user_node, 'tag', name="groups", value=",".join (g.group_name for g in tg_user.groups if tg_user))
                etree.SubElement(user_node, 'tag', name='user_name', value=tg_user.user_name)


        #try to remove value from user node
        user_node.attrib.pop('value', None)

        return user_node

    #@expose(content_type='text/json')
    @expose()
    def loggers(self, *arg, **kw):
        """
        Set logging level dynamically
        post /admin/loggers
        """
        view = kw.pop ('view', 'short')
        fmt = kw.pop ('format', 'xml')
        #filter = kw.pop ('filter', 'bq.')
        if fmt == 'json':
            response.headers['Content-Type']  = 'text/json'
        elif fmt == 'xml':
            response.headers['Content-Type']  = 'text/xml'

        if request.method == 'GET':
            loggers = [ {'name': ln, 'level': logging.getLevelName (lv.level)}
                        for ln, lv in logging.Logger.manager.loggerDict.items()
                        if hasattr (lv, 'level') #and lv.level != logging.NOTSET
            ]

            # filter and sort loggers
            loggers.sort(key=lambda x: x['name'])

            if fmt == 'json':
                return json.dumps (loggers)
            elif fmt == 'xml':
                xml = etree.Element('resource', name='loggers', uri='/admin/loggers')
                for l in loggers:
                    etree.SubElement(xml, 'logger', name=l.get('name'), value=l.get('level'))
                return etree.tostring(xml)

        elif request.method in ('POST', 'PUT'):

            if request.headers['Content-Type'] == 'text/json':
                loggers = json.loads (request.body)
            else:
                xml = etree.fromstring(request.body)
                loggers = [{'name': l.get('name'), 'level': l.get('value')} for l in xml.xpath('logger')]

            for l in loggers:
                ln = l.get('name')
                lv = l.get('level')
                log.debug ("Changing log level of %s to %s", ln, lv)
                lg = logging.getLogger(ln)
                lg.setLevel (lv)
            return ""

    @expose()
    def logs(self, *arg, **kw):
        """
        get /admin/logs/config or /admin/logs - log config, this will return a local or a remote url
        get /admin/logs/read - read local log lines, by default 1000 last lines
        get /admin/logs/read/172444095 - read local log lines starting from a given time stamp
        """

        # TODO dima: add timestamp based read

        #log.info ("STARTING table (%s): %s", datetime.now().isoformat(), request.url)
        path = request.path_qs.split('/')
        path = [unquote(p) for p in path if len(p)>0]
        operation = path[2] if len(path)>2 else ''

        log_url = config.get ('bisque.logger')

        if operation == 'config' or operation == '':
            # dima: here we have to identify what kind of logs we are using
            if log_url is not None:
                log_url = urlutil.urljoin (request.url, log_url)
                xml = etree.Element('log', name='log', uri=log_url, type='remote')
            else:
                xml = etree.Element('log', name='log', uri='/admin/logs/read', type='local')
            response.headers['Content-Type']  = 'text/xml'
            return etree.tostring(xml)
        elif operation == 'read':
            # dima, this will only work for local logger
            if log_url is not None:
                redirect(log_url)
            try:
                fn = logging.getLoggerClass().root.handlers[0].stream.filename
                logs = tail(fn, 1000)
                response.headers['Content-Type']  = 'text/plain'
                return ''.join(logs)
            except Exception:
                abort(500, 'Error while reading the log' )
        abort(400, 'not a supported operation' )

    @expose(content_type='text/xml')
    def cache(self, *arg, **kw):
        """
            Deletes system cache

            DELETE cache
        """
        if request.method == 'DELETE':
            return self.clearcache()
        return '<resource/>'


    @expose(content_type='text/xml')
    def user(self, *arg, **kw):
        """
            Main user expose

            Merges the shadow user with the normal user for admins easy access to the password
            columns

            GET user: returns list of all users in xml info see get_all_users for format

            GET user/uniq: returns user in xml info see get_user for format

            GET user/uniq/login: logins in the admin as the user resource provided

            POST user: creates new user, see post_user for format

            PUT user/uniq: update info on user see put_user for format

            DELETE user/uniq: deletes user, see delete user for format

            DELETE user/uniq/image
                Deletes only the users image data and not the user itself
        """
        http_method = request.method.upper()

        if len(arg)==1:
            if http_method == 'GET':
                return self.get_user(arg[0], **kw)
            elif http_method == 'PUT':
                if request.body:
                    return self.put_user(arg[0], request.body, **kw)
            elif request.method == 'DELETE':
                return self.delete_user(arg[0])
            else:
                abort(400)
        elif len(arg)==2:
            if arg[1]=='login':
                if http_method == 'GET':
                    return self.loginasuser(arg[0])
            elif arg[1]=='image':
                if http_method == 'DELETE':
                    uniq = arg[0]
                    bquser = data_service.resource_load(uniq=uniq)
                    #bquser = DBSession.query(BQUser).filter(BQUser.resource_uniq == uniq).first()
                    if bquser:
                        self.deleteimages(bquser.get ('name'), will_redirect=False)
                        return '<resource name="delete_images" value="Successful">'
                    else:
                        abort(404)
        else:
            if http_method == 'GET':
                return self.get_all_users(*arg, **kw)
            elif http_method == 'POST':
                if request.body:
                    return self.post_user(request.body, **kw)
        abort(400)


    def get_all_users(self, *arg, **kw):
        """
            Returns a list of all users in xml with password and diplay name.
            (Note: may be removed in version 0.6 due to redundant functionality
            of data_service)

            Limited command support, does not have view=deep,clean..

            document format:
                <resource>
                    <user name="user" owner="/data_service/00-aYnhJQA5BJVm4GDpuexc2G" permission="published"
                    resource_uniq="00-aYnhJQA5BJVm4GDpuexc2G" ts="2015-01-30T02:23:18.414000" uri="admin/user/00-aYnhJQA5BJVm4GDpuexc2G">
                        <tag name="email" value="myemail@email.com"/>
                        <tag name="display_name" value="user"/>
                    </user>
                    <user>...
                </resource>
        """

        kw['wpublic'] = 1
        users =  data_service.query(resource_type = 'user', **kw)
        view = kw.pop('view', None)
        resource = etree.Element('resource', uri=str(request.url))
        for u in users:
            user = self.add_admin_info2node(u, view)
            resource.append(user)
        return etree.tostring(resource)


    def get_user(self, uniq, **kw):
        """
            Returns requested user in xml with password and diplay name.
            (Note: may be removed in version 0.6 due to redundant functionality
            of data_service)

            document format:
                <user name="user" owner="/data_service/00-aYnhJQA5BJVm4GDpuexc2G" permission="published"
                resource_uniq="00-aYnhJQA5BJVm4GDpuexc2G" ts="2015-01-30T02:23:18.414000" uri="/data_service/00-aYnhJQA5BJVm4GDpuexc2G">
                    <tag name="email" value="myemail@email.com"/>
                    <tag name="display_name" value="user"/>
                    <tag name="password" value="******"/> //everything will be served in plan text no password will be returned
                    ...
                </user>
        """
        view=kw.pop('view', 'short')
        user = data_service.resource_load(uniq, view=view)
        if user is not None and user.tag =='user':
            user = self.add_admin_info2node(user, view)
            return etree.tostring(user)
        else:
            abort(403)

    def _update_groups(self, tg_user, groups):
        """
        @param tg_user : a tg User
        @param a list of group names
        """
        tg_user.groups = []
        for grp_name in groups:
            if not grp_name:
                continue
            grp  = DBSession.query (Group).filter_by (group_name = grp_name).first()
            if grp is None:
                log.error ("Unknown group %s used ", grp_name)
                continue
            tg_user.groups.append(grp)
        log.debug ("updated groups %s", tg_user.groups)


    def post_user(self, doc, **kw):
        """
            Creates new user with tags, the owner of the tags is assigned to the user

            document format:
                <user name="user">
                    <tag name="password" value="12345"/>
                    <tag name="email" value="myemail@email.com"/>
                    <tag name="display_name" value="user"/>
                </user>
        """
        userxml = etree.fromstring(doc)
        required_tags = ['user_name','password', 'email', 'display_name']
        tags = {}
        if userxml.tag == 'user':
            user_name = userxml.attrib['name']
            if user_name:
                tags['user_name'] = user_name
                for t in userxml.xpath('tag'):
                    tags[t.get('name')] = t.get('value')
                    #if (t.attrib['name']=='password') or (t.attrib['name']=='email'):
                    if t.get('name') in REMOVE_TAGS:
                        t.getparent().remove(t) #removes email and password
                        if t.attrib['name'] == 'email':
                            userxml.attrib['value'] = t.attrib['value'] #set it as value of the user
                if all(k in tags for k in required_tags):
                    log.debug("ADMIN: Adding user: %s" , str(user_name))
                    u = User(user_name=tags['user_name'], password=tags['password'], email_address=tags['email'], display_name=tags['display_name'])
                    DBSession.add(u)
                    self._update_groups(u, tags.get ('groups', '').split (','))
                    try:
                        transaction.commit()
                    except IntegrityError:
                        abort(405, 'Another user already has this user name or email address')
                    #r = BQUser.query.filter(BQUser.resource_name == tags['user_name']).first()
                    r = data_service.query(resource_type='user', name=tags['user_name'], wpublic=1)
                    if len(r)>0:
                        admin = get_username() #get admin user
                        set_current_user(tags['user_name']) #change document as user so that all changes are owned by the new user
                        r = data_service.update_resource('/data_service/%s'%r[0].attrib.get('resource_uniq'), new_resource=userxml)
                        set_current_user(admin) #set back to admin user
                        return self.get_user('%s'%r.attrib.get('resource_uniq'), **kw)
                    else:
                        abort(400)
        abort(400)


    def put_user(self, uniq, doc, **kw):
        """
            update user

            @param: uniq - resource uniq for the user
            @param: doc - document in the format shown below

            document format:
                <user name="user" resource_uniq="00-1235218954">
                    <tag name="password" value="12345"/> or <tag name="password" value="******"/>
                    <tag name="email" value="myemail@email.com"/>
                    <tag name="display_name" value="user"/>
                </user>
        """
        userxml = etree.fromstring(doc)
        required_tags = ['user_name','password', 'email', 'display_name']
        tags = {}
        if userxml.tag == 'user':
            user_name = userxml.attrib.get('name')
            if user_name:
                #tags['user_name'] = user_name
                for t in userxml.xpath('tag'):
                    tags[t.get ('name')] = t.get('value')
                    #if t.attrib['name'] == 'password' or t.attrib['name']=='email':
                    if t.get('name') in REMOVE_TAGS:
                        t.getparent().remove(t) #removes email and password
                        if t.attrib['name'] == 'email':
                            userxml.attrib['value'] = t.attrib.get('value') #set it as value of the user

                if all(k in tags for k in required_tags): #checks to see if all required tags are present
                    #update tg_user
                    #tg_user = DBSession.query(User).filter(User.user_name == tags.get('user_name')).first()
                    #tg_user = User.by_user_name(tags.get('user_name'))
                    tg_user = User.by_user_name(user_name)
                    if not tg_user:
                        log.debug('No user was found with name of %s. Please check core tables?',  user_name)
                        abort(404)
                    #reset values on tg user
                    tg_user.email_address = tags.get("email", tg_user.email_address)

                    if tags['password'] and tags['password'].count('*') != len(tags['password']): #no password and ***.. not allowed passwords
                        tg_user.password = tags.get("password", tg_user.password) #just set it as itself if nothing is provided
                    #else:
                    #    tags.pop("password", None) #remove the invalid password

                    tg_user.display_name = tags.get("display_name", tg_user.display_name)
                    self._update_groups(tg_user, tags.get ('groups', '').split(','))
                    if tags.get ('user_name') != user_name:
                        tg_user.user_name = tags.get ('user_name')
                        userxml.set ('name' , tags['user_name'])
                    #del tags['user_name']

                    log.debug("ADMIN: Updated user: %s" , str(user_name))
                    transaction.commit()
                    ### ALL loaded variables are detached

                    #userxml.attrib['resource_uniq'] = r.attrib['resource_uniq']
                    #reset BQUser
                    admin = get_username() #get admin user
                    set_current_user(tags['user_name']) #change document as user so that all changes are owned by the new user
                    r = data_service.update_resource(resource=userxml, new_resource=userxml, replace=True)
                    log.debug ("Sent XML %s", etree.tostring (userxml))
                    set_current_user(admin) #set back to admin user
                    #DBSession.flush()
                    return self.get_user(r.attrib['resource_uniq'], **kw)
        abort(400)


    def delete_user(self, uniq):
        """
            Deletes user

            @param uniq - resource uniq for the user

        """
        # Remove the user from the system for most purposes, but
        # leave the id for statistics purposes.
        bquser = DBSession.query(BQUser).filter(BQUser.resource_uniq == uniq).first()
        if bquser:
            log.debug("ADMIN: Deleting user: %s" , str(bquser) )
            user = DBSession.query(User).filter (User.user_name == bquser.resource_name).first()
            log.debug ("Renaming internal user %s" , str(user))

            if user:
                DBSession.delete(user)
                # delete the access permission
                for p in DBSession.query(TaggableAcl).filter_by(user_id=bquser.id):
                    log.debug ("KILL ACL %s" ,  str(p))
                    DBSession.delete(p)
                self.deleteimages(bquser.resource_name, will_redirect=False)
                #DBSession.delete(bquser)

                #transaction.commit()
            data_service.del_resource(bquser)
            return '<resource>Delete User</resource>'

        abort(400)


    def deleteimage(self, imageid=None, **kw):
        log.debug("image: %s " , str(imageid) )
        image = DBSession.query(Image).filter(Image.id == imageid).first()
        DBSession.delete(image)
        transaction.commit()
        redirect(request.headers.get("Referer", "/"))


    def deleteuser(self, username=None,  **kw):
        #DBSession.autoflush = False

        # Remove the user from the system for most purposes, but
        # leave the id for statistics purposes.
        user = DBSession.query(User).filter (User.user_name == username).first()
        log.debug ("Renaming internal user %s" , str( user))
        if user:
            DBSession.delete(user)
            #user.display_name = ("(R)" + user.display_name)[:255]
            #user.user_name = ("(R)" + user.user_name)[:255]
            #user.email_address = ("(R)" + user.email_address)[:16]

        user = DBSession.query(BQUser).filter(BQUser.resource_name == username).first()
        log.debug("ADMIN: Deleting user: %s",  str(user) )
        # delete the access permission
        for p in DBSession.query(TaggableAcl).filter_by(user_id=user.id):
            log.debug ("KILL ACL %s" , str( p))
            DBSession.delete(p)
        #DBSession.flush()

        self.deleteimages(username, will_redirect=False)
        DBSession.delete(user)
        transaction.commit()
        redirect('/admin/users')


    def deleteimages(self, username=None,  will_redirect=True, **kw):
        user = DBSession.query(BQUser).filter(BQUser.resource_name == username).first()
        log.debug("ADMIN: Deleting all images of: %s" , str(user) )
        images = DBSession.query(Image).filter( Image.owner_id == user.id).all()
        for i in images:
            log.debug("ADMIN: Deleting image: %s" , str(i) )
            DBSession.delete(i)
        if will_redirect:
            transaction.commit()
            redirect('/admin/users')
        return dict()


    def loginasuser(self, uniq):
        log.debug ('forcing login as user')
        user = DBSession.query(BQUser).filter (BQUser.resource_uniq == uniq).first()
        if user:
            response.headers = request.environ['repoze.who.plugins']['friendlyform'].remember(request.environ,
                                                                                              {'repoze.who.userid':user.name})
            redirect("/client_service")
        else:
            abort(404)

    def clearcache(self):
        log.info("CLEARING CACHE")
        def clearfiles (folder):
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except OSError as e:
                    log.debug ("unlinking failed: %s", file_path)
                except Exception as e:
                    log.exception('while removing %s' % file_path)

        server_cache = data_path('server_cache')
        clearfiles(server_cache)
        log.info("CLEARED CACHE")
        return '<resource name="cache_clear" value="finished">'

    def get_variables(self):
        #bisque_root = config.get ('bisque.root')
        bisque_root = request.application_url
        bisque_organization = config.get ('bisque.organization', 'BisQue')
        bisque_email = config.get ('bisque.admin_email', 'info@bisque')

        variables = {
            'service_name': bisque_organization,
            'service_url': '<a href="%s">%s</a>'%(bisque_root, bisque_organization),
            'user_name': 'username',
            'email': 'user@email',
            'display_name': 'First Last',
            'bisque_email' : bisque_email,
        }
        return variables

    def do_notify_users(self, userlist, message):
        log.debug(message)
        variables = self.get_variables()

        #for users
        users = data_service.query(resource_type='user', wpublic='true', view='full')
        for u in users:
            variables['user_name'] = u.get('name')
            variables['email'] = u.get('value')
            variables['display_name'] = u.find('tag[@name="display_name"]').get('value')
            if variables['email'] not in userlist:
                continue

            msg = copy.deepcopy(message)
            msg = string.Template(msg).safe_substitute(variables)
            #for v,t in variables.iteritems():
            #    msg = msg.replace('$%s'%v, t)

            # send
            log.info('Sending message to: %s', variables['email'])
            log.info('Message:\n%s', msg)

            try:
                notify_service.send_mail (
                    variables['bisque_email'],
                    variables['email'],
                    'Notification from %s service'%variables['service_name'],
                    msg,
                )
            except Exception:
                log.exception("Mail not sent")


    @expose (content_type='text/xml')
    def group(self, *args, **kw):
        """
            GET /admin/group: returns list of all groups <resource> <group name="a" /> <group ... /> </resource>

            POST /admin/group: creates new group,
                  <group name="new_group" /> or <resource> <group ..> <group ../> </resource>
                  shortcut:  POST /group/new_group with no body
            PUT /admin/group  : same as POST

            DELETE /admin/group/group_name : delete the group

        """


        log.debug ("GROUP %s %s", args, kw)
        reqformat = kw.pop('format', None)
        http_method = request.method.upper()
        if http_method == 'GET':
            resource =  self.get_groups (*args, **kw)
        elif http_method == 'DELETE':
            resource = self.delete_group(*args, **kw)
        elif http_method in ('PUT', 'POST'):
            resource = self.new_group(*args, **kw)
        else:
            abort (400, "bad request")
        accept_header = request.headers.get ('accept')
        formatter, content_type  = find_formatter (reqformat, accept_header)
        response.headers['Content-Type'] = content_type
        return formatter(resource)

    def get_groups (self, *args, **kw):
        resource = etree.Element ('resource')
        for group in DBSession.query (Group):
            etree.SubElement (resource, 'group', name = group.group_name)
        return resource

    def delete_group (self, *args, **kw):
        if len(args):
            group_name = args[0]
        else:
            content_type = request.headers.get('Content-Type')
            inputer = find_inputer (content_type)
            body = request.body_file.read()
            log.debug ("DELETE content %s", body)
            els = inputer (body)
            group_name = els.xpath ('//group/@name')[0]

        resource = etree.Element ('resource')
        group = DBSession.query (Group).filter_by (group_name = group_name).first()
        if group:
            etree.SubElement (resource, 'group', name = group.group_name)
            DBSession.delete(group)

        return resource

    def new_group (self, *args, **kw):
        if len(args):
            group_names = args
        else:
            content_type = request.headers.get('Content-Type')
            inputer = find_inputer (content_type)
            els = inputer (request.body_file)
            group_names = els.xpath ('//group/@name')
        resource = etree.Element ('resource')
        for nm in group_names:
            g = Group(group_name  = nm)
            DBSession.add (g)
            etree.SubElement (resource, 'group', name=nm)

        try:
            transaction.commit()
        except (IntegrityError, InvalidRequestError) as e:
            transaction.abort()
            abort (400, "Bad request %s" %e)

        return resource

def initialize(url):
    """ Initialize the top level server for this microapp"""
    log.debug ("initialize %s" , url)
    return AdminController(url)


#def get_static_dirs():
#    """Return the static directories for this server"""
#    package = pkg_resources.Requirement.parse ("bqserver")
#    package_path = pkg_resources.resource_filename(package,'bq')
#    return [(package_path, os.path.join(package_path, 'admin_service', 'public'))]



__controller__ = AdminController
__staticdir__ = None
__model__ = None
