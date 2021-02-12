# ==================================================================
# module list
# ------------------------------------------------------------------
# python        3.6    (apt)
# pytorch       latest (pip)
# ==================================================================

FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04
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
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        build-essential \
        ca-certificates \
        cmake net-tools iputils-ping wget \
        byobu curl git htop man unzip vim \
        liblapack3 libblas-dev liblapack-dev gfortran \
        && \
# ==================================================================
# python 3
# ------------------------------------------------------------------
	DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        software-properties-common \
        && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        python3 python3-dev \
        python3-lxml python3-numpy python3-tk \
        libsm6 libxext6 libxrender1 libfontconfig1 \
	&& \
    wget -O ~/get-pip.py \
        https://bootstrap.pypa.io/get-pip.py && \
    python3 ~/get-pip.py && \
    ln -s /usr/bin/python3 /usr/local/bin/python3 && \
    ln -s /usr/bin/python3 /usr/local/bin/python && \
    rm -f /usr/bin/python && \
    $PIP3_INSTALL \
        setuptools \
        && \
    $PIP3_INSTALL \
        numpy \
        pandas \
        cloudpickle \
        scikit-learn==0.20.0 \
		scipy==1.4.1 \
        matplotlib \
        Cython \
        && \
# ==================================================================
# pytorch
# ------------------------------------------------------------------
	$PIP3_INSTALL \
    future \
    protobuf \
    enum34 \
    pyyaml \
    typing \
	Pillow \
	tqdm \
	nltk \
	opencv-python \
	opencv-contrib-python \
	h5py \
	imgaug \
	IPython[all] \
        && \

    $PIP3_INSTALL \
        torch==1.2.0 \
        torchvision==0.4.0 \
        && \
# ==================================================================
# Additional packages
# ------------------------------------------------------------------
    $PIP3_INSTALL \
        SimpleITK \
	morphsnakes \
        scikit-image \
        nibabel \
        nilearn \
        && \
    $PIP3_INSTALL -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple \
        bisque-api==0.5.9 \
        && \
    $PIP3_INSTALL \
        requests==2.10.0 \
        && \
## ==================================================================
## Additional packages
## ------------------------------------------------------------------
#	$PIP3_INSTALL \
#    SimpleITK \
#	scikit-image \
#	morphsnakes \
#        && \
#    $PIP3_INSTALL \
#		requests==2.18.4 \
#		six \
#		requests_toolbelt==0.6.2 \
#        && \
# ==================================================================
# config & cleanup
# ------------------------------------------------------------------
    ldconfig && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* ~/*

## ==================================================================
## Additional packages
## ------------------------------------------------------------------
RUN	python3 -m pip --no-cache-dir install --upgrade \
    pymks \
    twine==1.8.0\
	pydist-cli==0.1.0\
	requests==2.18.4 \
	six \
	requests_toolbelt==0.6.2

RUN	python3 -m pip --no-cache-dir install --upgrade tifffile

		
# ==================================================================
# Volume  & Entry Layer
# ------------------------------------------------------------------
RUN mkdir /module
RUN mkdir /module/source
RUN mkdir /module/public
RUN mkdir /module/data
WORKDIR /module
COPY ./source /module/source/
COPY ./public /module/public/
COPY ./source/data /module/data/

COPY PythonScriptWrapper /module/
COPY PythonScriptWrapper.py /module/
COPY ./*.* /module/
#COPY pydist /module/pydist/
ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
#CMD [ 'python' 'PythonScriptWrapper.py' ]
CMD [ 'PythonScriptWrapper' ]