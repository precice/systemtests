# General architecture

When running on Travis tests are executed as specified in the file `.travis.yml` located in the root of the systemtests repository. The several stages of testing are outlined below.
If running a local tests (compared to the standard build on the Travis servers) the steps are identical, but the push to the remote DockerHub repository is absent.

## Building preCICE

Several images of preCICE are built, based on different systems (Ubuntu 16.04/18.04, Arch Linux) and different specifications
of properties of the image ( root/non-root, package, different MPI versions ). This corresponds to the `Dockerfile.$systemname$.${system_spec}`
Resulting images are then pushed to the [Dockerhub](https://hub.docker.com/u/precice).

## Building solvers

Is done once for every solver, using `Dockerfile.${solver_name}`.

Resulting images are then stored on the [Dockerhub](https://hub.docker.com/u/precice).

## Building adapters

To build an adapter we follow a two-stage build, first importing from the preCICE image and then importing from the solver's image
(if the solver's image is actually relevant for building the adapter).We can import from different preCICE base images by specifying `from`
argument during building of the image, e.g:
```
docker build --build-arg from=precice/precice-ubuntu1804.home-develop -d Dockerfile.openfoam-adapter -t openfoam-adapter-ubuntu1804.home-develop .
```
Note, that due to the fact that each adapter "adapts" differently, the general procedure is slightly different and is outlined below:

- **SU2 adapter**
  Since the SU2 adapter modifies the SU2 source code, it makes no sense to copy a clean SU2 build, because it will need to be rebuilt. Instead we directly build adapted
  SU2 source.

- **deal.II adapter**
  deal.II is a library and the adapter just needs to link to it. Thus, we perform the import of deal.II image and only build
  the adapter

- **CalculiX adapter**
  We only import the necessary libraries (Spooles, ARPACK), since the CalculiX adapter modifies the CalculiX source code.

- **OpenFOAM adapter**
  Same as for the deal.II adapter.

- **Nutils adapter**
  The Nutils adapter is a Python script with Nutils and preCICE for a particular test case. We therefore only provide a Nutils adapter Dockerfile for
 the test running stage (not for the building stage).

- **FEniCS adapter**
  We install FEniCS, together with the FEniCS adapter using `Dockerfile.fenics-adapter` file.


All adapters are built using user `precice` with `gid` and `uid` equal to 1000 (by default) and of `precice` group. As a last building stage they create folder for the file system volume mapping in `/home/precice/Data` folder.

This is done to ensure consistent user rights for writing and reading from mounted directories without a need to use root user on the host system. Running root within container will work, but will lead to output directory being owned by root on host. Running with different users in different directories will cause problems with access to e.g. `/home/precice/Data/Exchange` directory. More information and motivation behind the solution can be found [this blogs post](https://medium.com/@nielssj/docker-volumes-and-file-system-permissions-772c1aee23ca) and [this issue](https://github.com/moby/moby/issues/2259).

## The tests

The actual tests are provided in `systemtests/tests`. For testing, we spawn containers with the necessary solvers for the simulation. The execution is controlled using [docker-compose](https://docs.docker.com/compose/). Separate volumes are created for the input and the output of every adapter. An additional docker network is created and used for the communication between containers. Exchange of data is done using an additional, common volume. The general pattern across the tests for such volumes are paths such as `/home/precice/Data/Exchange`, `/home/precice/Data/Input`, `/home/precice/Data/Output`, as explained above.

The tests are based on the corresponding tutorials from the [tutorials repository](https://github.com/precice/tutorials). Since tests run using independent containers, several modifications are necessary to split the input to solvers in different directories, to adjust the simulated time, or to potentially change a solver's version, as well as to modify the `precice-config.xml` for the communication pattern we use in docker. This is done using the `Dockerfile.tutorial_data` image, which clones the tutorial data and adjusts and splits the input to different solvers. It is then used as the first container spawned by `docker-compose`.

Afterwards, when the simulation finishes, the output is copied from all the solvers into the common volume and is compared to the reference output. An error is thrown if they don't match.

Since it is possible for the output of two identical tests to differ in floating points due to a different machine or OS(as we test different systems and properties), after simple, file by file comparison of the output,
the files are also compared numerically using `compare_results.sh`. This script strips away non-numerical data and then compares files field by field with respect to a specified relative tolerance (default maximum allowed difference is 1 percent)

In either case after a test finishes, all the related volumes, networks and containers are removed.

### Required environment variables

The following environment variables are required for running the tests:

* `SYSTEST_REMOTE`: Specifies the user on Dockerhub from which the baseimage is pulled. Example: `precice/`
* `PRECICE_BASE`: Specifies the features of the baseimage used for running the test. Example: `ubuntu1604.home-develop` or `ubuntu1804.home-develop`
* `<PARTICIPANT>_TAG`: Specifies the tag that will be used for the baseimage for each of the participants. Example: `latest`

### Running the tests

There are two possibilities for running the tests:

1. Use `system_testing.py`: Go to `systemtests` and run `python3 system_testing.py -s <TESTCASE>` (e.g. `python3 system_testing.py -s fe-fe --base Ubuntu1804.home`). For more information on the script run `python3 system_testing.py --help`.
2. Use `docker compose up`: Go to the corresponding test (e.g. `systemtests/tests/TestCompose_fe-fe.Ubuntu1804.home`) and run `docker-compose up`. Note that `.env` defines the previously mentioned environment variables required for running the tests.
