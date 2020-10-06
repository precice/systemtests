# Useful documentation

* [Docker](https://docs.docker.com/)
* [Docker-compose](https://docs.docker.com/compose/)
* [Main Travis docs](https://docs.travis-ci.com/)
* [Travis API](https://developer.travis-ci.com/)


# Useful patterns and commands
##  During development of standalone Dockerfiles

If something fails during building, you can determine the failing command and comment out the remaining of the Dockerfile. Then, rebuild and tag (e.g. `test_image`). You can then interactively try to follow the commented out section of the Dockerfile, by starting the container interactively:
```
   docker run -it --rm test_image /bin/bash
```
Usually it is much easier to debug in this way.

If you are developing a new base image for preCICE, make sure you create a user `precice`, in group `precice` with `uid` and `gid` equal to 1000, as done in
other base dockerfiles. Additionally, make sure that precice in installed in `/home/precice/precice`, and create folders `/home/precice/Data/Exchange`,
`/home/precice/Data/Input` and `/home/precice/Data/Output`, that should be owned by `precice` user.

## During development of the test cases

There is a `generate_test.py` script provided, that make is easier to generate all the necessary docker configuration files. Make sure to read through the generated files,
make sure it suits your test case and adjust where needed.

If something fails during running `docker-compose` due to communication problems or invalid input, the easiest way to debug is:

1. Add a sleep timer (e.g. `sleep 1000`) after running failed command
2. Rerun the failing setup
3. Attach to the failing container with e.g.
```
   docker-compose run -it calculix-adapter
```
4. You can then try to rerun the commands in `docker-compose.yml` and check the folders `/home/precice/Data/Input`, `/home/precice/Data/Exchange`,
`/home/precice/Data/Output`. Make sure the `precice-config.xml` is properly setup, input can be read and folders have proper rights (folders should be
owned by user `precice`, not the `root` user and not the user of your local machine, unless its `gid` and `uid` matches the one specified in the base Dockerfile)

You should also make sure that running both on a local and a remote machine work, testing both `local_test.py` and `system_testing.py` with the considered test case.

## If something fails on Travis

1. Inspect the build log
2. Restart the build (maybe it is a connection problem)
3. Try to replicate it locally with e.g.
```
   python3 system_testing.py -s su2-ccx
```
4. If it fails locally, use above-mentioned techniques to debug it. If is does not, bad luck.

## If a systemtest request fails with 'HTTP Error 403: Forbidden'

It might happen at some point that the `trigger_systemtests.py` script responsible for triggering builds through the Travis API starts to fail with the error above. This could happen due to the `TRAVIS_ACCESS_TOKEN` expiring and is potentially easy to fix. To renew the token, generate a new one locally using the Travis CLI (taken from [here](https://blog.travis-ci.com/2013-01-28-token-token-token)):

```
gem install travis && travis login && travis token
```

and replace the current `TRAVIS_ACCESS_TOKEN` value in the TravisCI systemtests dashboard.

## If there are network problems

It can happen, that you cannot access the network from the inside of docker. You can try to fix it using `--network=host` during build of docker images or by specifying `network: host` in the `docker-compose.yml`. You might also want to add this parameter in `build_image` function in `docker.py`.


## If CI on adapters does not work

You first need to add `TRAVIS_ACCESS_TOKEN` as environment variable on your system.
Then you can  run and check the generated JSON file without sending a request
```
   python3 trigger_systemtests.py --adapter su2 --test
```
If it looks fine, you can run it without `--test` to actually send the request to Travis. Then check the triggered builds.
If there are no builds visible there, check the `requests` section of Travis, maybe Travis could not interpret the request correctly.

## If you want to use Dockerfiles for your own development

Some users might want to run coupled simulations without having everything installed on the same system.
For instance mount input folders from your machine to `/home/precice/Data/Input` in the container and get output from
`/home/precice/Data/Output`.

With the provided setup and a few tweaks this is easy to achieve. Using the example of the fenics-adapter:

```
docker build -f Dockerfile.Ubuntu1804.home -t precice-user --build-arg uid=$UID --build-arg gid=$GID .
docker build -f Dockerfile.fenics-adapter -t fenics-adapter-user --build-arg from=precice-user
```

where `GID` and `UID` are you group id (obtained e.g. with `id -a` on Linux).

Then you need to create a volume for data exchange and modify `precice-config.xml`, so that the data exchange folder
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
Output can then be copied from the containers.

## If you want to run the tests based on code from a non-default branch

Depending on the test case several code components are used (preCICE, bindings, adapter(s), tutorial). Sometimes it becomes necessary to use a branch that is different from the one that is used as default (e.g. `develop` is used for the preCICE images. See [here](https://github.com/precice/systemtests/blob/ec4ef9d4aedd0087dfb3a8ed98fdf7a1267c7751/precice/Dockerfile.Ubuntu1604.home#L50-L52)).

### Non-default branch for preCICE 

If you want to use a different branch for the preCICE image, you can just use the [`--branch` option](https://github.com/precice/systemtests/blob/master/system_testing.py#L178) when you run `system_testing.py`.

### Non-default branch for other components

For other components we do not have a nice interface (see https://github.com/precice/systemtests/issues/121). However, there is a workaround:

We want to use the branch `feature` of the FEniCS adapter instead of the default branch `master` for the test `fe-fe`. We only want to run the test locally on our machine. 

1. We have to modify the `Dockerfile` correspondingly to use the branch `feature`.
2. Make sure that the modified `Dockerfile` is used to build the image `precice/fenics-adapter-ubuntu1804.home-develop`. 
```
$ docker image build -t precice/fenics-adapter-ubuntu1804.home-develop -f Dockerfile.fenics-adapter --build-arg from=precice/precice-ubuntu1804.home-develop .
```
3. The modified image will then be used in the test (see [here](https://github.com/precice/systemtests/blob/ec4ef9d4aedd0087dfb3a8ed98fdf7a1267c7751/tests/TestCompose_fe-fe.Ubuntu1804.home/docker-compose.yml#L19)), if we run the test locally.
```
$ python3 system_testing.py -s fe-fe --base Ubuntu1804.home
```

*Note:*

If you really want to make sure that you do not use the wrong images, you can also use the hash (something like `c5f77b336bcb`) that you get from `docker image list` instead of the tag `precice/fenics-adapter-ubuntu1804.home-develop`

```
$ docker image list
REPOSITORY                                                 TAG                 IMAGE ID            CREATED             SIZE
precice/fenics-adapter-ubuntu1804.home-develop             latest              c5f77b336bcb        2 minutes ago       1.68GB
```

Use it in the docker compose file [`systemtests/tests/TestCompose_fe-fe.Ubuntu1804.home/docker-compose.yml`](https://github.com/precice/systemtests/blob/ec4ef9d4aedd0087dfb3a8ed98fdf7a1267c7751/tests/TestCompose_fe-fe.Ubuntu1804.home/docker-compose.yml#L19)

change
```
image: "${SYSTEST_REMOTE}fenics-adapter${PRECICE_BASE}:${FENICS_TAG}"
```
to
```
image: "c5f77b336bcb"
```
