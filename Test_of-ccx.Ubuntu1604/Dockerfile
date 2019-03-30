# System testing preCICE with openfoam-adapter and calculix-adapter

# Building on top of the latets preCICE-build
ARG from=precice/precice:latest
FROM $from

USER root
ENV USER=root

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    software-properties-common \
    curl \
    apt-transport-https \
    cmake \
    automake \
    autoconf \
    autotools-dev \
    libyaml-cpp-dev && \
    rm -rf /var/lib/apt/lists/*

# Installing OpenFOAM 4.1
RUN add-apt-repository "http://dl.openfoam.org/ubuntu dev" && \
    sh -c "curl -s http://dl.openfoam.org/gpg.key | apt-key add -" && \
    add-apt-repository http://dl.openfoam.org/ubuntu && apt update && \
    apt-get -qq --no-install-recommends install openfoam4 && \
    rm -rf /var/lib/apt/lists/*

# Downloading Calculix 2.15
WORKDIR /
RUN curl -s http://www.dhondt.de/ccx_2.15.src.tar.bz2 | tar -xj

# Installing spooles
WORKDIR /
RUN mkdir spooles.2.2 && cd spooles.2.2 && \
    curl -s http://www.netlib.org/linalg/spooles/spooles.2.2.tgz | tar -xz && \
    cd /spooles.2.2/Tree/src/ && \
    sed -i 's/drawTree/draw/g' makeGlobalLib && \
    cd /spooles.2.2/ && \
    sed -i "s#CC = /usr/lang-4.0/bin/cc#CC = /usr/bin/cc#g" Make.inc && \
    make lib && cd /spooles.2.2/MT/src/ && make

# Downloading and installing ARPACK
RUN curl -s https://www.caam.rice.edu//software/ARPACK/SRC/arpack96.tar.gz | tar -xz && \
    mv ARPACK /usr/local/ARPACK \
    && cd /usr/local/ARPACK \
    && sed -i 's/$(HOME)/\/usr\/local/g' ARmake.inc \
    && sed -i 's/\/bin\/make/make/g' ARmake.inc \
    && sed -i 's/f77/gfortran/g' ARmake.inc \
    && sed -i 's/SUN4/INTEL/g' ARmake.inc \
    && sed -i 's/-cg89//g' ARmake.inc \
    && sed -i 's/      EXTERNAL           ETIME/*     EXTERNAL           ETIME/g' UTIL/second.f \
    && make all

# Rebuild image if force_rebuild after that command
ARG CACHEBUST

# Building openfoam-adapter
WORKDIR /
RUN git clone https://github.com/precice/openfoam-adapter.git
WORKDIR /openfoam-adapter
RUN . /opt/openfoam4/etc/bashrc && ./Allwmake

# Building calculix-adapter
WORKDIR /
RUN git clone https://github.com/precice/calculix-adapter.git
WORKDIR /calculix-adapter/
COPY Makefile_of_ccx /calculix-adapter/Makefile
RUN make

ENV PATH="/calculix-adapter/bin:${PATH}"

# Downloading tutorial and meshes and set endTime to 5.0
WORKDIR /
RUN git clone https://github.com/precice/tutorials.git
WORKDIR /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX
RUN ./Download_meshes
COPY precice-config_serial.xml /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX/precice-config_serial.xml
COPY controlDict /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX/Inner-Fluid/system/controlDict
COPY controlDict /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX/Outer-Fluid/system/controlDict

# Simulating
# WORKDIR /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX
# RUN . /opt/openfoam4/etc/bashrc && ./Allrun

# Simulating with reduced output for travis ci
COPY reducing_log_of-ccx /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX
RUN ./reducing_log_of-ccx

# Copy output to folder Output for further examination
WORKDIR /
RUN mkdir Output && \
    cp -r /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX/Inner-Fluid /Output/ && \
    cp -r /tutorials/CHT/heat_exchanger/buoyantSimpleFoam-CalculiX/Outer-Fluid /Output/

