import os
from sqlalchemy import  MetaData, create_engine
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker, mapper as sa_mapper
from bq.util.configfile import ConfigFile

tc = ConfigFile()
if os.path.exists ('config/site.cfg'):
    tc.read(open('config/site.cfg'))
db = tc.get('app:main', 'sqlalchemy.url')
if db is None:
    print "Please set sqlalchemy.url in site.cfg "




engine = None
metadata = MetaData()

maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

def session_mapper (scoped_session):
    def mapper (cls, *arg, **kw):
        cls.query = scoped_session.query_property ()
        return sa_mapper (cls, *arg, **kw)
    return mapper

mapper = session_mapper (DBSession)


#engine = create_engine(db, echo = False)
if engine:
    metadata.bind = engine
    DBSession.configure(bind=engine)
    print "attached to", engine
