# System testing preCICE bindings

# Building on top of the latest preCICE-build
ARG from=precice/precice-ubuntu1804.home-develop
FROM $from

USER root
ENV USER=root

ENV FORTRAN=gfortran

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    cython3 python3-pip python3-numpy python3-mpi4py python3-setuptools python3-dev && \
    rm -rf /var/lib/apt/lists/*
    
USER precice

ARG branch=develop

# Clones the precice python bindings
WORKDIR /home/precice
RUN git clone --branch $branch https://github.com/precice/python-bindings.git
# Builds the precice python bindings
WORKDIR /home/precice/python-bindings
RUN pip3 install --user .

# Runs the python solverdummy
RUN cd solverdummy && python3 solverdummy.py precice-config.xml SolverOne MeshOne & python3 solverdummy.py precice-config.xml SolverTwo MeshTwo

# Builds the C solverdummy
WORKDIR $PRECICE_ROOT/examples/solverdummies/c
RUN cmake . && make
RUN ./solverdummy ../precice-config.xml SolverOne MeshOne & ./solverdummy ../precice-config.xml SolverTwo MeshTwo

# Builds the C++ solverdummy
WORKDIR $PRECICE_ROOT/examples/solverdummies/cpp
RUN cmake . && make
RUN ./solverdummy ../precice-config.xml SolverOne MeshOne & ./solverdummy ../precice-config.xml SolverTwo MeshTwo

# Builds the Fortran solverdummy
WORKDIR $PRECICE_ROOT/examples/solverdummies/fortran
RUN make
RUN cd ..
RUN ./solverdummy ../precice-config.xml SolverOne MeshOne & ./solverdummy ../precice-config.xml SolverTwo MeshTwo

# Clones the fortran-module
WORKDIR /home/precice
RUN git clone --branch $branch https://github.com/precice/fortran-module.git
# Builds the fortran module
WORKDIR /home/precice/fortran-module
RUN make
# Builds the f2003 solverdummy
WORKDIR /home/precice/fortran-module/examples/solverdummy
RUN make
RUN ./solverdummy precice-config.xml SolverOne MeshOne & ./solverdummy precice-config.xml SolverTwo MeshTwo

# Creating Output folder
USER root
RUN mkdir /Output
USER precice
