"""
Script for pushing travis internal files to a github repository.

This script pushes to: https://github.com/precice/precice_st_output.

    Example:
        Example use to push output files and logfile of system test of-of:

            $ python push.py -s -t of-of
"""

from jinja2 import Template
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import argparse, os, sys, time
from common import call, ccall, capture_output, get_test_participants, chdir


def get_response(url, **kwargs):

    headers = {
      "Travis-API-Version": "3",
      "Authorization": "token {}".format(os.environ['TRAVIS_ACCESS_TOKEN'])
    }

    req = Request(url, headers = headers, **kwargs )
    response = urlopen( req ).read().decode()

    return response



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
    response = get_response(txt_url)

    # if log cutoff is enabled
    if tail > 0:
        job_log = "\n".join( response.split("\n")[-tail:] )
    else:
        job_log = response

    return job_log


def add_readme(
        job_path,
        type='test',
        output_enabled=False,
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
        readme_rendered = tmp.render(
            type=type,
            job_name=job_name,
            job_success=job_success,
            branch=branch,
            pr_branch=pr_branch,
            is_pr=is_pr,
            job_link=job_link,
            output_enabled=output_enabled,
            output_missing=output_missing,
            additional_info=additional_info,
            logs_missing=logs_missing,
            message=message)

    with chdir(job_path):
        with open("README.md", "w") as f:
            f.write(readme_rendered)
        ccall("git add README.md")



if __name__ == "__main__":

    repo_folder = "precice_st_output"
    default_base = "Ubuntu1804.home"
    default_st_branch = "master"

    parser = argparse.ArgumentParser(description='Push build/test logs to output repository. Optionally includes result data (for tests only).')
    parser.add_argument('-o', '--output', action='store_true', help="Enable result storage (only for tests, disabled by default)", )
    parser.add_argument('--branch', type=str, help="Branch of preCICE that was used for this build. Setting this value has no effect on execution.", default='develop')
    parser.add_argument('--st-branch', type=str, help="Branch of precice_st_output to push to", default=default_st_branch)
    args = parser.parse_args()

    try:
        from build_info import *
    except ModuleNotFoundError:
        print("##########################################\n" +
              "The file 'build_info.py' was not found.\n" +
              "This indicates a problem with a previous build step.\n" +
              "Check the log prior to this message for more information.\n" +
              "##########################################")
        exit(1)
    # Ensure that build_info file is intact
    assert(build_type in ['precice', 'adapter', 'test'])


    job_id = os.environ["TRAVIS_JOB_ID"]
    job_result = os.environ["TRAVIS_TEST_RESULT"]
    job_success = True if (job_result == '0') else False
    job_name = os.environ["TRAVIS_JOB_NAME"]

    build_folder = os.environ["TRAVIS_BUILD_NUMBER"] # example: "1832"
    job_folder_unpadded = os.environ["TRAVIS_JOB_NUMBER"] # example: "1832.8"
    job_folder = "{}.{:02d}".format(build_folder, int(job_folder_unpadded.split('.')[1]))

    ccall("git clone -b {st_branch} https://github.com/precice/precice_st_output".\
        format(st_branch=args.st_branch))


    # Path to repository folder
    repo_path = os.path.join(os.getcwd(), repo_folder)
    # Path to job folder
    job_path = os.path.join(os.getcwd(), repo_folder, build_folder, job_folder)

    output_missing = False

    # Path to Logs folder inside a job folder
    log_path = os.path.join(job_path, "Logs")
    ccall("mkdir -p {}".format(log_path))
    # Path to Output folder inside a job folder
    output_path = os.path.join(job_path, "Output")


    if build_type == 'adapter':
        # 'docker_tag' is imported from the build info file
        ccall("docker create --name adapter -it {} bash ".format(docker_tag))
        ccall("docker container ls -a")
        ccall("docker cp adapter:/home/precice/Logs {}".format(job_path))

    if build_type == 'test':
        # 'test_path' is imported from the build info file
        ccall("mkdir -p {}".format(output_path))

        if test_type=='compose':
            # extract files from container, IF ENABLED (requires a compose test)
            if args.output:
                ccall("docker cp tutorial-data:/Output {}".format(job_path))
                # Check if Output is missing, given that the option is enabled
                if not os.listdir(output_path):
                    ccall("echo '# Output was enabled, but no output files found!' > {path}".format(path=
                    os.path.join(output_path, "README.md")))
                    output_missing = True

            ccall("cp -r {test_path}/Logs {job_path}".\
                   format(test_path=test_path, job_path=job_path))

    # create travis log
    with chdir(log_path):
        with open("travis.log", "w") as log:
            travis_log = get_travis_job_log(job_id)
            log.write(travis_log)
    # Check if Logs directory is empty. If yes, include a small README
    logs_missing = False
    if not os.listdir(log_path):
        ccall("echo '# No log files found!' > {path}".format(path=
        os.path.join(log_path, "README.md")))
        logs_missing= True

    # create README
    add_readme(
        job_path,
        type=type,
        output_enabled=args.output,
        output_missing=output_missing,
        logs_missing=logs_missing)

    # cleanup build info file after reading
    ccall("rm ./build_info.py")


    os.chdir(repo_path)
    with chdir(repo_path):
        ccall("git add {}".format(job_path))

    # finally commit
    commit_msg = job_name
    commit_msg += " - Success" if job_success else " - FAILURE"
    if build_type == 'test' and args.output:
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

    print("Finished pushing to {}-{}!".format(repo_folder,args.st_branch))
