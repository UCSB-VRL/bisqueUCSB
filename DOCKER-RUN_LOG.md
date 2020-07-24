```sh
amil@amil:~/bisqueUCSB$ docker run -itp 8080:8080 bisque-developer-beta:0.7-broccolli
+ CMD=bootstrap
+ shift
+ INDEX=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
+ CONFIG=./config/site.cfg
+ export PIP_INDEX_URL=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
+ PIP_INDEX_URL=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
++ pwd
+ reports=/source/reports/
+ BUILD=/builder/
+ BQHOME=/source/
+ VENV=/usr/lib/bisque
+ '[' '!' -d /source/reports/ ']'
++ pwd
+ echo 'In ' /source 'BISQUE in' /source/ 'Reports in' /source/reports/
In  /source BISQUE in /source/ Reports in /source/reports/
+ cd /source/
+ '[' bootstrap = build ']'
+ source /usr/lib/bisque/bin/activate
++ deactivate nondestructive
++ unset -f pydoc
++ '[' -z '' ']'
++ '[' -z '' ']'
++ '[' -n /bin/bash ']'
++ hash -r
++ '[' -z '' ']'
++ unset VIRTUAL_ENV
++ '[' '!' nondestructive = nondestructive ']'
++ VIRTUAL_ENV=/usr/lib/bisque
++ export VIRTUAL_ENV
++ _OLD_VIRTUAL_PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
++ PATH=/usr/lib/bisque/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
++ export PATH
++ '[' -z '' ']'
++ '[' -z '' ']'
++ _OLD_VIRTUAL_PS1=
++ '[' x '!=' x ']'
+++ basename /usr/lib/bisque
++ PS1='(bisque) '
++ export PS1
++ alias pydoc
++ '[' -n /bin/bash ']'
++ hash -r
+ '[' bootstrap = bootstrap ']'
+ echo BOOTSTRAPPING
BOOTSTRAPPING
+ umask 0002
+ ls -l
total 180
drwxr-xr-x  2 root root  4096 Jul 24 12:13 boot
drwxr-xr-x  1 root root  4096 Jul 24 12:33 bqapi
drwxr-xr-x  1 root root  4096 Jul 24 12:33 bqcore
drwxr-xr-x  1 root root  4096 Jul 24 12:33 bqengine
drwxr-xr-x  1 root root  4096 Jul 24 12:34 bqfeature
drwxr-xr-x  1 root root  4096 Jul 24 12:34 bqserver
drwxr-xr-x  2 root root  4096 Jul 24 12:13 builder
drwxr-xr-x  2 root root  4096 Jul 24 12:34 config
drwxr-xr-x  3 root root  4096 Jul 24 12:13 config-defaults
drwxr-xr-x 29 root root  4096 Jul 24 12:13 contrib
-rw-r--r--  1 root root  3124 Jul 24 12:13 COPYRIGHT
drwxr-xr-x  3 root root  4096 Jul 24 12:34 data
-rw-r--r--  1 root root  4192 Jul 24 12:32 Dockerfile.caffe.xenial
-rw-r--r--  1 root root   135 Jul 24 12:13 entry.sh
-rw-r--r--  1 root root  1957 Jul 24 12:13 LICENSE
-rw-r--r--  1 root root   153 Jul 24 12:13 Makefile
drwxr-xr-x  3 root root  4096 Jul 24 12:13 migrations
drwxr-xr-x  1 root root  4096 Jul 24 12:34 modules
-rw-r--r--  1 root root  9917 Jul 24 12:13 pavement.py
-rw-r--r--  1 root root 43589 Jul 24 12:13 paver-minilib.zip
drwxr-xr-x  2 root root  4096 Jul 24 12:34 plugins
drwxr-xr-x 15 root root  4096 Jul 24 12:34 public
drwxr-xr-x  2 root root  4096 Jul 24 12:13 pytest-bisque
-rw-r--r--  1 root root   187 Jul 24 12:13 pytest.ini
-rw-r--r--  1 root root  1732 Jul 24 12:13 README.md
drwxr-xr-x  2 root root  4096 Jul 24 12:32 reports
-rw-r--r--  1 root root  2658 Jul 24 12:13 requirements.txt
-rw-r--r--  1 root root  3764 Jul 24 12:13 run-bisque.sh
-rw-r--r--  1 root root   225 Jul 24 12:13 setup.py
-rw-r--r--  1 root root   421 Jul 24 12:13 sources.list
-rw-r--r--  1 root root    78 Jul 24 12:13 start-bisque.sh
-rw-r--r--  1 root root   257 Jul 24 12:13 virtualenv.sh
+ '[' -d /builder/boot-scripts.d ']'
+ ls -l /builder/boot-scripts.d
total 4
-rwxr-xr-x 1 root root 47 Jul 24 12:13 B10-fullconfig.sh
+ for f in '${BUILD}boot-scripts.d/B*.sh'
+ echo 'Executing **BOOT /builder/boot-scripts.d/B10-fullconfig.sh **'
Executing **BOOT /builder/boot-scripts.d/B10-fullconfig.sh **
+ '[' -f /builder/boot-scripts.d/B10-fullconfig.sh ']'
+ bash /builder/boot-scripts.d/B10-fullconfig.sh
+ bq-admin setup -y fullconfig
INFO:root:Generating grammar tables from /usr/lib/python2.7/lib2to3/Grammar.txt
INFO:root:Generating grammar tables from /usr/lib/python2.7/lib2to3/PatternGrammar.txt
Developer installation
DIRS:  {'bin': '/usr/lib/bisque/bin', 'run': '.', 'share': '.', 'plugins': './plugins', 'packages': '/usr/lib/bisque/lib/python2.7/site-packages', 'data': './data', 'virtualenv': '/usr/lib/bisque', 'default': './config-defaults', 'jslocation': 'bqcore', 'modules': './modules', 'depot': './external', 'config': './config', 'public': './public'}
This is the main installer for Bisque

    The system will initialize and be ready for use after a succesfull
    setup has completed.

    Several questions must be answered to complete the install.  Each
    question is presented with default in brackets [].  Pressing
    <enter> means that you are accepting the default value. You may
    request more information by responding with single '?' and then <enter>.

    For example:
    What is postal abbreviation of Alaska [AK]?

    The default answer is AK and is chosen by simply entering <enter>

    
Beginning install of ['bisque', 'engine'] with ['fullconfig'] 
CALLING  <function install_server_defaults at 0x7f47194dd320>
Server config
Top level site variables are:
  bisque.admin_email=YourEmail@YourOrganization
  bisque.admin_id=admin
  bisque.organization=Your Organization
  bisque.paths.root=.
  bisque.server=http://0.0.0.0:8080
  bisque.title=Image Repository
{'backend': 'paster',
 'e1.bisque.has_database': 'false',
 'e1.bisque.static_files': 'false',
 'e1.services_enabled': 'engine_service',
 'e1.url': 'http://0.0.0.0:27000',
 'h1.services_disabled': '',
 'h1.url': 'http://0.0.0.0:8080',
 'servers': 'h1'}
PARAMS {'e1.bisque.has_database': 'false', 'h1.url': 'http://0.0.0.0:8080', 'servers': 'h1', 'h1.services_disabled': '', 'e1.url': 'http://0.0.0.0:27000', 'e1.bisque.static_files': 'false', 'e1.services_enabled': 'engine_service', 'backend': 'paster'}
Created paster config:  ./config/h1_paster.cfg
CALLING  <function install_mail at 0x7f47194dd668>
Please review/edit the mail.* settings in site.cfg for you site
CALLING  <function install_secrets at 0x7f47194dd7d0>
CALLING  <function install_database at 0x7f47194dc488>
Trying to import driver sqlite3...
Driver successfully imported.
Checking whether database "data/bisque.db" already exists...
Yes, it exists.
12:42:51,794 INFO  [bq.config] DATABASE sqlite:///data/bisque.db
12:42:51,794 INFO  [bq.config] SQLLite special handling NullPool timoout
12:42:51,800 INFO  [bq.websetup] Creating all tables
12:42:51,834 INFO  [bq.websetup] found service engine_service = bq.engine.controllers.engine_service
12:42:52,042 INFO  [bq.websetup] Creating tables for engine_service = bq.engine.controllers.engine_service
12:42:52,042 INFO  [bq.websetup] found service core = bq.core.controllers.root
12:42:52,061 INFO  [bq.websetup] Creating tables for core = bq.core.controllers.root
12:42:52,061 INFO  [bq.websetup] found service data_service = bq.data_service.controllers.data_service
12:42:52,093 INFO  [bq.websetup] Creating tables for data_service = bq.data_service.controllers.data_service
12:42:52,096 INFO  [bq.websetup] found service blob_service = bq.blob_service.controllers.blobsrv
12:42:52,235 INFO  [bq.websetup] Creating tables for blob_service = bq.blob_service.controllers.blobsrv
12:42:52,235 INFO  [bq.websetup] found service pipeline = bq.pipeline.controllers.service
12:42:52,239 INFO  [bq.websetup] Creating tables for pipeline = bq.pipeline.controllers.service
12:42:52,239 INFO  [bq.websetup] found service ingest_service = bq.ingest.controllers.ingest_server
12:42:53,516 INFO  [bq.image_service.server] Available converters: openslide (1.1.1), imgcnv (2.4.3), ImarisConvert (8.0.2), bioformats (5.1.1)
12:42:53,518 INFO  [bq.websetup] Creating tables for ingest_service = bq.ingest.controllers.ingest_server
12:42:53,521 INFO  [bq.websetup] found service stats = bq.stats.controllers.stats_server
12:42:53,527 INFO  [bq.websetup] Creating tables for stats = bq.stats.controllers.stats_server
12:42:53,527 INFO  [bq.websetup] found service admin = bq.admin_service.controllers.service
12:42:53,531 INFO  [bq.websetup] Creating tables for admin = bq.admin_service.controllers.service
12:42:53,531 INFO  [bq.websetup] found service graph = bq.graph.controllers.graph
12:42:53,535 INFO  [bq.websetup] Creating tables for graph = bq.graph.controllers.graph
12:42:53,538 INFO  [bq.websetup] found service module_service = bq.module_service.controllers.module_server
12:42:53,544 INFO  [bq.websetup] Creating tables for module_service = bq.module_service.controllers.module_server
12:42:53,547 INFO  [bq.websetup] found service auth_service = bq.client_service.controllers.auth_service
12:42:53,551 INFO  [bq.websetup] Creating tables for auth_service = bq.client_service.controllers.auth_service
12:42:53,552 INFO  [bq.websetup] found service client_service = bq.client_service.controllers.service
12:42:53,555 INFO  [bq.websetup] Creating tables for client_service = bq.client_service.controllers.service
12:42:53,558 INFO  [bq.websetup] found service image_service = bq.image_service.controllers.service
12:42:53,560 INFO  [bq.websetup] Creating tables for image_service = bq.image_service.controllers.service
12:42:53,560 INFO  [bq.websetup] found service dataset_service = bq.dataset_service.controllers.dataset_service
12:42:53,564 INFO  [bq.websetup] Creating tables for dataset_service = bq.dataset_service.controllers.dataset_service
12:42:53,565 INFO  [bq.websetup] found service export = bq.export_service.controllers.export_service
12:42:53,594 INFO  [bq.websetup] Creating tables for export = bq.export_service.controllers.export_service
12:42:53,594 INFO  [bq.websetup] found service preference = bq.preference.controllers.service
12:42:53,598 INFO  [bq.websetup] Creating tables for preference = bq.preference.controllers.service
12:42:53,599 INFO  [bq.websetup] found service registration = bq.registration.controllers.registration_service
12:42:53,666 INFO  [bq.websetup] Creating tables for registration = bq.registration.controllers.registration_service
12:42:53,676 INFO  [bq.websetup] found service usage = bq.usage.controllers.usage
12:42:53,682 INFO  [bq.websetup] Creating tables for usage = bq.usage.controllers.usage
12:42:53,682 INFO  [bq.websetup] found service import = bq.import_service.controllers.import_service
12:42:53,689 INFO  [bq.websetup] Creating tables for import = bq.import_service.controllers.import_service
12:42:53,689 INFO  [bq.websetup] found service notebook_service = bq.client_service.controllers.dn_service
12:42:53,694 INFO  [bq.websetup] Creating tables for notebook_service = bq.client_service.controllers.dn_service
12:42:53,694 INFO  [bq.websetup] found service table = bq.table.controllers.service
12:42:53,851 INFO  [bq.websetup] Creating tables for table = bq.table.controllers.service
12:42:53,851 INFO  [bq.websetup] found service notify = bq.client_service.controllers.notify_service
12:42:53,853 INFO  [bq.websetup] Creating tables for notify = bq.client_service.controllers.notify_service
12:42:53,853 INFO  [bq.websetup] found service features = bq.features.controllers.service
12:42:53,926 WARNI [bq.features] Failed to import: MyFeatures reason No module named scipy.signal 
12:42:53,938 WARNI [bq.features] Failed to import: ScikitImage reason No module named skimage.feature 
12:42:53,944 INFO  [bq.websetup] Creating tables for features = bq.features.controllers.service
INFO  [alembic.migration] Context impl SQLiteImpl.
INFO  [alembic.migration] Will assume non-transactional DDL.
/usr/lib/bisque/local/lib/python2.7/site-packages/sqlalchemy/sql/sqltypes.py:226: SAWarning: Unicode type received non-unicode bind param value 'mex'. (this warning may be suppressed after 10 occurrences)
  (util.ellipses_string(value),))
/usr/lib/bisque/local/lib/python2.7/site-packages/sqlalchemy/sql/sqltypes.py:226: SAWarning: Unicode type received non-unicode bind param value 'initialization'. (this warning may be suppressed after 10 occurrences)
  (util.ellipses_string(value),))
/usr/lib/bisque/local/lib/python2.7/site-packages/sqlalchemy/sql/sqltypes.py:226: SAWarning: Unicode type received non-unicode bind param value 'user'. (this warning may be suppressed after 10 occurrences)
  (util.ellipses_string(value),))
/usr/lib/bisque/local/lib/python2.7/site-packages/sqlalchemy/sql/sqltypes.py:226: SAWarning: Unicode type received non-unicode bind param value '(root)'. (this warning may be suppressed after 10 occurrences)
  (util.ellipses_string(value),))
/usr/lib/bisque/local/lib/python2.7/site-packages/sqlalchemy/sql/sqltypes.py:226: SAWarning: Unicode type received non-unicode bind param value 'tag'. (this warning may be suppressed after 10 occurrences)
  (util.ellipses_string(value),))
/usr/lib/bisque/local/lib/python2.7/site-packages/sqlalchemy/sql/sqltypes.py:226: SAWarning: Unicode type received non-unicode bind param value 'display_name'. (this warning may be suppressed after 10 occurrences)
  (util.ellipses_string(value),))
/usr/lib/bisque/local/lib/python2.7/site-packages/sqlalchemy/sql/sqltypes.py:226: SAWarning: Unicode type received non-unicode bind param value 'admin'. (this warning may be suppressed after 10 occurrences)
  (util.ellipses_string(value),))
Running setup_config() from bq.websetup
CALLING  <function install_preferences at 0x7f47194dd6e0>
CALLING  <function install_engine_defaults at 0x7f47194dd410>
Engine config
Top level site variables are:
  bisque.engine=http://0.0.0.0:27000
  bisque.paths.root=.
{'e1.url': 'http://0.0.0.0:27000'}
Warning: Please review the [server] section of site.cfg after modifying site variables
CALLING  <function install_docker at 0x7f47194dc848>
CALLING  <function install_matlab at 0x7f47194dc758>
CONFIG ./config/runtime-bisque.cfg
WARNING: Matlab is required for many modules
CALLING  <function install_runtime at 0x7f47194dd5f0>
No condor was found. See bisque website for details on using condor
+ CMD=start
+ shift
+ '[' start = pylint ']'
+ '[' start = unit-tests ']'
+ '[' start = function-tests ']'
+ '[' start = start ']'
+ '[' '!' -f config/site.cfg ']'
+ '[' -d /builder/start-scripts.d ']'
+ ls -l /builder/start-scripts.d
total 4
-rwxr-xr-x 1 root root 78 Jul 24 12:13 R50-start-bisque.sh
+ for f in '${BUILD}start-scripts.d/R*.sh'
+ echo 'Executing ** START /builder/start-scripts.d/R50-start-bisque.sh **'
Executing ** START /builder/start-scripts.d/R50-start-bisque.sh **
+ '[' -f /builder/start-scripts.d/R50-start-bisque.sh ']'
+ bash /builder/start-scripts.d/R50-start-bisque.sh
starting h1

```
