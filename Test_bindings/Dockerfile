# System testing preCICE bindings

# Building on top of the latest preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

ENV FORTRAN=gfortran

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    python python-dev \
    python3 python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Installing necessary python dependecies; we have to use pip, since cython provided by apt-get is too old.
RUN wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py && \
    python3 get-pip.py && \
    python2 get-pip.py && \
    pip2 install Cython mpi4py numpy enum34 && \
    pip3 install Cython mpi4py numpy enum34

# Builds the precice python binding for python2
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
RUN python2 setup.py install

# Builds the precice python binding for python3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
RUN python3 setup.py install

# Runs the python solverdummy with python2
WORKDIR $PRECICE_ROOT/tools/solverdummies/python
RUN python2 solverdummy.py ../precice-config.xml SolverOne MeshOne & python solverdummy.py ../precice-config.xml SolverTwo MeshTwo

# Runs the python solverdummy with python3
WORKDIR $PRECICE_ROOT/tools/solverdummies/python
RUN python3 solverdummy.py ../precice-config.xml SolverOne MeshOne & python3 solverdummy.py ../precice-config.xml SolverTwo MeshTwo

# Builds the C solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/c
RUN cmake . && make

# Builds the C++ solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/cpp
RUN cmake . && make

# Builds the Fortran solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/fortran
RUN make 

# Creating Output folder
RUN mkdir /Output
