# How to add tests

To add a new test to the Travis build, simply add a corresponding entry in the `.travis.yml` file in a fitting stage under the `jobs: include:` section. The current stages are `Building preCICE`, `Building adapters`, `Tests`.

Here is an example job which builds the SU2 adapter:

```bash
- stage: Building adapters
  name: SU2 adapter
  if: fork = false
  script:
    - docker build -f adapters/Dockerfile.su2-adapter -t precice/su2-adapter-ubuntu1604.home-develop .
```

An entry should at least contain `name` and `script` keys such that the job can be run by travis and identified in the build log. In this example the additional `if` conditions avoids this job to execute if the build is running on a fork of the systemtests repository. Many more specifications are available if necessary, check the [Travis docs](https://docs.travis-ci.com/) for more info.

## Post-script actions

Most likely your preCICE build/adapter build/adapter test outputs some result data at the end, which should be either pushed to DockerHub (for docker images) of the 'precice_st_output' repository (for test logs). These pushes can be conditional as well, e.g. only pushing a docker image if the build actually exited successfully.
Such conditional pushes are realized by adding specific commands in `after_failure` and `deploy` sections.

#### Post-failure

Here is an example of how to use the `after_failure` key:
```bash
  - stage: Tests
    name: "[16.04] SU2 <-> Calculix"
    script:
      - python system_testing.py -s su2-ccx
    after_failure:
      - python push.py -t su2-ccx
```
Youc can specify commands the same way you do for the main script. This code will only be run if the main script commands return a non-zero exit code.

#### Post-success

**Note**: `after_success` sections are available in TravisCI. However, it is strongly recommended to use `deploy`. The reason is that a build with failing code in `after_success` sections will still get shown as successful, which makes it harder to detect failures.

A deployment requires several additional arguments to function properly. These do not need to be specifically adjusted for your test and can be directly copied into your test. Here is an code snippet from a deploying job:

```bash
    - stage: Building preCICE
      name: "Arch Linux"
      if: fork = false
      script:
        - docker build -f precice/Dockerfile.Arch -t precice/precice-arch-develop .
      deploy:
        skip_cleanup: true
        provider: script
        on:
          all_branches: true
        script: >-
          echo "$DOCKER_PASSWORD" | docker login -u precice --password-stdin &&
          docker push precice/precice-arch-develop:latest
```

The `deploy: script` contains the actual commands you wish to execute after a successful run. Additionally, the following arguments must be provided inside the `deploy` key:

- `skip_cleanup: true`

  This prevents TravisCI from stashing all changes made during the build, i.e. cleaning all results we actually wish to push.


- `provider: script`

  Specifies that the deployment phase uses our manually provided script.


- `on: all_branches: true`

  With this the deployment can be issued on any branch. This allows us to execute commands from the same branch that triggered a Travis build, and for any branch. If this key is not set, the deployment scripts would be run exclusively on `master` instead (independent of which branch the build runs on).


- `script: >-   [actual deploy script]`

  The `>-` is *critical* here. For one, **deploy scripts can only consist of a single line**. This means that we have to chain commands together (note the `&&` at line end) and use `>` to extend them into multiple lines. The addition of the hyphen `-` prevents the last command to be trailed by a newline character `/n`. **If this hyphen is omitted, the `/n` character in the command might get parsed as only `n`, which appends a character to the final command and makes it invalid!**



## Need help setting up a test?

If you are experiencing any issues, don't hesitate to ask for assisstance on [Gitter](https://gitter.im/precice/Lobby) or [Discourse](https://precice.discourse.group/).
