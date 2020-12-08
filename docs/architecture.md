# General architecture

At the moment, the systemtest procedure is being run on the [TravisCI platform](https://travis-ci.org/github/precice). Note that this is subject to change soon: TravisCI itself is currently [migrating](https://docs.travis-ci.com/user/migrate/open-source-repository-migration) (changing the domain from `travis-ci.org` to `travis-ci.com`), and on top of that we plan on [transferring the systemtests to another platform alltogether](https://github.com/precice/systemtests/issues/253).

Running tests on TravisCI has two requirements: the repository needs to be registered as acive on TravisCI, and it must contain a file named `.travis.yml` located in the root of the repository. Assuming these criteria are met, TravisCI will then 'watch' the repository for changes and trigger a build whenever a change to the repository is made (the exact behavior of what to do is specified in the repository settings tab on the TravisCI dashboard). Once a build has been triggered, TravisCI boots up a virtual machine that executes commands as specified in `.travis.yml`. 

We structure TravisCI builds into three distinct stages; building preCICE, building adapters, and tests. Details of each stage are outlined below.


The python and bash scripts located in the systemtests root directory each serve a specific task regarding the building/pushing/testing of dockerfiles. Here a short list of them and their respective purposes:

- `build_precice.py`: Builds preCICE dockerimages.
- `push_precice.py`: Pushes preCICE dockerimages to DockerHub.
- `build_adapter.py`: Builds adapter dockerimages.
- `push_adapter.py`: Pushes adapter dockerimages to DockerHub.
- `system_testing.py`: Core script for tests. Manages the docker environment for testing and compares output of test to reference using utility scripts.
- `silent_compose.sh`: Utility for `system_testing.py`. Sets up the docker test environment. 
- `compare_results.sh`: Utility for `system_testing.py`. Compares textual and numeric data between two folders.
- `push.py`: Utility script that pushes data to `precice_st_output`. Mainly used for storing/accessing reference data when debugging.
- `local_test.py`: Wrapper script for running systemtests on local machine. This is not used by the CI platform.
- `trigger_systemtests.py`: Sends a build request to TravisCI. Mostly used from adapter repositories in order to trigger a build on systemtests.
- `generate_test.py`: Utility script that generates files/directories for a new test.
- `docker.py | common.py`: Modules containing docker-related functions | general functions respectively. Used by other scripts.


## Building preCICE

In this stage we pull and install the latest preCICE version from the precice-repository. Since we wish to test multiple operating systems (Ubuntu 18.04/20.04, Arch Linux) and specifications ( install method, MPI version, settings/flags used when installing precice ), we create multiple images with their names specifying the set of architecture and properties used. Images are of the following format:
```
precice/precice-{architecture}.{property1}.{property2}.{property3}-{precice branch}
```
For this purpose, we also use different dockerfiles located in the `precice` directory of this repository. These dockerfiles contain arguments we can set at build time to further adjust the installation, meaning that one dockerfile is used for creating mutliple different preCICE images. Names of dockerfiles are formatted as `Dockerfile.{architecture}.{property1}.{property2}.{property3}`.

Upon successful build, the resulting images are then pushed to the [Dockerhub/precice](https://hub.docker.com/u/precice).

## Building adapters

Here, we now start from a baseimage that has preCICE already installed and install a specific adapter on top of it. The adapters all have their own dockerfiles, as they generally have different prerequisites.

---
**Important note: building solvers**

Some adapters require us to install their corresponding solver before beginning the install of the adapter itself. For some versions of the adapters, this can be a quite lengthy process, meaning that we would like to 'skip' this step when building adapters (as this adds unnecessary build time). For this purpose, we sometimes 'pre-build' a dockerimage with the solver installed on it, and then copy the installed solver into our adapter dockerfile when actually building the adapter. The dockerfiles for these pre-installs are stored in the `solver` directory, though note that currently they are not incorporated in the TravisCI building procedure; instead these only need to be built once (usually on a local machine and then pushed to the dockerhub from there) and are only rebuilt when we wish to change the version of the solver. 

Only some of the solver-dockerfiles are currently in use, we decide on a case by case basis if we prefer the decreased build time of using a prebuild solver or the convenience/simplicity of having the adapter-dockerfile install the solver itself.

---

To build an adapter we follow a two-stage build, first importing from the preCICE image and then importing from the solver's image (optional). Which preCICE base image to import from is specified by using the `from`
argument during building of the image, e.g:
```
docker build --build-arg from=precice/precice-ubuntu1804.home-develop -d Dockerfile.openfoam-adapter -t openfoam-adapter-ubuntu1804.home-develop .
```

The adapers mostly require different installation methods, below a rough description of how to build each adapter:

- **SU2 adapter**
  Since the SU2 adapter modifies the SU2 source code, it makes no sense to copy a clean SU2 build from an external solver image, since we need to rebuild it anyways. Instead, we clone the SU2 source and build it here. Currently, we are using the fixed SU2 version `v6.0.0`.

- **deal.II adapter**
  deal.II is a library and the adapter just needs to link to it. Thus, we import a pre-built deal.II solver image and build only the adapter in the dockerfile. Note that at time of building we are required to set the number of dimensions the adapter is built for. Since we run tests both for 2D- and 3D-scenarios, we have to build two separate adapter images.
  
- **CalculiX adapter**
  We only import the necessary libraries (Spooles, ARPACK), since the CalculiX adapter modifies the CalculiX source code. We use the fixed version `2.16`.
  
- **OpenFOAM adapter**
  Since we began using mainly OF v2006, the installation process is now simple enough that we choose to perform it directly in the adapter dockerfile. Prior to this, we were copying OF5 from a solver image.
  
- **Nutils adapter**
  The Nutils adapter is simply a Python script with Nutils and preCICE for a particular test case. As a result, there is nothing to be done at this build stage. We only provide a Dockerfile for the running the test in the next stage.

- **FEniCS adapter**
  We install the FEniCS solver together with the FEniCS adapter when building.
  
- **CodeAster adapter**
  Here we again use a prebuilt image of the solver named `precice/codeaster` and only perform the adapter install.


All adapters are built by user `precice` with `gid` and `uid` equal to 1000 (by default) and member of  the `precice` group. At the end of the install we also create a structure of folders:`/home/precice/Data` and `/home/precice/Logs` in each of the adapters.
This is done to ensure consistent user rights for writing and reading from mounted directories without a need to use root user on the host system. Running root within container *will work*, but will lead to output directory being owned by root on host. Running with different users in different directories will cause problems with access to e.g. `/home/precice/Data/Exchange` directory. More information and motivation behind the solution can be found [this blogs post](https://medium.com/@nielssj/docker-volumes-and-file-system-permissions-772c1aee23ca) and [this issue](https://github.com/moby/moby/issues/2259).

## Running tests

At this stage, we spawn containers with the necessary solvers for the simulation. The execution is controlled using [docker-compose](https://docs.docker.com/compose/). Separate volumes are created for the input and the output of every adapter. An additional docker network is created and used for the communication between containers. Exchange of data is done using an additional, common volume. The general pattern across the tests for such volumes are paths
such as `/home/precice/Data/Exchange`, `/home/precice/Data/Input`, `/home/precice/Data/Output`, which were mentioned above.

The tests are based on the corresponding tutorials from the [tutorials repository](https://github.com/precice/tutorials). Since tests run using independent containers, several modifications are necessary to split the input to solvers in different directories, to adjust the simulated time, or to potentially change a solver's version, as well as to modify the `precice-config.xml` for the communication pattern we use in docker. This is mainly done using the `Dockerfile.tutorial_data` image, which clones the tutorial data and adjusts the input to different solvers. It is then used as the first container spawned by `docker-compose`, followed by containers for each of the tutorial participants. In general, the test then runs by having the participant containers computing their respective tasks and the `tutorial_data` container serving as central setup location and data storage.

Afterwards, when the simulation finishes, the output is copied from all the solvers into the common volume. The testing script then extracts this data from the docker containers and compares them to the reference output using `compare_results.sh`. An error is thrown if they don't match.

The comparison goes as follows:
- First, check scan the output files to determine if an are missing and if the files differ at all. If the content of a file fully matches its respective reference, it will not be considered in further steps.
- After finding all non-matching files, compare these more thoroughly. There are numerous file differences which we expect to happen; time-stamps, dates, memory adresses, small floating point differences due to running on a different machine or OS. These, however, should not flag a test as failure. The script thus checks the file for textual and numerical differences and filters out any keywords that signify a values we expect to vary beforehand. This then leaves a comparison of filtered text and filtered numbers. For the latter we specifically compute the largest difference observed in a single entry and the overall average of differences. If these exceed their specified relative tolerance (default 0.1 percent), an error is thrown.

In either case, after a test finishes, all the related volumes, networks and containers are removed.
