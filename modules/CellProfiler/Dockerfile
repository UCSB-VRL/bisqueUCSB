FROM ubuntu:14.04
#FROM debian:jessie
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update                                            && \
    apt-get -y upgrade                                           && \
    apt-get -y install                                              \
      cython                                                        \
      git                                                           \
      openjdk-7-jdk                                                 \
      python-h5py                                                   \
      python-imaging                                                \
      python-libtiff                                                \
      python-lxml                                                   \
      python-matplotlib                                             \
      python-mysqldb                                                \
      python-numpy                                                  \
      python-pandas                                                 \
      python-pip                                                    \
      python-scipy                                                  \
      python-skimage                                                \
      python-sklearn                                                \
      python-vigra                                                  \
      python-wxgtk2.8                                               \
      python-zmq                                                    \
      libmysqlclient-dev                                            \
      libhdf5-dev                                                   \
      xvfb                                                          \
      libxml2
RUN pip install --upgrade cython
RUN pip install dask
RUN pip install --upgrade six

WORKDIR /module
# was: WORKDIR /usr/local/src
RUN git clone https://github.com/CellProfiler/CellProfiler.git
#RUN cd CellProfiler && git checkout 2.1.1
RUN cd CellProfiler && git checkout 2.2.0

WORKDIR /module/CellProfiler
ENV  JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64
ENV  LD_LIBRARY_PATH /usr/lib/jvm/java-7-openjdk-amd64/jre/lib/amd64/server:/usr/lib/jvm/java-7-openjdk-amd64:/usr/lib/jvm/java-7-openjdk-amd64/include
#RUN pip install                                                     \
#  --requirement                                                     \
#    requirements.txt
RUN python setup.py install
RUN pip install --editable .
RUN yes | pip uninstall prokaryote
RUN pip install prokaryote==1.0.11
RUN pip install javabridge
RUN pip install centrosome
RUN pip install bioformats
RUN pip install python-bioformats
RUN pip install                                                     \
  --editable                                                        \
    git+https://github.com/CellH5/cellh5.git#egg=cellh5             \
  --upgrade
#RUN python external_dependencies.py
RUN  echo "def fetch_external_dependencies(overwrite=False): \n\
          return \n\
     " >> external_dependencies.py

#RUN python CellProfiler.py --build-and-exit

COPY CellProfiler /module/CellProfiler/
COPY pydist /module/CellProfiler/pydist/

#RUN mv /module/CellProfiler/pydist/CellProfiler/libxml2.so.2 /module/CellProfiler/pydist/CellProfiler/libxml2.so.2.bak
#RUN ln -s /usr/lib/x86_64-linux-gnu/libxml2.so.2 /module/CellProfiler/pydist/CellProfiler
RUN mkdir /module/CellProfiler/workdir

RUN rm -rf /module/CellProfiler/.git

ENV PATH /module/CellProfiler:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

CMD  [ "CellProfiler" ]