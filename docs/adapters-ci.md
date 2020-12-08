
# Continuous Integration on adapter repositories

This file documents the use of the `trigger_systemtests.py` script, which ensures continuous integration for adapters. This primarily means that adapter repositories can create build testing their current code (including different branches
and pull request versions) without unnecessary code duplication. In order to understand this section in depth, one should read through the `trigger_systemtests.py` script as well (though starting with this document is probably more helpful).

## Triggering a TravisCI build from the adapter

In order not to duplicate and store systemtest code on each of the adapter repositories, we instead reuse the testing system provided here. This is done by employing the Travis API to trigger Travis builds of selected test subsets from this systemtests repository after performing a commit on an adapter repository. 

For this purpose, we use the `trigger_systemtests.py` script to generate custom JSON with fitting job specifications and sending it to TravisCI. If executed correcty, this triggers a build to start on the systemtests page on TravisCI. For an overview of build triggering and custom jobs see [this page](https://docs.travis-ci.com/user/triggering-builds/).

To illustrate the process of triggering a build, let's look at the operations in chronological order using [this example from the fenics-adapter repository](https://travis-ci.org/github/precice/fenics-adapter/builds/741877203):

1. Firstly, a [change is commited on the adapter repository](https://github.com/precice/fenics-adapter/commit/71c6941fdb96de69bab139b706d66db228075737).

2. TravisCI picks up on this commit and [initiates a build on the adapter repository](https://travis-ci.org/github/precice/fenics-adapter/builds/741877203). Note that this requires two things: the adapter repository must be listed as active in the TravisCI precice dashboard and the repository [must contain a `.travis.yml` file for TravisCI to execute](https://github.com/precice/fenics-adapter/blob/71c6941fdb96de69bab139b706d66db228075737/.travis.yml).

3. TravisCI [boots up a machine to execute the instructions in the adapters `.travis.yml` file](https://travis-ci.org/github/precice/fenics-adapter/builds/741877203). These contain a command to pull one file, `trigger_systemtests.py`, from the precice/systemtests repository and call it with a certain set of arguments that is specific to this adapter. Note that this step is performed on the TravisCI page of the adapter, not on systemtests!

4. The TravisCI machine creates a JSON-formatted request to build a job on precice/systemtests and sends it to Travis. The request contains a simplified build job of two stages:
- Building the adapter
- Running tests in which the adapter participates

    This request is then received and upon parsing creates a [second, independent build that runs on precice/systemtests](https://travis-ci.org/github/precice/systemtests/builds/741879219). After sending the request, the original adapter build will either exit immediately or stall until it hears back from the triggered systemtests build before stopping. This behavior is dictated [by the `--wait` flag, which if set will cause the build to wait until the systemtests one is resolved](https://github.com/precice/fenics-adapter/blob/71c6941fdb96de69bab139b706d66db228075737/.travis.yml#L10).

5. Depending on the result of the triggered build, the original adapter build will either fail or succeed.

    *Note:  that if we omit`--wait`, this build will immediately exit as 'success' before the actual build on systemtests resolves. In this case, the systemtests build will contain an additional command at its end that causes it to send back another build request to the original adapter repository. This third build only contains the command `return false` and thus serves as notification that the systemtests build corresponding to the commit has failed. (This is quite hacky and in practice never used, as we mostly use `--wait` in the adapters. If someone plans to build upon this feature, it is probably best to find a simpler way to achieve this callback.)*

## Running on different branches/pull requests

During the adapters TravisCI job, the `trigger_systemtests.py` script checks if it is running on non-master-branch/pull-request-branch  (using the `TRAVIS_BRANCH` and `TRAVIS_PULL_REQUEST` environment variables). If that is the case, the generated JSON file is patched with additional bash script calls that modify the adapters Dockerfile with additional instructions (such that it checks out the correct branch before cloning the repostory, for instance).

The resulting adapter image is then tagged with the name of the branch/pull request and pushed to [DockerHub](https://hub.docker.com/u/precice). This is done to prevent the PR image from overwriting other images (e.g. the regularly used `develop` variant of the adapter). The test that follows after building the adapter will use this special image variant. More specifically, the tag is determined in `docker-compose.yml` with the `{${SOLVER_NAME}_TAG}` variable (defaults to `latest`).

## Adding CI for the adapter's repository

When setting up a new adapter to use the systemtests CI, the following modifications need to be made:

- [The adapter repository must be activated on TravisCI](https://docs.travis-ci.com/user/tutorial/#to-get-started-with-travis-ci-using-github).

- A `.travis.yml` file must be generated in the adapter repository. For illustration purposes let us consider [the fenics-adapter implementation of `.travis.yml`](https://github.com/precice/fenics-adapter/blob/71c6941fdb96de69bab139b706d66db228075737/.travis.yml) as an example:

    ```yaml
    matrix: 
      include: 
      - os: linux
        name: "Systemtests"
        if: fork = false AND ( branch = master OR branch = develop )
        python: "3.6" 
        env: PY=python3
        script:
        - curl -LO --retry 3 https://raw.githubusercontent.com/precice/systemtests/develop/trigger_systemtests.py
        - travis_wait 60 $PY trigger_systemtests.py --adapter fenics --wait
    ```

    You don't have to match this exact format when creating your own `.travis.yml` file, but make sure that the following lines are included:
    
    1. `if: fork = false AND ( branch = master OR branch = develop )`: this ensures that tests only run from the original repository (non-fork) and only if the commits are made to `master`/`develop` or a PR which targets these branches.
        
    2. `- curl -LO --retry 3 https://raw.githubusercontent.com/precice/systemtests/develop/trigger_systemtests.py`: this pulls the latest `develop` version of `trigger_systemtests.py` for use in the adapter repository.
        
    3. `- travis_wait 60 $PY trigger_systemtests.py --adapter fenics --wait` launches the request for the fenics-adapter with the `--wait` flag. Note that `travis_wait 60` is not necessary.

- A specification for the adapter must be added into the `adapter_info` dictionary in `trigger_systemtests`.

- A `TRAVIS_ACCESS_TOKEN` for the TravisCI precice user must be added as [environment variable in the adapters repository](https://docs.travis-ci.com/user/environment-variables/#defining-variables-in-repository-settings). This is required for the request to be permitted. You can find the token under the [Travis profile page](https://travis-ci.org/account/preferences).
