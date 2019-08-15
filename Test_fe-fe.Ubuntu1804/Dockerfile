# System testing preCICE with fenics-adapter

# Building on top of the latest preCICE-build
ARG from=precice/precice:latest
FROM $from

USER root
ENV USER=root

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    apt-utils \
    software-properties-common \
    python3 \
    python3-dev \
    python3-pip && \   
    rm -rf /var/lib/apt/lists/*

# Install pip dependecies; we have to use pip, since cython provided by apt-get is too old.
RUN wget -q https://bootstrap.pypa.io/get-pip.py -O get-pip.py && \
    python3 get-pip.py

# Installing FEniCS
RUN add-apt-repository -y ppa:fenics-packages/fenics && \
    apt-get -qq update && \
    apt-get -qq install --no-install-recommends fenics && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --user cython  # TODO: can we put this dependency into requirements.txt of python_future?

# Builds the python_future python bindings for python3
RUN cd $PRECICE_ROOT/src/precice/bindings/python_future && \
    pip3 install --user .
    
# Builds the precice python bindings for python3
RUN cd $PRECICE_ROOT/src/precice/bindings/python && \
    pip3 install --user .

# Rebuild image if force_rebuild after that command
ARG CACHEBUST

# Building fenics-adapter
WORKDIR /
RUN git clone https://github.com/precice/fenics-adapter.git && \
    cd fenics-adapter && \
    pip3 install --user . && \
    python3 setup.py test

# Downloading tutorial and run it
WORKDIR /
RUN git clone https://github.com/precice/tutorials.git
WORKDIR /tutorials/HT/partitioned-heat/fenics-fenics
RUN pip3 install --user -r requirements.txt && \    
    python3 heat.py -d & python3 heat.py -n

# Copying output files to a folder for further examination
WORKDIR /
RUN ls /tutorials/HT/partitioned-heat/fenics-fenics
RUN mkdir Output && \
    cp /tutorials/HT/partitioned-heat/fenics-fenics/precice-HeatDirichlet-convergence.log /Output/ && \
    cp /tutorials/HT/partitioned-heat/fenics-fenics/precice-HeatDirichlet-iterations.log /Output/ && \
    cp /tutorials/HT/partitioned-heat/fenics-fenics/precice-HeatNeumann-convergence.log /Output/ && \
    cp /tutorials/HT/partitioned-heat/fenics-fenics/precice-HeatNeumann-iterations.log  /Output/   
