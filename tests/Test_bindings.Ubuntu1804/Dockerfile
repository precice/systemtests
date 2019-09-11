# System testing preCICE bindings

# Building on top of the latets preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

ENV FORTRAN=gfortran

# Installing necessary dependecies
RUN apt-get -qq update && apt-get -qq install \
    python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Builds the python_future python bindings for python3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python_future
RUN pip3 install --user .
    
# Builds the precice python bindings for python3
WORKDIR $PRECICE_ROOT/src/precice/bindings/python
RUN pip3 install --user .

# Runs the python solverdummy with python3
WORKDIR $PRECICE_ROOT/tools/solverdummies/python
RUN python3 solverdummy.py ../precice-config.xml SolverOne MeshOne & python3 solverdummy.py ../precice-config.xml SolverTwo MeshTwo

# Runs the python_future solverdummy with python3
WORKDIR $PRECICE_ROOT/tools/solverdummies/python_future
RUN python3 solverdummy.py ../precice-config.xml SolverOne MeshOne & python3 solverdummy.py ../precice-config.xml SolverTwo MeshTwo

# Builds the C solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/c
RUN cmake . && make
RUN ./solverdummy ../precice-config.xml SolverOne MeshOne & ./solverdummy ../precice-config.xml SolverTwo MeshTwo

# Builds the C++ solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/cpp
RUN cmake . && make
RUN ./solverdummy ../precice-config.xml SolverOne MeshOne & ./solverdummy ../precice-config.xml SolverTwo MeshTwo

# Builds the Fortran solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/fortran
RUN make
RUN cd ..
RUN ./solverdummy ../precice-config.xml SolverOne MeshOne & ./solverdummy ../precice-config.xml SolverTwo MeshTwo

# Builds the f2003 solverdummy
WORKDIR $PRECICE_ROOT/tools/solverdummies/f2003
RUN gfortran $PRECICE_ROOT/src/precice/bindings/f2003/SolverInterfaceF2003.f90 -o solverdummy solverdummy.f03 $(pkg-config --libs-only-L --libs-only-l libprecice)
)
RUN ./solverdummy ../precice-config.xml SolverOne MeshOne & ./solverdummy ../precice-config.xml SolverTwo MeshTwo

# Creating Output folder
RUN mkdir /Output
