"""
### WIP ###
Script for pushing travis internal files to a github repository.

This script pushes to: https://github.com/precice/precice_st_output.

    Example:
        Example use to push output files and logfile of system test of-of:

            $ python push.py -s -t of-of
"""

from jinja2 import Template
from urllib.request import Request, urlopen
import argparse, os, sys, time
from common import call, ccall, capture_output, get_test_participants, chdir

def generate_commit_message(output_dir, success, test, base):

    travis_build_number = os.environ["TRAVIS_BUILD_NUMBER"]
    travis_build_web_url = os.environ["TRAVIS_BUILD_WEB_URL"]
    travis_job_number = os.environ["TRAVIS_JOB_NUMBER"]
    travis_job_web_url = os.environ["TRAVIS_JOB_WEB_URL"]
    commit_msg_lines = []

    if success:
        commit_msg_lines = ["Success Job: {}".format(travis_job_number)]
    else:
        commit_msg_lines = ["Failure Job: {}".format(travis_job_number)]
        # folder with output was not created, we probably failed before producing
        # any of the results
        if not os.path.isdir(output_dir):
            commit_msg_lines += ["[Failed to produce results]"]

    commit_msg_lines += ["Base: {}".format(base)]
    commit_msg_lines += ["Test: {}".format(test)]
    commit_msg_lines += ["Build url: {}".format(travis_build_web_url)]
    commit_msg_lines += ["Job url: {}".format(travis_job_web_url)]

    return commit_msg_lines

def get_travis_job_log(job_id, tail = 0):

    txt_url = "https://api.travis-ci.org/v3/job/{}/log.txt".format(job_id)
    req = Request(txt_url)
    response = urlopen( req ).read().decode()

    # if log cutoff is enabled
    if tail > 0:
        job_log = "\n".join( response.split("\n")[-tail:] )
    else:
        job_log = response

    return job_log


def add_readme(
        job_path,
        output=False,
        output_missing=False,
        logs_missing=False,
        message=None
        ):
    """
    Create a README.md at the location specified by readme_path.
    """
    job_link = os.environ["TRAVIS_JOB_WEB_URL"]
    job_name = os.environ["TRAVIS_JOB_NAME"]
    job_success = True if (os.environ["TRAVIS_TEST_RESULT"] == '0') else False

    branch = os.environ["TRAVIS_BRANCH"]
    pr_branch = os.environ["TRAVIS_PULL_REQUEST_BRANCH"]
    is_pr = False if (pr_branch == "") else True

    if (output_missing or logs_missing or message):
        additional_info = True
    else:
        additional_info = False

    with open(os.path.join('templates','readme_template', 'README.md')) as f:
        tmp = Template(f.read())
        readme_rendered = tmp.render(locals())

    with chdir(job_path):
        with open("README.md", "w") as f:
            f.write(readme_rendered)
        ccall("git add README.md")



if __name__ == "__main__":

    repo_folder = "precice_st_output"
    default_base = "Ubuntu1604.home"
    default_st_branch = "master"

    parser = argparse.ArgumentParser(description='Push test output and logs to output repository')
    parser.add_argument('-t', '--test', help="Choose systemtest, results of which to push")
    parser.add_argument('-b', '--base', type=str, help="Base image of the test", default=default_base)
    parser.add_argument('-o', '--output', action='store_true', help="Enable result storage (disabled by default)", )
    parser.add_argument('--st-branch', type=str, help="Branch of precice_st_output to push to", default=default_st_branch)
    parser.add_argument('--petsc', action='store_true', help="Use preCICE with PETSc as base image")
    args = parser.parse_args()

    job_id = os.environ["TRAVIS_JOB_ID"]
    job_result = os.environ["TRAVIS_TEST_RESULT"]
    job_success = True if (job_result == '0') else False
    job_name = os.environ["TRAVIS_JOB_NAME"]

    build_folder = os.environ["TRAVIS_BUILD_NUMBER"]
    job_folder = os.environ["TRAVIS_JOB_NUMBER"]

    # TODO: change default to master branch when merging
    ccall("git clone -b {st_branch} https://github.com/precice/precice_st_output".\
        format(st_branch=args.st_branch))

    # Path to repository folder
    repo_path = os.path.join(os.getcwd(), repo_folder)
    # Path to job folder
    job_path = os.path.join(os.getcwd(), repo_folder, build_folder, job_folder)
    # Path to Output folder inside a job folder
    output_path = os.path.join(job_path, "Output")
    # Path to Logs folder inside a job folder
    log_path = os.path.join(job_path, "Logs")

    ccall("mkdir -p {}".format(log_path))
    ccall("mkdir -p {}".format(output_path))


    # extract files from container, IF ENABLED
    if args.output:
        ccall("docker cp tutorial-data:/Output {}".format(job_path))


    # move container logs into correct folder, only compose tests have containers
    compose_tests = ["dealii-of", "of-of", "su2-ccx", "of-ccx", "of-of_np",
            "fe-fe","nutils-of", "of-ccx_fsi"]
    if args.test in compose_tests:
        test_dirname = "TestCompose_{systest}".format(systest=args.test)
        test_dirname += "." + args.base
        if args.petsc:
            test_dirname += ".PETSc"
        test_path = os.path.join(os.getcwd(), 'tests', test_dirname)
        ccall("cp -r {test_path}/Logs {job_path}".\
               format(test_path=test_path, job_path=job_path))


    # create travis log
    with chdir(log_path):
        with open("travis.log", "w") as log:
            log.write(get_travis_job_log(job_id))



    # Check if Output is missing, given it is enabled
    output_missing = False
    if args.output:
        if not os.listdir(output_path):
            ccall("echo '# Output was enabled, but no output files found!' > {path}".format(path=
            os.path.join(output_path, "README.md")))
            output_missing = True

    # Check if Logs directory is empty. If yes, include a small README
    logs_missing = False
    if not os.listdir(log_path):
        ccall("echo '# No log files found!' > {path}".format(path=
        os.path.join(log_path, "README.md")))
        logs_missing= True


    # create README
    add_readme(
        job_path,
        output=args.output,
        output_missing=output_missing,
        logs_missing=logs_missing)


    os.chdir(repo_path)
    with chdir(repo_path):
        ccall("git add {}".format(job_path))

    # finally commit
    commit_msg = job_name
    commit_msg += " - Success" if job_success else " - FAILURE"
    if args.output:
        if output_missing:
            commit_msg += ", MISSING OUTPUT"
    if logs_missing:
        commit_msg += ", MISSING LOGS"
    ccall("git commit -m '{}'".format(commit_msg))
    ccall("git config user.name 'Precice Bot'")
    ccall("git config user.email ${PRECICE_BOT_EMAIL}")
    ccall("git remote set-url origin https://${GH_TOKEN}@github.com/precice/precice_st_output.git > /dev/null 2>&1")


    failed_push_count = 0
    failed_push_limit = 50
    # push, retry if failed
    while call("git push"):
        ccall("git pull --rebase")
        failed_push_count += 1
        if failed_push_count >= failed_push_limit:
            break
