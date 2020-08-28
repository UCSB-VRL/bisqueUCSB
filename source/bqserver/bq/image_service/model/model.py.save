import logging

from sqlalchemy import Table, Column, Integer, String, Text, Index, MetaData, DateTime, ForeignKey, UnicodeText, Unicode
from sqlalchemy.orm import mapper,  relation
from sqlalchemy.exc import ProgrammingError
from tg import config


from bq.core.model import metadata, DBSession as session

log = logging
log = logging.getLogger('bq.blobdb')


files = Table('files', metadata,
              Column('id', Integer, primary_key=True),
              Column('sha1', String(40), index=True), # new column v2
              Column('uri', Unicode(512), index=True),
              Column('owner', Text), 
              Column('perm', Integer),
              Column('ts', DateTime(timezone=False)),
              Column('original', Text),
              Column('file_type', Text), # new column v2
              Column('local', Text) # new column v3              
              )

file_acl = Table('file_acl', metadata,
                 Column('id', Integer, ForeignKey('files.id'), primary_key=True),
                 Column('user', Unicode(255), primary_key=True),
                 Column('permission', Integer),
                 )

#sha1_index = Index ('sha1_index', files.c.sha1)
#file_url_index = Index ('file_url_index', files.c.uri)


#def create_tables(bind):
#    metadata.bind = bind 
#    print "CREATE BLOBDB TABLES"
#    files.create(checkfirst=True)
#    file_acl.create(checkfirst=True)
#    sha1_index = create_index ('sha1_index', files.c.sha1)
#    file_url_index = create_index ('file_url_index', files.c.uri)
    

#############################################################
# FileEntry
#############################################################
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

class FileAcl(object):
    pass

#############################################################
# DB
#############################################################

mapper(FileAcl, file_acl)
mapper(FileEntry, files, properties={
    '_id_db' : files.c.id,
    'acls'  : relation(FileAcl, lazy=True, cascade="all, delete-orphan",
                      #primaryjoin = (FileEntry.id == FileAcl.id),
                      )

    })

#turbogears.startup.call_on_startup.append(create_tables)

