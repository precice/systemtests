import argparse, docker
                           
if __name__ == "__main__":
    # Parsing flags
    parser = argparse.ArgumentParser(description='Build local.')
    parser.add_argument('-d', '--dockerfile', type=str, help="Choose Dockerfile you want to build", default= "Dockerfile.Ubuntu1604.home")
    parser.add_argument('-b', '--branch', help="preCICE branch to use", default = "develop")
    parser.add_argument('-u', '--docker-username', help="docker username")
    parser.add_argument('-f', '--force-rebuild', nargs='+', help="Force rebuild of variable parts of docker image",
                        default = [], choices  = ["precice", "tests"])
    args = parser.parse_args()
    tag = args.docker_username.lower() + "/" + args.dockerfile.lower() + '-' + args.branch.lower() 
    docker.build_image(tag = tag,
                       dockerfile = args.dockerfile,
                       build_args = {"branch" : args.branch},
                       force_rebuild = args.force_rebuild,
                       namespace = "")
                       