# System testing preCICE bindings

# Building on top of the latets preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    python-enum34 python3-pip
    
# Installing necessary python dependecies; we have to use pip, since cython provided by apt-get is too old.
RUN pip3 install --upgrade pip
RUN pip3 install Cython mpi4py numpy

# Builds and installs the precice python binding for python3 using pip3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
RUN pip3 install -e .

# Runs the python solverdummy with python3
WORKDIR $PRECICE_ROOT/tools/solverdummies/python
RUN python3 solverdummy.py precice-config.xml SolverOne MeshOne & python3 solverdummy.py precice-config.xml SolverTwo MeshTwo

# Builds the C solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/c
RUN scons

# Builds the C++ solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/cpp
RUN mpic++ -std=c++11 main.cpp -lprecice

# Builds the Fortran solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/fortran
RUN scons

# Creating Output folder
RUN mkdir /Output
