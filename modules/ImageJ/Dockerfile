FROM ubuntu
ENV DEBIAN_FRONTEND none
RUN apt-get update -y && apt-get install -y \
   xvfb \
   wget \
   zip
RUN apt-get install -y libxrender-dev libxtst-dev
# install Fiji

WORKDIR /module
RUN wget -O /module/fiji.zip http://downloads.imagej.net/fiji/latest/fiji-linux64.zip
RUN unzip fiji.zip
RUN rm fiji.zip

WORKDIR /module/workdir

COPY ImageJ /module/workdir
COPY pydist /module/workdir/pydist/

#RUN mkdir /module/workdir

ENV PATH /module/Fiji.app:/module/workdir:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN ImageJ-linux64 --update update
CMD  [ "ImageJ" ]
