# System testing preCICE bindings

# Building on top of the latets preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install python3 python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /python-venv/ && \
    source /python-venv/bin/activate && \
    bin/pip install -U pip

# Builds the precice python binding for python3
RUN pip3 install $PRECICE_ROOT/src/precice/bindings/python

# Runs the python solverdummy with python3
WORKDIR $PRECICE_ROOT/tools/solverdummies/python
RUN pip3 install -r requirements.txt && \
    python3 solverdummy.py precice-config.xml SolverOne MeshOne & python3 solverdummy.py precice-config.xml SolverTwo MeshTwo

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
