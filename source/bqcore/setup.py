# -*- coding: utf-8 -*-
#quckstarted Options:
#
# sqlalchemy: True
# auth:       sqlalchemy
# mako:       False
#
#

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

#from bq.release import __VERSION__
__VERSION__="0.5.9"

setup(
    name='bqcore',
    version=__VERSION__,
    description='',
    author='',
    author_email='',
    #url='',
    install_requires=[
        "Pylons==1.0",
        "WebOb==1.0.8", # WebOb==1.0.8bisque1
        "decorator>=3.3",
        "TurboGears2==2.1.5", #TurboGears2==2.1.5bisque
        "Genshi",
        "zope.sqlalchemy >= 0.4",
        "repoze.tm2 >= 1.0a5",
        "SQLAlchemy",
        #"sqlalchemy-migrate",
        "Alembic",
        "repoze.what-quickstart",
        "repoze.what >= 1.0.8",
        "repoze.what-quickstart",
        "repoze.who-friendlyform >= 1.0.4",
        "repoze.what-pylons >= 1.0",
        "repoze.what.plugins.sql",
        "repoze.who <= 1.99",
#        "tgext.admin >= 0.3.9",
        "tw.forms",
        #"repoze.who.plugins.ldap",  #Optional for LDAP login
        #"repoze.who.plugins.openid",  #Optional for OpenID login


        # "TurboGears2 == 2.1.2",
        # "SQLAlchemy >= 0.7.2",
        # "zope.sqlalchemy >= 0.4",
        # "repoze.tm2 >= 1.0a5",
        # "repoze.what-quickstart",
        # "repoze.what >= 1.0.8",
        # "repoze.what-quickstart",
        # "repoze.who-friendlyform >=1.0.4",
        # "repoze.what-pylons >= 1.0rc3",
        # "repoze.what.plugins.sql",
        # "repoze.who ==1.0.18",
        # #"repoze.who.plugins.ldap",  #Optional
        # "tgext.admin>=0.3.9",
        # "tw.forms",
        #########################
        # Bisque dependencies
        "lxml",
#        "virtualenv",
        "poster",
        "linesman",
        "shortuuid",
        #"Minimatic",
        ],
    #setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2'],
    packages=find_packages (),
    namespace_packages = ['bq'],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest',
                   'Nose',
                   'coverage',
                   'wsgiref',
                   'repoze.who-testutil',
                   'pylint',
                   ],
    #package_data={'bq': ['core/i18n/*/LC_MESSAGES/*.mo',
    #                             'core/templates/*/*',
    #                             'core/public/*/*']},

    message_extractors={'bq': [
            ('**.py', 'python', None),
            ('core/templates/**.mako', 'mako', None),
            ('core/templates/**.html', 'genshi', None),
            ('core/public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = bq.config.middleware:make_app

    [paste.filter_factory]
    add_global = bq.config.middleware:add_global

    [paste.app_install]
    main = pylons.util:PylonsInstaller

      [console_scripts]
      bq-admin = bq.commands.admin:main
      bqdev-upload-binary = bq.commands.uploadbinary:main
      bq-upload-images = bq.commands.uploadimages:main

      [bq.commands]
      create-core    = bq.commands.create:createCoreService
      create-service = bq.commands.create:createService
      create-module = bq.commands.create:createModule
      server = bq.commands.admin:server
      setup   = bq.commands.admin:setup
      deploy   = bq.commands.admin:deploy
      sql     = bq.commands.admin:sql
      preferences= bq.commands.admin:preferences
      database  = bq.commands.admin:database
      stores    = bq.commands.admin:stores
      password    = bq.commands.admin:password
      hosturl     = bq.commands.admin:hosturl

      [paste.paster_create_template]
      bisque_core = bq.commands.bisque_template:CoreServiceTemplate
      bisque_service = bq.commands.bisque_template:ServiceTemplate
      bisque_module = bq.commands.bisque_template:ModuleTemplate

      [bisque.services]
      core   = bq.core.controllers.root

    """,
)
