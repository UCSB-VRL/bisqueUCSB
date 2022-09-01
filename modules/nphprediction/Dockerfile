# ==================================================================
# module list
# ------------------------------------------------------------------
# python        3.6    (apt)
# pytorch       latest (pip)
# ==================================================================

FROM ubuntu:18.04
ARG DEBIAN_FRONTEND="noninteractive"

RUN APT_INSTALL="apt-get install -y --no-install-recommends" && \
    PIP3_INSTALL="python3 -m pip --no-cache-dir install --upgrade" && \
    GIT_CLONE="git clone --depth 10" && \
    rm -rf /var/lib/apt/lists/* \
           /etc/apt/sources.list.d/cuda.list \
           /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-get update && \
# ==================================================================
# tools
# ------------------------------------------------------------------
    $APT_INSTALL \
        build-essential \
        ca-certificates \
        cmake net-tools iputils-ping wget \
        byobu curl git htop man unzip vim \
        liblapack3 libblas-dev liblapack-dev gfortran \
        && \
# ==================================================================
# python 3
# ------------------------------------------------------------------
    $APT_INSTALL \
        software-properties-common \
        && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    $APT_INSTALL \
        python3 python3-dev \
        python3-lxml python3-numpy python3-tk \
        libsm6 libxext6 libxrender1 libfontconfig1 \
	&& \
    wget -O ~/get-pip.py \
        https://bootstrap.pypa.io/pip/3.6/get-pip.py && \
    python3 ~/get-pip.py && \
    ln -s /usr/bin/python3 /usr/local/bin/python3 && \
    ln -s /usr/bin/python3 /usr/local/bin/python && \
    rm -f /usr/bin/python && \
    $PIP3_INSTALL \
        setuptools \
        && \
# ==================================================================
# Additional packages
# ------------------------------------------------------------------
    $PIP3_INSTALL \
        SimpleITK \
        tables \
	morphsnakes \
	joblib==0.14.0 \
	nibabel==3.0.0 \
	numpy==1.18.1 \
	opencv-python==4.1.2.30 \
	pandas==0.25.3 \
	scikit-image==0.16.1 \
	scikit-learn==0.22.1 \
	scipy==1.2.0 \
	six==1.13.0 \
	torch==1.2.0 \
	torchvision==0.4.0 \
	nipype==1.8.2 \
	bqapi-ucsb \
        && \
    $PIP3_INSTALL -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple \
        requests==2.18.4 \
	six \
	requests_toolbelt==0.6.2 \
        && \
# ==================================================================
# config & cleanup
# ------------------------------------------------------------------
    ldconfig && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* ~/*

# ==================================================================
# Volume  & Entry Layer
# ------------------------------------------------------------------
RUN mkdir /module
RUN mkdir /module/source
WORKDIR /module
COPY ./source /module/source
# COPY ./bqapi /module/bqapi
COPY ./public /module

COPY PythonScriptWrapper /module/
COPY PythonScriptWrapper.py /module/


ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
CMD [ 'PythonScriptWrapper' ]


