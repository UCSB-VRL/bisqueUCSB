#!/usr/bin/env python
import sys
import os
from migrate.versioning.shell import main
import bq
from bq.util.configfile import ConfigFile
from bq.release import __VERSION__ as bq_version
from sqlalchemy import create_engine, sql
def sqltext(DBURI, statement):
    try:
        engine = create_engine(DBURI, echo= False)
        result = engine.execute(sql.text(statement))
        return 0, result.fetchall()
    except Exception:
        pass
    return 1, []


# first pull initial values from config files
#iv = initial
tc = ConfigFile()
if os.path.exists ('config/site.cfg'):
    tc.read(open('config/site.cfg'))

db = tc.get('app:main', 'sqlalchemy.url')
if db is None:
    print "Please set sqlalchemy.url in site.cfg "

def check_upgrade(db):
    ' Reset version numbers to 0  when moving to 0.5.1'
    #
    result, rows =  sqltext(db, "select count(*) from files;")
    if result == 1:
        return
    result, rows =  sqltext(db, "select version from migrate_version;")
    if result == 0:
        version = int(rows[0][0])
        if version >3:
            sqltext(db, 'update migrate_version set version=0;');



check_upgrade(db=db)
main(url=db, repository='bqcore/migration/')

