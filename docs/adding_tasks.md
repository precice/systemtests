# How to add tasks

To add a new tasks to the Travis build, simply add a corresponding entry in the `.travis.yml` file in a fitting stage under the `jobs: include:` section. The current stages are `Building preCICE`, `Building adapters`, `Tests`.


An entry should at least contain `name` and `script` keys such that the job can be run by Travis and identified in the build log. In this example the additional `if` conditions avoids this job to execute if the build is running on a fork of the systemtests repository. Many more specifications are available if necessary, check the [Travis docs](https://docs.travis-ci.com/) for more info.

Most likely your preCICE build/adapter build/adapter test outputs some result data at the end, which in the case of precice- and adapter builds should be pushed to DockerHub using the respective `push_precice.py`/`push_adapter.py` scripts. On top of that, one can push a logfile recording the build status to the `precice_st_output` repository by calling `push.py`. If the performed job was a test, this `push.py` call can be augmented with the `-o` flag, which will also upload Output data to the repository (in addition to the logfile). Note that the `push.py` command makes use of information stored intermittently in `build_info.py`, which serves as a way to transmit information from scripts called earlier on in the command chain. This file is created by `push_precice.py`, `push_adapter.py` and `systemtesting.py`


Here is an example job we might run on TravisCI that builds the SU2 adapter:

```bash
    - stage: Building adapters
      name: "[18.04] SU2 adapter"
      if: fork = false
      script:
        - python build_adapter.py --dockerfile adapters/Dockerfile.su2-adapter --operating-system ubuntu1804 --precice-installation home --docker-username $DOCKER_USERNAME
        - python push_adapter.py --dockerfile adapters/Dockerfile.su2-adapter --operating-system ubuntu1804 --precice-installation home --docker-username $DOCKER_USERNAME
        - python push.py
```
The three script commands perform the following actions:
- `build_adapter.py` builds the adapter image. In this case, it will build a SU2-adapter image using the respective Dockerfile under `adapters`, using a baseimage of preCICE that is named `precice/precice-ubuntu1804.home-develop`. More generally, this baseimage is called `{docker-username}/precice-{operating-system}.{precice-installation}-{branch}`, whereby `docker-username` will be set to `precice` when running in TravisCI (as this is the value given by `$DOCKER_USERNAME`). `branch` is an optional argument that was not explicitly specified in this call, therefore it defaults to `develop`.
- `push_adapter.py` will push the respective adapter image, using a similar naming convention: `{docker-username}/{adapter-name}-{operating-system}.{precice-installation}-{branch}`, which in this case resolves to `precice/su2-adapter-ubuntu1804.home-develop`.
- `push.py` will upload a log of the build to `precice_st_output`.


In the case of a test, the command looks a little different. Here an example where we test OpenFOAM-OpenFOAM:

```bash
    - stage: Tests
      name: "[18.04] OpenFOAM <-> OpenFOAM"
      script:
        - python system_testing.py -s of-of -v
        - python push.py
```

In the case of a test, we generally only use two script commands:
- `systemtesting.py` will execute the test we specify using `-s`, in this case `of-of` (the script will then execute the test files found under `tests/TestCompose_of-of`). The verbose `-v` flag is optional and will cause the script to print the full output of each participant to the console (useful when debugging tests). If this flag is omitted, the script will instead only give periodic updates about the current simulation status.
- `push.py` will upload a log of the test to `precice_st_output`, similar as with adapter/precice builds. Additionally, you can add the output flag `-o` to the script call to also have it push the generated `Output` folder containing all result files. This allows you to check the output produced on the CI platform, which otherwise is inaccessible and will be deleted at the end of the job. Note that keeping this flag enabled for a long time will cause `precice_st_output` to store a lot of (possibly unnecessary) data.


## Need help setting up a job?

If you are experiencing any issues, don't hesitate to ask for assisstance on [Gitter](https://gitter.im/precice/Lobby) or [Discourse](https://precice.discourse.group/).
