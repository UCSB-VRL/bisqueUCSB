
from setuptools import setup, find_packages

#from bq.release import __VERSION__
__VERSION__="0.5.9"

setup(
    name='bqengine',
    version=__VERSION__,
    description='',
    author='',
    author_email='',
    #url='',
    install_requires=[
#                      "bqapi",
                      "httplib2",
                      "pyinstaller",
                      ],
    packages= find_packages(),
    namespace_packages = ['bq'],
    setup_requires=["hgtools"],
    include_package_data=True,
    zip_safe = False,
    #include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    #package_data={'': ['*.html',]},
    message_extractors = {'bq': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.paster_command]
    load_engine = bq.engine.commands.load_engine:LoadEngine
    [paste.paster_global_command]
    load_glo_engine = bq.engine.commands.load_engine:LoadEngine
    [bisque.services]
    engine_service = bq.engine.controllers.engine_service

    [bq.commands]
    module = bq.engine.commands.module_admin:module_admin
    engine = bq.engine.commands.engine_admin:engine_admin
    """,
)
