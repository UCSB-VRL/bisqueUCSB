#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='Minimatic',
    version='2.0',
    description='Upgraded version of Minimatic for Python 3.10+: CSS and Javascript Minification/Combination for WebHelpers',
    long_description=open('README.txt').read(),
    author='Wahid Sadique Koly (original author: Pedro Algarvio)',
    author_email='contact@wskoly.xyz',
    maintainer='Wahid Sadique Koly',
    maintainer_email='contact@wskoly.xyz',
    install_requires=[
        "Pylons",
        "WebHelpers",
        "beaker",
        "cssutils"
    ],
    tests_require=['nose'],
    test_suite='nose.collector',
    zip_safe=False,
    packages=find_packages(exclude=['tests', 'tests.fixtures']),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pylons',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    # python_requires='>=3.10',
)
