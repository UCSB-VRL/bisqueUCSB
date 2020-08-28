
Supervisord
===========

(linux/mac os only).

Bisque can be used as a system service using supervisord_ which will manage the starting
and stoping of the process when the system boots.   Our demonstration file will
only manage  bisque and the module engine and not web-server, database as those are usually
started by other means.

Installation
------------

Use your standard installation too if available

::
    apt-get install python-supervisord


On redhat system, please google it or follow instructions in supervisord_.

You will need to edit the paths contained in the ``contrib/supervisord/supervisord.conf`` and
``contrib/supervisord/bisque.conf`` and then copy them to the proper system location.

::
   cp  contrib/supervisord/supervisord.conf  /etc/supervisord/
   cp  contrib/supervisord/bisque.conf  /etc/supervisord/conf.d


Setup a front web service  (see contrib/nginx)


Running
-------

::
    supervisorsctl reload
    supervisorsctl status


Stoping and starting
---------------------

  The services will automatically be started.  You can start each on individual or as a group

::
    supervisorsctl stop uwsgi_engine
    supervisorsctl stop group:bisque



.. _supervisord: http://supervisord.org
