"""use ondelete

Revision ID: 4687c8254c92
Revises: None
Create Date: 2012-08-03 10:51:24.484005

"""

# revision identifiers, used by Alembic.
revision = '4687c8254c92'
down_revision = None
extend_existing=True

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Remove old Foreign Contraints
    from sqlalchemy.engine.reflection import Inspector 
    insp = Inspector.from_engine(op.get_bind()) 

    for table in ('taggable', 'values', 'vertices', 'taggable_acl'):
        fks = insp.get_foreign_keys(table) 
        for fk in fks:
            print "Dropping Constraint : %s" % fk
            op.drop_constraint(fk['name'], table, "foreignkey")
    print "Creating new foriegn keys"
    for table in ('taggable', 'values', 'vertices', ):
        op.create_foreign_key("%s_children_fk" % table, 
                              table, 'taggable', 
                              ["resource_parent_id"], ["id"],
                              ondelete="CASCADE")
        op.create_foreign_key("%s_document_fk" %table, 
                              table , 'taggable', 
                              ["document_id"], ["id"],
                              ondelete="CASCADE")
    op.create_foreign_key("mex_fk", 'taggable', 'taggable', ['mex_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key("owner_fk", 'taggable', 'taggable', ['owner_id'], ['id'], ondelete='CASCADE')

    op.create_foreign_key("user_fk", 'taggable_acl', 'taggable', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key("taggable_fk", 'taggable_acl', 'taggable', ['taggable_id'], ['id'], ondelete='CASCADE')


def downgrade():
    print "Removing foreign keys"
    for table in ('taggable', 'values', 'vertices'):
        op.drop_constraint( "%s_children_fk" %table,  table, 'foreignkey')
        op.drop_constraint( "%s_document_fk" %table,  table, 'foreignkey')
