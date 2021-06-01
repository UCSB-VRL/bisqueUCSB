# -*- coding: utf-8 -*-
"""Setup the bqcore application"""

import logging

from bq.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)

from schema import setup_schema
import bootstrap

def setup_app(command, conf, vars):
    log.info("+++++++++++\n\n\n\n\nSetting up app+++++++++++")
    """Place any commands to setup bq here"""
    load_environment(conf.global_conf, conf.local_conf)
    log.info("=================\n\n\n\nEnvironment loaded")
    setup_schema(command, conf, vars)
    log.info("==================\n\n\n\nsetup schema done")
    bootstrap.bootstrap(command, conf, vars)
    log.info("===================\n\n\n\nbootstrap done")

