# System testing preCICE bindings

# Building on top of the latets preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

ENV FORTRAN=gfortran

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    cython  python-pip  python-numpy  python-mpi4py  python-setuptools  python-dev  python-enum34 \
    cython3 python3-pip python3-numpy python3-mpi4py python3-setuptools python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Builds the python_future python bindings for python2
WORKDIR $PRECICE_ROOT/src/precice/bindings/python_future
RUN pip2 install --user .

# Builds the python_future python bindings for python3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python_future
RUN pip3 install --user .
    
# Builds the precice python bindings for python2
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
RUN pip2 install --user . 

# Builds the precice python bindings for python3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
RUN pip3 install --user .

# Runs the python solverdummy with python2
WORKDIR $PRECICE_ROOT/tools/solverdummies
RUN python2 python/solverdummy.py precice-config.xml SolverOne MeshOne & python python/solverdummy.py precice-config.xml SolverTwo MeshTwo

# Runs the python solverdummy with python3
WORKDIR $PRECICE_ROOT/tools/solverdummies
RUN python3 python/solverdummy.py precice-config.xml SolverOne MeshOne & python3 python/solverdummy.py precice-config.xml SolverTwo MeshTwo

# Runs the python_future solverdummy with python2
WORKDIR $PRECICE_ROOT/tools/solverdummies
RUN python2 python_future/solverdummy.py precice-config.xml SolverOne MeshOne & python python_future/solverdummy.py precice-config.xml SolverTwo MeshTwo

# Runs the python_future solverdummy with python3
WORKDIR $PRECICE_ROOT/tools/solverdummies
RUN python3 python_future/solverdummy.py precice-config.xml SolverOne MeshOne & python3 python_future/solverdummy.py precice-config.xml SolverTwo MeshTwo

# Builds the C solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/c
RUN cmake . && make
RUN cd ..
RUN ./c/solverdummy precice-config.xml SolverOne MeshOne & ./c/solverdummy precice-config.xml SolverTwo MeshTwo

# Builds the C++ solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/cpp
RUN cmake . && make
RUN cd ..
RUN ./cpp/solverdummy precice-config.xml SolverOne MeshOne & ./cpp/solverdummy precice-config.xml SolverTwo MeshTwo

# Builds the Fortran solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/fortran
RUN make
RUN cd ..
RUN ./fortran/solverdummy precice-config.xml SolverOne MeshOne & ./fortran/solverdummy precice-config.xml SolverTwo MeshTwo

# Builds the f2003 solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/f2003
RUN gfortran $PRECICE_ROOT/src/precice/bindings/f2003/SolverInterfaceF2003.f90 -o solverdummy solverdummy.f03 -L/home/precice/precice-install/lib -lprecice
RUN cd ..
RUN ./f2003/solverdummy precice-config.xml SolverOne MeshOne & ./f2003/solverdummy precice-config.xml SolverTwo MeshTwo

# Creating Output folder
RUN mkdir /Output
