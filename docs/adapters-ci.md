
# General architecture 

## Triggering the build from the adapter 

In order not to duplicate tests on different adapters, and reuse functionality provided here, Travis API 
is used to trigger selected tests from this repository after commits to the adapters repositories. This is done by
generating custom JSON with specification of the job and sending it to the Travis that triggers the build. Once the tests are finished
their return status is queried/sent back (controlled by `--wait` argument) to the Travis job on the adapter repository, making it fail/pass, depending on the return status.
You can learn more from `trigger_systemtests.py`, that handles all job generation and triggering.

Since we don't need run full set of tests, when generating JSON only following stages are added:
- Building the adapter 
- Running the tests in which it participates

## Running on different branches and pull requests

During the Travis job on the adapter if it is identified, that the job is running on pull request on non-master branch (using 
`TRAVIS_BRANCH` and `TRAVIS_PULL_REQUEST` environment variables), the JSON is patched with additional bash script that modifies
the adapter Dockerfiles with additional instruction to switch to the needed branch (obviously the instruction is injected prior 
to actually building an image).

The resultant image is then tagged with the name of the branch/pull request and pushed to the Dockerhub. In the `docker-compose.yml` the image tag 
is controlled using  `{${SOLVER_NAME}_TAG}`( defaults to `latest`). Similarly this environment variables is also specified in the specification of the Travis job
for every solver participating in the test.

## Adding CI on the adapter

Add specifications of the adapter to the `adapter_info` dictionary in `trigger_systemtests`.
Then the only thing remaining is to add `.travis.yml` to the adapter:

    - if: branch = master
      script: |
        curl -LO --retry 3 https://raw.githubusercontent.com/precice/systemtests/master/trigger_systemtests.py
        python trigger_systemtests.py --adapter openfoam

We also need to add `TRAVIS_ACCESS_TOKEN` in each adapter repository as a secure variable to authenticate build triggering. It can be found on the [Travis profile page](https://travis-ci.org/account/preferences).
