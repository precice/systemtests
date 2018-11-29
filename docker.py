import configparser, datetime, subprocess


def get_namespace():
    # cp = configparser.ConfigParser()
    # cp.read("configuration")
    # return cp["Docker"]["Namespace"]
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

def build_image(tag, dockerfile = "Dockerfile", build_args = {}, force_rebuild = False):
    if force_rebuild:
        build_args["CACHEBUST"] = datetime.datetime.now().isoformat() # A unique string for every invocation
    args = " ".join(["--build-arg " + a + "=" + b for a, b in build_args.items()])
    cmd = "docker build --file {dockerfile} --tag {namespace}{tag} {build_args} .".format(dockerfile=dockerfile, namespace=get_namespace(), tag=tag.lower(), build_args=args)
    print("EXECUTING:", cmd)
    subprocess.run(cmd, shell = True, check = True)
