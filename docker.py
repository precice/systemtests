import configparser, subprocess


def get_namespace():
    # cp = configparser.ConfigParser()
    # cp.read("configuration")
    # return cp["Docker"]["Namespace"]
    return "st_"

def get_images():
    cmd = r'docker image list --filter=reference="%s*" --format="{{.Repository}}"' % get_namespace()
    print(cmd)
    cp = subprocess.run(cmd, stdout = subprocess.PIPE, shell = True, check = True)
    images = cp.stdout.decode().split("\n")
    return [i for i in images if len(i) > 0] # Remove empty lines

def get_containers():
    cmd = r'docker ps -a --filter=name="%s*" --format="{{.Names}}"' % get_namespace()
    print(cmd)
    cp = subprocess.run(cmd, stdout = subprocess.PIPE, shell = True, check = True)
    images = cp.stdout.decode().split("\n")
    return [i for i in images if len(i) > 0] # Remove empty lines

def build_image(tag, dockerfile = "Dockerfile", build_args = {}):
    args = " ".join(["--build-arg " + a + "=" + b for a, b in build_args.items()])
    cmd = "docker build -f {} -t {}{} {} .".format(dockerfile, get_namespace(), tag, args)
    print(cmd)
    subprocess.run(cmd, shell = True, check = True)
