FROM ubuntu:16.04

LABEL maintainer="amil@ucsb.edu"
LABEL build_date="2025-03-01"

RUN echo "Install Bisque System"

########################################################################################
# Linux System Package Installs for BisQue
########################################################################################

RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    software-properties-common \
    && apt-add-repository multiverse \
    && apt-get update -qq && apt-get install -y --no-install-recommends \
    xvfb \
    firefox \
    wget \
    tightvncserver \
    x11vnc \
    xfonts-base \
    python-pip \
    python-virtualenv \
    python-numpy \
    python-scipy \
    libhdf5-dev \
    cmake \
    libmysqlclient-dev \
    postgresql \
    postgresql-client \
    python-paver \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    openslide-tools \
    python-openslide \
    libfftw3-dev \
    libgdcm2.6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update  -qq \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
    ffmpeg \
    git \
    locales \
    less \
    libasound2 \
    libasound2-data \
    libblas3 \
    libblas-common \
    libbz2-1.0 \
    libgdbm3 \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-common \
    libgfortran3 \
    libglib2.0-0 \
    libglib2.0-data \
    libblosc1 \
    libgomp1 \
    libgv-python \
    libice6 \
    libjasper1 \
   libjbig0 \
    libjpeg62 \
    liblapack3 \
    liblzo2-2 \
    libmagic1 \
    libogg0 \
    libopenjpeg5 \
    libopenslide0 \
    libopenslide-dev \
    liborc-0.4-0 \
    libpixman-1-0 \
    libpng12-0 \
    libpq5 \
    libpython2.7-minimal \
    libquadmath0 \
    libschroedinger-1.0-0 \
    libsm6 \
    libsqlite3-0 \
    libstdc++5 \
    libtheora0 \
    libtiff5-dev \
    libx11-6 \
    libx11-data \
    libxau6 \
    libxcb1 \
    libxcb-render0 \
    libxcb-shm0 \
    libxdmcp6 \
    libxext6 \
    libxml2 \
    libxrender1 \
    libxslt1.1 \
    libxvidcore4 \
    mercurial \
    openjdk-8-jdk \
    python-minimal \
    ##### PYTHON 3 #####
    build-essential \
    vim  \ 
    sudo \
    curl \
    ca-certificates \
    && update-ca-certificates \
    && apt-get clean \
    && find  /var/lib/apt/lists/ -type f -delete


########################################################################################
# Install Docker
########################################################################################

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get update -qq && \
    apt-get install -y --no-install-recommends docker-ce && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

########################################################################################

RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
RUN locale

########################################################################################
# Install Image Converter for BisQue
########################################################################################

WORKDIR /var/opt

# Image Convert
RUN wget https://biodev.ece.ucsb.edu/binaries/depot/imgcnv_ubuntu16_2.4.3.tar.gz
RUN tar -xvzf imgcnv_ubuntu16_2.4.3.tar.gz
RUN cp imgcnv_ubuntu16_2.4.3/imgcnv /usr/local/bin/
RUN cp imgcnv_ubuntu16_2.4.3/libimgcnv.so.2.4.3 /usr/local/lib/
RUN ln -s /usr/local/lib/libimgcnv.so.2.4.3 /usr/local/lib/libimgcnv.so.2.4
RUN ln -s /usr/local/lib/libimgcnv.so.2.4 /usr/local/lib/libimgcnv.so.2
RUN ln -s /usr/local/lib/libimgcnv.so.2 /usr/local/lib/libimgcnv.so
RUN ldconfig

########################################################################################
# COPY BASH Scripts for BisQue
#   - Set workdir early  as may wipe out contents
########################################################################################

WORKDIR /source
COPY run-bisque.sh bq-admin-setup.sh virtualenv.sh /builder/
COPY start-bisque.sh /builder/start-scripts.d/R50-start-bisque.sh
COPY builder/ /builder/build-scripts.d/
COPY boot/ /builder/boot-scripts.d/

########################################################################################
# RUN BASH Scripts for BisQue
#   - Install virtual ENV
#   - Set biodev pip index and install pip dependencies
########################################################################################

RUN /builder/virtualenv.sh
# ENV PY_INDEX=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple

# Set custom Python package index and configure pip
ENV PY_INDEX=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple
RUN mkdir -p /root/.pip && echo "\
[global]\n\
index-url = $PY_INDEX\n\
trusted-host = biodev.ece.ucsb.edu\n" > /root/.pip/pip.conf

# # Install certifi for updated CA certificates
# RUN pip install certif
# ENV SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")

########################################################################################
# COPY Source Code
#   - Install requirements.txt first to install all python deps
#   - Added at the end for easy updates to source code
########################################################################################
COPY  source/requirements.txt /source


RUN /builder/run-bisque.sh build
ADD  source /source

RUN /builder/bq-admin-setup.sh
########################################################################################
# Install Minio and Argo CLI
########################################################################################

# RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc && chmod +x mc &&  mv mc /usr/bin/mc

# COPY config.json /root/.mc/config.json

# Download the binary
RUN curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.2.8/argo-linux-amd64.gz

# Unzip
RUN gunzip argo-linux-amd64.gz

# Make binary executable
RUN chmod +x argo-linux-amd64 && mv ./argo-linux-amd64 /usr/local/bin/argo

########################################################################################

ENTRYPOINT ["/builder/run-bisque.sh"]

CMD [ "bootstrap","start"]

