from setuptools import setup, find_packages

version = '2.0.0'

install_requires = [
    'WebOb',
    'Tempita',
    'Pygments',
    'Paste',
]

with open('README.rst', encoding='utf-8') as f:
    README = f.read()

with open('CHANGELOG', encoding='utf-8') as f:
    CHANGELOG = f.read()

setup(
    name='WebError',
    version=version,
    description="Web Error handling and exception catching (modernized for Python 3.10+)",
    long_description=README + '\n\n' + CHANGELOG,
    long_description_content_type='text/x-rst',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
    ],
    keywords='wsgi error-handling middleware',
    author='Wahid Sadique Koly (original authors: Ben Bangert, Ian Bicking, Mark Ramm)',
    author_email='contact@wskoly.xyz',
    # url='https://github.com/wskoly/weberror', 
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    package_data={'weberror.evalexception': ["*.html.tmpl", "media/*"]},
    zip_safe=False,
    install_requires=install_requires,
    python_requires='>=3.10',
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'webtest',
        'Paste'
    ],
    entry_points="""
    [paste.filter_app_factory]
    main = weberror.evalexception:make_general_exception
    error_catcher = weberror.errormiddleware:make_error_middleware
    evalerror = weberror.evalexception:make_eval_exception
    """,
)
