# preCICE Systemtests Documentation

Here you will find general documentation for the preCICE systemtesting architecture.

## What are systemtests?

This repository fulfills a variety of functions, which are handled by separate files/folders.
Roughly outlined, these functions are:

- Chronologically checking the integrity of preCICE and all related adapters for a variety of solvers. This is done by building them from source using Docker images. After a successful build the respective image is then uploaded to DockerHub for public use. These finished images are also involved in later tests/builds. When building the docker image for an adapter, for instance, we begin by pulling a Dockerhub image that has preCICE already installed.

- Providing a method to trigger a systemtests build from other preCICE repositories (specifically the preCICE adapters) in order to checking the integrity of the specific adapter.

- Logging results and storing debug output by pushing it to the repository `precice_st_output`. (This is subject to be replaced with a fitting storage mechanism in the future).


The repository written in a combination of Dockerfiles, Python, and Bash. The execution is done on TravisCI platform, though this is subject to change in the future (possibly migrating to GitLabCI/GitHubCI).

## Where to start?

- General overview of the testing architecture is provided in [`architecture.md`](./architecture.md). **(If you are new, read this first!)**
- Handling of CI for the individual adapters is described in [`adapters-ci.md`](./adapters-ci.md)
- Some tips and practices for the development are found in [`development.md`](./development.md)
