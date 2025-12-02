#!/usr/bin/env python
import sys
from setuptools import setup, find_packages

version = '2.0.0'

tests_require = ['nose', 'Jinja2>=2.2.1']
if not sys.platform.startswith('java'):
    tests_require.extend(['Genshi', 'coverage>=2.85'])

setup(
    name="Pylons",
    version=version,
    description='Forked and updated Pylons Web Framework (Python 3.10+ compatible)',
    long_description=open("README.rst").read(),
    keywords='web wsgi lightweight framework sqlalchemy formencode mako templates',
    license='BSD',
    author='Wahid Sadique Koly (original authors: Ben Bangert, Philip Jenvey, James Gardner)',
    author_email='contact@wskoly.xyz',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=tests_require,
    install_requires=[
        "Routes>=2.5.1", "WebHelpers>=1.3", "Beaker>=1.13.0",
        "Paste>=3.10.1", "PasteDeploy>=3.1.0", "PasteScript>=3.7.0",
        "FormEncode>=2.1.1", "simplejson>=3.20.1", "decorator>=5.2.1",
        "nose>=1.3.7", "Mako>=1.3.10", "WebError>=0.13.1", "WebTest>=3.0.4",
        "Tempita>=0.6.0", "MarkupSafe>=3.0.2", "WebOb>=1.8.9",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Framework :: Pylons",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    extras_require={
        'genshi': ['Genshi==0.7.9'],
        'jinja2': ['Jinja2'],
    },
    # python_requires='>=3.10',
    entry_points="""
    [paste.paster_command]
    controller = pylons.commands:ControllerCommand
    restcontroller = pylons.commands:RestControllerCommand
    routes = pylons.commands:RoutesCommand
    shell = pylons.commands:ShellCommand

    [paste.paster_create_template]
    pylons = pylons.util:PylonsTemplate
    pylons_minimal = pylons.util:MinimalPylonsTemplate

    [paste.filter_factory]
    debugger = pylons.middleware:debugger_filter_factory

    [paste.filter_app_factory]
    debugger = pylons.middleware:debugger_filter_app_factory
    """,
)
