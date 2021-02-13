FROM ubuntu:xenial
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update                                            && \
    apt-get -y upgrade                                           && \
    apt-get -y install                                              \
      python
RUN apt-get -y install python-lxml python-numpy
RUN apt-get -y install python-pip
RUN apt-get -y install python-scipy python-configparser python-h5py
RUN pip install tqdm
RUN pip install pymks
RUN pip install tables scipy
RUN pip install --user --install-option="--prefix=" -U scikit-learn==0.19.1
RUN pip install -i https://biodev.ece.ucsb.edu/py/bisque/prod/+simple bisque-api==0.5.9
RUN pip install scikit-image
RUN pip install requests==2.10.0


RUN mkdir /module
RUN mkdir /module/source
WORKDIR /module
COPY ./source /module/source

COPY PythonScriptWrapper /module/
COPY PythonScriptWrapper.py /module/
COPY pydist /module/pydist/
ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
CMD [ 'PythonScriptWrapper' ]

#WORKDIR /module
#COPY PythonScriptWrapper /module/
#COPY PythonScriptWrapper.py /module/
#COPY getSegmentation.py /module/
#COPY pydist /module/pydist/
#ENV PATH /module:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
#CMD [ 'PythonScriptWrapper' ]
