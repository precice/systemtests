# preCICE System Tests
Design und Implementation of system tests for the distributed multi-physics simulation package preCICE

# Setup and running

## Dependencies

Make sure to install 

* preCICE (https://github.com/precice/precice/wiki)
* docker (see https://docs.docker.com/install/linux/docker-ce/ubuntu/)
    * make sure you can run docker as non-root user (see https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user)
    * test your docker installation with ```docker run hello-world```
* ```python3``` 
    * with ```configparser``` (install for example with ```pip3 install configparser```)
* additional dependencies depending on the test you want to run

## Run a system test

Example command:

```python3 local_test.py -b mpi_single_ports -s of-of su2-ccx -f precice```

see ```python3 local_test.py --help``` for explanation of the command line arguments.

## Troubleshooting

* If you receive an error like ```W: Failed to fetch http://archive.ubuntu.com/ubuntu/dists/xenial/InRelease  Temporary failure resolving 'archive.ubuntu.com'```, the following [answer on stackoverflow](https://stackoverflow.com/a/40516974) might help. Even, if the suggested verification step does not work, give the systemtests another try. Sometimes it works...
* If you run into problems during compilation of preCICE in your docker container, try to use ```python3 local_test.py --force_rebuild precice```.

# preCICE
- Dockerfile.precice docker image with ubuntu 16.04 and preCICE
[preCICE - github](https://github.com/precice)

# System tests
- su2-ccx coupled simulation with SU2 and CalculiX
[FSI tutorial](https://github.com/precice/precice/wiki/FSI-tutorial)
- of-of coupled simulation with OpenFOAM
[Tutorial for CHT: Flow over a heated plate](https://github.com/precice/openfoam-adapter/wiki/Tutorial-for-CHT:-Flow-over-a-heated-plate)
- of-ccx conjugate heat transfer simulation with OpenFOAM and CalculiX
[Tutorial for CHT with OpenFOAM and CalculiX](https://github.com/precice/precice/wiki/Tutorial-for-CHT-with-OpenFOAM-and-CalculiX)
- precice Testing some components of preCICE: dummy solvers and Python bindings


# travis.yml
Continuous Integration config.
Two [build stages](https://docs.travis-ci.com/user/build-stages/):
- stage 1 (build stage): precice docker image build and pushed to [Docker Hub](https://hub.docker.com/u/precicecoupling)
- stage 2 (testing stage): build su2-ccx, of-of, of-ccx and push outputfiles to repo

# compare_*.py
Python script to compare reference data with output data.

# Others
- Makefile_*: needed to build calculix-adapter in su2-ccx and of-ccx
- push_*: script to push outputfiles back to rep [HowTo](https://gist.github.com/willprice/e07efd73fb7f13f917ea#file-push-sh)
- How to push to [hub.docker.com](https://hub.docker.com/) [link1](https://docs.travis-ci.com/user/docker/#Pushing-a-Docker-Image-to-a-Registry) [link2](https://docs.travis-ci.com/user/build-stages/share-docker-image/)
- log_*: script to log infomation about the build

# Status
[![Build Status](https://travis-ci.org/precice/systemtests.svg?branch=master)](https://travis-ci.org/precice/systemtests)

# How to create a new system tests
1. Create a directory `Test_mysystemtest`.
2. Create a `Dockerfile` in there.
3. Create a directory `referenceOutput` there.
4. Copy the output files to a folder `/Output/` (inside the container).
