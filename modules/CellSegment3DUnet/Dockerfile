# ==================================================================
# module list (Base Cuda 9.0 Devel Image is 2.71GB)
# ------------------------------------------------------------------
# python        2.7    (apt)
# pytorch       latest (pip)
# ==================================================================

FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04
RUN APT_INSTALL="apt-get install -y --no-install-recommends" && \
    PIP2_INSTALL="python2 -m pip --no-cache-dir install" && \
    GIT_CLONE="git clone --depth 10" && \
    rm -rf /var/lib/apt/lists/* \
           /etc/apt/sources.list.d/cuda.list \
           /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-get update && \
# ==================================================================
# tools
# ------------------------------------------------------------------
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        build-essential \
        ca-certificates \
        cmake net-tools iputils-ping wget \
        byobu curl git htop man unzip vim \
        liblapack3 libblas-dev liblapack-dev gfortran \
        && \
# ==================================================================
# python 2
# ------------------------------------------------------------------
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        software-properties-common \
        && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        python2.7 \
        python2.7-dev python-pip python-setuptools python-lxml python-numpy python-tk python-configparser \
        && \
    # wget -O ~/get-pip.py \
    #     https://bootstrap.pypa.io/get-pip.py && \
    # python2.7 ~/get-pip.py && \
    ln -s /usr/bin/python2.7 /usr/local/bin/python2 && \
    ln -s /usr/bin/python2.7 /usr/local/bin/python && \
    # $PIP2_INSTALL \
    #     setuptools \
    #     && \
    $PIP2_INSTALL \
        # setuptools \
        numpy \
        scipy==1.0.1  \
        tables==3.4.0 \
        pandas==0.23.1 \
        h5py==2.9.0   \
        cloudpickle==1.0.0 \
        scikit-learn==0.20.0 \
        matplotlib==2.2.5 \
        Cython==0.29.4 \
        && \
# ==================================================================
# pytorch
# ------------------------------------------------------------------
    $PIP2_INSTALL \
        future \
        protobuf \
        enum34 \
        pyyaml \
        typing \
    	torchvision==0.2.1 \
        && \
    $PIP2_INSTALL \
        torch_nightly -f \
        https://download.pytorch.org/whl/nightly/cu90/torch_nightly.html \
        && \
# ==================================================================
# Additional packages
# ------------------------------------------------------------------
    $PIP2_INSTALL \
        SimpleITK \ 
	morphsnakes \
        scikit-image \
        nibabel \
        nilearn \
        && \
    $PIP2_INSTALL -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple \
        bisque-api==0.5.9 \
        && \
    $PIP2_INSTALL \
        requests==2.10.0 \
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
COPY ./public /module/source

COPY PythonScriptWrapper /module/
COPY PythonScriptWrapper.py /module/
#COPY pydist /module/pydist/
ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
#CMD [ 'python' 'PythonScriptWrapper.py' ]
CMD [ 'PythonScriptWrapper' ]
