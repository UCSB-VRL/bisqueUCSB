from setuptools import setup, find_packages

#from bq.release import __VERSION__
__VERSION__="0.5.9"

setup(name='bisque_api',
      version=__VERSION__,
      description="Bisque Module API",
      author='Center for Bioimage informatics',
      author_email='cbi@biodev.ece.ucsb.edu',
      #home_page = 'http://biodev.ece.ucsb.edu/projects/bisque',
      url='http://biodev.ece.ucsb.edu/projects/bisque',
      packages= find_packages(), # ['bqapi', 'bqapi. ],
#      namespace_packages = ['bq'],
      install_requires=[
          "six",
          "requests >=2.4.1",
          "requests_toolbelt >= 0.6.2",
        ],
      extras_require = {
          'lxml' : [ 'lxml'],
          'CAS'  : ['BeautifulSoup4' ],
          'feature' : ['tables'],
          'table' : ['tables'],
          'image_service' : ['tifffile', 'tables'],

      },

      zip_safe= True,
      classifiers = (
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
  )
