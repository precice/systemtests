# System testing preCICE bindings

# Building on top of the latets preCICE-build
ARG from=precice/precice:develop
FROM $from

USER root
ENV USER=root

RUN apt-get -qq update && apt-get -qq install python3

# create a new non-root user that has access to $PRECICE_ROOT
RUN adduser testuser
RUN chown -R testuser $PRECICE_ROOT

# Run compile and test script as non-root
USER testuser
ENV USER=root
WORKDIR $PRECICE_ROOT
RUN python3 tools/compileAndTest.py -t
