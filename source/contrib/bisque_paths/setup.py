
from setuptools import setup
setup(name='bisque_paths',
      version='1.0',
      install_requires = [
        'requests',
        'argparse',
        'six',
        ],

      py_modules = ['bisque_paths' ],

      entry_points = {
        'console_scripts' : [
            'bqpath = bisque_paths:main',
            'bq-path = bisque_paths:main',
            ]
        }

      )
