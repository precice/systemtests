# preCICE System Tests
[![Build Status](https://travis-ci.org/precice/systemtests.svg?branch=master)](https://travis-ci.org/precice/systemtests)

System tests for the distributed multi-physics coupling library library preCICE

# Dependencies

* [preCICE](https://github.com/precice/precice)
* [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
    * Make sure you can run docker as non-root user (see [here](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user))
    * Test your docker installation with e.g. ```docker run hello-world```
* [docker-compose](https://docs.docker.com/compose/)
* ```python3``` 
    * With ```configparser``` (install for example with ```pip3 install configparser```)

## Run a system test

```
   python3 local_test.py -s of-of su2-ccx -f Dockefile.Ubuntu1604.home
``` 

More information can be found in the [docs](docs/))
