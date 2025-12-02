# Updated by Wahid Sadique Koly on 2025-07-29 to align with the new upgraded codebase.

FROM ubuntu:22.04

LABEL maintainer="amil@ucsb.edu"
LABEL build_date="2025-03-01"

# Set noninteractive frontend to avoid hanging
ENV DEBIAN_FRONTEND=noninteractive

RUN echo "Install Bisque System"

########################################################################################
# Linux System Package Installs for BisQue (Ubuntu 22.04)
########################################################################################

# Update package lists and install basic dependencies
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    ca-certificates \
    curl \
    wget \
    gnupg \
    lsb-release \
    && apt-add-repository multiverse \
    && apt-get update -qq

# Install Python and scientific computing packages
RUN apt-get install -y --no-install-recommends \
    python3-pip \
    python3-venv \
    python3-numpy \
    python3-scipy \
    python3-openslide \
    python3-minimal \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install database and development tools
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    libhdf5-dev \
    libmysqlclient-dev \
    postgresql \
    postgresql-client \
    graphviz \
    libgraphviz-dev \
    openslide-tools \
    libfftw3-dev \
    libgdcm3.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install X11 and display tools
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    xvfb \
    firefox \
    tightvncserver \
    x11vnc \
    xfonts-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install core system libraries (part 1) - CORRECTED for Ubuntu 22.04
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    locales \
    less \
    libasound2 \
    libasound2-data \
    libblas3 \
    libbz2-1.0 \
    libgdbm-compat4 \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-common \
    libgfortran5 \
    libglib2.0-0 \
    libglib2.0-data \
    libblosc1 \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install core system libraries (part 2) - CORRECTED for Ubuntu 22.04
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    libice6 \
    libjbig0 \
    libjpeg-turbo8 \
    liblapack3 \
    liblzo2-2 \
    libmagic1 \
    libogg0 \
    libopenslide0 \
    libopenslide-dev \
    liborc-0.4-0 \
    libpixman-1-0 \
    libpng16-16 \
    libpq5 \
    libquadmath0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install core system libraries (part 3) - CORRECTED for Ubuntu 22.04
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    libsm6 \
    libsqlite3-0 \
    libstdc++6 \
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
    libfreeimage3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install development tools and Java
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
    mercurial \
    openjdk-8-jdk \
    vim \
    sudo \
    libjpeg-dev \
    libjpeg8-dev \
    && update-ca-certificates \
    && apt-get clean \
    && find /var/lib/apt/lists/ -type f -delete

# Fix ImarisConvert library dependencies - create symlink for older JPEG library version
RUN ln -sf /usr/lib/x86_64-linux-gnu/libjpeg.so.8 /usr/lib/x86_64-linux-gnu/libjpeg.so.62

# Set Java environment for bioformats
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

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
ENV LANG=en_US.UTF-8
RUN locale

########################################################################################
# Install Image Converter for BisQue (Ubuntu 22.04)
########################################################################################

WORKDIR /var/opt

# Install new imgcnv dependencies
RUN apt-get update -qq && \
    apt-get install --fix-missing --yes --no-install-recommends --purge \
    libavformat58 libavcodec58 libswscale5 libavutil56 \
    libhdf5-103 libhdf5-cpp-103 \
    libgdcm3.0 libjpeg-turbo8 libopenslide0 libfftw3-3 liblzma5 \
    libsqlite3-0 libraw20 libtiff5 libtiffxx5 libopenjp2-7 libpng16-16 \
    libexiv2-27 libwebp7 liblcms2-2 libzstd1 zlib1g libjbig0 libdeflate0 liblerc3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download the new imgcnv archive
RUN wget https://files.wskoly.xyz/bisque/imgcnv_ubuntu22_3.15.0.tar.xz

# Extract the .tar.xz archive
RUN tar -xvJf imgcnv_ubuntu22_3.15.0.tar.xz

# Copy the binary and shared library to appropriate system paths
RUN cp imgcnv_ubuntu22_3.15.0/imgcnv /usr/local/bin/
RUN cp imgcnv_ubuntu22_3.15.0/libimgcnv.so.3.15.0 /usr/local/lib/

# Create symbolic links for shared library versioning
RUN ln -s /usr/local/lib/libimgcnv.so.3.15.0 /usr/local/lib/libimgcnv.so.3.15
RUN ln -s /usr/local/lib/libimgcnv.so.3.15 /usr/local/lib/libimgcnv.so.3
RUN ln -s /usr/local/lib/libimgcnv.so.3 /usr/local/lib/libimgcnv.so

# Update the shared library cache
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
# ENV PY_INDEX=https://vat.ece.ucsb.edu/py/bisque/xenial/+simple

# Set custom Python package index and configure pip
# ENV PY_INDEX=https://vat.ece.ucsb.edu/py/bisque/xenial/+simple
# RUN mkdir -p /root/.pip && echo "\
# [global]\n\
# index-url = $PY_INDEX\n\
# trusted-host = biodev.ece.ucsb.edu\n" > /root/.pip/pip.conf

# # Install certifi for updated CA certificates
# RUN pip install certif
# ENV SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")

########################################################################################
# COPY Source Code
#   - Install requirements.txt first to install all python deps
#   - Added at the end for easy updates to source code
########################################################################################

ADD source /source
RUN /builder/run-bisque.sh build

RUN /builder/bq-admin-setup.sh

########################################################################################
# Fix: bioformats and third-party tools integration
########################################################################################

# Ensure bioformats tools are properly configured
RUN if [ -f /usr/lib/bisque/bin/bioformats_package.jar ]; then \
    echo "Bioformats JAR found, testing functionality..." && \
    java -cp /usr/lib/bisque/bin/bioformats_package.jar loci.formats.tools.ImageInfo 2>/dev/null || echo "Bioformats JAR needs runtime configuration"; \
    fi

# Create environment script for bioformats tools
RUN echo '#!/bin/bash\n\
    export BF_JAR_DIR=/usr/lib/bisque/bin\n\
    export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64\n\
    export PATH=$JAVA_HOME/bin:$PATH\n' > /etc/bioformats-env.sh && \
    chmod +x /etc/bioformats-env.sh

# Test ImarisConvert functionality
RUN if [ -f /usr/lib/bisque/bin/ImarisConvert ]; then \
    echo "Testing ImarisConvert..." && \
    /usr/lib/bisque/bin/ImarisConvert --help >/dev/null 2>&1 && echo "ImarisConvert working" || echo "ImarisConvert needs additional libraries"; \
    fi

# Verify OpenSlide installation
RUN python3 -c "import openslide; print('OpenSlide version:', openslide.__version__)" && \
    echo "OpenSlide verification complete"

# Create proper wrapper scripts for third-party tools in system PATH
RUN echo '#!/bin/sh\nSUB=ImarisConvert_glibc2.11\nexport LD_LIBRARY_PATH="/usr/lib/bisque/bin/$SUB"\nexec /usr/lib/bisque/bin/$SUB/ImarisConvert "$@"' > /usr/local/bin/ImarisConvert && \
    echo '#!/usr/bin/env bash\nBF_PROG=loci.formats.tools.ImageInfo /usr/lib/bisque/bin/bf.sh "$@"' > /usr/local/bin/showinf && \
    echo '#!/usr/bin/env bash\nBF_PROG=loci.formats.tools.ImageConverter /usr/lib/bisque/bin/bf.sh "$@"' > /usr/local/bin/bfconvert && \
    chmod +x /usr/local/bin/ImarisConvert /usr/local/bin/showinf /usr/local/bin/bfconvert && \
    echo "Third-party tools wrapper scripts created"

# Set container environment markers for BisQue setup scripts
ENV DOCKER_CONTAINER=1
ENV BQ_CONTAINER_BUILD=1

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

