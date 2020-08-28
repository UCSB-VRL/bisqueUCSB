"""Apache mod_wsgi script for BisqueCore

Point to this script in your apache config file.
A template config file was generated as the file `BisqueCore` sitting
next to this file

Make sure the apache user (normally www-data) owns your application's
deployment path (/usr/local/turbogears/BisqueCore).  On Linux machines you can
accomplish this with:

.. code-block:: bash

    sudo chown -R www-data:www-data /usr/local/turbogears/BisqueCore

The BASELINE pattern creates a root VirtualEnv on which your
application-specific VirtualEnv's will be based, and which will
can shared among potentially multiple projects.  If you haven't
yet created the BASELINE VirtualEnv you can created it with:

.. code-block:: bash

    sudo mkdir /usr/local/pythonenv
    sudo virtualenv --no-site-packages /usr/local/pythonenv/BASELINE

Make sure that the apache user owns the /usr/local/pythonenv/BASELINE virtualenv.
On Linux machines you can ensure this with:

.. code-block:: bash

    sudo chown -R www-data:www-data /usr/local/pythonenv/BASELINE

For details on BASELINE and the general mod_wsgi/VirtualEnv pattern
used here, see:

    http://code.google.com/p/modwsgi/wiki/VirtualEnvironments
"""
import sys

# This block provides support for the default virtualenv
# deployment pattern.  The option `--virtualenv=` on the
# `paster modwsgi_deploy` command line will skip this section entirely.
prev_sys_path = list(sys.path)

import site
site.addsitedir('/usr/local/pythonenv/{{package}}/lib/python2.6/site-packages')

#Move just added item to the front of the python system path.
#Not needed if modwsgi>=3.0. Uncomment next 6 lines.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path
#End of virtualenv support

# This adds your project's root path to the PYTHONPATH so that you can import
# top-level modules from your project path.  This is how TurboGears QuickStarted
# projects are laid out by default.
import os, sys
sys.path.append('/usr/local/bisque/{{package}}')

# Set the environment variable PYTHON_EGG_CACHE to an appropriate directory
# where the Apache user has write permission and into which it can unpack egg files.
os.environ['PYTHON_EGG_CACHE'] = '/usr/local/bisque/{{package}}/python-eggs'

# Initialize logging module from your TurboGears config file
from paste.script.util.logging_config import fileConfig
fileConfig('/usr/local/bisque/{{package}}/production.ini')

# Finally, load your application's production.ini file.
from paste.deploy import loadapp
application = loadapp('config:/usr/local/bisque/{{package}}/production.ini')
