FROM ubuntu:xenial

#FROM nvidia/cuda:10.2-cudnn7-runtime-ubuntu16.04
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
        apt-get install -y software-properties-common && \
        add-apt-repository ppa:deadsnakes/ppa && \
        apt-get update -y  && \
        apt-get install -y build-essential python3.6 python3.6-dev python3-pip && \
        apt-get install -y git  && \
        # update pip
        python3.6 -m pip install pip --upgrade && \
        python3.6 -m pip install wheel

RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get -y install python-pip liblapack3 libblas-dev liblapack-dev gfortran
RUN apt-get update
#RUN apt-get install vim
# RUN apt-get -y install nvidia-container-runtime
RUN apt-get -y install vim
RUN rm -f /usr/bin/python && ln -s /usr/bin/python3.6 /usr/bin/python


RUN pip install numpy
RUN pip install torch==1.6.0
RUN pip install torchvision==0.7.0
RUN pip install nibabel
RUN pip install lxml
RUN pip install pillow
RUN pip install SimpleITK
RUN pip install git+https://github.com/JoHof/lungmask
RUN pip install opencv-python
RUN pip install -U scikit-learn
RUN pip install torchsummary
RUN pip install tables
# RUN pip install -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple bisque-api==0.5.9
# RUN pip install -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple
# RUN pip install bqapi
RUN pip install requests-toolbelt
RUN pip install requests==2.10.0
RUN apt-get -y install python-lxml

RUN mkdir /module
RUN mkdir /module/source
WORKDIR /module
COPY ./source /module/source
COPY ./public /module
COPY ./bqapi /module/bqapi

COPY PythonScriptWrapper /module/
COPY PythonScriptWrapper.py /module/
# COPY source  /module/
# COPY pydist /module/pydist/
# RUN python setup.py install && cd ..
COPY predict.py /module/

COPY epoch30_ResNet152.pt /module/

ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

CMD [ 'PythonScriptWrapper' ]
