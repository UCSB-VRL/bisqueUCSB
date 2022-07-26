# Load base ubuntu image 
#FROM nvidia/cuda:8.0-cudnn5-devel-ubuntu16.04
FROM tensorflow/tensorflow:2.3.0
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update

# Use Python 3.8 as default python interpreter
RUN apt-get install -y python3 python3-dev python3-pip
RUN ln -sf /usr/bin/python3.8 /usr/bin/python

# Install initial dependencies
RUN apt-get install -y build-essential cmake pkg-config wget git libfftw3-dev
RUN apt-get install ffmpeg libsm6 libxext6  -y

# Install pip requirements
RUN pip install -U pip
RUN pip install tensorflow opencv-python numpy matplotlib \ 
    scipy scikit-learn scikit-image

# Copy python command line source code of malsee tool
COPY models/ /module/models
COPY src/ /module/src

WORKDIR /module/

####################################################################
######################## Append From Here Down #####################
####################################################################

# ===============bqapi for python3 Dependencies=====================
# pip install in this exact order
RUN pip install six
RUN pip install lxml
RUN pip install requests==2.18.4
RUN pip install requests-toolbelt

# =====================Build Directory Structure====================

COPY PythonScriptWrapper.py /module/
COPY public/ /module/public
COPY bqapi/ /module/bqapi

# Replace the following line with your {ModuleName}.xml
COPY SeamCarvingDetection.xml /module/SeamCarvingDetection.xml

ENV PATH /module:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV PYTHONPATH $PYTHONPATH:/module/src
