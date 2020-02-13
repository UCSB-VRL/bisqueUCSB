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

 Main model for bisquik database

DESCRIPTION
===========

 Usage::
   image = Image()
   image.addTag ('name', 'image 1')
   for tg in image.tags:
       print tg.name, tg.value


"""
import urlparse
from datetime import datetime

import sqlalchemy
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, String, DateTime, Unicode, Float
from sqlalchemy import Text, UnicodeText
from sqlalchemy.orm import relation, class_mapper, object_mapper, validates, backref
from sqlalchemy import MetaData, exceptions
from sqlalchemy.sql import and_
from sqlalchemy.ext.associationproxy import association_proxy

from tg import config, session
from bq.core import identity
from bq.core.permission import *
from bq.util.memoize import memoized

#from bq.MS import module_service
#session.mex = None


import logging
log = logging.getLogger("bq.data_service")

# Automatically create the registration tables when TurboGears starts up
#turbogears.startup.call_on_startup.append(create_tables)

from migration.versions.env002 import metadata, DBSession, mapper
current_session = DBSession

files = Table('files', metadata, autoload=True)
#              Column('id', Integer, primary_key=True),
#              Column('sha1', String(40), index=True), # new column v2
#              Column('uri', Unicode(512), index=True),
#              Column('owner', Text),
#              Column('perm', Integer),
#              Column('ts', DateTime(timezone=False)),
#              Column('original', Text),
#              Column('file_type', Text), # new column v2
#              Column('local', Text) # new column v3
#              )
files_acl = Table('file_acl', metadata, autoload=True)



names = Table('names', metadata, autoload=True)
#               Column('id', Integer, primary_key = True),
#               Column('name', UnicodeText)
#               )


taggable = Table('taggable', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('tb_id', Integer, ForeignKey('names.id')),
    Column('mex', Integer, ForeignKey('taggable.id'), key='mex_id'),
#                 Column('mex_id', Integer, ForeignKey('taggable.id')),
                 Column('ts', DateTime(timezone=False)),
                 Column('perm', Integer), #ForeignKey('permission_sets.set_id')
                 Column('owner_id', Integer, ForeignKey('taggable.id')),
                 Column('resource_uniq', String(40)),
                 Column('resource_type', Unicode(255) ),  # will be same as tb_id UniqueName
                 Column('resource_name', Unicode (1023)),
                 Column('resource_user_type', Unicode(1023) ),
                 Column('resource_value',  UnicodeText),
                 Column('resource_parent_id', Integer, ForeignKey('taggable.id')),
                 Column('document_id', Integer, ForeignKey('taggable.id')), # Unique Elemen#
                 )

images= Table ('images', metadata, autoload=True)
#               Column('id', Integer, ForeignKey('taggable.id'),primary_key=True),
#               Column('src', Text),
#               Column('x', Integer),
#               Column('y', Integer),
#               Column('z', Integer),
#               Column('t', Integer),
#               Column('ch', Integer))

tags = Table ('tags', metadata, autoload=True)
#              Column('id',  Integer, ForeignKey('taggable.id'), primary_key=True),
#              Column('parent_id', Integer, ForeignKey('taggable.id'), index=True),
#              Column('type_id',  Integer, ForeignKey('names.id')),
#              Column('name_id', Integer, ForeignKey('names.id'), index=True),
#              Column('indx', Integer),
#              )

gobjects = Table ('gobjects', metadata, autoload=True)
#              Column('id', Integer, ForeignKey('taggable.id'), primary_key=True),
#              Column('parent_id', Integer, ForeignKey('taggable.id'), index=True),
#              Column('type_id',  Integer, ForeignKey('names.id')),
#              Column('name_id', Integer, ForeignKey('names.id')),
#              Column('indx', Integer),
#              )



#simplevalues = Table ('simplevalues', metadata,
#          Column('id',  Integer, ForeignKey('taggable.id'), primary_key=True),
values = Table ('values', metadata, autoload=True)
#          Column('parent_id',Integer, ForeignKey('taggable.id'),primary_key=True),
#          Column('indx', Integer, primary_key = True, autoincrement=False),
#          Column('valstr', UnicodeText),
#          Column('valnum', Float),
#          Column('valobj', Integer, ForeignKey('taggable.id'))
#                      )

vertices = Table ('vertices', metadata, autoload=True)
   # Column('id', Integer, ForeignKey('taggable.id'), primary_key=True),
#                Column('parent_id',Integer, ForeignKey('taggable.id'), primary_key=True),
#                Column('indx', Integer, primary_key=True, autoincrement=False),
#                Column('x', Float),
#                Column('y', Float),
#                Column('z', Float),
#                Column('t', Float),
#                Column('ch', Integer))



users = Table ('users', metadata, autoload=True)
#               Column('id', Integer, ForeignKey('taggable.id'), primary_key=True),
#               Column('user_name', UnicodeText),
#               Column('display_name', UnicodeText),
#               Column('email_address', UnicodeText),
#               Column('password', UnicodeText),
            # Column('tg_user_id', Integer, ForeignKey('tg_user.user_id')),
            # Column('default_perm_id', Integer, ForeignKey('permission_sets.set_id')),
#)

groups = Table ('groups', metadata, autoload=True)
#                Column('id', Integer, ForeignKey('taggable.id'), primary_key=True),
#                Column ('group_name', UnicodeText),
#                Column ('display_name', UnicodeText))


templates = Table ('templates', metadata, autoload=True)
#                   Column('id', Integer, ForeignKey('taggable.id'),  primary_key=True),
#                   Column ('name', Text))

#engines = Table('engines', metadata,
#                Column('id', Integer, primary_key=True),
#                Column('name', String))

modules = Table ('modules', metadata, autoload=True)
#                 Column('id', Integer,
#                        ForeignKey('taggable.id'), primary_key=True),
#                 Column('name', Text),
#                 Column('codeurl', Text),
#                 Column('module_type_id', Integer, ForeignKey('names.id'))
#                 )

mex = Table ('mex', metadata, autoload=True)
#             Column('id',  Integer,
#                    ForeignKey('taggable.id'), primary_key=True),
#             Column('module', Text),
#             Column('status', Text)
#             )

dataset = Table ('datasets', metadata, autoload=True)
#                 Column('id', Integer, ForeignKey('taggable.id'), primary_key=True),
#                 Column('name', Text),
#                 )

taggable_acl = Table('taggable_acl', metadata, autoload=True)
#                     Column('taggable_id', Integer, ForeignKey('taggable.id'), primary_key=True),
#                     Column('user_id', Integer, ForeignKey('taggable.id'),primary_key=True),
#                     Column('permission', Integer),
#                     )

services = Table ('service', metadata, autoload=True)
#                  Column('id',  Integer,
#                         ForeignKey('taggable.id'), primary_key=True),
#                  Column('type', Text),
#                  Column('uri', Text),
#                  )

# permission_tokens = Table ('permission_tokens', metadata,
#                             Column('id', Integer, primary_key=True),
#                             Column ('name', String),
#                             Column ('description', String))
# permission_sets = Table ('permission_sets', metadata,
#       Column('set_id', Integer, primary_key=True),
#       Column('taggable_id', Integer, ForeignKey('taggable.id'), nullable=True),
# )
# permission_set_tokens = Table ('permission_set_tokens', metadata,
#       Column('token_id', Integer, ForeignKey('permission_tokens.id')),
#       Column('set_id', Integer, ForeignKey('permission_sets.set_id')),
# )


#ctx = turbogears.database.session.context
###############################
# Basic types
import weakref
class EntitySingleton(type):
    """a metaclass that insures the creation of unique and
    non-existent entities for a particular constructor argument.  if
    an entity with a particular constructor argument was already
    created, either in memory or in the database, it is returned in
    place of constructing the new instance."""

    def __init__(cls, name, bases, dct):
        cls.instances = weakref.WeakValueDictionary()

    def __call__(cls, name):
        #sess = current_session()
        sess = current_session
        name = unicode(name)
        hashkey =  name
        #hashkey = name
        try:
            instance = cls.instances[hashkey]
            instance = sess.merge (instance)
            return instance
        except KeyError:
            instance = sess.query(cls).filter(cls.name==name).first()
            #log.debug('read %s in %s' % (instance, id(session.context)) )
            if instance is None:
                #log.debug('no value in sess' + str(hashkey))
                instance = type.__call__(cls, name)
                sess.add(instance)
                # optional - flush the instance when it's saved
                #try:
                #    #sess.flush()
                #    #sess.flush()
                #    #sess.commit()
                #    sess.refresh(instance)
                #except exceptions.SQLError:
                    # if desired, add a check for the specific
                    # constraint error code/message, if
                    # known
                    #log.debug('error while saving' + str(hashkey))
                #    instance = sess.query(cls).filter(cls.name==name).first()
                #    if instance is None:
                #        #log.debug ('still no val:' + str(hashkey))
                #       raise
            cls.instances[hashkey] = instance
            return instance

class UniqueName(object):
    __metaclass__ = EntitySingleton
    def __init__(self, name):
        log.debug ("unique name:" + name)
        self.name = unicode(name)

    def __repr__(self):
        return 'UniqueName('+self.name+')'

    def __str__(self):
        return self.name



# The following are deprecated
class TagName(UniqueName):
    pass
class GObjectType(UniqueName):
    pass
class Engine(UniqueName):
    pass

class TableName(UniqueName):
    pass
# end deprecations





######################################################################
#
def parse_uri(uri):
    ''' Parse a bisquik uri into host , dbclass , and ID
    @type  uri: string
    @param uri: a bisquik uri representation of a resourc
    @rtype:  A triplet (host, dbclass, id)
    @return: The parse resouece
    '''
    url = urlparse.urlsplit(uri)
    name, id = url[2].split('/')[-2:]
    return url[1], name, id

def map_url (uri):
    '''Load the object specified by the root tree and return a rsource
    @type   root: Element
    @param  root: The db object root with a uri attribute
    @rtype:  tag_model.Taggable
    @return: The resource loaded from the database
    '''
    # Check that we are looking at the right resource.

    net, name, ida = parse_uri(uri)
    name, dbcls = dbtype_from_name(name)
    resource = DBSession.query(dbcls).get (ida)
    #log.debug("loading uri name (%s) type (%s) = %s" %(name,  str(dbcls), str(resource)))
    return resource



################################
# Taggable types
#

class FileEntry(object):

#    def __init__(self):
#        self.id = None

    def _set_id(self, new_id):
      #self._id_db = new_id+1
      pass

    def _get_id(self):
      return self._id_db-1

    id = property( _get_id, _set_id )

    def str(self):
        return "FileEntry(%s, %s, %s, %s, %s)" % (self.id, self.sha1, self.uri, self.owner, self.perm, self.ts, self.original, self.file_type )



class Taggable(object):
    """
    Base type for taggable objects.  Taggable
    objects can have any number of name/value pairs
    associated with it.
    """
    xmltag = 'resource'

    def __init__(self, resource_type = None, owner = None):
        #if self.__class__ == Taggable and resource_type:
        #    self.table = resource_type
        #else:
        #    self.table = str(object_mapper(self).local_table)
            #log.debug ("System Taggable %s using %s" %( self.__class__,  self.table));
            #self.table = self.xmltag
        if resource_type is None:
            resource_type = self.xmltag
        self.resource_type = resource_type
        self.ts = datetime.now()
        #log.debug("new taggable user:" + str(session.dough_user.__dict__) )
        #if owner is None:
        #    owner  = identity.current.get_bq_user()
        log.debug (".owner = %s mex = %s" % (owner, mex))
        #if owner:
        #    self.owner_id = owner.id
        #self.mex_id = session.get('mex.id', None)
        #mex_id = DBSession.get ('mex.id', None)
        #mex    = module_service.get_mex()
        #if mex_id is not None:
        #    self.mex_id = mex_id
        self.perm = PUBLIC
        #if owner :
        #    self.perm = PRIVATE
        #if identity.current_mex():
        #    self.mex_id = int ( identity.current_mex() )
        #if owner is None:
        #    log.warn ("CREATING taggable %s with no owner" % str(self) )
        #    admin = identity.get_admin()
        #    if admin:
        #        log.warn("Setting owner to admin")
        #        self.owner_id = admin.id

    def resource (self):
        return "%s/%s" % ( self.table , self.id)
    resource = property(resource)

    def uri (self):
        if hasattr(self,'parent') and self.parent is not None:
            parent = self.parent.loadFull()
            return "%s/%s/%s" % (parent.uri , self.table, self.id)
        else:
            return "%s/%s" % (self.table, self.id)

    uri = property(uri)

    def gettable(self):
        if self.table_name is not None:
            return self.table_name.name
        return self.__class__.xmltag
    def settable(self, v):
        self.table_name = UniqueName(v)

    table = property(gettable, settable)
    type  = property(gettable, settable)

    @validates('owner')
    def validate_owner (self, key, owner):
        if isinstance(owner, basestring) and owner.startswith ('http'):
            return map_url (owner)
        return owner


#    def get_owner (self):
#        if self.owner_ob:
#            return self.owner_ob.user_name
#    def set_owner (self,name):
#        self.owner_ob = BQUser.filter_by (user_name=name).one()
#    owner = property(get_owner, set_owner)
    def clear(self, what=['tags', 'gobjects']):
        '''Clear all the children'''
        results = []
        if 'tags' in what:
            results.extend(self.tags)
            self.tags = []
            log.debug ('cleared tags')
        if 'gobjects' in what:
            results.extend(self.gobjects)
            self.gobjects = []
            log.debug ('cleared gobjects')
        return results

    def fieldTag(self, nm, v = None):
        t = DBSession.query(Tag).filter(and_(self.id == tags.c.parent_id,
                                           tags.c.name_id== UniqueName(nm).id)).first()
        if not t:
            t = Tag()
            t.name = nm
            self.tags.append(t)
        return t

    def findtag (self, nm, create=False):
        for t in self.tags:
            if t.name == nm:
                return t
        t=None
        if create:
            t = Tag()
            t.name = nm
            self.tags.append(t)
        return t

    def loadFull(self):
        'hack to load polymorphic taggable type'
        table, dbtype = dbtype_from_name(self.table)
        if dbtype != Taggable:
            return DBSession.query(dbtype).get (self.id)
        return self

    def __str__(self):
        #return "%s/%s" % (self.__class__.xmltag,  str(self.id))
        return self.uri


class Image(Taggable):
    """
    Image object
    """
    xmltag = 'image'


class Tag(Taggable):
    '''
    Tag object (name,value) pair.
    Tag have for the following properties:
    '''
    xmltag = 'tag'

    def __str__(self):
        return 'tag "%s":"%s"' % (unicode(self.name), unicode(self.value))

    # Tag.name helper functions
    def getname(self):
        if self.tagname:
            return self.tagname.name
        return None
    def setname(self, v):
        self.tagname = UniqueName(v)
    name = property(getname, setname)

    # Tag.type helper functions
    def gettype (self):
        if self.type_name is not None:
            return self.type_name.name
        return self.xmltag
    def settype(self, v):
        self.type_name = UniqueName(v)
    tag_type = property(gettype, settype)
    type = property(gettype, settype)


    # Tag.parent helper
    # Handled by mapper

    # Tag.indx used for ordering tags
    def get_index(self):
        return self.indx
    def set_index(self, v):
        self.indx = v
    index = property(get_index, set_index)

    # Tag.value helper functions
    def newval(self, v, i = 0):
        if type(v) == str or type(v) == unicode:
            v = Value(i, s = v)
        elif type(v) == int or type(v) == float:
            v = Value(i, n = v)
        elif isinstance(v, Taggable):
            v = Value(i, o = v)
        else:
            raise BadValue("Tag "+self.name, v)
        return v

    def getvalue(self):
        value = None
        if len(self.values) == 1:
            return self.values[0].value
        else:
            # call SimpleValue decoder
            return [ v.value for v in self.values ]

    def setvalue(self, v):
        if type(v) == list:
            l = [ self.newval(v[i], i) for i in xrange(len(v)) ]
        else:
            l = [ self.newval(v, 0) ]
        self.values = l
    value = property(fget=getvalue,
                     fset=setvalue,
                     doc="Value of tag")


    def clear(self, what=None):
        '''Clear all the children'''
        super(Tag, self).clear()
        log.debug ('cleared values')
        old = self.values
        self.values = []
        return old

    # Tag.values
    #  List of SimpleValues

    # Tag.vertices
    #  List of vertices



#    def match(nm, value):
#        return session.query(Tag).select_by (tagnames.c.name == nm,
#                                             valstr = value)
#    match = staticmethod (match)
class Value(object):
    xmltag = 'value'

    def __init__(self, ind=None, s = None, n = None, o = None):
        self.indx = ind
        self.valstr = s
        self.valnum = n
        self.object = o

    def getvalue(self):
        value = ''
        if self.valstr: value = self.valstr
        elif self.valobj: value = self.objref
        elif self.valnum: value = self.valnum
        return value
    def setvalue(self, v):
        if type(v) == str or type(v) == unicode:
            self.valstr = v
            self.valnum = None
            self.valobj = None
        elif type(v) == int or type(v) == float:
            self.valnum = v
            self.valstr = None
            self.valobj = None
        elif isinstance(v, Taggable):
            self.objref = v
            self.valnum = None
            self.valstr = None

    def remvalue(self):
        self.valstr = None
        self.valnum = None
        self.valobj = None

    value = property(fget=getvalue,
                     fset=setvalue,
                     fdel=remvalue,
                     doc="Value of tag")

    def gettype (self):
        if self.valobj: return "object"
        elif self.valnum: return "number"
        return "string"
    def settype (self,x):
        pass
    type = property (gettype, settype)

    def getobjid(self):
        return self.valobj
    taggable_id = property(getobjid)

    # Tag.indx used for ordering tags
    def get_index(self):
        return self.indx
    def set_index(self, v):
        self.indx = v
    index = property(get_index, set_index)


    def __str__ (self):
        return unicode( self.value )


class Vertex(object):
    xmltag = 'vertex'

    def get_index(self):
        return self.indx
    def set_index(self, v):
        self.indx = v
    index = property(get_index, set_index)
    def __str__ (self):
        return "<vertex x=%s y=%s z=%s t=%s ch=%s index=%s />" % (self.x, self.y,self.z,self.t,self.ch, self.indx)


class GObject(Taggable):
    xmltag = 'gobject'

    # Tag.name helper functions
    def getname(self):
        if self.tagname:
            return self.tagname.name
        return ""
    def setname(self, v):
        #log.debug ("Setting gobject name " + v);
        if self.tagname is None or self.tagname.name != v :
            self.tagname = UniqueName(v)
        #log.debug ("Setting gobject name " + str(UniqueName(v)));

    name = property(getname, setname)

    # Tag.type helper functions
    def gettype (self):
        if self.type_name:
            return self.type_name.name
        return None
    def settype(self, v):
        #log.debug ('set type ' + v)
        if (self.type_name is None or self.type_name.name != v) :
            self.type_name = UniqueName(v)
    tag_type = property(gettype, settype)
    type = property(gettype, settype)

    # Tag.indx used for ordering tags
    def get_index(self):
        return self.indx
    def set_index(self, v):
        self.indx = v
    index = property(get_index, set_index)

    def clear(self, what=None):
        '''Clear all the children'''
        super(GObject, self).clear()
        log.debug ('cleared vertices')
        old = self.vertices
        self.vertices = []
        return old

#    def __str__(self):
#        return 'gobject %s:%s' % (self.name, str(self.type))





class BQGroup(Taggable):
    '''
    Group object: a group of other objects.
    The element of the group are formed
    as tag/value pairs with tag=='group_member'
    '''
    xmltag = 'group'

    def __init__(self, group_name):
        #super(Group, self).__init__()
        self.group_name = group_name
        self.members    = self.fieldTag ('members')

    def __str__(self):
        return self.group_name

    def __repr__(self):
        return self.group_name

    def group_id(self):
        return self.id
    group_id = property(group_id)

    def addMember(self, member):
        self.members.value = self.members.value + [ member ]

    def delMember(self, member_id):
        pass

    def addPermission(self, perm):
        self.addTag('permission', perm)

    def users(self):
        return self.selectTags('group_member')

    users = property(users)

    def permissions(self):
        return self.selectTags('permission')

    permissions = property(permissions)

    def contains(self, m):
        return m in self.members.values





class BQUser(Taggable):
    '''
    User object
    '''
    xmltag = 'user'

    def __init__(self, user_name=None, password=None,
					email_address=None, display_name=None,
					create_tg=False, tg_user = None, **kw):
        super(BQUser, self).__init__()
        if not display_name: display_name = user_name

        if create_tg and tg_user is None:
            tg_user = User()
            tg_user.user_name = user_name
            tg_user.email_address = email_address
            tg_user.password = password
            tg_user.display_name = display_name
            DBSession.add(tg_user)

        self.perm = PUBLIC
        self.user_name = tg_user.user_name
        self.password = tg_user.password
        self.email_address = tg_user.email_address
        self.display_name = tg_user.display_name
        DBSession.add(self);
        #DBSession.flush();
        #DBSession.refresh(self)

        #tg_user.dough_user_id = self.id
        self.owner_id = self.id

    @classmethod
    def new_user (cls, email, password, create_tg = False):
        bquser =  cls( user_name= email,
                       email_address=email,
                       display_name=email,
                       password = password)
        DBSession.add (bquser)
        DBSession.flush()
        DBSession.refresh(bquser)
        bquser.owner_id = bquser.id

        if create_tg:
            tg_user = User()
            tg_user.user_name = user_name
            tg_user.email_address = email_address
            tg_user.password = password
            tg_user.display_name = display_name
            #tg_user.dough_user_id = self.id
            DBSession.add(tg_user)
            DBSession.flush()

        return bquser


#     def init_permissions(self):
#         if not self.user_name:
#             raise IllegalOperation('no user_name for permission')
#         u_r = PermissionToken()
#         u_r.name = "R_" + self.user_name
#         u_w = PermissionToken()
#         u_w.name = "W_" + self.user_name
#         session.add(u_r)
#         session.add(u_w)
#         permissions = PermissionSet(self.id)
#         self.perm =  permissions
#         self.default_perm = permissions
#         permissions.add(u_r)
#         permissions.add(u_w)
#         global r_all, w_all
#         permissions.add(r_all)
#         permissions.add(w_all)
#         #self.permission = permissions


#    def __str__(self):
#        return "%s/%d" % (self.user_name, self.id)

    def __repr__(self):
        return "BQUser<user_name: '%s', display_name: '%s'>" % (self.user_name, self.display_name)

    def user_id(self):
        return self.id
    user_id = property(user_id)

    def addPermission(self, perm):
        self.perm.addTag('permission', perm)

    def groups(self):
        # Find group objects that have a member == self.
        # 1.  iterate groups searching for group_member == self
        # 2.  find taggables with tag=='group_member' and value=='self'
        #     and convert to groups
        pass

    groups = property(groups)

    def permissions(self):
        return self.selectTags('permission')

    permissions = property(permissions)

    def email(self):
        return self.email_address


class Template(Taggable):
    '''
    A pre-canned group of tags
    '''
    xmltag = 'template'

class Module(Taggable):
    '''
    A module is a runnable routine that modifies the database
    There are several required tags for every module:
    for each input/output a type tag exists:
       (formal_input: [string, float, tablename])
       (formal_output: [tagname, tablename])

    '''
    xmltag ='module'
    def get_module_type(self):
        if self.module_type:
            return self.module_type.name
        return ""
    def set_module_type(self, v):
        self.module_type = UniqueName(v)
    type = property(get_module_type, set_module_type)

class ModuleExecution(Taggable):
    '''
    A module execution is an actual execution of a module.
    Executions must have the folling tags available:
      (actual_input: taggable_id)
      (actual_output: taggable_id)
    '''
    xmltag ='mex'
    def closed(self):
        return self.status in ('FINISHED', 'FAILED')

class Dataset(Taggable):
    xmltag = 'dataset'


class PermissionToken(object):
    '''
    Permission Token object i.e. R_all, W_user1
    '''

class PermissionSetToken(object):
    '''
    Permission Token object i.e. R_all, W_user1
    '''

class PermissionSet(object):
    '''
    A Set of permissions.
    '''
    def __init__(self, o):
        '''Create a permissionSet for object o'''
        if o:
            self.taggable = o
    def add(self, token):
        pst = PermissionSetToken()
        pst.token=token
        pst.set = self

        self.tokens.append (pst)

class TaggableAcl(object):
    """A permission for EDIT or READ on a taggable object
    """
    xmltag = "auth"


    def setperm(self, perm):
        self.permission = { "read":0, "edit":1 } .get(perm, 0)
    def getperm(self):
        return [ "read", "edit"] [self.permission]

    action = property(getperm, setperm)

    def __str__(self):
        return "resource:%s  user:%s permission:%s" % (self.taggable_id,
                                                       self.user_id,
                                                       self.action)

class Service (Taggable):
    """A executable service"""
    xmltag = "service"

    def __str__(self):
        return "%s module=%s engine=%s" % (self.uri, self.module, self.engine)

#################################################
# Simple Mappers
mapper( UniqueName, names)
#session.mapper(UniqueName, names)

mapper( Value, values,
              properties = {
    'parent' : relation (Tag, lazy=True,
                         primaryjoin =(taggable.c.id == values.c.parent_id)),
    'objref' : relation(Taggable, uselist=False,
                        primaryjoin=(values.c.valobj==taggable.c.id),
                        enable_typechecks=False
                        ),
    }
    )

mapper( Vertex, vertices)
mapper(TaggableAcl, taggable_acl,
       properties = {
           'user'    : relation(BQUser,
                                passive_deletes="all",
                                uselist=False,
                                primaryjoin=(taggable_acl.c.user_id==
                                             users.c.id),
                                foreign_keys=[users.c.id])
           })



mapper(FileEntry, files, properties={
    '_id_db' : files.c.id,
#    'acls'  : relation(FileAcl, lazy=True, cascade="all, delete-orphan",
#                      #primaryjoin = (FileEntry.id == FileAcl.id),
#                      )

    })


############################
# Taggable mappers

mapper( Taggable, taggable,
                       properties = {
    'table_name' : relation(UniqueName,
                            primaryjoin=(taggable.c.tb_id == names.c.id),
                            uselist = False,
                            ),

    'tags' : relation(Tag, lazy=True, viewonly=True, cascade="all, delete-orphan",
                         primaryjoin= (tags.c.parent_id==taggable.c.id)),
#                         primaryjoin= and_(taggable.c.resource_parent_id==taggable.c.id,
#                                           taggable.c.resource_type == 'tag')),
    'gobjects' : relation(GObject, viewonly=True, lazy=True, cascade="all, delete-orphan",
                         primaryjoin= (gobjects.c.parent_id==taggable.c.id)),
#                         primaryjoin= and_(taggable.c.resource_parent_id==taggable.c.id,
#                                           taggable.c.resource_type == 'gobject')),
    'acl'  : relation(TaggableAcl, lazy=True, cascade="all, delete-orphan",
                      primaryjoin = (TaggableAcl.taggable_id == taggable.c.id)),
    'children' : relation(Taggable, lazy=True, cascade="all, delete-orphan",
                          primaryjoin = (taggable.c.id == taggable.c.resource_parent_id),
                          foreign_keys=[taggable.c.resource_parent_id]),
    'values' : relation(Value,  lazy=True, cascade="all, delete-orphan",
                        primaryjoin =(taggable.c.id == values.c.parent_id),
                        foreign_keys=[values.c.parent_id]
                        ),
    'vertices' : relation(Vertex, lazy=True, cascade="all, delete-orphan",
                          primaryjoin =(taggable.c.id == vertices.c.parent_id),
                          foreign_keys=[vertices.c.parent_id]
                          ),

    'docnodes': relation(Taggable,
                         lazy='dynamic',
                         cascade = "all",
                         post_update=True,
                         primaryjoin = (taggable.c.id == taggable.c.document_id),
                         backref = backref('document', post_update=True, remote_side=[taggable.c.id]),
                         )


    }
              )

mapper( Image, images, inherits=Taggable)
mapper( Tag, tags, inherits=Taggable,
                  inherit_condition=(tags.c.id == taggable.c.id),
                  properties={
    'tagname': relation(UniqueName, uselist=False,
                        primaryjoin =(tags.c.name_id==names.c.id)),
    'parent' : relation (Taggable, lazy=True,
                         primaryjoin =(tags.c.parent_id == taggable.c.id)),
    'type_name' : relation (UniqueName, uselist=False,
                       primaryjoin =(tags.c.type_id==names.c.id)),
#    'values' : relation(Value,  lazy=True, cascade="all, delete-orphan",
#                        primaryjoin =(taggable.c.id == values.c.parent_id),
#                        foreign_keys=[values.c.parent_id]
#                        ),
    }
              )


mapper( GObject, gobjects, inherits=Taggable,
                  inherit_condition=(gobjects.c.id == taggable.c.id),
                  properties={
    'tagname': relation(UniqueName,
                        primaryjoin =(gobjects.c.name_id==names.c.id)),
    'parent' : relation (Taggable, lazy=True,
                         primaryjoin =(gobjects.c.parent_id == taggable.c.id)),
    'type_name' : relation (UniqueName,
                       primaryjoin =(gobjects.c.type_id==names.c.id)),
#    'vertices' : relation(Vertex, cascade="all, delete-orphan",
#                          primaryjoin =(taggable.c.id == vertices.c.parent_id),
#                          foreign_keys=[vertices.c.parent_id]
#                          ),
    }
              )




mapper(BQGroup, groups, inherits=Taggable)
mapper(BQUser, users, inherits=Taggable,
    properties = {
#        'tguser' : relation(User, uselist=False,
#            primaryjoin=(User.user_name == users.c.user_name),
#            foreign_keys=[User.user_name]),

        'owned' : relation(Taggable,
                           lazy = True,
                           cascade = None,
                           primaryjoin = (users.c.id == taggable.c.owner_id),
                           foreign_keys=[taggable.c.owner_id],
                           backref = backref('owner', post_update=True),
                           )

    }
)
def bquser_callback (tg_user, operation, **kw):
    # Deleted users will receive and update callback
    if tg_user is None:
        return
    if operation =='create':
        u = DBSession.query(BQUser).filter_by(user_name=tg_user.user_name).first()
        if u is None:
            log.info ('creating BQUSER ')
            BQUser(tg_user=tg_user)
            return
    if operation  == 'update':
        u = DBSession.query(BQUser).filter_by(user_name=tg_user.user_name).first()
        if u is not None:
            u.email_address = tg_user.email_address
            u.password = tg_user.password
            u.display_name = tg_user.display_name
        return



#User.callbacks.append (bquser_callback)


mapper(Template, templates, inherits=Taggable)

mapper(Module, modules, inherits=Taggable,
              properties = {
    'module_type' : relation(UniqueName,
                      primaryjoin = (modules.c.module_type_id==names.c.id)),


    }
              )

mapper(ModuleExecution, mex, inherits=Taggable,
       inherit_condition=(mex.c.id == taggable.c.id),
       properties = {
        'owned' : relation(Taggable,
                           lazy = True,
                           cascade = None,
                           primaryjoin = (mex.c.id == taggable.c.mex_id),
                           foreign_keys=[taggable.c.mex_id],
                           backref = backref('mex', post_update=True),
                           )
        },
       )
mapper( Dataset, dataset,
              inherits=Taggable,
              inherit_condition=(dataset.c.id == taggable.c.id))

mapper( Service, services,
        inherits=Taggable,
        inherit_condition=(services.c.id == taggable.c.id),
        properties = {
            'engine' : services.c.uri,
            'module' : services.c.type,
            }
        )


#################################################
# Support Functions

#class_mapper(User).add_property('dough_user',
#    relation(BQUser,
#         primaryjoin=(User.dough_user_id == Taggable.id),
#         foreign_keys=[Taggable.id],
#    )
#)

def registration_hook(action, **kw):
    if action=="new_user":
        u = kw.pop('user', None)
        if u:
            BQUser.new_user (u.email_adress)

    elif action=="update_user":
        u = kw.pop('user', None)
        if u:
            bquser = DBSession.query(BQUser).filter_by(email_adress=u.email_address).first()
            if not bquser:
                bquser = BQUser.new_user (u.email_adress)

            bquser.display_name = u.display_name
            bquser.user_name = u.user_name

    elif action =="delete_user":
        pass


def db_setup():
    global admin_user, init_module, init_mex
    admin_user = BQUser.query.filter(BQUser.user_name == u'admin').first()
    if not admin_user:
        admin_user = BQUser.new_user(password=u'admin', email = u'admin')
        init_module = Module ()
        init_mex = ModuleExecution ()
        DBSession.add (init_module)
        DBSession.add (init_mex)
        DBSession.flush()

        DBSession.refresh (init_module)
        DBSession.refresh (init_mex)
        admin_user.mex_id = init_mex.id

        init_module.owner_id = admin_user.id
        init_module.mex_id = init_mex.id
        init_module.name  = "initialize"

        init_mex.mex_id = init_mex.id
        init_mex.owner_id = admin_user.id
        init_mex.module = "initialize"
        init_mex.status = "FINISH"
    identity.set_admin (admin_user)


def db_load():
    global admin_user, init_module, init_mex
    admin_user = DBSession.query(BQUser).filter_by(user_name=u'admin').first()
    init_module= DBSession.query(Module).filter_by(name='initialize').first()
    init_mex   = DBSession.query(ModuleExecution).filter_by(module='initialize').first()
    log.info( "initalize mex = %s" % init_mex)


def init_admin():
#    admin_group = Group.query.filter(Group.group_name == u'admin').first()
#    if not admin_group:
#        admin_group = Group(group_name = u'admin', display_name = u'Administrators')
#        session.add(admin_group)
#        session.flush()

    log.debug ("admin user = %s" %  admin_user)
    return admin_user






@memoized
def dbtype_from_name(table):
    ''' Return a tuple of table name and the most specific database type'''
    if table in metadata.tables:
        for mapper_ in  list(sqlalchemy.orm._mapper_registry):
            #logger.debug ("map"+str(mapper_.local_table))
            if mapper_.local_table == metadata.tables[table]:
                return (table, mapper_.class_)
    return (table, Taggable)

@memoized
def dbtype_from_tag(tag):
    ''' Given a tag,
    Return a tuple of table name and the most specific database type
    '''
    for mapper_ in  list(sqlalchemy.orm._mapper_registry):
        #logger.debug ("map"+str(mapper_.local_table))
        if hasattr(mapper_.class_, 'xmltag') and mapper_.class_.xmltag == tag:
            return (tag, mapper_.class_)
    return (tag, Taggable)

@memoized
def all_resources ():
    ''' Return the setof unique names that are taggable objects
    '''
    names = DBSession.query(UniqueName).filter(UniqueName.id == Taggable.tb_id).all()
    log.debug ('all_resources' + str(names))
    return names



