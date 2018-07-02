#!/usr/bin/env python3
"""Script for testing on the local machine.

This script allows to build preCICE with a branch choosen by the user, execute
all or choosen system tests and allows to push the results to the output repository
of preCICE system test.

    Example:
        Example to use preCICE branch "master" and only system tests "of-of" and "su2-ccx":

            $ python local_test.py --branch=master --systemtest of-of su2-ccx
"""

import subprocess
import argparse
import os
from common import call

# Parsing flags
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Build local.')
parser.add_argument('-b', '--branch', help="choose branch you want to use for preCICE", default = "develop")
parser.add_argument('-s', '--systemtest', nargs='+', help="choose system tests you want to use", default = ['of-of', 'of-ccx', 'su2-ccx'])
args = parser.parse_args()

if __name__ == "__main__":
    tests = args.systemtest
    
    # Checking for older docker images
    lst1 = [ x for x in tests if call("docker image ls | grep " + x, stdout=subprocess.DEVNULL) == 0 ]
    if call("docker image ls | grep precice", stdout=subprocess.DEVNULL) == 0:
        lst1.append('precice')
    if lst1:
        print("Deleting following docker images:\n")
        for x in lst1:
            call("docker image ls | grep " + x)
        answer = input("\nOk? (yes/no)\n")
        if answer in ["yes", "y"]:
            for x in lst1:
                call("docker rmi -f " + x)
        else:
            print("BE CAREFUL!: Not deleting previous images can later lead to problems.\n\n")
            
    # Checking for older docker containers
    lst2 = [ x for x in tests if call("docker ps -a | grep " + x + "_container", stdout=subprocess.DEVNULL) == 0 ]
    if lst2:
        print("Deleting following docker containers\n")
        for x in lst2:
            call("docker ps -a | grep " + x + "_container")
        answer = input("\nOk? (yes/no)\n")
        if answer in ["yes", "y"]:
            for x in lst2:
                call("docker rm -f " + x + "_container")
        else:
            print("BE CAREFUL!: Not deleting previous containers can later lead to problems.")

    # Building preCICE
    print("\n\nBuilding preCICE docker image with choosen branch\n\n")
    branch = args.branch
    call("docker build -f Dockerfile.precice -t precice-{branch} --build-arg branch={branch} .".format(branch=branch), check=True)

    # Starting system tests
    failed = []
    success = []
    for x in tests:
        print("\n\nStarting system test %s\n\n" % x)
        try:
            call("python system_testing.py --local --systemtest " + x, check=True)
        except subprocess.CalledProcessError:
            failed.append(x)
        else:
            success.append(x)

    # Results
    print("\n\n\n\n\nLocal build finished.\n")
    if success:
        print("Following system tests succeeded: ")
        print(", ".join(success))
        print('\n')
    if failed:
        print("Following system tests failed: ")
        print(", ".join(failed))
        print('\n')

    # Push
    answer = input("Do you want to push the results (logfiles and possibly output files) to the output repo? (yes/no)\n")
    if answer in ["yes", "y"]:
        for x in success:
            call("python push.py --success --test " + x + " --branch " + args.branch, check=True)
        for y in failed:
            call("python push.py --test " + y + " --branch " + args.branch, check=True)
