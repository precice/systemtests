ARG from=precice/precice-ubuntu1604.home-develop
FROM $from
USER root

RUN apt-get -qq update && apt-get -qq install \
    python3 python3-dev \
    libsm6 libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Installing necessary python dependecies; we have to use pip, since cython provided by apt-get is too old.
RUN wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py && \
    python3 get-pip.py

USER precice
RUN pip3 install --user cython mpi4py numpy enum34 matplotlib vtk

ARG branch=develop

ARG CACHEBUST

RUN mkdir /Output

# Builds the precice python bindings for python3
RUN pip3 install --user https://github.com/precice/python-bindings/archive/$branch.zip

WORKDIR /home/precice/
RUN git clone https://github.com/precice/elastictube1d.git

WORKDIR /home/precice/elastictube1d


RUN ./Allrun

# transfer only VTK results
RUN cp -r VTK /Output/
