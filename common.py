import subprocess

def call(cmd, **kwargs):
    """ Runs cmd in a shell, returns its return code. """
    print("EXECUTING:", cmd)
    cp = subprocess.run(cmd, shell=True, **kwargs)
    return cp.returncode

import os

def get_tests(root = os.getcwd()):
    """ List of all available system tests """
    return[s[5:] for s in os.listdir(root) if s.startswith("Test_")]
