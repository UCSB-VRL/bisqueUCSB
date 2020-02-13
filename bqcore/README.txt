Bisque application. 

Installation and Setup
======================

Install ``bisque`` using the setup.py script::

    $ cd bqcore
    $ python setup.py install

Create the project database for any model classes defined::

    $ paster setup-app development.ini

Start and stop the paste http server::

bq-admin servers start

...

bq-admin servers stop







Testing 
========================

Nose tests are available 
    $ nosetests   
Some useful options:
     -s   : Dont capture stdout (any stdout output will be printed immediately) 

or to see coverage stats

    $ cd bqcore
    $ nosetests --with-coverage --cover-package=bq
