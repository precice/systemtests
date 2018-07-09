import subprocess

def call(cmd, **kwargs):
    """ Runs cmd in a shell, returns its return code. """
    print("EXECUTING:", cmd)
    cp = subprocess.run(cmd, shell=True, **kwargs)
    return cp.returncode

def ccall(cmd,  **kwargs):
    """ Runs cmd in a shell, returns its return code. Raises exception on error """
    return call(cmd, check = True, **kwargs)
    

import os

def get_tests(root = os.getcwd()):
    """ List of all available system tests """
    return[s[5:] for s in os.listdir(root) if s.startswith("Test_")]
