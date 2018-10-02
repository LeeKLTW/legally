FROM ubuntu
USER root
RUN apt-get update && apt-get upgrade -y \
        && apt-get install -y git

RUN wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda-2.3.0-Linux-x86_64.sh
RUN bash Anaconda-2.3.0-Linux-x86_64.sh

RUN conda update -n base conda
RUN conda install -c anaconda gensim 
RUN conda install -y -c conda-forge \
        tensorflow \
        jupyter_contrib_nbextensions \
