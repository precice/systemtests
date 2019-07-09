# System testing preCICE with fenics-adapter

# Building on top of the latest preCICE-build
ARG from=precice/precice:latest
FROM $from

USER root
ENV USER=root

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    apt-utils \
    python3 \
    python3-dev \
    software-properties-common && \
    rm -rf /var/lib/apt/lists/*

# Install pip dependecies; we have to use pip, since cython provided by apt-get is too old.
RUN wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py && \
    python3 get-pip.py

# Installing FEniCS
RUN add-apt-repository -y ppa:fenics-packages/fenics && \
    apt-get -qq update && \
    apt-get -qq --no-install-recommends install fenics && \
    rm -rf /var/lib/apt/lists/*

# switch to non-root user
USER precice

# install necessary python modules as non-root user
RUN pip3 install --user Cython mpi4py numpy enum34 scipy

# Builds the python_future python bindings for python3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python_future
RUN pip3 install --user .
    
# Builds the precice python bindings for python3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
RUN pip3 install --user .

# Rebuild image if force_rebuild after that command
ARG CACHEBUST

# Building fenics-adapter
WORKDIR $HOME
RUN git clone https://github.com/precice/fenics-adapter.git
WORKDIR $HOME/fenics-adapter
RUN pip3 install --user .

# test the adapter
RUN python3 -c "import mpi4py; print(mpi4py.__file__)"  
RUN python3 -c "import numpy; print(numpy.__file__)"  
RUN python3 -c "import fenicsadapter"  
RUN python3 setup.py test

# Downloading tutorial and run it
WORKDIR $HOME
RUN git clone https://github.com/precice/tutorials.git
WORKDIR $HOME/tutorials/HT/partitioned-heat/fenics-fenics
RUN python3 heat.py -d & python3 heat.py -n

# Check output

## TODO: compare iteration count to reference result!

