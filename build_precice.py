import argparse, docker
import system_testing
import os
                           
if __name__ == "__main__":
    # Parsing flags
    parser = argparse.ArgumentParser(description='Build local docker image of preCICE.')
    parser.add_argument('-d', '--dockerfile', type=str, help="Choose Dockerfile you want to build", default="precice/Dockerfile.Ubuntu1604.home")
    parser.add_argument('-b', '--branch', help="preCICE branch to use", default="develop")
    parser.add_argument('-p', '--petsc', help="set 'yes', if you want to build with PETSc.", default="no", choices={'yes', 'no'})
    parser.add_argument('-u', '--docker-username', help="docker username", default=os.environ["DOCKER_USERNAME"] if "DOCKER_USERNAME" in os.environ else "precice")
    parser.add_argument('-f', '--force-rebuild', nargs='+', help="Force rebuild of variable parts of docker image", default = [], choices  = ["precice", "tests"])
    args = parser.parse_args()

    dockerfile = os.path.basename(args.dockerfile)
    assert(dockerfile.split(".")[0] == "Dockerfile")  # We have the convention that our Dockerfiles always start with the term "Dockerfile"

    # converting features provided in filename to dictionary
    features = dict()
    i = 0
    for feature in dockerfile.split(".")[1:]:  # Extract features from filename and join features with "." as separator.
        i += 1
        if i == 1:  # first feature is mandatory always describes the os
            assert(feature in ["Ubuntu1604", "Ubuntu1804", "Arch"])  # we expect that one of the following operating systems is used
            features["os"] = feature
        if i == 2:  # second feature is optional if it exists it describes the preCICE installation
            assert(feature in ["package", "home", "sudo"])  # we expect that one of the following installation procedures is used
            features["installation"] = feature
        if i >= 3:  # third and following features are optional
            assert(feature in ["mpich"])  # we expect one of these optional features
            if feature is "mpich":
                features["mpich"] = "yes"
    assert(i > 0)  # at least one feature (the os) should have been provided
    if args.petsc == "yes":
        features["petsc"] = "yes"

    print("Building preCICE image with the following features: {}".format(features))

    tag = system_testing.compose_tag(args.docker_username, "precice", features, args.branch)
    docker.build_image(tag=tag,
                       dockerfile=args.dockerfile,
                       build_args={"branch" : args.branch, "petsc_para" : args.petsc},
                       force_rebuild=args.force_rebuild,
                       namespace="")
                       
