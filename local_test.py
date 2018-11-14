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
from common import call, ccall
from system_testing import build_run_compare


def test_is_considered(test, features):
    test_specializations = test.split('.')
    test_specializations = test_specializations[1:]  # get specialization of test (e.g. test only for Ubuntu1604)
    for test_specialization in test_specializations:  # check all specializations of the test whether they are met by features of the base image         
        if not test_specialization in features:
            # test specialization does not match provided features of base image -> we will not run the test with the provided base image
            return False
    return True


def determine_specialization(test):
    """
    The specialization degree of a test is simply determined, by counting the number of appended specializations.
    Example:
    test_bindings has specialization degree 1
    test_bindings.Ubuntu1804 has specialization degree 2
    """
    return test.split('.').__len__()


def determine_test_name(test):
    return test.split('.')[0]
    

def filter_for_most_specialized_tests(all_tests):
    """
    We only want to consider the most specialized test, if several tests are availabe. This function removes duplicate tests and filters for the most specialized version.
    """
    most_specialized_tests = {}
    for test in all_tests:
        test_name = determine_test_name(test)
        specialization_degree = determine_specialization(test)
        if not test_name in most_specialized_tests:  # test has not been added to the dict so far
            most_specialized_tests[test_name] = test
        elif determine_specialization(most_specialized_tests[test_name]) < specialization_degree:  # test has already been added to the dict, but the currently evaluated test is more specialized
            most_specialized_tests[test_name] = test
    return most_specialized_tests


def filter_tests(all_tests, base_dockerfile):
    base_features = base_dockerfile.split('.')  # put features of base Dockerfile separated by . in a list (e.g. Dockerfile.Ubuntu1604 has feature Ubuntu1604)
    base_features.remove('Dockerfile')  # remove Dockerfile    
    executed_tests = []
    for test in all_tests:        
        if test_is_considered(test, base_features):  # check all tests for compatibility with features of base image (e.g. base image with Ubuntu1604 feature cannot run tests with Ubuntu1804 specialization
            executed_tests.append(test)
    executed_tests = filter_for_most_specialized_tests(executed_tests)
    return list(executed_tests.values())
    

# Parsing flags
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Build local.')
parser.add_argument('-b', '--branch', help="Branch you want to use for preCICE", default = "develop")
parser.add_argument('-d', '--dockerfile', help="Dockerfile used to create preCICE base image", default = "Dockerfile.Ubuntu1604")
parser.add_argument('-s', '--systemtest', nargs='+', help="System tests you want to use", default = common.get_tests(), choices = common.get_tests())
parser.add_argument('-f', '--force_rebuild', nargs='+', help="Force rebuild of variable parts of docker image", default = [], choices  = ["precice", "tests"])
args = parser.parse_args()

if __name__ == "__main__":
    tests = args.systemtest

    tests = filter_tests(tests, args.dockerfile)
    print(tests)
   
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
            build_run_compare(test, args.dockerfile.lower(), args.branch, True, "tests" in args.force_rebuild)
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

    # Push
    answer = input("Do you want to push the results (logfiles and possibly output files) to the output repo? (yes/no)\n")
    if answer in ["yes", "y"]:
        for x in success:
            ccall("python push.py --success --test " + x + " --branch " + args.branch)
        for y in failed:
            ccall("python push.py --test " + y + " --branch " + args.branch)
