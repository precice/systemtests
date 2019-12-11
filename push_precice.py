import argparse, docker
import system_testing
import os
                           
if __name__ == "__main__":
    # Parsing flags
    parser = argparse.ArgumentParser(description='Build local.')
    parser.add_argument('-d', '--dockerfile', type=str, help="Choose Dockerfile you want to build", default="precice/Dockerfile.Ubuntu1604.home")
    parser.add_argument('-b', '--branch', help="preCICE branch to use", default="develop")
    parser.add_argument('-p', '--petsc', help="set 'yes', if you want to build with PETSc.", default="no", choices={'yes', 'no'})
    parser.add_argument('-u', '--docker-username', help="docker username", default=os.environ["DOCKER_USERNAME"])
    args = parser.parse_args()

    dockerfile = os.path.basename(dockerfilepath)
    assert(dockerfile.split(".")[0] == "Dockerfile")  # We have the convention that our Dockerfiles always start with the term "Dockerfile"
    features = ".".join(dockerfile.split(".")[1:])  # Extract features from filename and join features with "." as separator.

    tag = system_testing.compose_tag(args.docker_username, "precice", features, args.branch, args.petsc)
    docker.push_image(tag=tag,
                      namespace="")
                       
