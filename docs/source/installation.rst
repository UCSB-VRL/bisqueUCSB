Installation Guide
==================
.. toctree::
   :maxdepth: 2

   release_notes
   advinstall

Installing bisque is simplified using the bisque bootstrap script [#]_.

Installing bisque is simplified using the bisque bootstrap_ script.


Required packages
-----------------

==========  =======================================  ===============   ============= ======== ==========
Package     Generic                                  Debian            Redhat        MacOS    Windows
----------  ---------------------------------------  ---------------   ------------- -------- ----------
Install     N/A                                      apt-get install   yum install   N/A      N/A     
==========  =======================================  ===============   ============= ======== ==========


::

 python2.6-dev   || http://www.python.org/download/         || python-dev      || python                || XCode  || [https://www.activestate.com/activepython/downloads/ ActivePython] ||
 setuptools      || http://pypi.python.org/pypi/setuptools/ ||                 ||                       ||        || [http://pypi.python.org/pypi/setuptools installer] ||
 virtualenv      || http://pypi.python.org/pypi/virtualenv  ||                 ||                       ||        || easy_install virtualenv ||
 libxml2-dev     || http://xmlsoft.org/downloads.html       || libxml2-dev     || libxml2-python.x86_64 || N/A    || [http://xmlsoft.org/sources/win32/python/ installer] || 
 libxslt-dev     || http://xmlsoft.org/XSLT/downloads.html  || libxslt1-dev    ||                       ||        ||  N/A    ||
 sqlite3         || http://www.sqlite.org/download.html     || libsqlite3-dev  ||  ?                    || N/A    || [http://www.sqlite.org/download.html installer]    ||



Prepare a Python Virtual Environment
------------------------------------

#. Create a bisque directory and download this `Bootstrap script <http://biodev.ece.ucsb.edu/binaries/download/bisque-bootstrap.py>`_
   ::
     mkdir bisque; cd bisque
     wget http://biodev.ece.ucsb.edu/binaries/download/bisque-bootstrap.py

#. Inside the bisque directory run the boostrap script which will create the python virtualenv ('''python2.6 or python2.7 REQUIRED'''), and download the initial files.
   ::
      bisque$ python bisque-bootstrap.py [--python=python2.6] bqenv

#. Activate the virtualenv before the next steps and before you executate any bisque commands or scripts

   * Linux or MacOS X:
     ::
        bisque$ source bqenv/bin/activate

   * Windows:
     ::
        bisque > bqenv\Scripts\activate.bat

   **You must activate the environment** if you logout or create a new shell before using command line tools with bisque.

#. Install imgcnv image manipulation (`imgcnv <http://biodev.ece.ucsb.edu/projects/bioimage/downloader/download/category/4>`_).  Look for  imgcnv_<SYSTEM>_1-XX.zip and click it. You will need to fill out a form to download. Note: the location of imgcnv should be added into the PATH environment variable. 
   ::
         (bqenv)$ unzip imgcnv_YYYYY-XX.zip
         (bqenv)$ cp imgcnv/imgcnv bqenv/bin
         (bqenv)$ chmod +x bqenv/bin/imgcnv

   If a pre-built package is not available you can compile ``imgcnv`` from source.   You will need download the the source code, have qmake and c/c++ compiler available.
   ::
      (bqenv)$ hg clone http://biodev.ece.ucsb.edu/hg/imgcnv
      (bqenv)$ cd imgcnv
      (bqenv)$ sh ./build-imgcnv-SYS.sh
      (bqenv)$ cp imgcnv ../bqenv/bin
      (bqenv)$ cd ..

   Debian-like system can use our debian repo to fetch the latest imgcnv. See CbiDebian for details.




Setup Bisque
------------

 You are about to configure the system.  Please take a look at the
 dependency table to insure you have the necessary system packages
 installed.  If you upgrading from a previous Bisque installation,
 please review the instructions at BisqueUpgrade before proceeding.

#. (optional) Install module dependencies.   This will allow the module to setup and tested in the next step.  You cam skip this step and install the dependencies at a later time,  by re-running ``bisque-setup --modules`` See `Add-on Module Dependencies`_.

#. Configure  the bisque system. You will be asked a series of question about your intended installation.  If unsure at any question, you can type '?' to receive help.  Otherwise please check the BisqueFaq
   ::
     (bqenv)$ # Activate YOUR Virtual Environment if you have not done so.. no command will work unless you do so.
     (bqenv)$ paver setup
     (bqenv)$ bq-admin setup

    If something fails during setup.. Don't panic.  You can run the different aspects of the setup again.  The list of setup modules is mercurial, binaries, site, database, modules, bioformats i.e  Simply run {{{bq-admin setup database }}}
#. Start the system 
   ::
     (bqenv)$ bq-admin server start

#.  Access the system with your browser (firefox, safari, chrome, etc).  The default intall only allow access from localhost (http://localhost:8080)

#.  **Congratulations!** You have installed bisque.  If you are using a sqlite database then the system  is suitable for small sites of several thousand images and only 1 or 2 users.  For larger systems please refer to :ref:`advinstall`.

#.  Please take a look at [Installation/ConfigureBisque Configuring a Bisque Site].

    * Shutdown the servers with:
      ::
         (bqenv)$ bq-admin server stop

Add-on Module Dependencies
--------------------------

Some of the add analysis modules also have there own requirements 
**Please ensure your virtualenv is active** before installing these:

  You will need to rerun bisque-setup.py.   You can answer N to all questions except the ``setup modules``.
  ::
    (bqenv)$ bq-admin setup modules




.. [#] http://biodev.ece.ucsb.edu/binaries/download/bisque_bootstrap.py
.. _bootstrap: http://biodev.ece.ucsb.edu/binaries/download/bisque_bootstrap.py




