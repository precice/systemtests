import subprocess

def call(cmd, **kwargs):
    """ Runs cmd in a shell, returns its return code. """
    print("EXECUTING:", cmd)
    cp = subprocess.run(cmd, shell=True, **kwargs)
    return cp.returncode
