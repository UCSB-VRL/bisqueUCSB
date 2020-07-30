from setuptools import setup

setup(name='bqwatcher',
      version='0.1',
      description='Watch directories for bisque event ',
      url='http://bitbucker.org/viqi/bqwatcher',
      author='ViQi ',
      author_email='',
      license='GNU',
      packages=['bq', 'bq.watcher',],
      zip_safe=False,
      install_requires = [ "watchdog", "bisque_paths" ],
      entry_points = {
          'console_scripts': ['bq-watcher=bq.watcher:main'],
          }
)
