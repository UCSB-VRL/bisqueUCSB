# -*- coding: utf-8 -*-
"""Setup the bqcore application"""
import pkg_resources
import logging
import transaction
from tg import config
import bq
from bq.util.paths import config_path

log = logging.getLogger('bq.websetup')
def setup_schema(command, conf, vars):
    """Place any commands to setup bq here"""
    # Load the models
    # <websetup.websetup.schema.before.metadata.create_all>
    log.info ( "Creating all tables" )
    bq.core.model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)
    #for tb_name, tb in bq.core.model.metadata.tables.items():
    #    print ('creating %s %s' % (tb_name, tb))
    #    tb.create(bind=config['pylons.app_globals'].sa_engine)
    for x in pkg_resources.iter_entry_points ("bisque.services"):
        try:
            log.info ('found service %s' % x)
            service = x.load()
        except Exception:
            log.exception("Issue loading %s" % x)
            continue
        log.info ("Creating tables for " + str(x))
        if hasattr(service, 'get_model'):
            model = service.get_model()
            if hasattr (model, 'create_tables'):
                model.create_tables(bind=config['pylons.app_globals'].sa_engine)
            else:
                model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine, checkfirst=True)

    #model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)
    # <websetup.websetup.schema.after.metadata.create_all>

    # then, load the Alembic configuration and generate the
    # version table, "stamping" it with the most recent rev:
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config(config_path ("alembic.ini"))
    #alembic_cfg = Config(config['global_conf']['__file__'])
    command.stamp(alembic_cfg, "head")
    transaction.commit()

