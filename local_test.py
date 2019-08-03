#!/usr/bin/env python3
"""Script for testing on the local machine.

This script allows to build preCICE with a branch choosen by the user, execute
all or choosen system tests and allows to push the results to the output repository
of preCICE system test.

    Example:
        Example to use preCICE branch "master" and only system tests "of-of" and "su2-ccx":

            $ python local_test.py --branch=master --systemtest of-of su2-ccx
"""

import argparse, os, subprocess
import docker, common
from common import call, ccall, determine_test_name, get_test_variants, filter_tests
from system_testing import build_run_compare



if __name__ == "__main__":
    # Parsing flags
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Build local.')
    parser.add_argument('-b', '--branch', help="Branch you want to use for preCICE", default = "develop")
    parser.add_argument('-d', '--dockerfile', help="Dockerfile used to create preCICE base image", default = "Dockerfile.Ubuntu1604.home")
    parser.add_argument('-s', '--systemtest', nargs='+', help="System tests you want to use", default = common.get_tests(), choices = common.get_tests())
    parser.add_argument('-f', '--force_rebuild', nargs='+', help="Force rebuild of variable parts of docker image", default = [], choices  = ["precice", "tests"])
    args = parser.parse_args()
    test_names = args.systemtest
    
    tests = []
    for test_name in test_names:
        tests += get_test_variants(test_name)
    tests = filter_tests(tests, args.dockerfile)
   
    # Checking for older docker containers
    lst2 = docker.get_containers()
    if lst2:
        print("Deleting following docker containers:", lst2)
        answer = input("\nOk? (yes/no)\n")
        if answer in ["yes", "y"]:
            for x in lst2:
                ccall("docker container rm -f " + x)
        else:
            print("BE CAREFUL!: Not deleting previous containers can later lead to problems.")

    # Building preCICE
    print("\n\nBuilding preCICE docker image with choosen branch\n\n")
    docker.build_image("precice-" + args.dockerfile.lower() + "-" + args.branch, args.dockerfile,
                       build_args = {"branch" : args.branch},
                       force_rebuild = "precice" in args.force_rebuild)
    # Starting system tests
    failed = []
    success = []
    for test in tests:
        test_basename = determine_test_name(test)
        print("\n\nStarting system test %s\n\n" % test)
        try:
            build_run_compare(test, args.dockerfile.lower(), args.branch.lower(), True, "tests" in args.force_rebuild)
        except subprocess.CalledProcessError:
            failed.append(test_basename)
        else:
            success.append(test_basename)

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
