# System testing preCICE bindings

# Building on top of the latest preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

# Builds the executables for running the test
WORKDIR $PRECICE_ROOT/src/cplscheme/tests/systemtest
RUN g++ dummy_serial.cpp -I/home/precice/precice-install/include -L/home/precice/precice-install/lib -lprecice -std=c++11 -o serial 
RUN mpic++ dummy_parallel.cpp -I/home/precice/precice-install/include -L/home/precice/precice-install/lib -lprecice -std=c++11 -o parallel

# Runs the test
RUN ./serial precice-config-hybrid.xml Serial NodesSerial & mpirun --allow-run-as-root -np 2 ./parallel precice-config-hybrid.xml Parallel NodesParallel

