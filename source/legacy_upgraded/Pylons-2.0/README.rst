Pylons
======

The Pylons web framework is designed for building web applications and
sites in an easy and concise manner. They can range from as small as a
single Python module, to a substantial directory layout for larger and
more complex web applications.

Pylons comes with project templates that help boot-strap a new web
application project, or you can start from scratch and set things up
exactly as desired.


Example `Hello World`
---------------------

..

    from paste.httpserver import serve
    from pylons import Configurator, Response

    class Hello(object):
        def __init__(self, request):
            self.request = request

        def index(self):
            return Response(body="Hello World!")


    if __name__ == '__main__':
        config = Configurator()
        config.begin()
        config.add_handler('home', '/', handler=Hello, action='index')
        config.end()
        serve(config.make_wsgi_app(), host='0.0.0.0')


Core Features
-------------

* A framework to make writing web applications in Python easy

* Utilizes a minimalist, component-based philosophy that makes it easy to
  expand on

* Harness existing knowledge about Python

* Extensible application design

* Fast and efficient, an incredibly small per-request call-stack providing
  top performance

* Uses existing and well tested Python packages


Current Status
--------------

Pylons 1.0 series is stable and production ready, but in maintenance-only
mode. The Pylons Project now maintains the Pyramid web framework for future
development. Pylons 1.0 users should strongly consider using Pyramid for
their next project.


Download and Installation
-------------------------

Pylons can be installed with `Easy Install
<http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

    > easy_install Pylons


Development Version
-------------------

Pylons development uses the git distributed version control system (DVCS)
with GitHub hosting the main repository here:

    `Pylons GitHub repository <https://github.com/Pylons/pylons>`_


Documentation
-------------

http://docs.pylonsproject.org/projects/pylons-webframework/en/latest/


Pylons
++++++

.. image:: https://secure.travis-ci.org/Pylons/pylons.png?branch=master
   :alt: Build Status
   :target: https://secure.travis-ci.org/Pylons/pylons

Pylons is a rapid web application development framework.

.. note::

    Pylons has merged with repoze.bfg, and is now in maintenance-only
    mode. It's highly recommended that new projects start with the new
    merged web framework, `pyramid <http://www.pylonsproject.org/>`_.

Install
=======

`Read the online Installation instructions
<http://docs.pylonsproject.org/projects/pylons-webframework/en/latest/gettingstarted.html#installing>`_.

If you want to install from source you can run the following command:

.. code-block :: bash

    $ python setup.py install

This will display a message and download setuptools if the module is not
already installed. It will then install Pylons and all its dependencies. You
may need root privileges to install setuptools.

Testing
=======

To test the source distribution run the following command:

.. code-block :: bash

    $ python setup.py test

This will install additional dependencies needed for the tests. As above, you
may need root privileges.

Documentation
=============

`Read the complete Pylons web framework documentation
<http://docs.pylonsproject.org/projects/pylons-webframework/>`_.

`Definitive Guide to Pylons <https://thejimmyg.github.io/pylonsbook/>`_ is a book about Pylons published by Apress, written by James Gardner, with free HTML rendering.

Generating documentation requires Sphinx:

.. code-block :: bash

    $ easy_install Sphinx

Then to build the documentation use the commands:

.. code-block :: bash

    $ cd pylons/docs/<lang>
    $ make html
