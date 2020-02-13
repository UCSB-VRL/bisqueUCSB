FROM ubuntu
ENV DEBIAN_FRONTEND none
RUN apt-get update -y && apt-get install -y \
   libglib2.0 \
   libxext6 \
   libglu1-mesa-dev
ADD http://dream3d.bluequartz.net/binaries/previous/DREAM3D-6.2.327-Linux-x86_64.tar.gz /
RUN tar -xzf /DREAM3D-6.2.327-Linux-x86_64.tar.gz
RUN mv /DREAM3D-6.2.327-Linux-x86_64 /dream3d
# dream3d searches for Plugins relative to the bin folder (on Linux); maybe a bug??
RUN ln -s /dream3d/Plugins /dream3d/bin
WORKDIR /module
COPY Dream3D /module/
COPY pydist /module/pydist/
ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
CMD  [ "Dream3D" ]
