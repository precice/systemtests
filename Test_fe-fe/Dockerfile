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

# Builds the python_future python bindings for python3
RUN cd $PRECICE_ROOT/src/precice/bindings/python_future && \
    pip3 install --user .
    
# Builds the precice python bindings for python3
RUN cd $PRECICE_ROOT/src/precice/bindings/python && \
    pip3 install --user .

# Rebuild image if force_rebuild after that command
ARG CACHEBUST

# Building fenics-adapter
RUN cd $HOME && \
    git clone https://github.com/precice/fenics-adapter.git && \
    cd $HOME/fenics-adapter && \
    pip3 install --user . && \
    python3 setup.py test

# Downloading tutorial and run it
RUN cd $HOME && \
    git clone https://github.com/precice/tutorials.git && \
    cd $HOME/tutorials/HT/partitioned-heat/fenics-fenics && \
    pip3 install --user -r requirements.txt && \
    python3 heat.py -d & python3 heat.py -n

# Check output

## TODO: compare iteration count to reference result!

# Copying output files to a folder for further examination
USER root
WORKDIR /
RUN mkdir Output

