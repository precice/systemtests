# System testing preCICE bindings

# Building on top of the latets preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    python-pip python-enum34 python3-pip
    
# Installing necessary python dependecies
RUN pip2 install --upgrade pip
RUN pip2 install Cython mpi4py
RUN pip3 install --upgrade pip
RUN pip3 install Cython mpi4py numpy

# Builds the precice python binding for python2
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
ENV PRECICE_MPI_IMPLEMENTATION=openmpi
RUN python2 setup.py install

# Builds the precice python binding for python3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
ENV PRECICE_MPI_IMPLEMENTATION=openmpi
RUN python3 setup.py install

# Runs the python solverdummy with python2
WORKDIR $PRECICE_ROOT/tools/solverdummies/python
RUN python2 solverdummy.py precice-config.xml SolverOne MeshOne & python solverdummy.py precice-config.xml SolverTwo MeshTwo

# Runs the python solverdummy with python3
WORKDIR $PRECICE_ROOT/tools/solverdummies/python
RUN python3 solverdummy.py precice-config.xml SolverOne MeshOne & python3 solverdummy.py precice-config.xml SolverTwo MeshTwo

# Builds the C solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/c
RUN scons

# Builds the C++ solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/cpp
RUN mpic++ -std=c++11 -I$PRECICE_ROOT/src main.cpp -lprecice

# Builds the Fortran solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/fortran
RUN scons
