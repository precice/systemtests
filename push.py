"""Script for pushing output and logfile to a repository.

This script pushes output files of a system test, if they exists, and a logfile
to the repository: https://github.com/precice/precice_st_output.

    Example:
        Example use to push output files and logfile of system test of-of:

            $ python push.py -s -t of-of
"""

import argparse, os, sys, time
from common import ccall, capture_output

# Parsing flags
parser = argparse.ArgumentParser(description='Build local.')
parser.add_argument('-b', '--branch', help="log choosen preCICE branch")
parser.add_argument('-t', '--test', help="choose system tests you want to use")
parser.add_argument('-s', '--success', action='store_true' ,help="only upload log file")
parser.add_argument('--base', type=str,help="Base preCICE image used", default= "Ubuntu1604")

args = parser.parse_args()

if __name__ == "__main__":
    systest = args.test

    # Creating new logfile. if it exists, truncate content.
    log = open("log_" + systest, "w")
    foam_version = 4.1
    # Saving versions of used software in system test systest.
    if systest == "of-ccx":
        log.write("OpenFOAM version: {}\n".format(foam_version))
        ccall(["echo OpenFOAM-adapter Version: $(git ls-remote https://github.com/precice/openfoam-adapter.git  | tail -1)"], stdout=log)
        log.write("CalculiX version: 2.12\n")
        ccall(["echo CalculiX-adapter Version: $(git ls-remote https://github.com/precice/calculix-adapter.git | tail -1)"], stdout=log)
        ccall(["echo tutorials Version: $(git ls-remote https://github.com/precice/tutorials.git | tail -1)"], stdout=log)
    elif systest == "of-of":
        log.write("OpenFOAM version: {}\n".format(foam_version))
        ccall(["echo OpenFOAM-adapter Version: $(git ls-remote https://github.com/precice/openfoam-adapter.git  | tail -1)"], stdout=log)
    elif systest == "su2-ccx":
        log.write("CalculiX version: 2.13\n")
        log.write("SU2 version: 6.0.0\n")
        ccall(["echo CalculiX-adapter Version: $(git ls-remote https://github.com/precice/calculix-adapter.git | head -n 1)"], stdout=log)
        ccall(["echo SU2-adapter Version: $(git ls-remote https://github.com/precice/su2-adapter.git | tail -1)"], stdout=log)
        ccall(["echo tutorials Version: $(git ls-remote https://github.com/precice/tutorials.git | tail -1)"], stdout=log)
    # Saving general information of all system tests.
    # Saving used distribution and preCICE version in logfile.
    # git ls-remote https://github.com/precice/precice.git | grep master
    if args.branch:
        ccall(["echo preCICE Version: $(git ls-remote https://github.com/precice/precice.git | grep "+ args.branch +")"], stdout=log)
    else:
        ccall(["echo preCICE Version: $(git ls-remote --tags https://github.com/precice/precice.git | tail -1)"], stdout=log)
    log.write("Base preCICE image used : {}\n".format(args.base))
    # Saving current date in logfile.
    localtime = str(time.asctime(time.localtime(time.time())))
    log.write("System testing at " + localtime + "\n")
    log.close()

    # Pushing outputfiles and logfile to repo.
    # Clone repository.
    ccall("git clone https://github.com/precice/precice_st_output")
    log_dir = os.getcwd() + "/precice_st_output/" + args.base
    ccall("mkdir -p " + log_dir)
    ccall("mv log_" + systest + " " + log_dir)

    if not args.success:
        system_suffix = "." + args.base
        # Move ouput to folder of this test case
        test_folder = os.getcwd() + '/Test_' + systest + system_suffix
        if not os.path.isdir(test_folder):
            test_folder = 'Test_' + systest
        source_dir = test_folder + "/Output"
        dest_dir = log_dir + "/Output_" + systest
        # source folder was not created, we probably failed before producing
        # any of the results
        if (not os.path.isdir(source_dir)):
            os.chdir(log_dir)
            ccall(["git add ."])
            ccall("git commit -m \"Failed to produce results. \" -m \"Build url: ${TRAVIS_JOB_WEB_URL}\"")
        else:
            os.chdir(log_dir)
            # something was committed to that folder before -> overwrite it
            if os.path.isdir(dest_dir):
                ccall("git rm -rf {}".format(dest_dir))
            ccall("mv {} {}".format(source_dir, dest_dir))
            ccall("git add .")
            if args.branch:
                ccall("git commit -m \"Output != Reference, local build with preCICE branch: "+ args.branch +"\"")
            else:
                ccall("git commit -m \"Output != Reference, build number: ${TRAVIS_BUILD_NUMBER} \" -m \"Build url: ${TRAVIS_JOB_WEB_URL}\"")
    else:
        os.chdir(log_dir)
        ccall("git add .")
        # remove previously failing results, if we succeed
        ccall("git rm -r --ignore-unmatch Output_" + systest)
        if args.branch:
            ccall("git commit -m \"Output == Reference, local build with preCICE branch: "+ args.branch +"\"")
        else:
            ccall("git commit -m \"Output == Reference, build number: ${TRAVIS_BUILD_NUMBER} \" -m \"Build url: ${TRAVIS_JOB_WEB_URL}\"")
    ccall("git remote set-url origin https://${GH_TOKEN}@github.com/precice/precice_st_output.git > /dev/null 2>&1")
    ccall("git push")
