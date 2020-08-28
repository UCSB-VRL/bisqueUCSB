"""clean_orphans

Revision ID: 138f50ba7665
Revises: 318381ec60ba
Create Date: 2018-04-30 13:32:02.538417

"""

# revision identifiers, used by Alembic.
revision = '138f50ba7665'
down_revision = '318381ec60ba'

import csv
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table

#from sqlalchemy import Table, MetaData, and_, disctinct
#from sqlalchemy.orm import sessionmaker
#from sqlalchemy.ext.declarative import declarative_base


def upgrade():
    conn = op.get_bind()
    ### Delete older 'preference' resource in resources where two or more exist

    # First save what you are deleting to 'preferences.csv'
    results = conn.execute ("""
    select * from taggable as t1, taggable as t2  where t1.resource_type = 'preference'  and t2.resource_type = 'preference' and t1.resource_parent_id = t2.resource_parent_id  and t1.id != t2.id and (t1.document_id, t1.id) not in ( select t1.document_id, max (t1.id) from taggable as t1 where  t1.resource_type = 'preference'  group by t1.document_id );
    """)
    with open ('preferences.csv', 'wb') as pref_file:
        pref_csv   = csv.writer (pref_file)
        row = results.fetchone()
        if row:
            pref_csv.writerow (row.keys())
            pref_csv.writerow (row.values())
        for row in results:
            pref_csv.writerow (row.values())

    #conn = op.get_bind()
    conn.execute (
        """delete from taggable where id in ( select  distinct t1.id    from taggable as t1, taggable as t2  where t1.resource_type = 'preference'  and t2.resource_type = 'preference' and t1.resource_parent_id = t2.resource_parent_id  and t1.id != t2.id and (t1.document_id, t1.id) not in ( select t1.document_id, max (t1.id) from taggable as t1 where  t1.resource_type = 'preference'  group by t1.document_id) ); """
                  )




    ### Delete all orphans (taggable with no parent that are not top-level i.e. have uniq)
    # First save what you are deleting to 'parent.csv'
    results = conn.execute (
        """
        select * from taggable where resource_parent_id is null and resource_uniq is null;
        """)
    with  open ('parent.csv', 'wb') as parent_file:
        parent_csv   = csv.writer (parent_file)
        row =  results.fetchone()
        if row:
            parent_csv.writerow (row.keys())
            parent_csv.writerow (row.values())
        for row in results:
            parent_csv.writerow (row.values())
    conn.execute (
        """
        delete from taggable where resource_parent_id is null and resource_uniq is null;
        """)

def downgrade():
    conn = op.get_bind()

    taggable = table ('taggable')
    with  open ('parent.csv', 'rb') as parent_file:
        parent_csv   = csv.DictReader (parent_file)
        conn.execute (taggable.insert(), [ dct for dct in parent_csv ])

    with  open ('preferences.csv', 'rb') as pfile:
        pcsv   = csv.DictReader (pfile)
        conn.execute (taggable.insert(), [ dct for dct in pcsv ])
