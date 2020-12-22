import datetime, subprocess


def get_namespace():
    return "st_"

def get_dockername():
    """ Returns the docker namespace resp. username. """
    return "precice"

def get_images():
    cmd = r'docker image list --filter=reference="%s*" --format="{{.Repository}}"' % get_namespace()
    print("EXECUTING:", cmd)
    cp = subprocess.run(cmd, stdout = subprocess.PIPE, shell = True, check = True)
    images = cp.stdout.decode().split("\n")
    return [i for i in images if len(i) > 0] # Remove empty lines

def get_containers():
    cmd = r'docker ps -a --filter=name="%s*" --format="{{.Names}}"' % get_namespace()
    print("EXECUTING:", cmd)
    cp = subprocess.run(cmd, stdout = subprocess.PIPE, shell = True, check = True)
    images = cp.stdout.decode().split("\n")
    return [i for i in images if len(i) > 0] # Remove empty lines

def build_image(tag, dockerfile="Dockerfile", build_args={}, force_rebuild=False, namespace=get_namespace(), docker_tag="latest", docker_login=True):
    if force_rebuild:
        build_args["CACHEBUST"] = datetime.datetime.now().isoformat() # A unique string for every invocation
    cmd = ""
    if docker_login:
        cmd += "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin && "

    args = " ".join(["--build-arg " + a + "=" + b for a, b in build_args.items()])
    cmd += f"docker build --network=host --file {dockerfile} --tag {namespace}{tag.lower()}:{docker_tag} {args} ."
    print("EXECUTING:", cmd)
    subprocess.run(cmd, shell=True, check=True)

def push_image(tag, namespace=get_namespace(), docker_tag="latest", docker_login=True):
    cmd = ""
    if docker_login:
        cmd += "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin && "

    cmd += f"docker push {namespace}{tag.lower()}:{docker_tag}"
    print("EXECUTING:", cmd)
    subprocess.run(cmd, shell=True, check=True)
