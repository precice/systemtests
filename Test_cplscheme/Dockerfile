# System testing preCICE bindings

# Building on top of the latest preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

# Builds the executables for running the test
WORKDIR $PRECICE_ROOT/src/cplscheme/tests/systemtest
RUN g++ dummy_serial.cpp -lprecice -o serial
RUN mpic++ dummy_parallel.cpp -lprecice -o parallel

# Runs the test
RUN ./serial precice-config-hybrid.xml Serial NodesSerial & mpirun -np 2 ./parallel precice-config-hybrid.xml Parallel NodesParallel

