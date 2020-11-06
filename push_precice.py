import argparse, docker, common
import system_testing
import os

if __name__ == "__main__":
    # Parsing flags
    parser = argparse.ArgumentParser(description='Build local preCICE image to Docker Hub.')
    parser.add_argument('-d', '--dockerfile', type=str, help="Choose Dockerfile you want to build", default="precice/Dockerfile.Ubuntu1804.package")
    parser.add_argument('-b', '--branch', help="preCICE branch to use", default="develop")
    parser.add_argument('-p', '--petsc', help="set 'yes', if you want to build with PETSc.", default="no", choices={'yes', 'no'})
    parser.add_argument('-u', '--docker-username', help="docker username", default=os.environ["DOCKER_USERNAME"] if "DOCKER_USERNAME" in os.environ else "precice")
    args = parser.parse_args()

    # Check if preCICE build succeeded
    # NOTE: requires push_precice.py to be called directly after build command!
    job_result = os.environ["TRAVIS_TEST_RESULT"]
    job_success = True if (job_result == '0') else False
    if job_success:

        dockerfile = os.path.basename(args.dockerfile)
        assert(dockerfile.split(".")[0] == "Dockerfile")  # We have the convention that our Dockerfiles always start with the term "Dockerfile"

        # converting features provided in filename to dictionary
        features = dict()
        i = 0
        for feature in dockerfile.split(".")[1:]:  # Extract features from filename and join features with "." as separator.
            i += 1
            if i == 1:  # first feature is mandatory always describes the os
                assert(feature in ["Ubuntu1604", "Ubuntu1804", "Ubuntu2004", "Arch"])  # we expect that one of the following operating systems is used
                features["os"] = feature
            if i == 2:  # second feature is optional if it exists it describes the preCICE installation
                assert(feature in ["package", "home", "sudo"])  # we expect that one of the following installation procedures is used
                features["installation"] = feature
            if i >= 3:  # third and following features are optional
                assert(feature in ["mpich"])  # we expect one of these optional features
                if feature == "mpich":
                    features["mpich"] = "yes"
        assert(i > 0)  # at least one feature (the os) should have been provided
        if args.petsc == "yes":
            features["petsc"] = "yes"

        tag = system_testing.compose_tag(args.docker_username, "precice", features, args.branch)
        docker.push_image(tag=tag,
                          namespace="")

        common.save_build_info(build_type='precice')

    else:
        print("#############################################################\n" +
              "No docker image was pushed because the previous job command failed.\n" +
              "Check the preceding preCICE build to find out what went wrong.\n" +
              "(Note that this script relies on being called *directly* after build_precice.py)\n" +
              "#############################################################")
        exit(1)
