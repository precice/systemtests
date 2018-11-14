# System testing preCICE bindings

# Building on top of the latets preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    cython python-enum34
    
# Rebuild image if force_rebuild after that command
ARG CACHEBUST

# Builds the precice python binding
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
ENV PRECICE_MPI_IMPLEMENTATION=openmpi
RUN python setup.py build_ext --inplace

# Builds the C solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/c
RUN scons

# Builds the C++ solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/cpp
RUN mpic++ -std=c++11 -I$PRECICE_ROOT/src main.cpp -lprecice

# Builds the Fortran solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/fortran
RUN scons


# Copy output to folder Output for further examination (currently disabled)
WORKDIR /
RUN mkdir Output
    # cp -r /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX/Inner-Fluid /Output/ && \
    # cp -r /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX/Outer-Fluid /Output/

