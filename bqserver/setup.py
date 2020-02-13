from setuptools import setup, find_packages
import sys, os

#from bq.release import __VERSION__
__VERSION__ = '0.5.9'

# -*- Extra requirements: -*-
install_requires = [
#        "bqcore",
        "ply",
        "gdata",
        "Turbomail",
        "genshi",
#        "TGScheduler",
        "boto",
        "numpy",
        "ordereddict",
        # Installed from http://biodev.ece.ucsb.edu/binaries/depot
        "tw.recaptcha",
        "tgext.registration2",
        "tw.output", #https://bitbucket.org/alexbodn/twoutput/get/af6904c504cf.zip
        "furl",
      ]

if sys.version_info  < ( 2, 7 ):
    install_requires.append('unittest2')


setup(name='bqserver',
      version=__VERSION__,
      description="Main Bisque server",
      long_description="""\
The bisque server
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='bioinformatics, image, database',
      author='Center for Bioinformatics',
      author_email='cbi@biodev.ece.ucsb.edu',
      url='http://bioimage.ucsb.edu',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages = ['bq'],
      message_extractors={'bq': [
          ('**.py', 'python', None),
          ('client_service/templates/**.mako', 'mako', None),
          ('client_service/templates/**.html', 'genshi', None),
          ('client_service/public/**', 'ignore', None)]},
      #setup_requires=["hgtools"],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      # -*- Entry points: -*-
    [bisque.services]
    client_service   = bq.client_service.controllers.service
    auth_service     = bq.client_service.controllers.auth_service
    admin            = bq.admin_service.controllers.service
    notebook_service = bq.client_service.controllers.dn_service
    data_service     = bq.data_service.controllers.data_service
    blob_service     = bq.blob_service.controllers.blobsrv
    image_service    = bq.image_service.controllers.service
    stats            = bq.stats.controllers.stats_server
    module_service   = bq.module_service.controllers.module_server
    export           = bq.export_service.controllers.export_service
    import           = bq.import_service.controllers.import_service
    registration     = bq.registration.controllers.registration_service
    ingest_service   = bq.ingest.controllers.ingest_server
    dataset_service  = bq.dataset_service.controllers.dataset_service
    usage            = bq.usage.controllers.usage
    graph            = bq.graph.controllers.graph
    preference       = bq.preference.controllers.service
    table            = bq.table.controllers.service
    pipeline         = bq.pipeline.controllers.service
    notify           = bq.client_service.controllers.notify_service
    [bq.commands]
    module = bq.module_service.commands.module_admin:module_admin
      """,
      )
