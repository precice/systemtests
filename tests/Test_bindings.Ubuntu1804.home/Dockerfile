# System testing preCICE bindings

# Building on top of the latest preCICE-build
ARG from=precice/precice-ubuntu1804.home-develop
FROM $from

USER root
ENV USER=root

ENV FORTRAN=gfortran

# Installing necessary dependecies
# Only install minimal python dependencies; pip should take care of installing all other dependencies
RUN apt-get -qq update && apt-get -qq install \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*
    
USER precice

RUN pip3 install --user --upgrade pip  # Use latest pip version. See https://github.com/precice/python-bindings#installing-the-package

ARG branch=develop

# Clones the precice python bindings
WORKDIR /home/precice
RUN git clone --branch $branch https://github.com/precice/python-bindings.git
# Builds the precice python bindings
WORKDIR /home/precice/python-bindings
RUN pip3 install --user .

# Runs the python solverdummy
WORKDIR /home/precice/python-bindings/solverdummy
RUN python3 solverdummy.py precice-config.xml SolverOne MeshOne & python3 solverdummy.py precice-config.xml SolverTwo MeshTwo

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
RUN git clone https://github.com/precice/fortran-module.git
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
