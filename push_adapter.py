import argparse, docker
import system_testing
import os
                           
if __name__ == "__main__":
    # Parsing flags
    parser = argparse.ArgumentParser(description='Push local adapter image to Docker Hub.')
    parser.add_argument('-d', '--dockerfile', type=str, help="Choose Dockerfile you want to build", default="adapters/Dockerfile.fenics-adapter")
    parser.add_argument('-b', '--branch', help="preCICE branch to use", default="develop")
    parser.add_argument('-u', '--docker-username', help="docker username", default=os.environ["DOCKER_USERNAME"] if "DOCKER_USERNAME" in os.environ else "precice")
    parser.add_argument('-os', '--operating-system', help="Operating system used by preCICE base image", default="ubuntu1604")
    parser.add_argument('-i', '--precice-installation', help="Installation mode used for preCICE", default="home")
    parser.add_argument('-p', '--petsc', help="set 'yes', if you want to use a preCICE base image that was built with PETSc.", default="no", choices={'yes', 'no'})
    parser.add_argument('-f', '--force-rebuild', nargs='+', help="Force rebuild of variable parts of docker image", default = [], choices  = ["precice", "tests"])
    args = parser.parse_args()

    dockerfile = os.path.basename(args.dockerfile)
    assert(dockerfile.split(".")[0] == "Dockerfile")  # We have the convention that our Dockerfiles always start with the term "Dockerfile"

    adapter_name = dockerfile.split(".")[1]  # Extract adapter name from filename

    # converting features provided via command-line to dictionary
    features = dict()
    assert(args.operating_system)
    if args.operating_system:  # first feature is mandatory always describes the os
        features["os"] = args.operating_system
    if args.precice_installation:  # second feature is optional if it exists it describes the preCICE installation
        features["installation"] = args.precice_installation
    if args.petsc == "yes":
        features["petsc"] = "yes"

    tag = system_testing.compose_tag(args.docker_username, adapter_name, features, args.branch)

    docker.push_image(tag=tag,
                      namespace="")
                       
