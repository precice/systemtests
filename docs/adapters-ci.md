
# Continuous Integration on adapters repositories

This file documents solution that ensures continuous integration for adapters, including different branch
and pull requests without unnecessary code duplication.

## Triggering the build from the adapter

In order not to duplicate tests on different adapters, and to reuse functionality provided here, we use the Travis API
to trigger selected tests present in this repository after commits to the adapters repositories. This is done by
generating custom JSON with specification of the job and sending it to the Travis that triggers the build on this repository(For the overview of build triggering and custom jobs 
see [here](https://docs.travis-ci.com/user/triggering-builds/)).
Correspondingly, in order to send this request a simple Travis job needs to be present on adapters repository, so that it runs the main triggering script.
Once the tests are finished, their return status is queried/sent back (controlled by `--wait` argument) to the Travis job on the adapter repository. 
In case `--wait` flag is on, Travis job on adapter's repository essentially performs a blocking call, that does not return until tests finish (two running jobs 
will be then seen in Travis dashboard - one for systemtests and one for the adapter). Alternatively, non-blocking call is possible - in that case, in order to indicate
failure of the test, the script will trigger "failing job" on the adapters repository if the test fails.

You can learn more from `trigger_systemtests.py`, which handles all of described functionality.

Since we don't need to run a full set of tests, only the following stages are added when generating the JSON job configuration file:
- Building the adapter
- Running the tests in which it participates

## Running on different branches and pull requests

During the adapter's Travis job, if it is identified that the job is running on a pull request on a non-master branch (using the
`TRAVIS_BRANCH` and `TRAVIS_PULL_REQUEST` environment variables), the generated JSON filed is patched with additional bash script that modifies
the adapter Dockerfiles with additional instruction to switch to the needed branch (the instruction should be injected prior
to actually building an image).

The resulting image is then tagged with the name of the branch/pull request and pushed to [Dockerhub](https://hub.docker.com/u/precice). In the `docker-compose.yml` the image tag
is controlled using  `{${SOLVER_NAME}_TAG}`( defaults to `latest`). Similarly, this environment variables is also specified in the specification of the Travis job
for every solver participating in the test.

## Adding CI for the adapter's repository

Add specifications of the adapter into the `adapter_info` dictionary in `trigger_systemtests`.
Then, the only thing remaining is to add a `.travis.yml` file to the adapter's repository, such as:

    - if: branch = master
      script: |
        curl -LO --retry 3 https://raw.githubusercontent.com/precice/systemtests/master/trigger_systemtests.py
        python3 trigger_systemtests.py --adapter openfoam

We also need to add a `TRAVIS_ACCESS_TOKEN` in each adapter's repository, as a secure variable to authenticate the build triggering. This token can be
found on the [Travis profile page](https://travis-ci.org/account/preferences).
