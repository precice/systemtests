# preCICE Systemtests Documentation

Here you will find general documentation for the preCICE systemtesting architecture.

## Why use precice/systemtests?

This repository fulfills a variety of functions, which are handled by separate files/folders.
Roughly outlined, these functions are:

- Chronologically checking the integrity of preCICE and all related adapters for a variety of solvers. This is done by building them from source using Docker images. After a successful build the respective image is then uploaded to DockerHub for public use. These finished images are also involved in later tests/builds. When building the docker image for an adapter, for instance, we begin by pulling a Dockerhub image that has preCICE already installed.

- Providing a method to trigger a systemtests build from other preCICE repositories (specifically the preCICE adapters) in order to checking the integrity of the specific adapter.

- Logging results and storing debug output by pushing it to the repository `precice_st_output`. (This is subject to be replaced with a fitting storage mechanism in the future).


The repository written in a combination of Dockerfiles, Python, and Bash. The execution is done on TravisCI platform, though this is subject to change in the future (possibly migrating to GitLabCI/GitHubCI).

## Where to start?

### Useful Documentation

* [Docker](https://docs.docker.com/)
* [Docker-compose](https://docs.docker.com/compose/)
* [TravisCI main docs](https://docs.travis-ci.com/)
* [TravisCI API](https://developer.travis-ci.com/)
* [Bash scripting](https://tiswww.case.edu/php/chet/bash/bashref.html) (most bash docs/cheatsheets you can find by googling are pretty good, this is only one example)
* [AWK scripting](https://www.grymoire.com/Unix/Awk.html) (as with bash, this is only one example)

### How to use systemtests 

- [`architecture.md`](./architecture.md): General overview of the testing architecture. **(If you are new, read this first!)**
- [`adapters-ci.md`](./adapters-ci.md): How to handle builds originating from adapter repositories.
- [`adding_tasks.md`](./adding_tasks.md): Explanation of the `.travis.yml` job structure.
- [`development.md`](./development.md): Tips and common practices for development.
