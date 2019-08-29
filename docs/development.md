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
4. You can then try to rerun command in `docker-compose.yml` and check the folders `/home/precice/Data/Input`, `/home/precice/Data/Exchange`, 
`/home/precice/Data/Output`. Make sure the `precice-config.xml` is properly setup, input can be read and folders have proper rights (folders should be
owned by user `precice`, not the `root` user and not the user of your local machine, unless its `gid` and `uid` matches the one specified in the base Dockerfile)

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

## If you want to use Dockefiles for your own development

Some users might want to run coupled simulation without having it installed on your own machine. 
For instance mount your own input for each adapter to `/home/precice/Data/Input` and get output from
`/home/precice/Data/Output`.

With the provided setup and a few tweaks it is easy to achieve. On the example of the fenics-adapter:

```
docker build -f Dockerfile.Ubuntu1804.home -t precice-user --build-arg uid=$UID --build-arg gid=$GID . 
docker build -f Dockerfile.fenics-adapter -t fenics-adapter-user --build-arg from=precice-user
```

where `GID` and `UID` are you group id (obtained e.g. with `id -a` on Linux).

Then you need to create volume for data exchange and modify `precice-config.xml`, so that data exchange folder 
is `/home/precice/Data/Exchange` and network is `eth0`.

```bash
docker volume create exchange
# this regex might differ depending on your precice-config.xml
sed -i 's|exchange-directory\="."|exchange-directory="/home/precice/Data/Exchange/" network="eth0"|g' \
    configs/precice-config.xml && cp $tutorial_path/config.yml  configs/config.yml
```

Then you are free to run your coupled simulation for each participant with:
```
docker run --user=precice -it -v $(pwd)/HT/partitioned-heat/fenics-fenics:/home/precice/Data/Input -v exchange:/home/precice/Data/Exchange fenics-adapter-user /bin/bash```
```
output can then be copied from the containers.
