# General architecture

When running on Travis tests are executed in the several stages that are outlined below. 
When it comes to local tests, steps are identical, but the push to the remote dockerhub repository is absent.

## Building preCICE

Several images of preCICE are built, based on different systems (Ubuntu 16.04/18.04, Arch Linux) and different specifications
of properties of the image ( root/non-root, package, different MPI versions ). This corresponds to the `Dockerfile.$systemname$.${system_spec}`
Resultant images are then pushed to the [Dockerhub](https://hub.docker.com/u/precice).

## Building solvers

Is done once for every solver, using `Dockefile.${solver_name}`. Resultant images are then stored on the [Dockerhub](https://hub.docker.com/u/precice).

## Building adapters


To build an adapter we follow a two-stage build, first importing from the preCICE image and then importing from the solver's image
(if the solver's image is actually relevant for building the adapter).We can import from different preCICE base images by specifying `from` 
argument during building of the image, e.g:
```
docker build --build-arg from=precice/precice-ubuntu1804.home-develop -f Dockerfile.openfoam-adapter -t openfoam-adapter-ubuntu1804.home-develop .
```
Note, that due to the fact that each adapter "adapts" differently, the general procedure is slightly different and is outlined below:

- **SU2 adapter**
  Since the SU2 adapter modifies the SU2 source code, it makes no sense to copy a clean SU2 build, because it will need to be rebuilt. Instead we directly build adapted
  SU2 source.

- **deal.II adapter**
  Since deal.II is a library and the adapter just needs to link with it, here we actually perform the import of deal.II image and only build
  the adapter

- **CalculiX adapter**
  We only import the necessary libraries (Spooles, ARPACK), since the CalculiX adapter modifies the CalculiX source code.

- **OpenFOAM adapter**
  Same as for the deal.II adapter.

- **Nutils adapter**
  The Nutils adapter is a Python script with Nutils and preCICE for a particular test case. We therefore only provide a Nutils adapter Dockefile for
 the test running stage (not for the building stage).

- **FEniCS adapter**
  We install FEniCS, together with the FEniCS adapter using `Dockefile.fenics-adapter` file.


All adapters are built using user `precice` with `gid` and `uid` equal to 1000 and of `precice` group. As a last building stage they create folder for the file system volume mapping in
`/home/precice/Data` folder.

## Running tests

At this stage, we spawn containers with the necessary solvers for the simulation. The execution is controlled using [docker-compose](https://docs.docker.com/compose/). Separate volumes are created for the input and the output of every adapter. An additional docker network is created and used for the communication between containers. Exchange of data is done using an additional, common volume. The general pattern across the tests for such volumes are paths
such as `/home/precice/Data/Exchange`, `/home/precice/Data/Input`, `/home/precice/Data/Output`, as explained above.

The tests are based on the corresponding tutorials from the [tutorials repository](https://github.com/precice/tutorials). Several modifications are necessary to split the input to solvers in different directories,
to adjust the simulated time, or to potentially change a solver's version, as well as to modify the `precice-config.xml` for the communication pattern we use in docker. This is done using the `Dockerfile.tutorial_data` image, which clones the tutorial data and adjusts and splits the input to different solvers. It is then used as the first container spawned by `docker-compose`.

Afterwards, when the simulation finishes, the output is copied from all the solvers into the common volume and is compared to the reference output. An error is thrown if they don't match.

Since it is possible for the output of two identical tests to differ in floating points due to a different machine or OS(as we test different systems and properties), after simple, file by file comparison of the output,
the files are also compared numerically using `compare_results.sh`. This script strips away non-numerical data and then compares files field by field with respect to a specified relative tolerance.

In either case after a test finishes, all the related volumes, networks and containers are removed.
