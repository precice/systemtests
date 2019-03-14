# Architecture

The architecture of the system tests consist out of two layers.
The interface between the layers are docker images.

## Grammar

```
// terminals
System         = string
TestClass      = string
Feature        = string
Dockerfile     = "Dockerfile"
TestPrefix     = "Test"
.              = "."
_              = "_"

// Non-terminals
SystemSpec     = System [. Feature]*
Base           = Dockerfile . SystemSpec
TestSpec       = TestClass | TestClass SystemSpec
Test           = TestPrefix _ TestSpec
```

## Base Images

### Naming Convention: 
Described by Grammar: `Base`

Examples:
```
Dockerfile.Ubuntu1804
Dockerfile.Ubuntu1804.Boost160
Dockerfile.Ubuntu1804.NoPETSc
Dockerfile.Ubuntu1604
Dockerfile.Ubuntu1604.Boost160
```

### Responsibilities:
The image needs to provide:
1) Software:
    1) `cmake`
    2) `make`
    3) `git`
    4) a C++ compiler
    5) MPI binaries
    6) `python3`
    7) `python3-dev`
    8) `pip`
2) all dependencies necessary to build and use preCICE
3) a user `precice` with a home directory containing:
    * `src` a checkout of the git repository
5) a discoverable install of preCICE:
    * `pgk-config --exist precice` returns true
    * `#include <precice/SolverInterface.hpp` has to work either out-of-the-box or by passing the flag `-I` using pkg-config.
    * `ld -lprecice` has to work either out-of-the-box or by passing the flag `-L` using pkg-config.
    * `binprecice` and `testprecice` have to be in `PATH`
    * `PRECICE_ROOT` hast to be set so that at least `runprecice` will be able to run the tests.

_Optional: after building preCICE, the "base" test-set has to be executed with `make test_base`!_

## Tests

### Naming Convention: 
Described by Grammar: `Base`

Examples:
```
Test_of-of
Test_of-of.Ubuntu1804
Test_of-of.Ubuntu1804.Boost160
Test_su2.Ubuntu1604
```

### Matching Logic:

Base images will be matched against Tests in the following way:
* For each `Base` image:
  * For each `TestClass`:
    * For each `Test` with matching `TestClass` and existing `SystemSpec`:
      * if `Test` and `Base` have matching `SystemSpec`
        * run the test
      * else if `Base` `SystemSpec` has `Features`:
        * drop a feature and repeat matching
      * else run Test with matching `TestClass` without `SystemSpec`

### Restrictions:
* Run commands as user `precice`
* Use `pip install --user` to install python dependencies
* Avoid using `apt-get` or other system specify package managers
* Do not use system specify package manager in a `Test` without `SystemSpec`

### Responsibilities:

* A failing `RUN` marks the test as failed.
* Do not fail silently!
