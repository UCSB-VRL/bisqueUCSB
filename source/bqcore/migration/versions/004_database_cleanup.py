from migrate import *
from sqlalchemy import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata

    from migration.versions.env002 import DBSession, metadata

    # meta = MetaData()
    metadata.bind = migrate_engine
    DBSession.configure(bind=migrate_engine)

    # Removing unused columns and tables
    from migration.versions.model002 import (
        dataset,
        files,
        files_acl,
        gobjects,
        groups,
        images,
        mex,
        modules,
        names,
        services,
        taggable,
        tags,
        templates,
        users,
        values,
        vertices,
    )

    ForeignKeyConstraint(columns=[taggable.c.tb_id], refcolumns=[names.c.id]).drop()
    taggable.c.tb_id.drop()
    taggable.c.mex_id.alter(name="mex_id")
    values.c.parent_id.alter(name="resource_parent_id")
    vertices.c.parent_id.alter(name="resource_parent_id")
    # Indexes
    doc_index = Index("resource_document_idx", taggable.c.document_id)
    doc_index.create()
    parent_index = Index("resource_parent_idx", taggable.c.resource_parent_id)
    parent_index.create()
    type_index = Index("resource_type_idx", taggable.c.resource_type)
    type_index.create()

    services.drop()
    dataset.drop()
    mex.drop()
    modules.drop()
    templates.drop()
    groups.drop()
    users.drop()
    images.drop()
    gobjects.drop()
    tags.drop()
    names.drop()

    files_acl.drop()
    files.drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pass
