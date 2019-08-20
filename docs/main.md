# General architecture 

Tests are executed in several stages: 

## Building preCICE

Several images of preCICE are built, based on different system (Ubuntu 16.04/18.04, Arch Linux) and different specifications
of properties of the image ( root/non-root, package, different MPI versions ). This corresponds to the `Dockerfile.$systemname$.${system_spec}`
Resultant images are then pushed to the dockerhub.

## Building solvers 

Is done once for every solver, using `Dockefile.${solver_name}`. Resultant images are then stored on the dockerhub.

## Building adapters

To build the adapter we follow two-stage builds, first importing from the preCICE image then from the solvers image (if the solvers image is
actually relevant for building the adapter). We can import from different preCICE base images by specifying `from` argument during building of the
the image, e.g:
```
docker build --build-arg from=precice/precice-ubuntu1804.home-develop -f Dockerfile.openfoam-adapter -t openfoam-adapter-ubuntu1804.home-develop .,
```
Note, that due to the fact that different adapter 'adapts' differently, the general procedure is slightly
different and is outlined below: 

- **SU2 adapter**

  Since SU2 adapter modifies SU2 source code, it makes no sense to copy clean SU2 build, because it will need to be rebuilt. Instead we just build the adapter
  from  SU2 source after applying the necessary modifications.

- **dealii adapter**
-
  Since **dealii** is a library and the adapter just needs to link with it, here we actually perform the import of **dealii** image and only build
  the actual adapter

- **CalculiX adapter**
  We only import the necessary libraries (Spooles, ARPACK), since CalculiX adapter modifies CalculiX source.

- **openFOAM adapter**
  Same as for deal.ii adapter.

- **Nutils adapter**
  There is no Nutils adapter. There is python script that communicates with Nutils and preCICE. We therefore provide Dockefile for it just for the where it is used,
  and don't build during adapter building stage, but during test running stage.

- **FEniCS adapter**
  We install FEniCS, together with adapter using `Dockefile.fenics-adapter` file.
  

All adapters are built using user `precice` with `gid` and `uid` equal to 1000 and of `precice` group. As a last build stage they create folder for the volume mapping in 
`/home/precice/Data` folder.

## Running tests

At this stage, we spawn containers with the necessary solvers for the simulation. The execution is controlled using [docker-compose](https://docs.docker.com/compose/). Separate volumes are created for the input and the output of every adapter. Additional docker network is created and used for the communication between containers. Exchange of the data is done using another common volume. The general pattern across of the tests for such volumes to have locations '/home/precice/Data/Exchange', '/home/precice/Data/Input',
'/home/precice/Data/Output', as explained above.

The tests are based on the corresponding tutorials from the [tutorials repository](https://github.com/precice/tutorials). Several modifications are necessary to decouple the input to solvers, adjust simulation time, or change solver version and to modify `precice-config.xml` for simulation with docker. This is done with `Dockerfile.tutorial_data` image, that clones the tutorial data, adjusts and splits the input to different solvers. It is then is used as first container spawned by `docker-compose`.

Afterwards, when the simulation finishes the output is copied from all the solvers into the common volume and compared to the reference output. An error is thrown if they don't match. In either case after tests finishes, all volumes, networks and containers are removed.
