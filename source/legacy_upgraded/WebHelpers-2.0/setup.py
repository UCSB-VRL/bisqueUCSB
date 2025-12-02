from setuptools import setup, find_packages

version = '2.0.0'

setup(
    name="WebHelpers",
    version=version,
    description='Web Helpers - Utility Functions for Web Applications',
    long_description="""
Web Helpers is a library of helper functions intended to make writing 
web applications easier. It's the standard function library for
Pylons and TurboGears 2, but can be used with any web framework. It also
contains a large number of functions not specific to the web, including text
processing, number formatting, date calculations, container objects, etc.

Version 2.0.0 updates the library to be compatible with Python 3.10+ and
improves performance for SQLAlchemy paginate functionality.

WebHelpers itself depends only on MarkupSafe, but certain helpers depend on
third-party packages as described in the docs.

The development version of WebHelpers is at
https://github.com/wskoly/webhelpers (forked from the original Bitbucket repo)

""",
    author='Wahid Sadique Koly (original authors: Mike Orr, Ben Bangert, Phil Jenvey)',
    author_email='contact@wskoly.xyz',
    # url='https://github.com/wskoly/webhelpers',  # Update with your fork or official URL
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'MarkupSafe>=2.0.1',  # Updated to ensure compatibility with Python 3.10+
    ],
    tests_require=[
        'nose',
        'Routes',
        'WebOb',
    ],
    test_suite='nose.collector',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points="""
    [buildutils.optional_commands]
    compress_resources = webhelpers.commands
    """,
    # python_requires='>=3.10',  # Ensure compatibility with Python 3.10+
)
