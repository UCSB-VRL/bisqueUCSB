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
import subprocess
import urlparse
import sqlalchemy
from datetime import datetime

from sqlalchemy import Table, Column, ForeignKey, Index
from sqlalchemy import Integer, String, DateTime, Unicode, Float, Boolean
from sqlalchemy import Text, UnicodeText
from sqlalchemy.orm import relation, class_mapper, object_mapper, validates, backref, synonym
from sqlalchemy.orm import foreign, remote
from sqlalchemy import exc
from sqlalchemy.sql import and_, case
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.orderinglist import ordering_list

from tg import config, session, request

from bq.core.model import mapper
from bq.core.model import DBSession as current_session
from bq.core.model import DBSession

from datetime import datetime

#import turbogears
#from turbogears.database import metadata, session
#from turbogears.util import request_available
from bq.core import identity
from bq.core.model import DeclarativeBase, metadata
from bq.core.model import User, Group
from bq.core.permission import PUBLIC, PRIVATE, perm2code, perm2str
from bq.util.memoize import memoized
from bq.util.hash import make_uniq_code

from irods_user import BisQueIrodsIntegration#from bq.MS import module_service
#session.mex = None


import logging
log = logging.getLogger("bq.data_service.tag_model")

global admin_user, init_module, init_mex
admin_user =  init_module = init_mex = None


# Legal attributes for Taggable
LEGAL_ATTRIBUTES = {
    'name': 'resource_name',  'resource_name' : 'resource_name',
    'type': 'resource_user_type', 'resource_user_type': 'resource_user_type',
    'value': 'resource_value', 'resource_value' : 'resource_value',
    'hidden': 'resource_hidden', 'resource_hidden': 'resource_hidden',
    'ts': 'ts', 'created': 'created',
    'unid' : 'resource_unid', 'resource_unid' : 'resource_unid',
    'uniq' : 'resource_uniq', 'resource_uniq' : 'resource_uniq',
    'mex': 'mex_id',   # 'mex_id': 'mex_id',
    'owner' : 'owner_id', 'owner_id' : 'owner_id',
     }



def create_tables1(bind):
    metadata.bind = bind
    """Create the appropriate database tables."""
    log.info( "Creating tag_model tables" )
    engine = config['pylons.app_globals'].sa_engine
    metadata.create_all (bind=engine, checkfirst = True)


taggable = Table('taggable', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('mex_id', Integer, ForeignKey('taggable.id', name="mex_fk", ondelete="CASCADE"),index=True),
                 Column('created', DateTime(timezone=False)),
                 Column('ts', DateTime(timezone=False), index=True),
                 Column('perm', Integer), #ForeignKey('permission_sets.set_id')
                 Column('owner_id', Integer, ForeignKey('taggable.id', name="owner_fk", ondelete="CASCADE"), index=True),
                 Column('resource_uniq', String(40), index=True, unique=True),
                 Column('resource_index', Integer),
                 Column('resource_hidden', Boolean),
                 Column('resource_type', Unicode(255), index=True ),  # will be same as tb_id UniqueName
                 Column('resource_name', Unicode (1023), index=True),
                 Column('resource_user_type', Unicode(1023), ),
                 Column('resource_value',  UnicodeText),
                 Column('resource_parent_id', Integer, ForeignKey('taggable.id', name="taggable_children_fk", ondelete="CASCADE"), index=True),
                 Column('document_id', Integer, ForeignKey('taggable.id', name="taggable_document_fk", ondelete="CASCADE"), index=True), # Unique Element
                 Column('resource_unid', UnicodeText),
                 Index('idx_user_unid', 'owner_id', 'resource_parent_id', 'resource_unid', unique=True,  mysql_length = {'resource_unid' : 255}),
                 Index ('idx_resource_value', 'resource_value', postgresql_ops = { 'resource_value' : 'text_pattern_ops' })
                 )

values = Table ('values', metadata,
          Column('resource_parent_id',Integer, ForeignKey('taggable.id', name="values_children_fk", ondelete="CASCADE"),primary_key=True),
          Column('indx', Integer, primary_key = True, autoincrement=False),
          Column('document_id',Integer, ForeignKey('taggable.id', name="values_document_fk", ondelete="CASCADE"), index=True),
          Column('valstr', UnicodeText),
          Column('valnum', Float),
          Column('valobj', Integer, ForeignKey('taggable.id')),
          Index ('idx_value_valobj', 'valobj')
                      )

vertices = Table ('vertices', metadata,
     Column('resource_parent_id',Integer, ForeignKey('taggable.id', name="vertices_children_fk", ondelete="CASCADE"), primary_key=True),
     Column('indx', Integer, primary_key=True, autoincrement=False),
     Column('document_id',Integer, ForeignKey('taggable.id', name="vertices_document_fk", ondelete="CASCADE"), index=True),
     Column('x', Float),
     Column('y', Float),
     Column('z', Float),
     Column('t', Float),
     Column('ch', Integer))

taggable_acl = Table('taggable_acl', metadata,
                     Column('taggable_id', Integer, ForeignKey('taggable.id'), primary_key=True),
                     Column('user_id', Integer, ForeignKey('taggable.id'),primary_key=True),
                     Column('permission', Integer, key="action_code"),
                     Index ('idx_taggableacl_taggable_id', 'taggable_id'),
                    )

# users = Table ('users', metadata,
#                Column('id', Integer, ForeignKey('taggable.id'), primary_key=True),
#                Column('user_name', UnicodeText),
#                Column('display_name', UnicodeText),
#                Column('email_address', UnicodeText),
#                Column('password', UnicodeText),
#                )

# groups = Table ('groups', metadata,
#                 Column('id', Integer, ForeignKey('taggable.id'), primary_key=True),
#                 Column ('group_name', UnicodeText),
#                 Column ('display_name', UnicodeText))


# templates = Table ('templates', metadata,
#                    Column('id', Integer, ForeignKey('taggable.id'),  primary_key=True),
#                    Column ('name', Text))

#engines = Table('engines', metadata,
#                Column('id', Integer, primary_key=True),
#                Column('name', String))

# modules = Table ('modules', metadata,
#                  Column('id', Integer,
#                         ForeignKey('taggable.id'), primary_key=True),
#                  Column('name', Text),
#                  Column('codeurl', Text),
#                  Column('module_type_id', Integer, ForeignKey('names.id'))
#                  )

# mex = Table ('mex', metadata,
#              Column('id',  Integer,
#                     ForeignKey('taggable.id'), primary_key=True),
#              Column('module', Text),
#              Column('status', Text)
#              )

# dataset = Table ('datasets', metadata,
#                  Column('id', Integer, ForeignKey('taggable.id'), primary_key=True),
#                  Column('name', Text),
#                  )


#dataset_members = Table ('dataset_member',
#                         Column ('dataset_id',
#                                 ForeignKey('taggable.id'), primary_key=True),
#                         Column ('item_id',


#
# Registered services
# Allow bisquik installation to access remote services defined here.
# services = Table ('service', metadata,
#                   Column('id',  Integer,
#                          ForeignKey('taggable.id'), primary_key=True),
#                   Column('type', Text),
#                   Column('uri', Text),
#                   )

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

class Taggable(object):
    """
    Base type for taggable objects.  Taggable
    objects can have any number of name/value pairs
    associated with it.
    """
    xmltag = 'resource'

    def __init__(self, resource_type = None, parent = None, owner_id = None, mex_id = None):
        """Create a taggable resource : not usually called directly

        @param resource_type: A string type of the new resource i.e. user, project etc.
        @param parent: A parent of the resource or None
        @owner_id: An integer ID, a BQUser, current user if None, False : don't set
        @mex_id: An integer ID, A ModuleExecution, current mex if None, or False : don't set
        """
        if resource_type is None:
            resource_type = self.xmltag
        self.resource_type = resource_type
        # By defualt you are the document
        if parent:
            parent.children.append(self)
            self.document = parent.document
            self.perm = parent.perm
            self.hidden = parent.hidden
        else:
            self.document = self
            self.resource_uniq = make_uniq_code()
            self.perm = PRIVATE
            #self.hidden = None


        #if self.resource_type == 'mex':
        #    self.mex = self
        #    session['mex'] = self

        #if self.resource_type == 'user':
        #    self.owner = self

        self.ts = datetime.now()
        #log.debug("new taggable user:" + str(session.dough_user.__dict__) )
        if mex_id is not False:
            mex_id = mex_id or current_mex_id()
            log.debug ("mex_id = %s" ,  mex_id)
            if mex_id is not None:
                log.debug ("setting mex_id %s" , mex_id)
                self.mex_id = mex_id

        if owner_id is not False:
            owner_id  = owner_id or identity.get_user_id()
            if owner_id is not None:
                if isinstance(owner_id, Taggable):
                    self.owner = owner_id
                else:
                    self.owner_id = owner_id
            else:
                log.warn ("CREATING taggable %s with no owner" , str(self) )
                admin = identity.get_admin()
                if admin:
                    log.warn("Setting owner to admin")
                    self.owner_id = admin.id

    def resource (self):
        return "%s/%s" % ( self.table , self.id)
    resource = property(resource)

    def uri (self):
        if getattr(self,'parent',None):
            #parent = self.parent.loadFull()
            return "%s/%s/%s" % (self.parent.uri , self.resource_type, self.id)
            #return "%s/%s" % (self.resource_type, self.id)
        else:
            return "%s" % (self.resource_uniq)
            #return "%s/%s" % (self.resource_type, self.resource_uniq)
            #return "%s/%s" % (self.resource_type, self.id)

    uri = property(uri)


    @validates('owner')
    def validate_owner (self, key, owner):
        if isinstance(owner, basestring) and owner.startswith ('http'):
            log.warn ("validating owner  %s" , str(owner))
            return map_url (owner)
        return owner


#    def get_owner (self):
#        if self.owner_ob:
#            return self.owner_ob.user_name
#    def set_owner (self,name):
#        self.owner_ob = BQUser.filter_by (user_name=name).one()
#    owner = property(get_owner, set_owner)

    def clear(self, what=['all']):
        '''Clear all the children'''
        results = []
        if 'all' in what:
            results.extend(self.children) # pylint: disable=access-member-before-definition
            del self.children[:]
            del self.values[:]
            del self.vertices[:]
            #self.children = []
            #self.tags = []
            #self.gobjects = []
            #self.values = []
            #self.vertices = []
            log.debug ('cleared all')
            return results
        else:
            for tg in self.children:
                if tg.tag in what:
                    self.children.remove (tg)
                    results.append (tg)
        log.debug ('cleared %s', what)
        return results

    def findtag (self, nm, create=False):
        for t in self.children:
            if t.resource_type == 'tag' and t.resource_name == nm:
                return t
        t=None
        if create:
            t = Tag(parent = self)
            t.resource_name = nm
        return t

    def loadFull(self):
        'hack to load polymorphic taggable type'
        #table, dbtype = dbtype_from_name(self.table)
        #if dbtype != Taggable:
        #    return DBSession.query(dbtype).get (self.id)
        return self

    # Tag.indx used for ordering tags
    def get_index(self):
        return self.resource_index
    def set_index(self, v):
        self.resource_index = v
    index = property(get_index, set_index)

    # Tag.indx used for ordering tags
    def get_name(self):
        return self.resource_name
    def set_name(self, v):
        self.resource_name = v
    name = property(get_name, set_name)
    # Tag.indx used for ordering tags
    def get_type(self):
        return self.resource_user_type
    def set_type(self, v):
        self.resource_user_type = v
    type = property(get_type, set_type)

    def get_permission(self):
        return perm2str.get(self.perm)
    def set_permission(self, pmv):
        log.debug("permission deep = %s" , pmv)
        def set_perm_deep(n, pmv):
            n.perm = pmv
            for k in n.children:
                set_perm_deep(k, pmv)
        set_perm_deep(self, perm2code.get(pmv))
        #self.perm = perm2code.get(v)


    permission = property(get_permission, set_permission)

    def get_hidden(self):
        return self.resource_hidden
    def set_hidden(self, hdv):
        def set_hidden_deep(n, hdv):
            n.resource_hidden = hdv
            for k in n.children:
                set_hidden_deep(k, hdv)
        set_hidden_deep(self, (hdv in ('True', 'true', True)) or None)
        return self.resource_hidden
    hidden = property(get_hidden, set_hidden)

    # Tag.value helper functions
    # def newval(self, v, i = 0):
    #     if isinstance(v,basestring):
    #         v = Value(i, s = v)
    #     elif type(v) == int or type(v) == float:
    #         v = Value(i, n = v)
    #     elif isinstance(v, Taggable):
    #         v = Value(i, o = v)
    #     else:
    #         raise BadValue("Tag "+self.name, v)
    #     return v
    # def getvalue(self):
    #     if self.resource_value is not None:
    #         return self.resource_value
    #     else:
    #         # call SimpleValue decoder
    #         values =  [ v.value for v in self.values ]
    #         if len(values) == 0:
    #             return None
    #         return values
    # def setvalue(self, v):
    #     self.resource_value = None
    #     if isinstance(v, list):
    #         l = [ self.newval(v[i], i) for i in xrange(len(v)) ]
    #         self.values = l
    #     elif isinstance(v, basestring):
    #         self.resource_value = v
    #     else:
    #         l = [ self.newval(v, 0) ]
    #         self.values = l
    # value = property(fget=getvalue,
    #                  fset=setvalue,
    #                  doc="resource_value")

    def getval(self):
        return self.resource_value
    def setval(self, v):
        self.resource_value = v
    value = property(getval, setval, doc='resource_value')

    #def __repr__(self):
    #    return u"<%s: %s=%s>" % (self.resource_type, self.resource_name, self.resource_value)
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

    # def clear(self, what=None):
    #     '''Clear values from tag'''
    #     super(Tag, self).clear()
    #     log.debug ('cleared values')
    #     old = self.values
    #     self.values = []
    #     return old

class Value(object):
    xmltag = 'value'

    def __init__(self, ind=None, s = None, n = None, o = None):
        self.indx = ind
        self.valstr = s
        self.valnum = n
        self.valobj = o

    def geturi(self):
        return "%s/%s" % (self.parent.uri, self.indx)

    uri = property (geturi)
    def clear(self):
        pass

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
            #self.valstr = str(v)  # This works and stores the resource_uniq in the valstr
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
        return "<value %s>" % self.value


class Vertex(object):
    xmltag = 'vertex'

    def geturi(self):
        return "%s/%s" % (self.parent.uri, self.indx)

    uri = property (geturi)
    def clear(self):
        pass
    def get_index(self):
        return self.indx
    def set_index(self, v):
        self.indx = v
    index = property(get_index, set_index)
    def __str__ (self):
        return "<vertex x=%s y=%s z=%s t=%s ch=%s index=%s />" % (self.x, self.y,self.z,self.t,self.ch, self.indx)


class GObject(Taggable):
    xmltag = 'gobject'

    # def clear(self, what=None):
    #     '''Clear all the children'''
    #     super(GObject, self).clear()
    #     log.debug ('cleared vertices')
    #     old = self.vertices
    #     #self.vertices = []
    #     return old

#    def __str__(self):
#        return 'gobject %s:%s' % (self.name, str(self.type))



class BQUser(Taggable):
    '''
    User object
    '''
    xmltag = 'user'

    def __init__(self, user_name=None, password=None,
					email_address=None, display_name=None,
					create_tg=False, tg_user = None, create_store=True,**kw):
        super(BQUser, self).__init__()
        if not display_name: display_name = user_name

        if create_tg and tg_user is None:
            tg_user = User()
            tg_user.user_name = user_name
            tg_user.email_address = email_address
            tg_user.password = password
            tg_user.display_name = display_name
            DBSession.add(tg_user)

        self.permission = 'published'
        self.resource_name = tg_user.user_name
        self.resource_value = tg_user.email_address
        dn = Tag (parent = self)
        dn.name = 'display_name'
        dn.value = tg_user.display_name or tg_user.user_name
        dn.owner = self
        self.owner = self
        self.permission = 'published'

        if create_store:
            #from bq.commands.stores import init_stores
            #init_stores (tg_user.user_name)
            root_store = BQStore(owner_id = self)
            root_store.resource_name='(root)'
            root_store.resource_unid='(root)'
            DBSession.add(root_store)


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
            tg_user.user_name = email
            tg_user.email_address = email
            tg_user.password = password
            tg_user.display_name = email
            #tg_user.dough_user_id = self.id
            DBSession.add(tg_user)
            DBSession.flush()

        return bquser

    def user_id(self):
        return self.id
    user_id = property(user_id)

    def get_groups(self):
        return DBSession.query(User).filter_by(user_name = self.resource_name).first().groups

    #def __str__(self):
    #    return "<user:%d %s %s>" % (self.id, self.resource_name, self.resource_value)

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
    # def get_module_type(self):
    #     if self.module_type:
    #         return self.module_type
    #     return ""
    # def set_module_type(self, v):
    #     self.module_type = UniqueName(v)
    # type = property(get_module_type, set_module_type)

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
    # alias for resource_value
    #status = taggable.c.resource_value
    #@hybrid_property
    def getstatus(self):
        return self.resource_value
    #@status.setter
    def setstatus(self, v):
        self.resource_value = v
    status = property(getstatus,setstatus)


class Dataset(Taggable):
    xmltag = 'dataset'

class BQStore(Taggable):
    xmltag = 'store'


class TaggableAcl(object):
    """A permission for EDIT or READ on a taggable object
    """
    xmltag = "auth"


    def setaction(self, perm):
        self.action_code = { "read":0, "edit":1 } .get(perm, 0)
    def getaction(self):
        return [ "read", "edit"] [self.action_code]

    action = property(getaction, setaction)

    def __str__(self):
        return "resource:%s  user:%s permission:%s" % (self.taggable_id,
                                                       self.user_id,
                                                       self.action)


class Service (Taggable):
    """A executable service"""
    xmltag = "service"

    def __str__(self):
        return "<service %s %s %s>" % (self.resource_name, self.resource_value, self.resource_user_type)

#################################################
# Simple Mappers
#mapper( UniqueName, names)
#session.mapper(UniqueName, names)

mapper( Value, values,
        properties = {
        #'resource_parent_id' : values.c.parent_id,
        #'parent' : relation (Taggable,
        #                 primaryjoin =(taggable.c.id == values.c.parent_id)),
        'objref' : relation(Taggable, uselist=False,
                            primaryjoin=(values.c.valobj==taggable.c.id),
                            enable_typechecks=False
                            ),
        #'document' : relation(Taggable, uselist=False,lazy=True,
        #                      primaryjoin=(values.c.document_id==taggable.c.id),
        #                      enable_typechecks=False,
        #                      )
        }
        )

mapper( Vertex, vertices,
        properties = {
        #'document' : relation(Taggable, uselist=False, lazy=True,
        #                      primaryjoin=(vertices.c.document_id==taggable.c.id),
        #                      enable_typechecks=False,
        #                      )
        }
        )
mapper(TaggableAcl, taggable_acl,)

############################
# Taggable mappers

taggable_discr = case (
    [(taggable.c.resource_type=='image', "image"),
     (taggable.c.resource_type=='tag', "tag"),
     (taggable.c.resource_type=='gobject', "gobject")],
     else_ = "taggable"
    )


mapper( Taggable, taggable,
#        polymorphic_on = taggable_discr,
#        polymorphic_identity = 'taggable',
                       properties = {
    # 'tags' : relation(Taggable, lazy=True, viewonly=True, #cascade="all, delete-orphan", passive_deletes=True,
    #                   #remote_side=[taggable.c.resource_parent_id, taggable.c.resource_type],
    #                   primaryjoin= and_(remote(taggable.c.resource_parent_id)==taggable.c.id,
    #                                     taggable.c.resource_type == 'tag'),
    #                   ),
    # 'gobjects' : relation(Taggable, lazy=True, viewonly=True, #cascade="all, delete-orphan", passive_deletes=True,
    #                       #remote_side=[taggable.c.resource_parent_id, taggable.c.resource_type],
    #                       primaryjoin= and_(remote(taggable.c.resource_parent_id)==taggable.c.id,
    #                                         remote(taggable.c.resource_type) == 'gobject')),

    'acl'  : relation(TaggableAcl, lazy=True, cascade="all, delete-orphan", passive_deletes=True,
                      primaryjoin = (TaggableAcl.taggable_id == taggable.c.document_id),
                      foreign_keys=[TaggableAcl.taggable_id],
                      backref = backref('resource', enable_typechecks=False, remote_side=[taggable.c.document_id])),

    'children' : relation(Taggable, lazy=True, cascade="all, delete-orphan", passive_deletes=True,
                          enable_typechecks = False,
                          primaryjoin = (taggable.c.id == taggable.c.resource_parent_id),
                          order_by = taggable.c.resource_index,
                          collection_class = ordering_list ('resource_index'),
                          backref = backref('parent', enable_typechecks=False, remote_side = [taggable.c.id]),
                          ),

    'childrenq' : relation(Taggable, lazy='dynamic', viewonly=True,
                           enable_typechecks = False,
                           primaryjoin = (taggable.c.id == taggable.c.resource_parent_id),
                           #remote_side = [taggable.c.resource_parent_id],

                           order_by = taggable.c.resource_index,
    #                       #collection_class = ordering_list ('resource_index')
                          ),

    'values' : relation(Value,  lazy=True, cascade="all, delete-orphan", passive_deletes=True,
                        order_by=[values.c.indx],
                        collection_class = ordering_list ('indx'),
                        primaryjoin =(taggable.c.id == values.c.resource_parent_id),
                        backref = backref('parent', enable_typechecks = False, remote_side=[taggable.c.id])
                        #foreign_keys=[values.c.parent_id]
                        ),
    'vertices':relation(Vertex, lazy=True, cascade="all, delete-orphan", passive_deletes=True,
                        order_by=[vertices.c.indx],
                        collection_class = ordering_list ('indx'),
                        primaryjoin =(taggable.c.id == vertices.c.resource_parent_id),
                        backref = backref('parent', enable_typechecks=False, remote_side=[taggable.c.id]),
                        #foreign_keys=[vertices.c.resource_parent_id]
                        ),

    # 'tagq' : relation(Taggable, lazy='dynamic',
    #                   remote_side=[taggable.c.resource_parent_id, taggable.c.resource_type],
    #                   primaryjoin= and_(remote(taggable.c.resource_parent_id)==taggable.c.id,
    #                                     remote(taggable.c.resource_type) == 'tag')),

    # The following primarily create a valid .document for Taggable, vertex, and value

    'docnodes': relation(Taggable, lazy=True,
                         cascade = "all, delete-orphan", passive_deletes=True,
                         enable_typechecks = False,
                         primaryjoin = (taggable.c.id == taggable.c.document_id),
                         backref = backref('document', #post_update=True,
                                           enable_typechecks=False, remote_side=[taggable.c.id]),
                         post_update = True,
                         ),

     'docvalues' : relation (Value, lazy=True,
                             cascade = "all, delete-orphan", passive_deletes=True,
                          enable_typechecks = False,
                          primaryjoin = (taggable.c.id == values.c.document_id),
                          backref = backref('document', #post_update=True,
                                            enable_typechecks=False, remote_side=[taggable.c.id]),
                          ),
     'docvertices' : relation (Vertex, lazy=True,
                               cascade = "all, delete-orphan", passive_deletes=True,
                          enable_typechecks = False,
                          primaryjoin = (taggable.c.id == vertices.c.document_id),
                          backref = backref('document', #post_update=True,
                                            enable_typechecks=False, remote_side=[taggable.c.id]),
                           ),
    }
        )

mapper( Image, inherits=Taggable,
        polymorphic_on = taggable.c.resource_type,
        polymorphic_identity = 'image',
        )
mapper( Tag, inherits=Taggable,
        polymorphic_on = taggable.c.resource_type,
        polymorphic_identity = 'tag',)
mapper( GObject,  inherits=Taggable,
        polymorphic_on = taggable.c.resource_type,
        polymorphic_identity = 'gobject',)
mapper(BQUser,  inherits=Taggable,
       polymorphic_on = taggable.c.resource_type,
       polymorphic_identity = 'user',
       properties = {
        'tguser' : relation(User, uselist=False,
            primaryjoin=(User.user_name == taggable.c.resource_name),
            foreign_keys=[User.user_name]),

        'owns' : relation(Taggable, lazy=True,
                          cascade = "all, delete-orphan", passive_deletes=True,
                          post_update = True,
                          enable_typechecks=False,
                          primaryjoin = (taggable.c.id == taggable.c.owner_id),
                          backref = backref('owner', post_update=True, remote_side=[taggable.c.id]),
                          ),

        'user_acls': relation(TaggableAcl,  lazy=True, cascade="all, delete-orphan",
                              passive_deletes = True,
                              primaryjoin= (taggable.c.id == taggable_acl.c.user_id),
                              backref = backref('user', enable_typechecks=False),
                              )

        }
       )
mapper(Template, inherits=Taggable,
        polymorphic_on = taggable.c.resource_type,
        polymorphic_identity = 'template')
mapper(Module, inherits=Taggable,
        polymorphic_on = taggable.c.resource_type,
        polymorphic_identity = 'module',)
mapper(ModuleExecution,  inherits=Taggable,
       polymorphic_on = taggable.c.resource_type,
       polymorphic_identity = 'mex',
       properties = {
        #"status":synonym("resource_value"), # map_column=True) ,
        'owns' : relation(Taggable,
                          lazy = True,
                          cascade = "all, delete-orphan", passive_deletes=True,
                          #cascade = None,
                          post_update = True,
                          enable_typechecks=False,
                          primaryjoin = (taggable.c.id == taggable.c.mex_id),
                          backref = backref('mex', post_update=True, remote_side=[taggable.c.id])),
        })
mapper( Dataset,  inherits=Taggable,
        polymorphic_on = taggable.c.resource_type,
        polymorphic_identity = 'dataset',)
mapper( BQStore,  inherits=Taggable,
        polymorphic_on = taggable.c.resource_type,
        polymorphic_identity = 'store',)
mapper( Service, inherits=Taggable,
        polymorphic_on = taggable.c.resource_type,
        polymorphic_identity = 'service')

#################################################
# Support Functions

#class_mapper(User).add_property('dough_user',
#    relation(BQUser,
#         primaryjoin=(User.dough_user_id == Taggable.id),
#         foreign_keys=[Taggable.id],
#    )
#)

def bquser_callback (tg_user, operation, **kw):
    # Deleted users will receive and update callback
    if tg_user is None:
        return
    if operation =='create':
        u = DBSession.query(BQUser).filter_by(resource_name=tg_user.user_name).first()
        if u is None:
            u = BQUser(tg_user=tg_user)
            DBSession.add(u)
            #log.info ('---> created BQUSER', tg_user.user_name, tg_user.email_address)
            
            try:
                log.info('created an iRODS user with password %s' , str(tg_user.password))
                irods_integ = BisQueIrodsIntegration()
                irods_integ.load_from_env()
                irods_integ.create_user(str(tg_user.user_name), str(tg_user.password))
                log.info ('created an iRODS user %s for BQUSER %s' , (tg_user.user_name, u.name))
            except Exception as e:
                log.exception ("An exception occured during iRODS account creation: %s" , str(e))
            try:
                subprocess.call(["mc", "admin", "user", "add", "ucsb", str(tg_user.user_name), str(tg_user.email_address)])
                subprocess.call(["mc", "admin", "group", "add", "ucsb", 'bisque', str(tg_user.user_name)])
                subprocess.call(["mc", "mb", "ucsb/{}".format(str(tg_user.user_name))])
            except Exception as e:
                log.exception ("An exception occured during MINIO S3 account creation: %s" , str(e))
        return


    if operation  == 'update':
        
        u = DBSession.query(BQUser).filter_by(resource_name=tg_user.user_name).first()
        if u is not None:
            u.value = tg_user.email_address
            dn = u.findtag('display_name', create=True)
            dn.value = tg_user.display_name
            dn.permission = 'published'
            log.info ('updated BQUSER %s' , u.name)

            # if password is updated
            if tg_user.password:
                # update iRODS Account
                try:
                    log.info('changing an iRODS user with password %s' , str(tg_user.password))
                    irods_integ = BisQueIrodsIntegration()
                    irods_integ.load_from_env()
                    irods_integ.update_user_password(str(tg_user.user_name), str(tg_user.password))
                    log.info ('updated the password of the iRODS user %s for BQUSER %s' , (tg_user.user_name, u.name))
                except Exception as e:
                    log.exception ("An exception occured during iRODS account update: %s" , str(e))
        return

User.callbacks.append (bquser_callback)

def registration_hook(action, **kw):
    log.info ('regisration_hook %s -> %s' % (action, kw))
    if action=="new_user":
        u = kw.pop('user', None)
        if u:
            BQUser.new_user (u.email_adress, u.password)
    elif action=="update_user":
        u = kw.pop('user', None)
        if u:
            bquser = DBSession.query(BQUser).filter_by(resource_value=u.email_address).first()
            if not bquser:
                bquser = BQUser.new_user (u.email_adress, u.password)
            dn = bquser.findtag('display_name', create=True)
            dn.value = u.display_name
            dn.permission = 'published'
            #bquser.display_name = u.display_name
            bquser.resource_name = u.user_name
            log.error('Fix the display_name')
    elif action =="delete_user":
        pass

def current_mex_id ():
    mex_id = None
    if hasattr(request,'identity'):
        mex_id = request.identity.get('bisque.mex_id', None)
        log.debug ("IDENTITY request %s" , (mex_id == 'None'))
    if mex_id is None:
        try:
            mex_id = session.get('mex_id', None)
            if mex_id is None and 'mex_uniq' in session :
                mex = DBSession.query(ModuleExecution).filter_by(resource_uniq = session['mex_uniq']).first()
                mex_id = session['mex_id'] = mex.id
            log.debug ("IDENTITY session %s" , ( mex_id == 'None'))
        except TypeError:
            # ignore bad session object
            pass
    if mex_id is None:
        log.debug("using initialization mex")
        if hasattr(request, 'initial_mex_id'):
            mex_id = request.initial_mex_id
        else:
            mex = DBSession.query(ModuleExecution).filter_by(
                resource_user_type = "initialization").first()
            if mex is None:
                log.error("No initialization (system) mex found: creating")
                #initial_mex = ModuleExecution()
                #initial_mex.mex = initial_mex
                #initial_mex.name = "initialization"
                #initial_mex.type = "initialization"
                #DBSession.add(initial_mex)
                #DBSession.flush()
                #DBSession.refresh(initial_mex)
                #mex = initial_mex

            mex_id = mex and mex.id
    if hasattr(request, 'identity') and mex_id is not None:
        request.identity['bisque.mex_id'] = mex_id

    log.debug ('IDENTITY mex_id %s' , mex_id)

    return mex_id


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


FILTERED=['user', 'system', 'store']

#@memoized
def all_resources ():
    ''' Return the setof unique names that are taggable objects
    '''
    #names = DBSession.query(UniqueName).filter(UniqueName.id == Taggable.tb_id).all()
    #log.debug ('all_resources' + str(names))
    names = [ x[0] for x in DBSession.query(Taggable.resource_type).filter_by (resource_parent_id=None).distinct().all() if x[0] not in FILTERED ]
    return names
