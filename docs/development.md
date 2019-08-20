# Useful documentation

* [Docker](https://docs.docker.com/)
* [Docker-compose](https://docs.docker.com/compose/)
* [Main Travis docs](https://docs.travis-ci.com/)
* [Travis API](https://developer.travis-ci.com/)


# Useful patterns and commands
##  During development of standalone Dockerfiles

If something fails during the build you can determine the command where it failed and comment out the remaining of the Dockerfile. Then rebuild and tag for instance `test_image`. You can then interactively try to follow commented out section of the Dockerfile, by starting the container interactively
```
   docker run -it --rm test_image /bin/bash
```
Usually in this way or similar it is way easier to debug errors.

## During development of the test cases

If something fails during running `docker-compose` due to communication problems or invalid input, the easiest way to debug is:

1. Add sleep timer (e.g. `sleep 1000`) after running failed command
2. Rerun the failed setup
3. Attach to the failed container with e.g.
```
   docker-compose run -it calculix-adapter
```
4. You can then try to rerun command in `docker-compose.yml` and check the folders `/home/precice/Data/Input`, `/home/precice/Data/Exchange`, `/home/precice/Data/Output`. Make sure the `precice-config.xml` is properly setup, input can be read and folders have proper rights.

You should also try to make sure, both runs on local and remote machine works by testing both `local_test.py` and `system_testing.py` with the considered test case.

## If something fails on Travis

1. Inspect the build log
2. Restart the build (maybe it is a connection problem)
3. Try to replicate it locally with e.g.
```
   python3 system_testing.py -s su2-ccx
``` 
4. If it fails locally, use above-mentioned techniques to debug it. If is does not, bad luck. 

## If there are some network problems

It can happen, that you cannot access the network from the inside of docker. You can try to fix it using `--network=host` during build of docker images or by specifying `network: host` in the `docker-compose.yml`.


## If CI on adapters does not work

You first need to add `TRAVIS_ACCESS_TOKEN` as environment variable on your system.
Then you can  run and check generated JSON file without sending a request
```
   python3 trigger_systemtests.py --adapter su2 --test
``` 
If it looks fine, you can run it without `--test` to actually send the request to Travis. Then check triggered builds.
If there are no builds visible there, check `requests` section of Travis, maybe Travis could not interpret request correctly.
