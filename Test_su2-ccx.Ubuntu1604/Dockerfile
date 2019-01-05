# System testing preCICE with SU2-adapter and calculix-adapter

# Building on top of the latest preCICE-build
ARG from=precicecoupling/precice:latest
FROM $from

USER root
ENV USER=root

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    cmake \
    curl \
    automake \
    autoconf \
    autotools-dev \
    libarpack2-dev \
    libyaml-cpp-dev    

# Downloading CalculiX 2.13
WORKDIR /
RUN curl -s http://www.dhondt.de/ccx_2.13.src.tar.bz2 | tar -xj

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
WORKDIR /
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

# Building calculix-adapter
WORKDIR /
RUN git clone https://github.com/precice/calculix-adapter.git
WORKDIR /calculix-adapter/
COPY Makefile_su2-ccx /calculix-adapter/Makefile
RUN make

ENV PATH="/calculix-adapter/bin:${PATH}"

# Downloading SU2 and SU2-adapter
WORKDIR /
RUN git clone --branch v6.0.0 https://github.com/su2code/SU2.git su2-source
RUN git clone https://github.com/precice/su2-adapter.git

ENV SU2_HOME="/su2-source"
ENV SU2_BIN="/su2-bin"
ENV SU2_RUN="/su2-bin/bin"
ENV PATH="/su2-bin/bin:${PATH}"
ENV PYTHONPATH="/su2-bin/bin:${PYTHONPATH}"

# Installing su2-adapter
WORKDIR /su2-adapter
RUN ./su2AdapterInstall

WORKDIR /su2-source
RUN ./configure --prefix=${SU2_BIN} CXXFLAGS="-std=c++11" --enable-mpi
RUN make -j 2 install

# Downloading tutorials
WORKDIR /
RUN git clone https://github.com/precice/tutorials.git

# Simulating
WORKDIR /tutorials/FSI/flap_perp/SU2-CalculiX
COPY reducing_log_su2-ccx /tutorials/FSI/flap_perp/SU2-CalculiX
USER root
RUN ./reducing_log_su2-ccx; exit 0

# Copying output files to a folder for further examination
WORKDIR /
RUN mkdir Output && cp /tutorials/FSI/flap_perp/SU2-CalculiX/flow*.vtk /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/flap.cvg /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/flap.dat /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/flap.sta /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/forces_breakdown.dat /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/precice-Calculix-convergence.log /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/precice-Calculix-iterations.log /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/precice-SU2_CFD-iterations.log /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/precice-Calculix-watchpoint-point1.log /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/restart_flow_*.dat /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/spooles.out /Output && \
cp /tutorials/FSI/flap_perp/SU2-CalculiX/surface_flow_*.csv /Output
