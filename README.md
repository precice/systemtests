# preCICE System Tests
[![Build Status](https://travis-ci.org/precice/systemtests.svg?branch=master)](https://travis-ci.org/precice/systemtests)

System tests for the distributed multi-physics coupling library library preCICE. 

This repository provides Dockerfiles for building preCICE images, solvers, and adapters, as well as docker-compose files and scripts that coordinate everything.
More information can be found in the [docs](docs/)

## Dependencies

* [preCICE](https://github.com/precice/precice)
* [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
    * Make sure you can run docker as non-root user (see [here](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user))
    * Test your docker installation with e.g. ```docker run --rm hello-world```
    * Test your network connectivity with `docker run --rm alpine ping 8.8.8.8`. See [`docs/development.md`](docs/development.md) if this does not work.
* [docker-compose](https://docs.docker.com/compose/)
* ```python3``` 


## Main scripts

- `system_testing.py` is the main script to run automatic testing on CI system
- `local_test.py` is a simple wrapper to run tests on a local machine
- `trigger_systemtests.py` is a script that can be used by CI on other repositories or from the local machine to trigger Travis builds


## Run a system test locally

To run OpenFOAM-OpenFOAM system test using Ubuntu 16.04 as the base for building preCICE and adapters:

```
   python3 local_test.py -s of-of -f Dockerfile.Ubuntu1604.home
```

Run `python3 local_test.py -h` for more information.
