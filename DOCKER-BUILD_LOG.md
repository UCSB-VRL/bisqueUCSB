# Docker Build Log

```sh
amil@amil:~/bisqueUCSB$ docker build -t bisque-developer-beta:0.7-broccolli -f Dockerfile.caffe.xenial .
Sending build context to Docker daemon  518.3MB
Step 1/22 : FROM biodev.ece.ucsb.edu:5000/caffe-runtime:xenial
 ---> 031ed4afa9b5
Step 2/22 : ENV DEBIAN_FRONTEND noninteractive
 ---> Using cache
 ---> 103884e6a3ca
Step 3/22 : ENV IMGCNV=imgcnv_ubuntu16_2.4.3
 ---> Using cache
 ---> 667c1b72ebaf
Step 4/22 : RUN apt-get update -qq && apt-get install -qq -y apt-transport-https wget
 ---> Using cache
 ---> 777a5ad0cb7f
Step 5/22 : RUN wget -q -O - https://biodev.ece.ucsb.edu/debian/cbi_repository_key.asc | apt-key add -
 ---> Using cache
 ---> 80ca52f265f1
Step 6/22 : RUN  echo "deb http://ftp.ucsb.edu/pub/mirrors/linux/ubuntu-archive xenial main restricted universe" >> /etc/apt/sources.list.d/bisque.list
 ---> Using cache
 ---> 89ec49fd98e2
Step 7/22 : RUN wget -q https://bitbucket.org/dimin/bioimageconvert/downloads/$IMGCNV.tar.gz     && tar xf $IMGCNV.tar.gz     && mv $IMGCNV/imgcnv /usr/bin     && mv $IMGCNV/libimgcnv.so* /usr/lib/x86_64-linux-gnu/     && rm -rf  $IMGCNV     && apt-get install -y --no-install-recommends     libswscale-ffmpeg3 libfftw3-3 libgdcm2.6 libavcodec-ffmpeg56 libavformat-ffmpeg56 libavutil-ffmpeg54 libhdf5-cpp-11
 ---> Using cache
 ---> 161a7dde6c21
Step 8/22 : RUN apt-get update  -qq     && apt-get install -y --no-install-recommends --allow-unauthenticated     git     locales     less     libasound2     libasound2-data     libblas3     libblas-common     libbz2-1.0     libgdbm3     libgdk-pixbuf2.0-0     libgdk-pixbuf2.0-common     libgfortran3     libglib2.0-0     libglib2.0-data     libblosc1     libgomp1     libgv-python     libice6     libjasper1    libjbig0     libjpeg62     liblapack3     liblzo2-2     libmagic1     libogg0     libopenjpeg5     libopenslide0     libopenslide-dev     liborc-0.4-0     libpixman-1-0     libpng12-0     libpq5     libpython2.7-minimal     libquadmath0     libschroedinger-1.0-0     libsm6     libsqlite3-0     libstdc++5     libtheora0     libtiff5-dev     libx11-6     libx11-data     libxau6     libxcb1     libxcb-render0     libxcb-shm0     libxdmcp6     libxext6     libxml2     libxrender1     libxslt1.1     libxvidcore4     mercurial     openjdk-8-jdk     python-minimal     build-essential     vim      sudo   && apt-get clean   && find  /var/lib/apt/lists/ -type f -delete
 ---> Using cache
 ---> a581f4de02f2
Step 9/22 : RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
 ---> Using cache
 ---> 72a539530607
Step 10/22 : ENV LANG en_US.UTF-8
 ---> Using cache
 ---> 6cc83c599734
Step 11/22 : RUN locale
 ---> Using cache
 ---> 52c37532b7cc
Step 12/22 : WORKDIR /source
 ---> Using cache
 ---> 748f78fad95a
Step 13/22 : ADD . /source
 ---> d2e9fc33cc04
Step 14/22 : COPY run-bisque.sh virtualenv.sh /builder/
 ---> b1c384a9253a
Step 15/22 : COPY start-bisque.sh /builder/start-scripts.d/R50-start-bisque.sh
 ---> f90d864828af
Step 16/22 : COPY builder/ /builder/build-scripts.d/
 ---> 18685721b7c1
Step 17/22 : COPY boot/ /builder/boot-scripts.d/
 ---> b45cbf9a0724
Step 18/22 : RUN bash virtualenv.sh
 ---> Running in 2f4ee94e1c3a
--2020-07-24 12:24:09--  https://pypi.python.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving pypi.python.org (pypi.python.org)... 151.101.24.223, 2a04:4e42:6::223
Connecting to pypi.python.org (pypi.python.org)|151.101.24.223|:443... connected.
HTTP request sent, awaiting response... 301 Redirect to Primary Domain
Location: https://pypi.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz [following]
--2020-07-24 12:24:09--  https://pypi.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving pypi.org (pypi.org)... 151.101.192.223, 151.101.64.223, 151.101.0.223, ...
Connecting to pypi.org (pypi.org)|151.101.192.223|:443... connected.
HTTP request sent, awaiting response... 301 Moved Permanently
Location: https://files.pythonhosted.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz [following]
--2020-07-24 12:24:09--  https://files.pythonhosted.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving files.pythonhosted.org (files.pythonhosted.org)... 151.101.25.63, 2a04:4e42:6::319
Connecting to files.pythonhosted.org (files.pythonhosted.org)|151.101.25.63|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1863951 (1.8M) [binary/octet-stream]
Saving to: ‘virtualenv-15.1.0.tar.gz’

     0K .......... .......... .......... .......... ..........  2% 3.25M 1s
    50K .......... .......... .......... .......... ..........  5% 8.96M 0s
   100K .......... .......... .......... .......... ..........  8% 18.1M 0s
   150K .......... .......... .......... .......... .......... 10% 10.0M 0s
   200K .......... .......... .......... .......... .......... 13% 15.6M 0s
   250K .......... .......... .......... .......... .......... 16% 14.3M 0s
   300K .......... .......... .......... .......... .......... 19% 12.2M 0s
   350K .......... .......... .......... .......... .......... 21% 19.0M 0s
   400K .......... .......... .......... .......... .......... 24% 15.7M 0s
   450K .......... .......... .......... .......... .......... 27% 19.0M 0s
   500K .......... .......... .......... .......... .......... 30% 14.4M 0s
   550K .......... .......... .......... .......... .......... 32% 19.3M 0s
   600K .......... .......... .......... .......... .......... 35% 15.6M 0s
   650K .......... .......... .......... .......... .......... 38% 17.8M 0s
   700K .......... .......... .......... .......... .......... 41% 15.1M 0s
   750K .......... .......... .......... .......... .......... 43% 25.7M 0s
   800K .......... .......... .......... .......... .......... 46% 16.2M 0s
   850K .......... .......... .......... .......... .......... 49% 16.5M 0s
   900K .......... .......... .......... .......... .......... 52% 17.2M 0s
   950K .......... .......... .......... .......... .......... 54% 38.6M 0s
  1000K .......... .......... .......... .......... .......... 57% 23.4M 0s
  1050K .......... .......... .......... .......... .......... 60% 13.6M 0s
  1100K .......... .......... .......... .......... .......... 63% 25.9M 0s
  1150K .......... .......... .......... .......... .......... 65% 17.0M 0s
  1200K .......... .......... .......... .......... .......... 68% 21.0M 0s
  1250K .......... .......... .......... .......... .......... 71% 56.2M 0s
  1300K .......... .......... .......... .......... .......... 74% 13.3M 0s
  1350K .......... .......... .......... .......... .......... 76% 25.4M 0s
  1400K .......... .......... .......... .......... .......... 79% 16.1M 0s
  1450K .......... .......... .......... .......... .......... 82% 51.8M 0s
  1500K .......... .......... .......... .......... .......... 85% 26.0M 0s
  1550K .......... .......... .......... .......... .......... 87% 14.5M 0s
  1600K .......... .......... .......... .......... .......... 90% 24.5M 0s
  1650K .......... .......... .......... .......... .......... 93% 14.6M 0s
  1700K .......... .......... .......... .......... .......... 96% 33.4M 0s
  1750K .......... .......... .......... .......... .......... 98% 28.8M 0s
  1800K .......... ..........                                 100% 56.0M=0.1s

2020-07-24 12:24:09 (16.0 MB/s) - ‘virtualenv-15.1.0.tar.gz’ saved [1863951/1863951]

virtualenv-15.1.0/
virtualenv-15.1.0/AUTHORS.txt
virtualenv-15.1.0/bin/
virtualenv-15.1.0/bin/rebuild-script.py
virtualenv-15.1.0/docs/
virtualenv-15.1.0/docs/changes.rst
virtualenv-15.1.0/docs/conf.py
virtualenv-15.1.0/docs/development.rst
virtualenv-15.1.0/docs/index.rst
virtualenv-15.1.0/docs/installation.rst
virtualenv-15.1.0/docs/make.bat
virtualenv-15.1.0/docs/Makefile
virtualenv-15.1.0/docs/reference.rst
virtualenv-15.1.0/docs/userguide.rst
virtualenv-15.1.0/LICENSE.txt
virtualenv-15.1.0/MANIFEST.in
virtualenv-15.1.0/PKG-INFO
virtualenv-15.1.0/README.rst
virtualenv-15.1.0/scripts/
virtualenv-15.1.0/scripts/virtualenv
virtualenv-15.1.0/setup.cfg
virtualenv-15.1.0/setup.py
virtualenv-15.1.0/tests/
virtualenv-15.1.0/tests/__init__.py
virtualenv-15.1.0/tests/test_activate.sh
virtualenv-15.1.0/tests/test_activate_output.expected
virtualenv-15.1.0/tests/test_cmdline.py
virtualenv-15.1.0/tests/test_virtualenv.py
virtualenv-15.1.0/virtualenv.egg-info/
virtualenv-15.1.0/virtualenv.egg-info/dependency_links.txt
virtualenv-15.1.0/virtualenv.egg-info/entry_points.txt
virtualenv-15.1.0/virtualenv.egg-info/not-zip-safe
virtualenv-15.1.0/virtualenv.egg-info/PKG-INFO
virtualenv-15.1.0/virtualenv.egg-info/SOURCES.txt
virtualenv-15.1.0/virtualenv.egg-info/top_level.txt
virtualenv-15.1.0/virtualenv.py
virtualenv-15.1.0/virtualenv_embedded/
virtualenv-15.1.0/virtualenv_embedded/activate.bat
virtualenv-15.1.0/virtualenv_embedded/activate.csh
virtualenv-15.1.0/virtualenv_embedded/activate.fish
virtualenv-15.1.0/virtualenv_embedded/activate.ps1
virtualenv-15.1.0/virtualenv_embedded/activate.sh
virtualenv-15.1.0/virtualenv_embedded/activate_this.py
virtualenv-15.1.0/virtualenv_embedded/deactivate.bat
virtualenv-15.1.0/virtualenv_embedded/distutils-init.py
virtualenv-15.1.0/virtualenv_embedded/distutils.cfg
virtualenv-15.1.0/virtualenv_embedded/python-config
virtualenv-15.1.0/virtualenv_embedded/site.py
virtualenv-15.1.0/virtualenv_support/
virtualenv-15.1.0/virtualenv_support/__init__.py
virtualenv-15.1.0/virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/pip-9.0.1-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl
running install
running build
running build_py
creating build
creating build/lib.linux-x86_64-2.7
copying virtualenv.py -> build/lib.linux-x86_64-2.7
creating build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/__init__.py -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/pip-9.0.1-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
running build_scripts
creating build/scripts-2.7
copying and adjusting scripts/virtualenv -> build/scripts-2.7
changing mode of build/scripts-2.7/virtualenv from 644 to 755
running install_lib
copying build/lib.linux-x86_64-2.7/virtualenv.py -> /usr/local/lib/python2.7/dist-packages
creating /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/pip-9.0.1-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/__init__.py -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
byte-compiling /usr/local/lib/python2.7/dist-packages/virtualenv.py to virtualenv.pyc
byte-compiling /usr/local/lib/python2.7/dist-packages/virtualenv_support/__init__.py to __init__.pyc
running install_scripts
copying build/scripts-2.7/virtualenv -> /usr/local/bin
changing mode of /usr/local/bin/virtualenv to 755
running install_egg_info
Writing /usr/local/lib/python2.7/dist-packages/virtualenv-15.1.0.egg-info
Removing intermediate container 2f4ee94e1c3a
 ---> 2de2b61c2137
Step 19/22 : ENV PY_INDEX=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
 ---> Running in d96f03ba9fc3
Removing intermediate container d96f03ba9fc3
 ---> 7c7729dcb697
Step 20/22 : RUN bash run-bisque.sh build
 ---> Running in 40feceebfe96
+ CMD=build
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
+ mkdir -p /source/reports/
++ pwd
+ echo 'In ' /source 'BISQUE in' /source/ 'Reports in' /source/reports/
In  /source BISQUE in /source/ Reports in /source/reports/
+ cd /source/
+ '[' build = build ']'
+ let returncode=0
+ echo BUILDING
BUILDING
+ '[' '!' -d /usr/lib/bisque ']'
+ virtualenv /usr/lib/bisque
New python executable in /usr/lib/bisque/bin/python
Installing setuptools, pip, wheel...done.
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
+ ls -l /builder//build-scripts.d
total 4
-rw-r--r-- 1 root root 408 Jul 24 12:13 20-build-bisque.sh
+ for f in '${BUILD}/build-scripts.d/*.sh'
Executing /builder//build-scripts.d/20-build-bisque.sh
+ echo 'Executing /builder//build-scripts.d/20-build-bisque.sh'
+ '[' -f /builder//build-scripts.d/20-build-bisque.sh ']'
+ /builder//build-scripts.d/20-build-bisque.sh
run-bisque.sh: line 34: /builder//build-scripts.d/20-build-bisque.sh: Permission denied
+ echo 'FAILED /builder//build-scripts.d/20-build-bisque.sh'
+ let returncode=2
FAILED /builder//build-scripts.d/20-build-bisque.sh
+ '[' 2 -ne 0 ']'
BUILD Failed
+ echo 'BUILD Failed'
+ exit 2
The command '/bin/sh -c bash run-bisque.sh build' returned a non-zero code: 2
amil@amil:~/bisqueUCSB$ vim Dockerfile.caffe.xenial 
amil@amil:~/bisqueUCSB$ vim Dockerfile.caffe.xenial 
amil@amil:~/bisqueUCSB$ docker build -t bisque-developer-beta:0.7-broccolli -f Dockerfile.caffe.xenial .
Sending build context to Docker daemon  518.3MB
Step 1/22 : FROM biodev.ece.ucsb.edu:5000/caffe-runtime:xenial
 ---> 031ed4afa9b5
Step 2/22 : ENV DEBIAN_FRONTEND noninteractive
 ---> Using cache
 ---> 103884e6a3ca
Step 3/22 : ENV IMGCNV=imgcnv_ubuntu16_2.4.3
 ---> Using cache
 ---> 667c1b72ebaf
Step 4/22 : RUN apt-get update -qq && apt-get install -qq -y apt-transport-https wget
 ---> Using cache
 ---> 777a5ad0cb7f
Step 5/22 : RUN wget -q -O - https://biodev.ece.ucsb.edu/debian/cbi_repository_key.asc | apt-key add -
 ---> Using cache
 ---> 80ca52f265f1
Step 6/22 : RUN  echo "deb http://ftp.ucsb.edu/pub/mirrors/linux/ubuntu-archive xenial main restricted universe" >> /etc/apt/sources.list.d/bisque.list
 ---> Using cache
 ---> 89ec49fd98e2
Step 7/22 : RUN wget -q https://bitbucket.org/dimin/bioimageconvert/downloads/$IMGCNV.tar.gz     && tar xf $IMGCNV.tar.gz     && mv $IMGCNV/imgcnv /usr/bin     && mv $IMGCNV/libimgcnv.so* /usr/lib/x86_64-linux-gnu/     && rm -rf  $IMGCNV     && apt-get install -y --no-install-recommends     libswscale-ffmpeg3 libfftw3-3 libgdcm2.6 libavcodec-ffmpeg56 libavformat-ffmpeg56 libavutil-ffmpeg54 libhdf5-cpp-11
 ---> Using cache
 ---> 161a7dde6c21
Step 8/22 : RUN apt-get update  -qq     && apt-get install -y --no-install-recommends --allow-unauthenticated     git     locales     less     libasound2     libasound2-data     libblas3     libblas-common     libbz2-1.0     libgdbm3     libgdk-pixbuf2.0-0     libgdk-pixbuf2.0-common     libgfortran3     libglib2.0-0     libglib2.0-data     libblosc1     libgomp1     libgv-python     libice6     libjasper1    libjbig0     libjpeg62     liblapack3     liblzo2-2     libmagic1     libogg0     libopenjpeg5     libopenslide0     libopenslide-dev     liborc-0.4-0     libpixman-1-0     libpng12-0     libpq5     libpython2.7-minimal     libquadmath0     libschroedinger-1.0-0     libsm6     libsqlite3-0     libstdc++5     libtheora0     libtiff5-dev     libx11-6     libx11-data     libxau6     libxcb1     libxcb-render0     libxcb-shm0     libxdmcp6     libxext6     libxml2     libxrender1     libxslt1.1     libxvidcore4     mercurial     openjdk-8-jdk     python-minimal     build-essential     vim      sudo   && apt-get clean   && find  /var/lib/apt/lists/ -type f -delete
 ---> Using cache
 ---> a581f4de02f2
Step 9/22 : RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
 ---> Using cache
 ---> 72a539530607
Step 10/22 : ENV LANG en_US.UTF-8
 ---> Using cache
 ---> 6cc83c599734
Step 11/22 : RUN locale
 ---> Using cache
 ---> 52c37532b7cc
Step 12/22 : WORKDIR /source
 ---> Using cache
 ---> 748f78fad95a
Step 13/22 : COPY . /source
 ---> a4f6211d1e4e
Step 14/22 : COPY run-bisque.sh virtualenv.sh /builder/
 ---> b3b411f97b21
Step 15/22 : COPY start-bisque.sh /builder/start-scripts.d/R50-start-bisque.sh
 ---> 4172f9ff245a
Step 16/22 : COPY builder/ /builder/build-scripts.d/
 ---> 72e56e32330d
Step 17/22 : COPY boot/ /builder/boot-scripts.d/
 ---> 760dc23a5473
Step 18/22 : RUN bash virtualenv.sh
 ---> Running in 357ca307657f
--2020-07-24 12:29:14--  https://pypi.python.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving pypi.python.org (pypi.python.org)... 151.101.24.223, 2a04:4e42:6::223
Connecting to pypi.python.org (pypi.python.org)|151.101.24.223|:443... connected.
HTTP request sent, awaiting response... 301 Redirect to Primary Domain
Location: https://pypi.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz [following]
--2020-07-24 12:29:14--  https://pypi.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving pypi.org (pypi.org)... 151.101.128.223, 151.101.0.223, 151.101.192.223, ...
Connecting to pypi.org (pypi.org)|151.101.128.223|:443... connected.
HTTP request sent, awaiting response... 301 Moved Permanently
Location: https://files.pythonhosted.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz [following]
--2020-07-24 12:29:14--  https://files.pythonhosted.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving files.pythonhosted.org (files.pythonhosted.org)... 151.101.41.63, 2a04:4e42:6::319
Connecting to files.pythonhosted.org (files.pythonhosted.org)|151.101.41.63|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1863951 (1.8M) [binary/octet-stream]
Saving to: ‘virtualenv-15.1.0.tar.gz’

     0K .......... .......... .......... .......... ..........  2% 1.81M 1s
    50K .......... .......... .......... .......... ..........  5% 3.92M 1s
   100K .......... .......... .......... .......... ..........  8% 10.1M 0s
   150K .......... .......... .......... .......... .......... 10% 5.87M 0s
   200K .......... .......... .......... .......... .......... 13% 8.33M 0s
   250K .......... .......... .......... .......... .......... 16% 6.87M 0s
   300K .......... .......... .......... .......... .......... 19% 9.44M 0s
   350K .......... .......... .......... .......... .......... 21% 9.30M 0s
   400K .......... .......... .......... .......... .......... 24% 5.94M 0s
   450K .......... .......... .......... .......... .......... 27% 9.71M 0s
   500K .......... .......... .......... .......... .......... 30% 8.45M 0s
   550K .......... .......... .......... .......... .......... 32% 7.57M 0s
   600K .......... .......... .......... .......... .......... 35% 9.39M 0s
   650K .......... .......... .......... .......... .......... 38% 8.70M 0s
   700K .......... .......... .......... .......... .......... 41% 8.87M 0s
   750K .......... .......... .......... .......... .......... 43% 10.8M 0s
   800K .......... .......... .......... .......... .......... 46% 10.5M 0s
   850K .......... .......... .......... .......... .......... 49% 8.91M 0s
   900K .......... .......... .......... .......... .......... 52% 9.08M 0s
   950K .......... .......... .......... .......... .......... 54% 12.9M 0s
  1000K .......... .......... .......... .......... .......... 57% 8.45M 0s
  1050K .......... .......... .......... .......... .......... 60% 12.2M 0s
  1100K .......... .......... .......... .......... .......... 63% 11.4M 0s
  1150K .......... .......... .......... .......... .......... 65% 10.3M 0s
  1200K .......... .......... .......... .......... .......... 68% 11.4M 0s
  1250K .......... .......... .......... .......... .......... 71% 12.8M 0s
  1300K .......... .......... .......... .......... .......... 74% 9.84M 0s
  1350K .......... .......... .......... .......... .......... 76% 10.9M 0s
  1400K .......... .......... .......... .......... .......... 79% 13.9M 0s
  1450K .......... .......... .......... .......... .......... 82% 9.79M 0s
  1500K .......... .......... .......... .......... .......... 85% 13.6M 0s
  1550K .......... .......... .......... .......... .......... 87% 16.6M 0s
  1600K .......... .......... .......... .......... .......... 90% 12.2M 0s
  1650K .......... .......... .......... .......... .......... 93% 11.8M 0s
  1700K .......... .......... .......... .......... .......... 96% 13.9M 0s
  1750K .......... .......... .......... .......... .......... 98% 14.8M 0s
  1800K .......... ..........                                 100% 9.96M=0.2s

2020-07-24 12:29:24 (8.47 MB/s) - ‘virtualenv-15.1.0.tar.gz’ saved [1863951/1863951]

virtualenv-15.1.0/
virtualenv-15.1.0/AUTHORS.txt
virtualenv-15.1.0/bin/
virtualenv-15.1.0/bin/rebuild-script.py
virtualenv-15.1.0/docs/
virtualenv-15.1.0/docs/changes.rst
virtualenv-15.1.0/docs/conf.py
virtualenv-15.1.0/docs/development.rst
virtualenv-15.1.0/docs/index.rst
virtualenv-15.1.0/docs/installation.rst
virtualenv-15.1.0/docs/make.bat
virtualenv-15.1.0/docs/Makefile
virtualenv-15.1.0/docs/reference.rst
virtualenv-15.1.0/docs/userguide.rst
virtualenv-15.1.0/LICENSE.txt
virtualenv-15.1.0/MANIFEST.in
virtualenv-15.1.0/PKG-INFO
virtualenv-15.1.0/README.rst
virtualenv-15.1.0/scripts/
virtualenv-15.1.0/scripts/virtualenv
virtualenv-15.1.0/setup.cfg
virtualenv-15.1.0/setup.py
virtualenv-15.1.0/tests/
virtualenv-15.1.0/tests/__init__.py
virtualenv-15.1.0/tests/test_activate.sh
virtualenv-15.1.0/tests/test_activate_output.expected
virtualenv-15.1.0/tests/test_cmdline.py
virtualenv-15.1.0/tests/test_virtualenv.py
virtualenv-15.1.0/virtualenv.egg-info/
virtualenv-15.1.0/virtualenv.egg-info/dependency_links.txt
virtualenv-15.1.0/virtualenv.egg-info/entry_points.txt
virtualenv-15.1.0/virtualenv.egg-info/not-zip-safe
virtualenv-15.1.0/virtualenv.egg-info/PKG-INFO
virtualenv-15.1.0/virtualenv.egg-info/SOURCES.txt
virtualenv-15.1.0/virtualenv.egg-info/top_level.txt
virtualenv-15.1.0/virtualenv.py
virtualenv-15.1.0/virtualenv_embedded/
virtualenv-15.1.0/virtualenv_embedded/activate.bat
virtualenv-15.1.0/virtualenv_embedded/activate.csh
virtualenv-15.1.0/virtualenv_embedded/activate.fish
virtualenv-15.1.0/virtualenv_embedded/activate.ps1
virtualenv-15.1.0/virtualenv_embedded/activate.sh
virtualenv-15.1.0/virtualenv_embedded/activate_this.py
virtualenv-15.1.0/virtualenv_embedded/deactivate.bat
virtualenv-15.1.0/virtualenv_embedded/distutils-init.py
virtualenv-15.1.0/virtualenv_embedded/distutils.cfg
virtualenv-15.1.0/virtualenv_embedded/python-config
virtualenv-15.1.0/virtualenv_embedded/site.py
virtualenv-15.1.0/virtualenv_support/
virtualenv-15.1.0/virtualenv_support/__init__.py
virtualenv-15.1.0/virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/pip-9.0.1-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl
running install
running build
running build_py
creating build
creating build/lib.linux-x86_64-2.7
copying virtualenv.py -> build/lib.linux-x86_64-2.7
creating build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/__init__.py -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/pip-9.0.1-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
running build_scripts
creating build/scripts-2.7
copying and adjusting scripts/virtualenv -> build/scripts-2.7
changing mode of build/scripts-2.7/virtualenv from 644 to 755
running install_lib
copying build/lib.linux-x86_64-2.7/virtualenv.py -> /usr/local/lib/python2.7/dist-packages
creating /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/pip-9.0.1-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/__init__.py -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
byte-compiling /usr/local/lib/python2.7/dist-packages/virtualenv.py to virtualenv.pyc
byte-compiling /usr/local/lib/python2.7/dist-packages/virtualenv_support/__init__.py to __init__.pyc
running install_scripts
copying build/scripts-2.7/virtualenv -> /usr/local/bin
changing mode of /usr/local/bin/virtualenv to 755
running install_egg_info
Writing /usr/local/lib/python2.7/dist-packages/virtualenv-15.1.0.egg-info
Removing intermediate container 357ca307657f
 ---> f002b535dd92
Step 19/22 : ENV PY_INDEX=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
 ---> Running in e1f03e5a952f
Removing intermediate container e1f03e5a952f
 ---> f75934f166b5
Step 20/22 : RUN bash run-bisque.sh build
 ---> Running in da05e8b6bc6d
+ CMD=build
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
+ mkdir -p /source/reports/
++ pwd
+ echo 'In ' /source 'BISQUE in' /source/ 'Reports in' /source/reports/
+ cd /source/
In  /source BISQUE in /source/ Reports in /source/reports/
+ '[' build = build ']'
+ let returncode=0
BUILDING
+ echo BUILDING
+ '[' '!' -d /usr/lib/bisque ']'
+ virtualenv /usr/lib/bisque
New python executable in /usr/lib/bisque/bin/python
Installing setuptools, pip, wheel...done.
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
+ ls -l /builder//build-scripts.d
total 4
-rw-r--r-- 1 root root 408 Jul 24 12:13 20-build-bisque.sh
+ for f in '${BUILD}/build-scripts.d/*.sh'
+ echo 'Executing /builder//build-scripts.d/20-build-bisque.sh'
Executing /builder//build-scripts.d/20-build-bisque.sh
+ '[' -f /builder//build-scripts.d/20-build-bisque.sh ']'
+ /builder//build-scripts.d/20-build-bisque.sh
run-bisque.sh: line 34: /builder//build-scripts.d/20-build-bisque.sh: Permission denied
+ echo 'FAILED /builder//build-scripts.d/20-build-bisque.sh'
+ let returncode=2
FAILED /builder//build-scripts.d/20-build-bisque.sh
+ '[' 2 -ne 0 ']'
BUILD Failed
+ echo 'BUILD Failed'
+ exit 2
The command '/bin/sh -c bash run-bisque.sh build' returned a non-zero code: 2
amil@amil:~/bisqueUCSB$ vim Dockerfile.caffe.xenial 
amil@amil:~/bisqueUCSB$ docker build -t bisque-developer-beta:0.7-broccolli -f Dockerfile.caffe.xenial .
Sending build context to Docker daemon  518.3MB
Step 1/24 : FROM biodev.ece.ucsb.edu:5000/caffe-runtime:xenial
 ---> 031ed4afa9b5
Step 2/24 : ENV DEBIAN_FRONTEND noninteractive
 ---> Using cache
 ---> 103884e6a3ca
Step 3/24 : ENV IMGCNV=imgcnv_ubuntu16_2.4.3
 ---> Using cache
 ---> 667c1b72ebaf
Step 4/24 : RUN apt-get update -qq && apt-get install -qq -y apt-transport-https wget
 ---> Using cache
 ---> 777a5ad0cb7f
Step 5/24 : RUN wget -q -O - https://biodev.ece.ucsb.edu/debian/cbi_repository_key.asc | apt-key add -
 ---> Using cache
 ---> 80ca52f265f1
Step 6/24 : RUN  echo "deb http://ftp.ucsb.edu/pub/mirrors/linux/ubuntu-archive xenial main restricted universe" >> /etc/apt/sources.list.d/bisque.list
 ---> Using cache
 ---> 89ec49fd98e2
Step 7/24 : RUN wget -q https://bitbucket.org/dimin/bioimageconvert/downloads/$IMGCNV.tar.gz     && tar xf $IMGCNV.tar.gz     && mv $IMGCNV/imgcnv /usr/bin     && mv $IMGCNV/libimgcnv.so* /usr/lib/x86_64-linux-gnu/     && rm -rf  $IMGCNV     && apt-get install -y --no-install-recommends     libswscale-ffmpeg3 libfftw3-3 libgdcm2.6 libavcodec-ffmpeg56 libavformat-ffmpeg56 libavutil-ffmpeg54 libhdf5-cpp-11
 ---> Using cache
 ---> 161a7dde6c21
Step 8/24 : RUN apt-get update  -qq     && apt-get install -y --no-install-recommends --allow-unauthenticated     git     locales     less     libasound2     libasound2-data     libblas3     libblas-common     libbz2-1.0     libgdbm3     libgdk-pixbuf2.0-0     libgdk-pixbuf2.0-common     libgfortran3     libglib2.0-0     libglib2.0-data     libblosc1     libgomp1     libgv-python     libice6     libjasper1    libjbig0     libjpeg62     liblapack3     liblzo2-2     libmagic1     libogg0     libopenjpeg5     libopenslide0     libopenslide-dev     liborc-0.4-0     libpixman-1-0     libpng12-0     libpq5     libpython2.7-minimal     libquadmath0     libschroedinger-1.0-0     libsm6     libsqlite3-0     libstdc++5     libtheora0     libtiff5-dev     libx11-6     libx11-data     libxau6     libxcb1     libxcb-render0     libxcb-shm0     libxdmcp6     libxext6     libxml2     libxrender1     libxslt1.1     libxvidcore4     mercurial     openjdk-8-jdk     python-minimal     build-essential     vim      sudo   && apt-get clean   && find  /var/lib/apt/lists/ -type f -delete
 ---> Using cache
 ---> a581f4de02f2
Step 9/24 : RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
 ---> Using cache
 ---> 72a539530607
Step 10/24 : ENV LANG en_US.UTF-8
 ---> Using cache
 ---> 6cc83c599734
Step 11/24 : RUN locale
 ---> Using cache
 ---> 52c37532b7cc
Step 12/24 : WORKDIR /source
 ---> Using cache
 ---> 748f78fad95a
Step 13/24 : COPY . /source
 ---> 03deb4eebc8c
Step 14/24 : COPY run-bisque.sh virtualenv.sh /builder/
 ---> 3a2d3643cd37
Step 15/24 : COPY start-bisque.sh /builder/start-scripts.d/R50-start-bisque.sh
 ---> 8e83f6a5c044
Step 16/24 : COPY builder/ /builder/build-scripts.d/
 ---> 2c8201a57907
Step 17/24 : COPY boot/ /builder/boot-scripts.d/
 ---> 5ce162dafb02
Step 18/24 : RUN find /builder/ -type f -iname "*.sh" -exec chmod +x {} \;
 ---> Running in 56adfd343d75
Removing intermediate container 56adfd343d75
 ---> ae2b45285fd3
Step 19/24 : RUN find /boot/ -type f -iname "*.sh" -exec chmod +x {} \;
 ---> Running in a860bf497f96
Removing intermediate container a860bf497f96
 ---> 66f846c47e3e
Step 20/24 : RUN /builder/virtualenv.sh
 ---> Running in b6204816585c
--2020-07-24 12:32:20--  https://pypi.python.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving pypi.python.org (pypi.python.org)... 151.101.24.223, 2a04:4e42:6::223
Connecting to pypi.python.org (pypi.python.org)|151.101.24.223|:443... connected.
HTTP request sent, awaiting response... 301 Redirect to Primary Domain
Location: https://pypi.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz [following]
--2020-07-24 12:32:20--  https://pypi.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving pypi.org (pypi.org)... 151.101.0.223, 151.101.128.223, 151.101.192.223, ...
Connecting to pypi.org (pypi.org)|151.101.0.223|:443... connected.
HTTP request sent, awaiting response... 301 Moved Permanently
Location: https://files.pythonhosted.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz [following]
--2020-07-24 12:32:20--  https://files.pythonhosted.org/packages/d4/0c/9840c08189e030873387a73b90ada981885010dd9aea134d6de30cd24cb8/virtualenv-15.1.0.tar.gz
Resolving files.pythonhosted.org (files.pythonhosted.org)... 151.101.25.63, 2a04:4e42:6::319
Connecting to files.pythonhosted.org (files.pythonhosted.org)|151.101.25.63|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1863951 (1.8M) [binary/octet-stream]
Saving to: ‘virtualenv-15.1.0.tar.gz’

     0K .......... .......... .......... .......... ..........  2% 1.86M 1s
    50K .......... .......... .......... .......... ..........  5% 4.28M 1s
   100K .......... .......... .......... .......... ..........  8% 10.6M 0s
   150K .......... .......... .......... .......... .......... 10% 6.04M 0s
   200K .......... .......... .......... .......... .......... 13% 15.2M 0s
   250K .......... .......... .......... .......... .......... 16% 28.3M 0s
   300K .......... .......... .......... .......... .......... 19% 20.0M 0s
   350K .......... .......... .......... .......... .......... 21% 7.40M 0s
   400K .......... .......... .......... .......... .......... 24% 19.8M 0s
   450K .......... .......... .......... .......... .......... 27% 13.3M 0s
   500K .......... .......... .......... .......... .......... 30% 19.1M 0s
   550K .......... .......... .......... .......... .......... 32% 11.1M 0s
   600K .......... .......... .......... .......... .......... 35% 18.1M 0s
   650K .......... .......... .......... .......... .......... 38% 17.4M 0s
   700K .......... .......... .......... .......... .......... 41% 18.2M 0s
   750K .......... .......... .......... .......... .......... 43% 11.2M 0s
   800K .......... .......... .......... .......... .......... 46% 18.2M 0s
   850K .......... .......... .......... .......... .......... 49% 12.9M 0s
   900K .......... .......... .......... .......... .......... 52% 29.3M 0s
   950K .......... .......... .......... .......... .......... 54% 10.7M 0s
  1000K .......... .......... .......... .......... .......... 57% 17.9M 0s
  1050K .......... .......... .......... .......... .......... 60% 12.5M 0s
  1100K .......... .......... .......... .......... .......... 63% 21.1M 0s
  1150K .......... .......... .......... .......... .......... 65% 10.5M 0s
  1200K .......... .......... .......... .......... .......... 68% 14.9M 0s
  1250K .......... .......... .......... .......... .......... 71% 19.3M 0s
  1300K .......... .......... .......... .......... .......... 74% 10.0M 0s
  1350K .......... .......... .......... .......... .......... 76% 16.8M 0s
  1400K .......... .......... .......... .......... .......... 79% 20.9M 0s
  1450K .......... .......... .......... .......... .......... 82% 18.9M 0s
  1500K .......... .......... .......... .......... .......... 85% 9.06M 0s
  1550K .......... .......... .......... .......... .......... 87% 19.9M 0s
  1600K .......... .......... .......... .......... .......... 90% 16.7M 0s
  1650K .......... .......... .......... .......... .......... 93% 18.9M 0s
  1700K .......... .......... .......... .......... .......... 96% 10.8M 0s
  1750K .......... .......... .......... .......... .......... 98% 16.9M 0s
  1800K .......... ..........                                 100% 56.4M=0.2s

2020-07-24 12:32:21 (11.4 MB/s) - ‘virtualenv-15.1.0.tar.gz’ saved [1863951/1863951]

virtualenv-15.1.0/
virtualenv-15.1.0/AUTHORS.txt
virtualenv-15.1.0/bin/
virtualenv-15.1.0/bin/rebuild-script.py
virtualenv-15.1.0/docs/
virtualenv-15.1.0/docs/changes.rst
virtualenv-15.1.0/docs/conf.py
virtualenv-15.1.0/docs/development.rst
virtualenv-15.1.0/docs/index.rst
virtualenv-15.1.0/docs/installation.rst
virtualenv-15.1.0/docs/make.bat
virtualenv-15.1.0/docs/Makefile
virtualenv-15.1.0/docs/reference.rst
virtualenv-15.1.0/docs/userguide.rst
virtualenv-15.1.0/LICENSE.txt
virtualenv-15.1.0/MANIFEST.in
virtualenv-15.1.0/PKG-INFO
virtualenv-15.1.0/README.rst
virtualenv-15.1.0/scripts/
virtualenv-15.1.0/scripts/virtualenv
virtualenv-15.1.0/setup.cfg
virtualenv-15.1.0/setup.py
virtualenv-15.1.0/tests/
virtualenv-15.1.0/tests/__init__.py
virtualenv-15.1.0/tests/test_activate.sh
virtualenv-15.1.0/tests/test_activate_output.expected
virtualenv-15.1.0/tests/test_cmdline.py
virtualenv-15.1.0/tests/test_virtualenv.py
virtualenv-15.1.0/virtualenv.egg-info/
virtualenv-15.1.0/virtualenv.egg-info/dependency_links.txt
virtualenv-15.1.0/virtualenv.egg-info/entry_points.txt
virtualenv-15.1.0/virtualenv.egg-info/not-zip-safe
virtualenv-15.1.0/virtualenv.egg-info/PKG-INFO
virtualenv-15.1.0/virtualenv.egg-info/SOURCES.txt
virtualenv-15.1.0/virtualenv.egg-info/top_level.txt
virtualenv-15.1.0/virtualenv.py
virtualenv-15.1.0/virtualenv_embedded/
virtualenv-15.1.0/virtualenv_embedded/activate.bat
virtualenv-15.1.0/virtualenv_embedded/activate.csh
virtualenv-15.1.0/virtualenv_embedded/activate.fish
virtualenv-15.1.0/virtualenv_embedded/activate.ps1
virtualenv-15.1.0/virtualenv_embedded/activate.sh
virtualenv-15.1.0/virtualenv_embedded/activate_this.py
virtualenv-15.1.0/virtualenv_embedded/deactivate.bat
virtualenv-15.1.0/virtualenv_embedded/distutils-init.py
virtualenv-15.1.0/virtualenv_embedded/distutils.cfg
virtualenv-15.1.0/virtualenv_embedded/python-config
virtualenv-15.1.0/virtualenv_embedded/site.py
virtualenv-15.1.0/virtualenv_support/
virtualenv-15.1.0/virtualenv_support/__init__.py
virtualenv-15.1.0/virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/pip-9.0.1-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl
virtualenv-15.1.0/virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl
running install
running build
running build_py
creating build
creating build/lib.linux-x86_64-2.7
copying virtualenv.py -> build/lib.linux-x86_64-2.7
creating build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/__init__.py -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/pip-9.0.1-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
copying virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl -> build/lib.linux-x86_64-2.7/virtualenv_support
running build_scripts
creating build/scripts-2.7
copying and adjusting scripts/virtualenv -> build/scripts-2.7
changing mode of build/scripts-2.7/virtualenv from 644 to 755
running install_lib
copying build/lib.linux-x86_64-2.7/virtualenv.py -> /usr/local/lib/python2.7/dist-packages
creating /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/pip-9.0.1-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/__init__.py -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/argparse-1.4.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/setuptools-28.8.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
copying build/lib.linux-x86_64-2.7/virtualenv_support/wheel-0.29.0-py2.py3-none-any.whl -> /usr/local/lib/python2.7/dist-packages/virtualenv_support
byte-compiling /usr/local/lib/python2.7/dist-packages/virtualenv.py to virtualenv.pyc
byte-compiling /usr/local/lib/python2.7/dist-packages/virtualenv_support/__init__.py to __init__.pyc
running install_scripts
copying build/scripts-2.7/virtualenv -> /usr/local/bin
changing mode of /usr/local/bin/virtualenv to 755
running install_egg_info
Writing /usr/local/lib/python2.7/dist-packages/virtualenv-15.1.0.egg-info
Removing intermediate container b6204816585c
 ---> a95772a2a169
Step 21/24 : ENV PY_INDEX=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
 ---> Running in 897294363e51
Removing intermediate container 897294363e51
 ---> 1e284ce8b56d
Step 22/24 : RUN /builder/run-bisque.sh build
 ---> Running in 5cf247e53f15
+ CMD=build
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
+ mkdir -p /source/reports/
++ pwd
+ echo 'In ' /source 'BISQUE in' /source/ 'Reports in' /source/reports/
In  /source BISQUE in /source/ Reports in /source/reports/
+ cd /source/
+ '[' build = build ']'
+ let returncode=0
+ echo BUILDING
+ '[' '!' -d /usr/lib/bisque ']'
BUILDING
+ virtualenv /usr/lib/bisque
New python executable in /usr/lib/bisque/bin/python
Installing setuptools, pip, wheel...done.
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
+ ls -l /builder//build-scripts.d
total 4
-rwxr-xr-x 1 root root 408 Jul 24 12:13 20-build-bisque.sh
+ for f in '${BUILD}/build-scripts.d/*.sh'
Executing /builder//build-scripts.d/20-build-bisque.sh
+ echo 'Executing /builder//build-scripts.d/20-build-bisque.sh'
+ '[' -f /builder//build-scripts.d/20-build-bisque.sh ']'
+ /builder//build-scripts.d/20-build-bisque.sh
+ PIP_INDEX_URL=
+ pip install -U pip
Collecting pip
  Downloading https://files.pythonhosted.org/packages/43/84/23ed6a1796480a6f1a2d38f2802901d078266bda38388954d01d3f2e821d/pip-20.1.1-py2.py3-none-any.whl (1.5MB)
Installing collected packages: pip
  Found existing installation: pip 9.0.1
    Uninstalling pip-9.0.1:
      Successfully uninstalled pip-9.0.1
Successfully installed pip-20.1.1
+ PIP_INDEX_URL=
+ pip install -U setuptools==34.4.1
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. pip 21.0 will drop support for Python 2.7 in January 2021. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Collecting setuptools==34.4.1
  Downloading setuptools-34.4.1-py2.py3-none-any.whl (390 kB)
Collecting packaging>=16.8
  Downloading packaging-20.4-py2.py3-none-any.whl (37 kB)
Collecting six>=1.6.0
  Downloading six-1.15.0-py2.py3-none-any.whl (10 kB)
Collecting appdirs>=1.4.0
  Downloading appdirs-1.4.4-py2.py3-none-any.whl (9.6 kB)
Collecting pyparsing>=2.0.2
  Downloading pyparsing-2.4.7-py2.py3-none-any.whl (67 kB)
Installing collected packages: six, pyparsing, packaging, appdirs, setuptools
  Attempting uninstall: setuptools
    Found existing installation: setuptools 28.8.0
    Uninstalling setuptools-28.8.0:
      Successfully uninstalled setuptools-28.8.0
Successfully installed appdirs-1.4.4 packaging-20.4 pyparsing-2.4.7 setuptools-34.4.1 six-1.15.0
+ pip install --extra-index-url https://pypi.org/simple -r requirements.txt
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. pip 21.0 will drop support for Python 2.7 in January 2021. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Looking in indexes: https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple, https://pypi.org/simple
Collecting Babel==1.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/641/c85738a4cafde/Babel-1.3-py2-none-any.whl (3.6 MB)
Collecting Beaker==1.6.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/383/c34630d280860/Beaker-1.6.4-py2-none-any.whl (45 kB)
Collecting FormEncode==1.3.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/35a/012dcd644ff20/FormEncode-1.3.1-py2-none-any.whl (337 kB)
Collecting Genshi==0.7
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/c2c/851c2b9c379b5/Genshi-0.7-cp27-cp27mu-linux_x86_64.whl (189 kB)
Collecting Mako==0.9.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/e89/d8b33e6adf93e/Mako-0.9.1-py2.py3-none-any.whl (75 kB)
Collecting MarkupSafe==0.21
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/910/55d2ea80a8923/MarkupSafe-0.21-cp27-cp27mu-linux_x86_64.whl (25 kB)
Collecting Minimatic==1.0.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/modified/%2Bf/f15/8deeccfab43d4/Minimatic-1.0.4-py2-none-any.whl (11 kB)
Collecting Paste==1.7.5.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/modified/%2Bf/148/cc80bc80b80be/Paste-1.7.5.2-py2-none-any.whl (635 kB)
Collecting PasteDeploy==1.3.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/464/521bfd6dff4c9/PasteDeploy-1.3.4-py2-none-any.whl (23 kB)
Collecting PasteScript==1.7.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/modified/%2Bf/daf/2d3b93920b3fa/PasteScript-1.7.3-py2-none-any.whl (111 kB)
Collecting Paver==1.2.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/e67/976633402d017/Paver-1.2.4-py2.py3-none-any.whl (295 kB)
Collecting Pillow==4.2.1
  Downloading Pillow-4.2.1-cp27-cp27mu-manylinux1_x86_64.whl (5.8 MB)
Collecting Pygments==1.6
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/775/be41cb9beb51a/Pygments-1.6-py2-none-any.whl (627 kB)
Collecting Pylons==1.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/f5c/8f648cd937399/Pylons-1.0-py2-none-any.whl (132 kB)
Collecting Routes==2.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/086/0aa5a4bbccdd0/Routes-2.0-py27-none-any.whl (45 kB)
Collecting SQLAlchemy==1.2.5
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/73e/821ce170def65/SQLAlchemy-1.2.5-cp27-cp27mu-linux_x86_64.whl (1.1 MB)
Collecting PySqlite==2.8.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/1f8/2f7ae96f745a4/pysqlite-2.8.3-cp27-cp27mu-linux_x86_64.whl (124 kB)
Collecting tempita==0.5.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/fd4/7e737024897ba/Tempita-0.5.2-py2-none-any.whl (13 kB)
Collecting ToscaWidgets==0.9.12
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/505/c6ac980cee94e/ToscaWidgets-0.9.12-py2-none-any.whl (75 kB)
Collecting TurboGears2==2.1.5
  Downloading https://biodev.ece.ucsb.edu/py/bisque/modified/%2Bf/e47/37d6be43b6c40/TurboGears2-2.1.5-py2-none-any.whl (107 kB)
Collecting TurboMail==3.0.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/a01/1739816549703/TurboMail-3.0.3-py2-none-any.whl (43 kB)
Collecting WebError==0.10.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/d2e/133f25d6d351e/WebError-0.10.3-py2-none-any.whl (85 kB)
Collecting WebFlash==0.1a9
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/ed4/3551f55670623/WebFlash-0.1a9-py2-none-any.whl (9.0 kB)
Collecting WebHelpers==1.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/6b6/5503f0b5f70bf/WebHelpers-1.3-py2-none-any.whl (149 kB)
Collecting WebOb==1.0.8
  Downloading https://biodev.ece.ucsb.edu/py/bisque/modified/%2Bf/000/269dac2bdb892/WebOb-1.0.8-py2-none-any.whl (60 kB)
Collecting WebTest==1.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/5f2/b155e5dcfc9ce/WebTest-1.1-py2-none-any.whl (20 kB)
Collecting alembic==0.6.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/3e9/6d7e290e31584/alembic-0.6.3-py2.py3-none-any.whl (71 kB)
Collecting altgraph==0.9
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/451/488040641e82b/altgraph-0.9-py2-none-any.whl (22 kB)
Collecting beautifulsoup4==4.3.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/f41/86d6d99bc4099/beautifulsoup4-4.3.2-py2-none-any.whl (76 kB)
Collecting boto3==1.4.8
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/edd/35eb7cd8d56f0/boto3-1.4.8-py2.py3-none-any.whl (128 kB)
Collecting jmespath==0.9.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/3f0/3b90ac8e0f3ba/jmespath-0.9.2-py2.py3-none-any.whl (23 kB)
Collecting botocore==1.8.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/726/62f245a9dd756/botocore-1.8.2-py2.py3-none-any.whl (3.8 MB)
Collecting docutils==0.13.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/de4/54f1015958450/docutils-0.13.1-py2-none-any.whl (537 kB)
Collecting cssutils==1.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/b64/f8567825d220d/cssutils-1.0-py2-none-any.whl (292 kB)
Collecting decorator==3.4.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/b62/0ee8fa49537ed/decorator-3.4.0-py2-none-any.whl (7.7 kB)
Collecting ecdsa==0.11
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/97d/c902311942b03/ecdsa-0.11-py2-none-any.whl (43 kB)
Collecting furl==0.3.7
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/1f3/81db9c757a586/furl-0.3.7-py2-none-any.whl (31 kB)
Collecting futures==3.0.5
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/f7f/16b6bf9653a91/futures-3.0.5-py2-none-any.whl (14 kB)
Collecting future==0.16.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/ab4/1dcdca4d48bd0/future-0.16.0-py2-none-any.whl (500 kB)
Collecting funcsigs==1.0.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/330/cc27ccbf7f1e9/funcsigs-1.0.2-py2.py3-none-any.whl (17 kB)
Collecting filechunkio==1.6
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/cf3/6e792e285b3c2/filechunkio-1.6-py2-none-any.whl (5.0 kB)
Collecting gdata==2.0.18
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/894/6eb4732cbcade/gdata-2.0.18-py2-none-any.whl (613 kB)
Collecting httplib2==0.7.1-1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/modified/%2Bf/bca/34c312d680175/httplib2-0.7.1_1-py2-none-any.whl (27 kB)
Collecting importlib==1.0.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/de4/ffb239e89314c/importlib-1.0.3-py2-none-any.whl (2.5 kB)
Collecting lxml==3.7.3
  Downloading lxml-3.7.3-cp27-cp27mu-manylinux1_x86_64.whl (6.8 MB)
Collecting nose==1.3.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/dc2/26d9c760938df/nose-1.3.1-py2-none-any.whl (154 kB)
Collecting openslide-python==1.1.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/f6b/815e16126b5b5/openslide_python-1.1.1-cp27-cp27mu-linux_x86_64.whl (24 kB)
Collecting ordereddict==1.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/74f/5be695aae57bf/ordereddict-1.1-py2-none-any.whl (3.3 kB)
Collecting orderedset==2.0.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/c24/42d4d49d42b8f/orderedset-2.0.1-cp27-cp27mu-linux_x86_64.whl (225 kB)
Collecting orderedmultidict==0.7.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/608/cf460a844292e/orderedmultidict-0.7.1-py2-none-any.whl (17 kB)
Collecting pbr==0.6
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/469/08c53731cbb9d/pbr-0.6-py2.py3-none-any.whl (62 kB)
Collecting pkginfo==1.2b1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/fe8/caae7fe1520d3/pkginfo-1.2b1-py2-none-any.whl (24 kB)
Collecting ply==3.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/0a0/37e09ac782d1c/ply-3.4-py2-none-any.whl (46 kB)
Collecting poster==0.8.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/bcc/8d2491f293efd/poster-0.8.1-py2-none-any.whl (15 kB)
Collecting psutil==4.3.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/409/a318cc7fa2982/psutil-4.3.0-cp27-cp27mu-linux_x86_64.whl (178 kB)
Collecting python_irodsclient
  Downloading python_irodsclient-0.8.3-py2.py3-none-any.whl (103 kB)
Collecting python_multipart==0.0.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/66b/54736d2a3eead/python_multipart-0.0.4-py2-none-any.whl (32 kB)
Collecting pycrypto==2.6.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/69c/e38edc01847b6/pycrypto-2.6.1-cp27-cp27mu-linux_x86_64.whl (502 kB)
Collecting python-dateutil==2.7.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/1ad/b80e7a782c12e/python_dateutil-2.7.3-py2.py3-none-any.whl (211 kB)
Collecting python-mimeparse==1.6.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/a29/5f03ff2034149/python_mimeparse-1.6.0-py2.py3-none-any.whl (6.1 kB)
Collecting pyinstaller==3.2.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/caa/fffbf1ee647f7/PyInstaller-3.2.1-py2-none-any.whl (2.3 MB)
Collecting pytz==2013.9
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/b6d/2dc844be7b184/pytz-2013.9-py2-none-any.whl (470 kB)
Collecting recaptcha-client==1.0.6
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/9fa/ff0338243ff46/recaptcha_client-1.0.6-py2-none-any.whl (6.6 kB)
Collecting repoze.lru==0.6
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/118/ac37fc3e781d4/repoze.lru-0.6-py2-none-any.whl (11 kB)
Collecting repoze.tm2==2.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/520/a25531669d505/repoze.tm2-2.0-py2-none-any.whl (11 kB)
Collecting repoze.what==1.0.9
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/4d0/01632bb0afc9c/repoze.what-1.0.9-py2-none-any.whl (21 kB)
Collecting repoze.what-pylons==1.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/426/e6938bee16f64/repoze.what_pylons-1.0-py2-none-any.whl (8.5 kB)
Collecting repoze.what-quickstart==1.0.9
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/509/d7f0e908e79b6/repoze.what_quickstart-1.0.9-py2-none-any.whl (10 kB)
Collecting repoze.what.plugins.sql==1.0.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/136/bb18f3a37ebe7/repoze.what.plugins.sql-1.0.1-py2-none-any.whl (9.3 kB)
Collecting repoze.who==1.0.19
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/495/740722cca9fa2/repoze.who-1.0.19-py2-none-any.whl (58 kB)
Collecting repoze.who-friendlyform==1.0.8
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/061/d093d9676f68c/repoze.who_friendlyform-1.0.8-py2-none-any.whl (7.9 kB)
Collecting repoze.who-testutil==1.0.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/020/a73594201628d/repoze.who_testutil-1.0.1-py2-none-any.whl (7.2 kB)
Collecting repoze.who.plugins.sa==1.0.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/bd2/776bf2be5cf3a/repoze.who.plugins.sa-1.0.1-py2-none-any.whl (6.8 kB)
Collecting requests==2.18.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/66d/3324b837676dd/requests-2.18.4-py2.py3-none-any.whl (91 kB)
Collecting requests_toolbelt==0.6.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/a25/2f66501663d65/requests_toolbelt-0.6.2-py2.py3-none-any.whl (49 kB)
Collecting s3transfer==0.1.10
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/bc5/2f38637f37572/s3transfer-0.1.10-py2.py3-none-any.whl (54 kB)
Collecting shortuuid==0.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/93b/d86e1dcd8b74d/shortuuid-0.4-py2-none-any.whl (4.2 kB)
Collecting simplejson==3.3.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/39b/9d3db323b7500/simplejson-3.3.3-cp27-cp27mu-linux_x86_64.whl (104 kB)
Collecting six==1.11
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/832/dc0e10feb1aa2/six-1.11.0-py2.py3-none-any.whl (10 kB)
Collecting tgext.registration2==0.5.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/modified/%2Bf/594/115a8f36c0819/tgext.registration2-0.5.2-py2-none-any.whl (55 kB)
Collecting transaction==1.4.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/9e9/fed0e5d44b051/transaction-1.4.1-py2-none-any.whl (44 kB)
Collecting tw.forms==0.9.9
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/455/4afeae8e2e77c/tw.forms-0.9.9-py2-none-any.whl (144 kB)
Collecting tw.output==0.5.0dev-20110906
  Downloading https://biodev.ece.ucsb.edu/py/bisque/modified/%2Bf/7fc/a7d1c52052134/tw.output-0.5.0dev_20110906-py2-none-any.whl (11 kB)
Collecting tw.recaptcha==0.8
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/e18/b198c99527cab/tw.recaptcha-0.8-py2-none-any.whl (6.5 kB)
Collecting unittest2==0.5.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/9f3/965c931b5ba25/unittest2-0.5.1-py2-none-any.whl (73 kB)
Collecting waitress==0.8.8
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/107/208775ac5f9f3/waitress-0.8.8-py2-none-any.whl (115 kB)
Requirement already satisfied: wsgiref==0.1.2 in /usr/lib/python2.7 (from -r requirements.txt (line 99)) (0.1.2)
Collecting xmlrunner==1.7.7
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/e5a/c4ad802310340/xmlrunner-1.7.7-cp27-none-any.whl (7.2 kB)
Collecting zope.interface==4.1.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/4a6/39229898d58b5/zope.interface-4.1.0-cp27-cp27mu-linux_x86_64.whl (148 kB)
Collecting zope.sqlalchemy==0.7.7
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/658/c702e0621a01c/zope.sqlalchemy-0.7.7-py2-none-any.whl (25 kB)
Collecting linesman==0.3.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/3e9/74cb22507fcb8/linesman-0.3.2-py2-none-any.whl (112 kB)
Collecting pygraphviz==1.3.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/a0b/ec16941cc3493/pygraphviz-1.3.1-cp27-cp27mu-linux_x86_64.whl (150 kB)
Collecting networkx==1.8
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/ff5/7e831c74d9c8f/networkx-1.8-py2-none-any.whl (906 kB)
Collecting olefile==0.44
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/409/820985e7e082d/olefile-0.44-py2.py3-none-any.whl (52 kB)
Collecting pyproj==1.9.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/3ed/bd6d71ea06765/pyproj-1.9.3-cp27-cp27mu-linux_x86_64.whl (3.5 MB)
Collecting geojson==1.0.9
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/c13/b1d2331e42b4d/geojson-1.0.9-py2-none-any.whl (13 kB)
Collecting pydicom==0.9.8
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/00d/aa29a3675333c/pydicom-0.9.8-py2-none-any.whl (461 kB)
Collecting xlrd==0.9.4
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/0ba/ca36836c164b9/xlrd-0.9.4-py2-none-any.whl (143 kB)
Collecting numexpr==2.6.2
  Downloading numexpr-2.6.2-cp27-cp27mu-manylinux1_x86_64.whl (363 kB)
Collecting numpy==1.12.0
  Downloading numpy-1.12.0-cp27-cp27mu-manylinux1_x86_64.whl (16.5 MB)
Collecting tables==3.4.2
  Downloading tables-3.4.2-3-cp27-cp27mu-manylinux1_x86_64.whl (4.4 MB)
Collecting pandas==0.19.2
  Downloading pandas-0.19.2-cp27-cp27mu-manylinux1_x86_64.whl (17.2 MB)
Collecting mahotas==1.4.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/eec/9bb2764042b48/mahotas-1.4.3-cp27-cp27mu-linux_x86_64.whl (4.1 MB)
Collecting libtiff==0.4.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/372/1f8df4c6296e4/libtiff-0.4.0-cp27-cp27mu-linux_x86_64.whl (198 kB)
Collecting psycopg2==2.6.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/ebb/35123fa4769c6/psycopg2-2.6.1-cp27-cp27mu-linux_x86_64.whl (341 kB)
Collecting pylint==1.9.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/a48/070545c12430c/pylint-1.9.2-py2.py3-none-any.whl (690 kB)
Collecting configparser==3.5.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/086/db04c94222b1e/configparser-3.5.0-py2-none-any.whl (27 kB)
Collecting py==1.4.34
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/2cc/b79b01769d991/py-1.4.34-py2.py3-none-any.whl (84 kB)
Collecting mccabe==0.6.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/ab8/a6258860da4b6/mccabe-0.6.1-py2.py3-none-any.whl (8.6 kB)
Collecting singledispatch==3.4.0.3
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/833/b46966687b3de/singledispatch-3.4.0.3-py2.py3-none-any.whl (12 kB)
Collecting astroid==1.6.5
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/0ef/2bf9f07c31509/astroid-1.6.5-py2.py3-none-any.whl (293 kB)
Collecting lazy-object-proxy==1.3.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/61a/6cf00dcb1a7f0/lazy_object_proxy-1.3.1-cp27-cp27mu-manylinux1_x86_64.whl (56 kB)
Collecting wrapt==1.10.10
  Downloading https://biodev.ece.ucsb.edu/py/bisque/xenial/%2Bf/c9b/e2b11a166d466/wrapt-1.10.10-cp27-cp27mu-linux_x86_64.whl (61 kB)
Collecting pytest==3.1.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/765/ce3acfff504c6/pytest-3.1.1-py2.py3-none-any.whl (179 kB)
Collecting prettytable==0.7.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/b96/c0345bf901c98/prettytable-0.7.2-cp27-none-any.whl (13 kB)
Collecting backports.functools-lru-cache==1.5
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/f0b/0e4eba956de51/backports.functools_lru_cache-1.5-py2.py3-none-any.whl (7.0 kB)
Collecting isort==4.2.5
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/a0c/38c1c5e4c70ea/isort-4.2.5-py2.py3-none-any.whl (40 kB)
Collecting pluggy==0.4.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/d27/66caddfbbc8ef/pluggy-0.4.0-py2.py3-none-any.whl (11 kB)
Collecting tifffile==0.14.0
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/9db/b2718a2f9ea27/tifffile-0.14.0-py2-none-any.whl (98 kB)
Collecting enum34==1.1.6
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/6bd/0f6ad48ec2aa1/enum34-1.1.6-py2-none-any.whl (12 kB)
Requirement already satisfied: pip>=1.0 in /usr/lib/bisque/lib/python2.7/site-packages (from pbr==0.6->-r requirements.txt (line 60)) (20.1.1)
Requirement already satisfied: setuptools in /usr/lib/bisque/lib/python2.7/site-packages (from pyinstaller==3.2.1->-r requirements.txt (line 70)) (34.4.1)
Collecting urllib3<1.23,>=1.21.1
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/063/30f386d6e4b19/urllib3-1.22-py2.py3-none-any.whl (132 kB)
Collecting certifi>=2017.4.17
  Downloading certifi-2020.6.20-py2.py3-none-any.whl (156 kB)
Collecting idna<2.7,>=2.5
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/8c7/309c718f94b3a/idna-2.6-py2.py3-none-any.whl (56 kB)
Collecting chardet<3.1.0,>=3.0.2
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/fc3/23ffcaeaed0e0/chardet-3.0.4-py2.py3-none-any.whl (133 kB)
Requirement already satisfied: packaging>=16.8 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->pyinstaller==3.2.1->-r requirements.txt (line 70)) (20.4)
Requirement already satisfied: appdirs>=1.4.0 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->pyinstaller==3.2.1->-r requirements.txt (line 70)) (1.4.4)
Requirement already satisfied: pyparsing>=2.0.2 in /usr/lib/bisque/lib/python2.7/site-packages (from packaging>=16.8->setuptools->pyinstaller==3.2.1->-r requirements.txt (line 70)) (2.4.7)
ERROR: linesman 0.3.2 has requirement networkx==1.7, but you'll have networkx 1.8 which is incompatible.
Installing collected packages: pytz, Babel, Beaker, FormEncode, Genshi, MarkupSafe, Mako, cssutils, WebHelpers, Minimatic, Paste, PasteDeploy, PasteScript, Paver, olefile, Pillow, Pygments, tempita, WebOb, WebError, decorator, WebTest, nose, simplejson, repoze.lru, Routes, Pylons, SQLAlchemy, PySqlite, ToscaWidgets, WebFlash, TurboGears2, TurboMail, alembic, altgraph, beautifulsoup4, futures, six, python-dateutil, docutils, jmespath, botocore, s3transfer, boto3, ecdsa, orderedmultidict, furl, future, funcsigs, filechunkio, gdata, httplib2, importlib, lxml, openslide-python, ordereddict, orderedset, pbr, pkginfo, ply, poster, psutil, prettytable, xmlrunner, python-irodsclient, python-multipart, pycrypto, python-mimeparse, pyinstaller, recaptcha-client, zope.interface, transaction, repoze.tm2, repoze.who, repoze.who-testutil, repoze.what, repoze.what-pylons, repoze.what.plugins.sql, repoze.who.plugins.sa, repoze.who-friendlyform, repoze.what-quickstart, urllib3, certifi, idna, chardet, requests, requests-toolbelt, shortuuid, tgext.registration2, tw.forms, tw.output, tw.recaptcha, unittest2, waitress, zope.sqlalchemy, networkx, pygraphviz, linesman, pyproj, geojson, pydicom, xlrd, numpy, numexpr, tables, pandas, mahotas, libtiff, psycopg2, configparser, backports.functools-lru-cache, isort, singledispatch, enum34, wrapt, lazy-object-proxy, astroid, mccabe, pylint, py, pytest, pluggy, tifffile
  Attempting uninstall: six
    Found existing installation: six 1.15.0
    Uninstalling six-1.15.0:
      Successfully uninstalled six-1.15.0
Successfully installed Babel-1.3 Beaker-1.6.4 FormEncode-1.3.1 Genshi-0.7 Mako-0.9.1 MarkupSafe-0.21 Minimatic-1.0.4 Paste-1.7.5.2 PasteDeploy-1.3.4 PasteScript-1.7.3 Paver-1.2.4 Pillow-4.2.1 PySqlite-2.8.3 Pygments-1.6 Pylons-1.0 Routes-2.0 SQLAlchemy-1.2.5 ToscaWidgets-0.9.12 TurboGears2-2.1.5 TurboMail-3.0.3 WebError-0.10.3 WebFlash-0.1a9 WebHelpers-1.3 WebOb-1.0.8 WebTest-1.1 alembic-0.6.3 altgraph-0.9 astroid-1.6.5 backports.functools-lru-cache-1.5 beautifulsoup4-4.3.2 boto3-1.4.8 botocore-1.8.2 certifi-2020.6.20 chardet-3.0.4 configparser-3.5.0 cssutils-1.0 decorator-3.4.0 docutils-0.13.1 ecdsa-0.11 enum34-1.1.6 filechunkio-1.6 funcsigs-1.0.2 furl-0.3.7 future-0.16.0 futures-3.0.5 gdata-2.0.18 geojson-1.0.9 httplib2-0.7.1-1 idna-2.6 importlib-1.0.3 isort-4.2.5 jmespath-0.9.2 lazy-object-proxy-1.3.1 libtiff-0.4.0 linesman-0.3.2 lxml-3.7.3 mahotas-1.4.3 mccabe-0.6.1 networkx-1.8 nose-1.3.1 numexpr-2.6.2 numpy-1.12.0 olefile-0.44 openslide-python-1.1.1 ordereddict-1.1 orderedmultidict-0.7.1 orderedset-2.0.1 pandas-0.19.2 pbr-0.6 pkginfo-1.2b1 pluggy-0.4.0 ply-3.4 poster-0.8.1 prettytable-0.7.2 psutil-4.3.0 psycopg2-2.6.1 py-1.4.34 pycrypto-2.6.1 pydicom-0.9.8 pygraphviz-1.3.1 pyinstaller-3.2.1 pylint-1.9.2 pyproj-1.9.3 pytest-3.1.1 python-dateutil-2.7.3 python-irodsclient-0.8.3 python-mimeparse-1.6.0 python-multipart-0.0.4 pytz-2013.9 recaptcha-client-1.0.6 repoze.lru-0.6 repoze.tm2-2.0 repoze.what-1.0.9 repoze.what-pylons-1.0 repoze.what-quickstart-1.0.9 repoze.what.plugins.sql-1.0.1 repoze.who-1.0.19 repoze.who-friendlyform-1.0.8 repoze.who-testutil-1.0.1 repoze.who.plugins.sa-1.0.1 requests-2.18.4 requests-toolbelt-0.6.2 s3transfer-0.1.10 shortuuid-0.4 simplejson-3.3.3 singledispatch-3.4.0.3 six-1.11.0 tables-3.4.2 tempita-0.5.2 tgext.registration2-0.5.2 tifffile-0.14.0 transaction-1.4.1 tw.forms-0.9.9 tw.output-0.5.0.dev20110906 tw.recaptcha-0.8 unittest2-0.5.1 urllib3-1.22 waitress-0.8.8 wrapt-1.10.10 xlrd-0.9.4 xmlrunner-1.7.7 zope.interface-4.1.0 zope.sqlalchemy-0.7.7
+ paver setup all
---> pavement.setup
installing all components from  set(['bqapi', 'bqengine', 'bqcore', 'bqserver', 'bqfeature'])
---> pavement.setup_developer
pip install -e ./bqapi
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. pip 21.0 will drop support for Python 2.7 in January 2021. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Looking in indexes: https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
Obtaining file:///source/bqapi
Requirement already satisfied: six in /usr/lib/bisque/lib/python2.7/site-packages (from bisque-api==0.5.9) (1.11.0)
Requirement already satisfied: requests>=2.4.1 in /usr/lib/bisque/lib/python2.7/site-packages (from bisque-api==0.5.9) (2.18.4)
Requirement already satisfied: requests_toolbelt>=0.6.2 in /usr/lib/bisque/lib/python2.7/site-packages (from bisque-api==0.5.9) (0.6.2)
Requirement already satisfied: urllib3<1.23,>=1.21.1 in /usr/lib/bisque/lib/python2.7/site-packages (from requests>=2.4.1->bisque-api==0.5.9) (1.22)
Requirement already satisfied: certifi>=2017.4.17 in /usr/lib/bisque/lib/python2.7/site-packages (from requests>=2.4.1->bisque-api==0.5.9) (2020.6.20)
Requirement already satisfied: idna<2.7,>=2.5 in /usr/lib/bisque/lib/python2.7/site-packages (from requests>=2.4.1->bisque-api==0.5.9) (2.6)
Requirement already satisfied: chardet<3.1.0,>=3.0.2 in /usr/lib/bisque/lib/python2.7/site-packages (from requests>=2.4.1->bisque-api==0.5.9) (3.0.4)
Installing collected packages: bisque-api
  Running setup.py develop for bisque-api
Successfully installed bisque-api
pip install -e ./bqengine
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. pip 21.0 will drop support for Python 2.7 in January 2021. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Looking in indexes: https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
Obtaining file:///source/bqengine
Requirement already satisfied: httplib2 in /usr/lib/bisque/lib/python2.7/site-packages (from bqengine==0.5.9) (0.7.1-1)
Requirement already satisfied: pyinstaller in /usr/lib/bisque/lib/python2.7/site-packages (from bqengine==0.5.9) (3.2.1)
Requirement already satisfied: setuptools in /usr/lib/bisque/lib/python2.7/site-packages (from pyinstaller->bqengine==0.5.9) (34.4.1)
Requirement already satisfied: packaging>=16.8 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->pyinstaller->bqengine==0.5.9) (20.4)
Requirement already satisfied: six>=1.6.0 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->pyinstaller->bqengine==0.5.9) (1.11.0)
Requirement already satisfied: appdirs>=1.4.0 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->pyinstaller->bqengine==0.5.9) (1.4.4)
Requirement already satisfied: pyparsing>=2.0.2 in /usr/lib/bisque/lib/python2.7/site-packages (from packaging>=16.8->setuptools->pyinstaller->bqengine==0.5.9) (2.4.7)
Installing collected packages: bqengine
  Running setup.py develop for bqengine
Successfully installed bqengine
pip install -e ./bqcore
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. pip 21.0 will drop support for Python 2.7 in January 2021. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Looking in indexes: https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
Obtaining file:///source/bqcore
Requirement already satisfied: Pylons==1.0 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.0)
Requirement already satisfied: WebOb==1.0.8 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.0.8)
Requirement already satisfied: decorator>=3.3 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (3.4.0)
Requirement already satisfied: TurboGears2==2.1.5 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (2.1.5)
Requirement already satisfied: Genshi in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (0.7)
Requirement already satisfied: zope.sqlalchemy>=0.4 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (0.7.7)
Requirement already satisfied: repoze.tm2>=1.0a5 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (2.0)
Requirement already satisfied: SQLAlchemy in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.2.5)
Requirement already satisfied: Alembic in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (0.6.3)
Requirement already satisfied: repoze.what-quickstart in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.0.9)
Requirement already satisfied: repoze.what>=1.0.8 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.0.9)
Requirement already satisfied: repoze.who-friendlyform>=1.0.4 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.0.8)
Requirement already satisfied: repoze.what-pylons>=1.0 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.0)
Requirement already satisfied: repoze.what.plugins.sql in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.0.1)
Requirement already satisfied: repoze.who<=1.99 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (1.0.19)
Requirement already satisfied: tw.forms in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (0.9.9)
Requirement already satisfied: lxml in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (3.7.3)
Requirement already satisfied: poster in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (0.8.1)
Requirement already satisfied: linesman in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (0.3.2)
Requirement already satisfied: shortuuid in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore==0.5.9) (0.4)
Requirement already satisfied: PasteDeploy>=1.3.3 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (1.3.4)
Requirement already satisfied: WebHelpers>=0.6.4 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (1.3)
Requirement already satisfied: WebError>=0.10.1 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (0.10.3)
Requirement already satisfied: Mako>=0.2.4 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (0.9.1)
Requirement already satisfied: WebTest>=1.1 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (1.1)
Requirement already satisfied: nose>=0.10.4 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (1.3.1)
Requirement already satisfied: Tempita>=0.2 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (0.5.2)
Requirement already satisfied: FormEncode>=1.2.1 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (1.3.1)
Requirement already satisfied: PasteScript>=1.7.3 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (1.7.3)
Requirement already satisfied: Beaker>=1.3dev in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (1.6.4)
Requirement already satisfied: simplejson>=2.0.8 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (3.3.3)
Requirement already satisfied: Paste>=1.7.2 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (1.7.5.2)
Requirement already satisfied: Routes>=1.12 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore==0.5.9) (2.0)
Requirement already satisfied: WebFlash>=0.1a8 in /usr/lib/bisque/lib/python2.7/site-packages (from TurboGears2==2.1.5->bqcore==0.5.9) (0.1a9)
Requirement already satisfied: Babel in /usr/lib/bisque/lib/python2.7/site-packages (from TurboGears2==2.1.5->bqcore==0.5.9) (1.3)
Requirement already satisfied: setuptools in /usr/lib/bisque/lib/python2.7/site-packages (from zope.sqlalchemy>=0.4->bqcore==0.5.9) (34.4.1)
Requirement already satisfied: zope.interface>=3.6.0 in /usr/lib/bisque/lib/python2.7/site-packages (from zope.sqlalchemy>=0.4->bqcore==0.5.9) (4.1.0)
Requirement already satisfied: transaction in /usr/lib/bisque/lib/python2.7/site-packages (from zope.sqlalchemy>=0.4->bqcore==0.5.9) (1.4.1)
Requirement already satisfied: repoze.who.plugins.sa>=1.0.1 in /usr/lib/bisque/lib/python2.7/site-packages (from repoze.what-quickstart->bqcore==0.5.9) (1.0.1)
Requirement already satisfied: repoze.who-testutil>=1.0b2 in /usr/lib/bisque/lib/python2.7/site-packages (from repoze.what>=1.0.8->bqcore==0.5.9) (1.0.1)
Requirement already satisfied: ToscaWidgets>0.9.7 in /usr/lib/bisque/lib/python2.7/site-packages (from tw.forms->bqcore==0.5.9) (0.9.12)
Collecting networkx==1.7
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/132/eab4411611abf/networkx-1.7-cp27-none-any.whl (880 kB)
Requirement already satisfied: pygraphviz in /usr/lib/bisque/lib/python2.7/site-packages (from linesman->bqcore==0.5.9) (1.3.1)
Requirement already satisfied: pillow in /usr/lib/bisque/lib/python2.7/site-packages (from linesman->bqcore==0.5.9) (4.2.1)
Requirement already satisfied: MarkupSafe>=0.9.2 in /usr/lib/bisque/lib/python2.7/site-packages (from WebHelpers>=0.6.4->Pylons==1.0->bqcore==0.5.9) (0.21)
Requirement already satisfied: Pygments in /usr/lib/bisque/lib/python2.7/site-packages (from WebError>=0.10.1->Pylons==1.0->bqcore==0.5.9) (1.6)
Requirement already satisfied: repoze.lru>=0.3 in /usr/lib/bisque/lib/python2.7/site-packages (from Routes>=1.12->Pylons==1.0->bqcore==0.5.9) (0.6)
Requirement already satisfied: pytz>=0a in /usr/lib/bisque/lib/python2.7/site-packages (from Babel->TurboGears2==2.1.5->bqcore==0.5.9) (2013.9)
Requirement already satisfied: packaging>=16.8 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->zope.sqlalchemy>=0.4->bqcore==0.5.9) (20.4)
Requirement already satisfied: six>=1.6.0 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->zope.sqlalchemy>=0.4->bqcore==0.5.9) (1.11.0)
Requirement already satisfied: appdirs>=1.4.0 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->zope.sqlalchemy>=0.4->bqcore==0.5.9) (1.4.4)
Requirement already satisfied: olefile in /usr/lib/bisque/lib/python2.7/site-packages (from pillow->linesman->bqcore==0.5.9) (0.44)
Requirement already satisfied: pyparsing>=2.0.2 in /usr/lib/bisque/lib/python2.7/site-packages (from packaging>=16.8->setuptools->zope.sqlalchemy>=0.4->bqcore==0.5.9) (2.4.7)
Installing collected packages: bqcore, networkx
  Running setup.py develop for bqcore
  Attempting uninstall: networkx
    Found existing installation: networkx 1.8
    Uninstalling networkx-1.8:
      Successfully uninstalled networkx-1.8
Successfully installed bqcore networkx-1.7
pip install -e ./bqserver
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. pip 21.0 will drop support for Python 2.7 in January 2021. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Looking in indexes: https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
Obtaining file:///source/bqserver
Requirement already satisfied: ply in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (3.4)
Requirement already satisfied: gdata in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (2.0.18)
Requirement already satisfied: Turbomail in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (3.0.3)
Requirement already satisfied: genshi in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (0.7)
Collecting boto
  Downloading https://biodev.ece.ucsb.edu/py/bisque/prod/%2Bf/13b/e844158d1bd80/boto-2.48.0-py2.py3-none-any.whl (1.4 MB)
Requirement already satisfied: numpy in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (1.12.0)
Requirement already satisfied: ordereddict in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (1.1)
Requirement already satisfied: tw.recaptcha in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (0.8)
Requirement already satisfied: tgext.registration2 in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (0.5.2)
Requirement already satisfied: tw.output in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (0.5.0.dev20110906)
Requirement already satisfied: furl in /usr/lib/bisque/lib/python2.7/site-packages (from bqserver==0.5.9) (0.3.7)
Requirement already satisfied: recaptcha-client in /usr/lib/bisque/lib/python2.7/site-packages (from tw.recaptcha->bqserver==0.5.9) (1.0.6)
Requirement already satisfied: ToscaWidgets>0.8 in /usr/lib/bisque/lib/python2.7/site-packages (from tw.recaptcha->bqserver==0.5.9) (0.9.12)
Requirement already satisfied: tw.forms in /usr/lib/bisque/lib/python2.7/site-packages (from tw.output->bqserver==0.5.9) (0.9.9)
Requirement already satisfied: orderedmultidict>=0.7.1 in /usr/lib/bisque/lib/python2.7/site-packages (from furl->bqserver==0.5.9) (0.7.1)
Requirement already satisfied: WebOb in /usr/lib/bisque/lib/python2.7/site-packages (from ToscaWidgets>0.8->tw.recaptcha->bqserver==0.5.9) (1.0.8)
Requirement already satisfied: FormEncode>=1.1 in /usr/lib/bisque/lib/python2.7/site-packages (from tw.forms->tw.output->bqserver==0.5.9) (1.3.1)
Installing collected packages: boto, bqserver
  Running setup.py develop for bqserver
Successfully installed boto-2.48.0 bqserver
pip install -e ./bqfeature
DEPRECATION: Python 2.7 reached the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 is no longer maintained. pip 21.0 will drop support for Python 2.7 in January 2021. More details about Python 2 support in pip, can be found at https://pip.pypa.io/en/latest/development/release-process/#python-2-support
Looking in indexes: https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
Obtaining file:///source/bqfeature
Requirement already satisfied: importlib in /usr/lib/bisque/lib/python2.7/site-packages (from bqfeature==0.5.9) (1.0.3)
Requirement already satisfied: bqcore in ./bqcore (from bqfeature==0.5.9) (0.5.9)
Requirement already satisfied: numpy in /usr/lib/bisque/lib/python2.7/site-packages (from bqfeature==0.5.9) (1.12.0)
Requirement already satisfied: pillow in /usr/lib/bisque/lib/python2.7/site-packages (from bqfeature==0.5.9) (4.2.1)
Requirement already satisfied: mahotas in /usr/lib/bisque/lib/python2.7/site-packages (from bqfeature==0.5.9) (1.4.3)
Requirement already satisfied: tables in /usr/lib/bisque/lib/python2.7/site-packages (from bqfeature==0.5.9) (3.4.2)
Requirement already satisfied: numexpr in /usr/lib/bisque/lib/python2.7/site-packages (from bqfeature==0.5.9) (2.6.2)
Requirement already satisfied: libtiff==0.4.0 in /usr/lib/bisque/lib/python2.7/site-packages (from bqfeature==0.5.9) (0.4.0)
Requirement already satisfied: Pylons==1.0 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.0)
Requirement already satisfied: WebOb==1.0.8 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.0.8)
Requirement already satisfied: decorator>=3.3 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (3.4.0)
Requirement already satisfied: TurboGears2==2.1.5 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (2.1.5)
Requirement already satisfied: Genshi in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (0.7)
Requirement already satisfied: zope.sqlalchemy>=0.4 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (0.7.7)
Requirement already satisfied: repoze.tm2>=1.0a5 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (2.0)
Requirement already satisfied: SQLAlchemy in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.2.5)
Requirement already satisfied: Alembic in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (0.6.3)
Requirement already satisfied: repoze.what-quickstart in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.0.9)
Requirement already satisfied: repoze.what>=1.0.8 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.0.9)
Requirement already satisfied: repoze.who-friendlyform>=1.0.4 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.0.8)
Requirement already satisfied: repoze.what-pylons>=1.0 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.0)
Requirement already satisfied: repoze.what.plugins.sql in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.0.1)
Requirement already satisfied: repoze.who<=1.99 in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (1.0.19)
Requirement already satisfied: tw.forms in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (0.9.9)
Requirement already satisfied: lxml in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (3.7.3)
Requirement already satisfied: poster in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (0.8.1)
Requirement already satisfied: linesman in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (0.3.2)
Requirement already satisfied: shortuuid in /usr/lib/bisque/lib/python2.7/site-packages (from bqcore->bqfeature==0.5.9) (0.4)
Requirement already satisfied: olefile in /usr/lib/bisque/lib/python2.7/site-packages (from pillow->bqfeature==0.5.9) (0.44)
Requirement already satisfied: six>=1.9.0 in /usr/lib/bisque/lib/python2.7/site-packages (from tables->bqfeature==0.5.9) (1.11.0)
Requirement already satisfied: PasteDeploy>=1.3.3 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (1.3.4)
Requirement already satisfied: WebHelpers>=0.6.4 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (1.3)
Requirement already satisfied: WebError>=0.10.1 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (0.10.3)
Requirement already satisfied: Mako>=0.2.4 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (0.9.1)
Requirement already satisfied: WebTest>=1.1 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (1.1)
Requirement already satisfied: nose>=0.10.4 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (1.3.1)
Requirement already satisfied: Tempita>=0.2 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (0.5.2)
Requirement already satisfied: FormEncode>=1.2.1 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (1.3.1)
Requirement already satisfied: PasteScript>=1.7.3 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (1.7.3)
Requirement already satisfied: Beaker>=1.3dev in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (1.6.4)
Requirement already satisfied: simplejson>=2.0.8 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (3.3.3)
Requirement already satisfied: Paste>=1.7.2 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (1.7.5.2)
Requirement already satisfied: Routes>=1.12 in /usr/lib/bisque/lib/python2.7/site-packages (from Pylons==1.0->bqcore->bqfeature==0.5.9) (2.0)
Requirement already satisfied: WebFlash>=0.1a8 in /usr/lib/bisque/lib/python2.7/site-packages (from TurboGears2==2.1.5->bqcore->bqfeature==0.5.9) (0.1a9)
Requirement already satisfied: Babel in /usr/lib/bisque/lib/python2.7/site-packages (from TurboGears2==2.1.5->bqcore->bqfeature==0.5.9) (1.3)
Requirement already satisfied: setuptools in /usr/lib/bisque/lib/python2.7/site-packages (from zope.sqlalchemy>=0.4->bqcore->bqfeature==0.5.9) (34.4.1)
Requirement already satisfied: zope.interface>=3.6.0 in /usr/lib/bisque/lib/python2.7/site-packages (from zope.sqlalchemy>=0.4->bqcore->bqfeature==0.5.9) (4.1.0)
Requirement already satisfied: transaction in /usr/lib/bisque/lib/python2.7/site-packages (from zope.sqlalchemy>=0.4->bqcore->bqfeature==0.5.9) (1.4.1)
Requirement already satisfied: repoze.who.plugins.sa>=1.0.1 in /usr/lib/bisque/lib/python2.7/site-packages (from repoze.what-quickstart->bqcore->bqfeature==0.5.9) (1.0.1)
Requirement already satisfied: repoze.who-testutil>=1.0b2 in /usr/lib/bisque/lib/python2.7/site-packages (from repoze.what>=1.0.8->bqcore->bqfeature==0.5.9) (1.0.1)
Requirement already satisfied: ToscaWidgets>0.9.7 in /usr/lib/bisque/lib/python2.7/site-packages (from tw.forms->bqcore->bqfeature==0.5.9) (0.9.12)
Requirement already satisfied: networkx==1.7 in /usr/lib/bisque/lib/python2.7/site-packages (from linesman->bqcore->bqfeature==0.5.9) (1.7)
Requirement already satisfied: pygraphviz in /usr/lib/bisque/lib/python2.7/site-packages (from linesman->bqcore->bqfeature==0.5.9) (1.3.1)
Requirement already satisfied: MarkupSafe>=0.9.2 in /usr/lib/bisque/lib/python2.7/site-packages (from WebHelpers>=0.6.4->Pylons==1.0->bqcore->bqfeature==0.5.9) (0.21)
Requirement already satisfied: Pygments in /usr/lib/bisque/lib/python2.7/site-packages (from WebError>=0.10.1->Pylons==1.0->bqcore->bqfeature==0.5.9) (1.6)
Requirement already satisfied: repoze.lru>=0.3 in /usr/lib/bisque/lib/python2.7/site-packages (from Routes>=1.12->Pylons==1.0->bqcore->bqfeature==0.5.9) (0.6)
Requirement already satisfied: pytz>=0a in /usr/lib/bisque/lib/python2.7/site-packages (from Babel->TurboGears2==2.1.5->bqcore->bqfeature==0.5.9) (2013.9)
Requirement already satisfied: packaging>=16.8 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->zope.sqlalchemy>=0.4->bqcore->bqfeature==0.5.9) (20.4)
Requirement already satisfied: appdirs>=1.4.0 in /usr/lib/bisque/lib/python2.7/site-packages (from setuptools->zope.sqlalchemy>=0.4->bqcore->bqfeature==0.5.9) (1.4.4)
Requirement already satisfied: pyparsing>=2.0.2 in /usr/lib/bisque/lib/python2.7/site-packages (from packaging>=16.8->setuptools->zope.sqlalchemy>=0.4->bqcore->bqfeature==0.5.9) (2.4.7)
Installing collected packages: bqfeature
  Running setup.py develop for bqfeature
Successfully installed bqfeature

Now run:
bq-admin setup 
+ bq-admin setup -y install
INFO:root:Generating grammar tables from /usr/lib/python2.7/lib2to3/Grammar.txt
INFO:root:Generating grammar tables from /usr/lib/python2.7/lib2to3/PatternGrammar.txt
INFO:bq.image_service.server:Available converters: openslide (1.1.1), imgcnv (2.4.3), ImarisConvert (8.0.2), bioformats (5.1.1)
WARNING:bq.features:Failed to import: MyFeatures reason No module named scipy.signal 
WARNING:bq.features:Failed to import: ScikitImage reason No module named skimage.feature 
WARNING:bq.util.io_misc:Could not remove "./public/core/css/all_css.css"
WARNING:bq.util.io_misc:Could not remove "./public/core/js/all_js.js"
INFO:minimatic:Combined -> ./public/core/css/all_css.css:
INFO:minimatic:Combined -> ./public/core/js/all_js.js:
Creating ./public
Making  ./public/engine_service
Making  ./public/core
Making  ./public/data_service
Making  ./public/ingest_service
Making  ./public/stats
Making  ./public/graph
Making  ./public/module_service
Making  ./public/client_service
Making  ./public/image_service
Making  ./public/dataset_service
Making  ./public/export
Problem loading registration = bq.registration.controllers.registration_service: 'User'
Making  ./public/usage
Making  ./public/import
Generating '/usr/lib/bisque/local/lib/python2.7/site-packages/libtiff/tiff_h_4_0_6.py'

Generating packaged JS and CSS files

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

    
Beginning install of ['bisque', 'engine'] with ['install'] 
CALLING  <function install_external_binaries at 0x7f5c20939aa0>
Matched section Linux-64bit-*
Fetching http://biodev.ece.ucsb.edu/binaries/depot/06B0FFFCAFA78EBE6843BDAADB14939554A85B66-ext-4.2.1-gpl.zip
Fetching http://biodev.ece.ucsb.edu/binaries/depot/FD36E37414682D1218295356A7EE14FE5695B4D5-bftools.5.1.1.zip
Fetching http://biodev.ece.ucsb.edu/binaries/depot/511B5E84692B123A89576086201B793C93096A74-libmbgl-linux-64-large.a
Fetching http://biodev.ece.ucsb.edu/binaries/depot/7B92AE8430943F2EC4C51AAC207FD41C39627584-feature_extractors-Linux-64bit.zip
Fetching http://biodev.ece.ucsb.edu/binaries/depot/9E7E137FCBA36D1CAC6189C5CE2AE82B079BC5B8-imarisconvert_glibc2.11.tar.gz
Fetching http://biodev.ece.ucsb.edu/binaries/depot/E672BCA974C87F22D4A72BFDF15C79AEDFA0A979-opencv-2.4.6-Linux-64bit.zip
CALLING  <function install_dependencies at 0x7f5c20939c08>
Unpacking ./external/extjs.zip into bqcore/bq/core/public
2.4.3

Found imgcnv version 2.4.3


Imgcnv is installed and no-precompiled version exists. Using installed version
Unpacking ./external/ImarisConvert.tar.gz into /usr/lib/bisque/bin
No pre-compiled version of openslide exists for your system
Please visit our mailing list https://groups.google.com/forum/#!forum/bisque-bioimage for help
CALLING  <function install_features at 0x7f5c20939e60>
Unpacking ./external/feature_extractors.zip into ./bqfeature/bq
To enable the feature service to read OME-bigtiff for feature extraction install
        libtiff4
        For Debian use the command apt-get install libtiff5-dev
        
Extracted opencv-2.4.6/python2.7/cv.py -> /usr/lib/bisque/lib/python2.7/site-packages/cv.py
Extracted opencv-2.4.6/python2.7/cv2.so -> /usr/lib/bisque/lib/python2.7/site-packages/cv2.so
CALLING  <function install_plugins at 0x7f5c209389b0>
INFO 'svn'not found: cannot fetch source repositories with svn 
INSTALL PLGINS  ['./plugins']
Checking ./plugins for modules
CALLING  <function install_public_static at 0x7f5c209396e0>
+ rm -rf external tools docs modules/UNPORTED
+ pwd
+ /bin/ls -l
/source
total 204
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
+ /bin/ls -l /bin/
total 7708
-rwxr-xr-x 1 root root 1037528 May 16  2017 bash
-rwxr-xr-x 3 root root   31352 Jul  4  2019 bunzip2
-rwxr-xr-x 3 root root   31352 Jul  4  2019 bzcat
lrwxrwxrwx 1 root root       6 Jul  4  2019 bzcmp -> bzdiff
-rwxr-xr-x 1 root root    2140 Jul  4  2019 bzdiff
lrwxrwxrwx 1 root root       6 Jul  4  2019 bzegrep -> bzgrep
-rwxr-xr-x 1 root root    4877 Jul  4  2019 bzexe
lrwxrwxrwx 1 root root       6 Jul  4  2019 bzfgrep -> bzgrep
-rwxr-xr-x 1 root root    3642 Jul  4  2019 bzgrep
-rwxr-xr-x 3 root root   31352 Jul  4  2019 bzip2
-rwxr-xr-x 1 root root   14672 Jul  4  2019 bzip2recover
lrwxrwxrwx 1 root root       6 Jul  4  2019 bzless -> bzmore
-rwxr-xr-x 1 root root    1297 Jul  4  2019 bzmore
-rwxr-xr-x 1 root root   52080 Mar  2  2017 cat
-rwxr-xr-x 1 root root   60272 Mar  2  2017 chgrp
-rwxr-xr-x 1 root root   56112 Mar  2  2017 chmod
-rwxr-xr-x 1 root root   64368 Mar  2  2017 chown
-rwxr-xr-x 1 root root  151024 Mar  2  2017 cp
-rwxr-xr-x 1 root root  154072 Feb 17  2016 dash
-rwxr-xr-x 1 root root   68464 Mar  2  2017 date
-rwxr-xr-x 1 root root   72632 Mar  2  2017 dd
-rwxr-xr-x 1 root root   97912 Mar  2  2017 df
-rwxr-xr-x 1 root root  126584 Mar  2  2017 dir
-rwxr-xr-x 1 root root   60680 Nov 30  2017 dmesg
lrwxrwxrwx 1 root root       8 Nov 24  2015 dnsdomainname -> hostname
lrwxrwxrwx 1 root root       8 Nov 24  2015 domainname -> hostname
-rwxr-xr-x 1 root root   31376 Mar  2  2017 echo
-rwxr-xr-x 1 root root      28 Apr 29  2016 egrep
-rwxr-xr-x 1 root root   27280 Mar  2  2017 false
-rwxr-xr-x 1 root root      28 Apr 29  2016 fgrep
-rwxr-xr-x 1 root root   49576 Nov 30  2017 findmnt
-rwxr-xr-x 1 root root  211224 Apr 29  2016 grep
-rwxr-xr-x 2 root root    2301 Oct 27  2014 gunzip
-rwxr-xr-x 1 root root    5927 Oct 27  2014 gzexe
-rwxr-xr-x 1 root root   98240 Oct 27  2014 gzip
-rwxr-xr-x 1 root root   14800 Nov 24  2015 hostname
-rwxr-xr-x 1 root root  498936 Mar  8  2018 journalctl
-rwxr-xr-x 1 root root   23152 May 14  2018 kill
-rwxr-xr-x 1 root root  170728 Apr  5  2017 less
-rwxr-xr-x 1 root root   10256 Apr  5  2017 lessecho
lrwxrwxrwx 1 root root       8 Apr  5  2017 lessfile -> lesspipe
-rwxr-xr-x 1 root root   19824 Apr  5  2017 lesskey
-rwxr-xr-x 1 root root    7764 Apr  5  2017 lesspipe
-rwxr-xr-x 1 root root   56152 Mar  2  2017 ln
-rwxr-xr-x 1 root root   48128 May 16  2017 login
-rwxr-xr-x 1 root root  453848 Mar  8  2018 loginctl
-rwxr-xr-x 1 root root  126584 Mar  2  2017 ls
-rwxr-xr-x 1 root root   77280 Nov 30  2017 lsblk
-rwxr-xr-x 1 root root   76848 Mar  2  2017 mkdir
-rwxr-xr-x 1 root root   64496 Mar  2  2017 mknod
-rwxr-xr-x 1 root root   39728 Mar  2  2017 mktemp
-rwxr-xr-x 1 root root   39768 Nov 30  2017 more
-rwsr-xr-x 1 root root   40152 Nov 30  2017 mount
-rwxr-xr-x 1 root root   14768 Nov 30  2017 mountpoint
-rwxr-xr-x 1 root root  130488 Mar  2  2017 mv
-rwxr-xr-x 1 root root  678496 Mar  8  2018 networkctl
lrwxrwxrwx 1 root root       8 Nov 24  2015 nisdomainname -> hostname
lrwxrwxrwx 1 root root      14 Feb  5  2016 pidof -> /sbin/killall5
-rwxr-xr-x 1 root root   97408 May 14  2018 ps
-rwxr-xr-x 1 root root   31472 Mar  2  2017 pwd
lrwxrwxrwx 1 root root       4 May 16  2017 rbash -> bash
-rwxr-xr-x 1 root root   39632 Mar  2  2017 readlink
-rwxr-xr-x 1 root root   60272 Mar  2  2017 rm
-rwxr-xr-x 1 root root   39632 Mar  2  2017 rmdir
-rwxr-xr-x 1 root root   19320 Jan 26  2016 run-parts
-rwxr-xr-x 1 root root   73424 Feb 12  2016 sed
lrwxrwxrwx 1 root root       4 Feb 17  2016 sh -> dash
lrwxrwxrwx 1 root root       4 Feb 17  2016 sh.distrib -> dash
-rwxr-xr-x 1 root root   31408 Mar  2  2017 sleep
-rwxr-xr-x 1 root root   72496 Mar  2  2017 stty
-rwsr-xr-x 1 root root   40128 May 16  2017 su
-rwxr-xr-x 1 root root   31408 Mar  2  2017 sync
-rwxr-xr-x 1 root root  659848 Mar  8  2018 systemctl
lrwxrwxrwx 1 root root      20 Mar  8  2018 systemd -> /lib/systemd/systemd
-rwxr-xr-x 1 root root   51656 Mar  8  2018 systemd-ask-password
-rwxr-xr-x 1 root root   39344 Mar  8  2018 systemd-escape
-rwxr-xr-x 1 root root  281840 Mar  8  2018 systemd-inhibit
-rwxr-xr-x 1 root root   47544 Mar  8  2018 systemd-machine-id-setup
-rwxr-xr-x 1 root root   35248 Mar  8  2018 systemd-notify
-rwxr-xr-x 1 root root  133704 Mar  8  2018 systemd-tmpfiles
-rwxr-xr-x 1 root root   68032 Mar  8  2018 systemd-tty-ask-password-agent
-rwxr-xr-x 1 root root   23144 Nov 30  2017 tailf
-rwxr-xr-x 1 root root  383632 Nov 17  2016 tar
-rwxr-xr-x 1 root root   10416 Jan 26  2016 tempfile
-rwxr-xr-x 1 root root   64432 Mar  2  2017 touch
-rwxr-xr-x 1 root root   27280 Mar  2  2017 true
-rwsr-xr-x 1 root root   27608 Nov 30  2017 umount
-rwxr-xr-x 1 root root   31440 Mar  2  2017 uname
-rwxr-xr-x 2 root root    2301 Oct 27  2014 uncompress
-rwxr-xr-x 1 root root  126584 Mar  2  2017 vdir
-rwxr-xr-x 1 root root   31376 Nov 30  2017 wdctl
-rwxr-xr-x 1 root root     946 Jan 26  2016 which
lrwxrwxrwx 1 root root       8 Nov 24  2015 ypdomainname -> hostname
-rwxr-xr-x 1 root root    1937 Oct 27  2014 zcat
-rwxr-xr-x 1 root root    1777 Oct 27  2014 zcmp
-rwxr-xr-x 1 root root    5764 Oct 27  2014 zdiff
-rwxr-xr-x 1 root root     140 Oct 27  2014 zegrep
-rwxr-xr-x 1 root root     140 Oct 27  2014 zfgrep
-rwxr-xr-x 1 root root    2131 Oct 27  2014 zforce
-rwxr-xr-x 1 root root    5938 Oct 27  2014 zgrep
-rwxr-xr-x 1 root root    2037 Oct 27  2014 zless
-rwxr-xr-x 1 root root    1910 Oct 27  2014 zmore
-rwxr-xr-x 1 root root    5047 Oct 27  2014 znew
+ echo DONE
DONE
+ mv /builder//build-scripts.d/20-build-bisque.sh /builder//build-scripts.d/20-build-bisque.sh.finished
+ '[' 0 -ne 0 ']'
+ exit 0
Removing intermediate container 5cf247e53f15
 ---> 3a997513e2de
Step 23/24 : ENTRYPOINT [ "/builder/run-bisque.sh"]
 ---> Running in e2536fd2e6cd
Removing intermediate container e2536fd2e6cd
 ---> 393cf52d02c7
Step 24/24 : CMD [ "bootstrap","start"]
 ---> Running in 336dc25d1607
Removing intermediate container 336dc25d1607
 ---> da324640579f
Successfully built da324640579f
Successfully tagged bisque-developer-beta:0.7-broccolli
```
