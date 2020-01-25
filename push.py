"""
### WIP ###
Script for pushing travis internal files to a github repository.

This script pushes to: https://github.com/precice/precice_st_output.

    Example:
        Example use to push output files and logfile of system test of-of:

            $ python push.py -s -t of-of
"""

# from trigger_systemtests import get_json_response
# from urllib.parse import urlencode
# from urllib.request import Request, urlopen
import argparse, os, sys, time
from common import call, ccall, capture_output, get_test_participants, chdir
import inspect
#
# def get_job_commit(job_id):
#     """ Checks commit that triggered travis job"""
#     url = "https://api.{TRAVIS_URL}/job/{JOB_ID}".format(TRAVIS_URL="travis-ci.org", JOB_ID=job_id)
#     resp =  get_json_response(url)
#     return resp['commit']
#
# def get_builds(user, repo, offset=0):
#     """ Get list of Travis builds of the repo """
#     url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/builds?offset={OFFSET}".format(TRAVIS_URL="travis-ci.org",
#             USER=user, REPO=repo, OFFSET = offset)
#     return get_json_response(url)
#
# def get_last_successfull_commit(user, repo):
#     """ Identify last commit the passed on Travis """
#
#     commit = {}
#     offset = 0
#     while not commit:
#         builds = get_builds(user, repo, offset = offset)
#         for build in builds["builds"]:
#             if build["state"] == "passed":
#                 commit = build["commit"]
#                 break
#         offset += 25
#
#     return commit
#
#
# def create_job_log(test, log, exit_status):
#
#     make_md_link = lambda name, link: "[{name}]({link})".format(name=
#             name, link=link)
#
#     build_url = os.environ["TRAVIS_BUILD_WEB_URL"]
#     build_number = os.environ["TRAVIS_BUILD_NUMBER"]
#     event_type = os.environ["TRAVIS_EVENT_TYPE"]
#     triggered_commit = os.environ["TRAVIS_COMMIT"]
#     job_id = os.environ["TRAVIS_JOB_ID"]
#     job_number = os.environ["TRAVIS_JOB_NUMBER"]
#     job_url = os.environ["TRAVIS_JOB_WEB_URL"]
#     commit_message = os.environ["TRAVIS_COMMIT_MESSAGE"]
#
#     # Decipher commit from the job message
#     if (event_type == "api"):
#         job_that_triggered = commit_message.split("Triggered by:")[-1]
#         if job_that_triggered == "manual script call":
#            event_type = "manual trigger"
#         else:
#            *_, adapter_name, _, adapter_job_id = job_that_triggered.split('/')
#            triggered_commit = get_job_commit(adapter_job_id)
#            event_type = "commit to the {}".format(adapter_name)
#     else:
#         triggered_commit = get_job_commit(job_id)
#
#     log.write("## Status: " + ("Passing" if not exit_status else "Failure") + " \n")
#     log.write("Build: {link} \n\n".format(link = make_md_link(build_number, build_url)))
#     log.write("Job: {link} \n\n".format(link = make_md_link(job_number, job_url)))
#     log.write("Triggered by: {link} \n".format(link =
#         make_md_link(event_type, triggered_commit['compare_url'])))
#
#     if exit_status:
#
#         adapters =  get_test_participants(test)
#         last_good_commits = {}
#         if adapters:
#             for adapter in adapters:
#                 last_good_commits[adapter] = get_last_successfull_commit('precice', adapter).get('compare_url')
#         last_good_commits['systemtests'] = get_last_successfull_commit('precice', 'systemtests').get('compare_url')
#         failed_info = "Last successful commits \n* {commits} \n".format(commits =
#                 "\n* ".join([make_md_link(name, commit) for name, commit in last_good_commits.items()]))
#         log.write(failed_info)
#
#     log.write("\n---\nLast 100 lines of the job log at the moment of push:\n")
#     log.write('```\n{job_log}\n```\n'.format(job_log =
#         get_travis_job_log(job_id)))
#     log.write(make_md_link("\nFull job log", "https://api.travis-ci.org/v3/job/{}/log.txt".format(job_id)))
#
#
# def add_output_files(output_dir, output_log_dir, success):
#
#     if success:
#         # Everything passes, no need to commit anything, remove previous output
#         ccall("git rm -r --ignore-unmatch {}".format(output_log_dir))
#     elif os.path.isdir(output_dir):
#         if os.path.isdir(output_log_dir):
#             # overwrite previous output to get rid of artifacts
#             ccall("git rm -rf {}".format(output_log_dir))
#         ccall("mv {} {}".format(output_dir, output_log_dir))
#         ccall("git add .")
# #
# def add_job_log(systest, failed, log_dir):
#     with chdir(log_dir):
#         log_name = "log_{test}.md".format(test = systest)
#         with open(log_name, "w") as log:
#             create_job_log(systest, log, failed)
#         ccall("git add {log_name}".format(log_name = log_name))


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
        else
        job_log = response

        return job_log

tag_descriptions = {
    'no_output' : "\n- **This test generated no Output files!** These should normally be stored in the folder '/Output' located at the root of the 'tutorial-data' container, but no files were found there.\n",
    'allowed_failure' : "\n- This test has been marked as allowed failure.\n"
}

def add_readme(job_path, job_result):
    """
    Create a README.md at the location specified by readme_path.
    """
    job_link = os.environ["TRAVIS_JOB_WEB_URL"]
    job_name = os.environ["TRAVIS_JOB_NAME"]
    job_status = "Success" if job_result else "Failure"

    readme_text = """
    # {name}

    Job Status: **{status}**

    [Link to Job page on TravisCI]({link})

    ---
    """.format(name=job_name, status=job_status, link=job_link)

    readme_text = inspect.cleandoc(readme_text) # cleans indentation
    with chdir(job_path):
        with open("README.md", "w") as readme:
            readme.write(readme_txt)
        ccall("git add README.md")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Push results from containers to output repository')
    parser.add_argument('-t', '--test', help="Choose systemtest, results of which to push")
    parser.add_argument('-b', '--base', type=str, help="Base image of the test", default="Ubuntu1604.home")
    parser.add_argument('--st-branch', type=str, help="Branch of precice_st_output to push to", default="EderK-push_files")
    args = parser.parse_args()

    repo_folder = "precice_st_output"
    build_folder = os.environ["TRAVIS_BUILD_NUMBER"]
    job_folder = os.environ["TRAVIS_JOB_NUMBER"]
    job_id = os.environ["TRAVIS_JOB_ID"]
    job_result = os.environ["TRAVIS_TEST_RESULT"]
    job_success = True if (job_result == 0) else False

    # TODO: change default to master branch when merging
    ccall("git clone -b {st_branch} https://github.com/precice/precice_st_output".\
        format(st_branch=args.st_branch))

    # Path to repository folder
    repo_path = os.path.join(os.getcwd(), repo_folder)
    # Path to job folder
    job_path = os.path.join(os.getcwd(), repo_folder, build_folder, job_folder)
    # Path to Output folder inside a job folder
    output_path = os.path.join(file_path, "Output")
    # Path to Logs folder inside a job folder
    logs_path = os.path.join(file_path, "Logs")

    # Dont need to mkdir, will be done by docker cp
    # ccall("mkdir -p {}".format(logs_path))
    # ccall("mkdir -p {}".format(output_path))

    # extract files from container
    ccall("docker cp tutorial-data:/Output {}".format(file_path))
    # move container logs into correct folder
    ccall("docker cp tutorial-data:/Logs {}".format(file_path))

    # create travis log
    with chdir(logs_path):
        with open("travis-log.md", "w") as log:
            log.write('```\n{log}\n```\n'.format(log=get_travis_job_log(job_id)))

    # create README
    add_readme(job_path, job_success)


    # Check if Output directory is empty. If yes, include a small README
    no_output = False
    if not os.listdir(output_path):
        ccall("echo '# No output files found!' > {path}".format(path=
        os.path.join(output_path, "README.md")))
        no_output = True
    # Check if Logs directory is empty. If yes, include a small README
    no_logs = False
    if not os.listdir(logs_path):
        ccall("echo '# No log files found!' > {path}".format(path=
        os.path.join(output_path, "README.md")))
        no_output = True

    os.chdir(repo_path)
    with chdir(repo_path):
        ccall("git add {}".format(file_path))

    # finally commit
    commit_msg = "Job Success" if job_success else "Job Failure"
    if no_output:
        commit_msg += ", NO OUTPUT"
    if no_logs:
        commit_msg += ", NO LOGS"
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
