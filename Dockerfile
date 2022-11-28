
FROM amilworks/bisque05-base-xenial

LABEL maintainer="amil@ucsb.edu"
LABEL build_date="2022-03-24"

########################################################################################
# Linux System Package Installs for BisQue
########################################################################################
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
  && apt-get clean \
  && find  /var/lib/apt/lists/ -type f -delete
########################################################################################




RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
RUN locale


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
ENV PY_INDEX=https://biodev.ece.ucsb.edu/py/bisque/xenial/+simple




########################################################################################
# COPY Source Code
#   - Install requirements.txt first to install all python deps
#   - Added at the end for easy updates to source code
########################################################################################
COPY source/requirements.txt /source

RUN /builder/run-bisque.sh build

ADD source /source
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
RUN . /usr/lib/bisque/bin/activate && \
    cd /source && \
    bq-admin server stop && \
    cd bqcore && python setup.py install && \
    cd ../bqserver && python setup.py install && cd .. && \
    bq-admin deploy && bq-admin server start
