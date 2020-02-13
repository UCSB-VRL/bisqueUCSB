FROM debian:jessie
#FROM phusion/baseimage
MAINTAINER Kris Kvilekval<kris@cs.ucsb.edu>
RUN apt-get update && apt-get install -yq python  unzip wget libxext6 libxt6

ENV MCR_URL  http://www.mathworks.com/supportfiles/downloads/R2015b/deployment_files/R2015b/installers/glnxa64/MCR_R2015b_glnxa64_installer.zip

ADD input.txt /mcr-install/input.txt
# Fetch locally
#COPY MCR_R2015b_glnxa64_installer.zip /mcr-install/

RUN cd /mcr-install && \
    wget -nv $MCR_URL && \
    unzip MCR_R2015b_glnxa64_installer.zip && \
    mkdir /opt/mcr && \
    ./install -inputFile input.txt && \
    cd / && \
    rm -rf mcr-install

ENV MATLAB_HOME /opt/mcr/v90
ENV LD_LIBRARY_PATH $MATLAB_HOME/runtime/glnxa64:\
$MATLAB_HOME/bin/glnxa64:\
$MATLAB_HOME/sys/os/glnxa64:\
$MATLAB_HOME/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:\
$MATLAB_HOME/sys/java/jre/glnxa64/jre/lib/amd64/server:\
$MATLAB_HOME/sys/java/jre/glnxa64/jre/lib/amd64:
ENV XAPPLRESDIR=$MATLAB_HOME/X11/app-defaults
ENV PATH /module:$PATH
COPY cacerts /opt/mcr/v90/sys/java/jre/glnxa64/jre/lib/security/cacerts
VOLUME /module
WORKDIR /module
#CMD ["/sbin/my_init"]
CMD [ "bash" ]
