# Tips/Tricks for using systemtests

This file contains small guidelines on what to do if you encounter some of the more common problems. Before reading this, one should make sure to read the other docs and/or be familiar with the code.

## Useful Documentation

See main [README.md](./README.md) under `Where to start`.

## Foreford: deciding where to run your builds
Whenever you detect a build failure and start investigating the failing command, it is recommended to make use of local builds (on your machine) as much as possible (as opposed to sending builds to the CI platform). This way you have much more interactive control over the test (e.g. being able to enter an active docker container to figure things out at runtime) and save computational resources on the platform that others might want to use. Nontheless, do not be afraid to use CI when necessary, sometimes an issue can only be resolved by checking how a certain build behaves in CI.

Note that the investigation methods below (whereby you interact with images/containers through a shell) require you to run the build locally.

## Investigating failures during the build stage of Dockerfiles
If something fails during building, you will be able to find the failing command in the logging output during building (Docker will print each line in the Dockerfile that it is about to execute). For debugging, you can then comment out all commands of the Dockerfile below **and including** the failing line. Then, rebuild the image (possibly tag it something distinct so that it doesn't interfere with actual functional Dockerfiles, e.g. `debug_fenics-adapter`). This will yield an intact docker image that you can then enter in interactive mode to check its status prior to failing and execute the failing command manually to see whats going on. To launch such an image interactively, see this command using the aforementioned example:
```
docker run -it --rm debug_fenics-adapter /bin/bash
```
The `-it` flags will cause you to enter a shell with which to interact with the target image. `/bin/bash` specifies the shell, `--rm` is an optional flag that ensures that the container will be removed after you exit it.

## Investigating failures during runtime of a docker-compose test
If failures occur during the runtime of a test (meaning the execution of a tutorial example using finished adapter Dockerfiles), the error most likely is happening during the execution of commands specified in `docker-compose.yml` and not whilst building a Dockerimage. In this case, you can hijack the running containers mid-test with the following:
```
docker exec -it id_of_target_container /bin/bash
```
Note that the ID of the wanted container is required, which you can obtain through `docker container ls`.
This allows you to interact with test participants through a shell while they are executing their specified docker-compose commands, which can be useful to identify issues that pop up during computation. Beware that by default, the container shuts down after it ends its command chain (from the docker-compose file) either through success or error, which will terminate your connection. A workaround in this case is to add a temporary sleep command, e.g. `sleep 10m`, at a fitting location in the launch commands.



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

## If something fails on TravisCI

1. Inspect the build log
2. Restart the build (maybe it is a connection problem)
3. Try to replicate it locally with e.g.
```
   python3 system_testing.py -s su2-ccx
```
4. If it fails locally, use above-mentioned techniques to debug it. If is does not, bad luck.

## If a systemtest request fails with 'HTTP Error 403: Forbidden'

It might happen at some point that the `trigger_systemtests.py` script responsible for triggering builds through the Travis API starts to fail with the error above. This could happen due to the `TRAVIS_ACCESS_TOKEN` expiring after some time and is potentially easy to fix. To renew the token, generate a new one locally using the Travis CLI (taken from [here](https://blog.travis-ci.com/2013-01-28-token-token-token)):

```
gem install travis && travis login && travis token
```

and replace the current `TRAVIS_ACCESS_TOKEN` value in the TravisCI systemtests dashboard.

## If there are network problems

It might happen that you cannot access the network from inside of docker. You can try to fix it using `--network=host` during build of docker images or by specifying `network: host` in the `docker-compose.yml`. You might also want to add this parameter in `build_image` function in `docker.py`.


## If CI on adapters does not work

For locally investigating this issue, make sure you have a `TRAVIS_ACCESS_TOKEN` stored as environment variable on your system.
Then you can then run and check the generated JSON file without sending an actual request to the server with:
```
   python3 trigger_systemtests.py --adapter su2 --test
```
If it looks fine, you can run it without `--test` to actually send the request to Travis. Then check in the Travis dashboard if a build was launched.
If not, you should at least be able to see the received request under `requests` section of Travis together with an explanation why the build was denied.

## If you want to use Dockerfiles for your own development

Some users might want to run coupled simulations without having everything installed on the same system.
For instance: mount input folders from your machine to `/home/precice/Data/Input` in the container and get output from
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
Output can then be copied from the containers afterwards.

## If you want to run the tests based on code from a non-default branch

Depending on the test case several code components are used (preCICE, bindings, adapter(s), tutorial). Sometimes it becomes necessary to use a branch different from the default (e.g. `develop` is used for the preCICE images. See [here](https://github.com/precice/systemtests/blob/ec4ef9d4aedd0087dfb3a8ed98fdf7a1267c7751/precice/Dockerfile.Ubuntu1604.home#L50-L52)).

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
