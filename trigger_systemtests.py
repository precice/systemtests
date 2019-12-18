"""
 Generate Travis API V3 request to trigger corresponding systemtests
 based on the adapter type. To adjust it for newly added system test modify
 struct `adapter_info` struct below with the name of the
 adapter repository, systemtests that should be run for it as
 well as the base image
"""

import json
import pprint
import os
import time
from sys import exit
import argparse
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from collections import namedtuple

adapter_info = namedtuple('adapter_info', 'repo tests base')

adapters_info = {"openfoam": adapter_info('openfoam-adapter', ['of-of', 'of-ccx'], 'Ubuntu1604.home'),
                 "calculix": adapter_info('calculix-adapter', ['of-ccx', 'su2-ccx'], 'Ubuntu1604.home'),
                 "su2": adapter_info('su2-adapter', ['su2-ccx'], 'Ubuntu1604.home'),
                 "dealii": adapter_info('dealii-adapter', ['dealii-of'], 'Ubuntu1604.home'),
                 "fenics": adapter_info('fenics-adapter', ['fe-fe'], 'Ubuntu1804.home')}


def get_json_response(url, **kwargs):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Travis-API-Version": "3",
        "Authorization": "token {}".format(os.environ['TRAVIS_ACCESS_TOKEN'])
    }

    req = Request(url, headers=headers, **kwargs)
    response = urlopen(req).read().decode()
    json_response = json.loads(response)

    return json_response


def adjust_travis_script(script, user, adapter):
    """ Patches travis job in case we are running on fork or a different branch """

    join_jobs = lambda jobs: " \&\& ".join(filter(None, jobs))

    branch = os.environ.get("TRAVIS_BRANCH")
    pull_req = os.environ.get("TRAVIS_PULL_REQUEST")

    branch_switch_cmd = None
    if branch:
        branch_switch_cmd = "git checkout {}".format(branch)

    pr_merge_cmd = None
    if pull_req and pull_req != "false":
        pr_merge_cmd = "git fetch origin\
        +refs/pull/{}/merge \&\& git checkout -qf FETCH_HEAD ".format(pull_req)

    post_clone_cmd = join_jobs([branch_switch_cmd, pr_merge_cmd])

    # inserts switching to a branch / merging a pull request
    # after cloning the adapter in all systemtests dockerfiles that use it
    preprocess_cmd = None
    if branch or not pull_req in [None, "false"]:
        preprocess_cmd = "grep -rl --include=\*Dockerfile* github.com/{user}/{adapter}.git |\
        xargs sed -i 's|\(github.com/{user}/{adapter}.git\)|\\1 \&\& cd \
        {adapter} \&\& {post_clone_cmd} \&\& cd .. |g'".format(user=user, adapter=
        adapters_info[adapter].repo, post_clone_cmd=post_clone_cmd)

    main_script = " && ".join(filter(None, ([preprocess_cmd, script])))

    return main_script


def determine_image_tag():
    """ Generates tag information based on the branch and pull request names """

    branch = os.environ.get("TRAVIS_BRANCH", "latest")
    pull_req = os.environ.get("TRAVIS_PULL_REQUEST")
    if pull_req and pull_req != 'false':
        return ".pr".join([branch, pull_req])
    else:
        return branch


def generate_travis_job(adapter, user, trigger_failure=True, branch="master"):
    triggered_by = os.environ["TRAVIS_JOB_WEB_URL"] if "TRAVIS_JOB_WEB_URL" in \
                                                       os.environ else "manual script call"

    base = adapters_info[adapter].base

    after_failure_action = "python push.py -t {TEST} --base {BASE} ;"
    main_test_script = "python system_testing.py -s {TEST} --base {BASE}"

    base_remote = "precice/precice-{base}-develop".format(base=base.lower())
    main_build_script = "docker build -f adapters/Dockerfile.{adapter} -t \
        {user}/{adapter}:{tag} --build-arg from={base_remote} .".format(adapter=
                                                                                                adapters_info[
                                                                                                    adapter].repo,
                                                                        user=user, base_remote=
                                                                                                base_remote,
                                                                        tag=determine_image_tag())

    if trigger_failure:
        after_failure_action += " python trigger_systemtests.py --failure --owner {USER} --adapter {ADAPTER}"

    # template for building this particular adapter
    build_template = {
        "stage": "Building adapter",
        "name": adapters_info[adapter].repo,
        "script": adjust_travis_script(main_build_script, user, adapter),
        "after_success":
            ['echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin',
             "docker push {user}/{adapter}:{tag}".format(adapter=
                                                         adapters_info[adapter].repo, user=user,
                                                         tag=determine_image_tag())]
    }

    # template for actually running an adapter in combination with other adapters
    systest_templates = {
        "stage": "Running tests",
        "name": "[{BASE}] {TESTNAME} <-> {TESTNAME}",
        # force docker-compose to consider an image with a particular tag
        "script": "export ${adapter_tag}={tag}; ".format(adapter_tag=adapter.upper() + "_TAG",
                                                         tag=determine_image_tag()) \
                  + main_test_script,
        "after_success": "python push.py -s -t {TEST}",
        "after_failure": after_failure_action
    }

    job_body = {
        "request": {
            "message": "{} systemtests".format(adapter),
            "branch": "{}".format(branch),
            "config": {
                # we need to use 'replace' to replace .travis.yml,
                # that is originally present in the repo
                "merge_mode": "replace",
                "sudo": "true",
                "dist": "trusty",
                "language": "python",
                "services": "docker",
                "python": "3.5",
                "jobs": {
                    "include": [
                    ]
                }
            }
        }
    }

    # generate jobs body for the request, build of an adapter
    # should be first stage
    jobs = [build_template]
    for tests in adapters_info[adapter].tests:
        job = {}
        for key, systest_template in systest_templates.items():
            job[key] = systest_template.format(TESTNAME=tests, USER=user, TEST=tests,
                                               ADAPTER=adapter, BASE=base)
        jobs.append(job)

    job_body["request"]["message"] = "{} systemtest. Triggered by:{}".format(adapter, triggered_by)
    job_body["request"]["config"]["jobs"]["include"] = jobs;

    return job_body


def trigger_travis_build(job_body, user, repo):
    """ Trigger custom travis build using "job_body" as specification
    in the user/repo using Travis API V3
    """

    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/requests".format(TRAVIS_URL="travis-ci.org",
                                                                          USER=user, REPO=repo)

    data = json.dumps(job_body).encode('utf8')

    return get_json_response(url, data=data)


def check_job_status(job_id):
    """ Checks status of the travis job"""
    url = "https://api.{TRAVIS_URL}/build/{JOB_ID}".format(TRAVIS_URL="travis-ci.org", JOB_ID=job_id)

    resp = get_json_response(url)
    return resp['state']


def get_requests(user, repo):
    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/requests".format(TRAVIS_URL="travis-ci.org",
                                                                          USER=user, REPO=repo)
    return get_json_response(url)


def query_request_info(user, repo, req_id):
    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/request/{REQUEST_ID}".format(TRAVIS_URL="travis-ci.org",
                                                                                      USER=user, REPO=repo,
                                                                                      REQUEST_ID=req_id)
    return get_json_response(url)


def trigger_travis_and_wait_and_respond(job_body, user, repo):
    json_response = trigger_travis_build(job_body, user, repo)
    request_id = json_response['request']['id']

    request_info = query_request_info(user, repo, request_id)
    # it case request is being processes slow for whatever reasons
    # (e.g) multiple requests were triggered, we don't yet have
    # info about job_id, so we'll wait until we have it
    print("Request pending..")
    while request_info.get('state') == 'pending':
        # for their reference in case of failures
        print("Current request status is {}".format(request_info['state']))
        request_info = query_request_info(user, repo, request_id)
        time.sleep(60)

    if request_info["result"] != "approved":
        raise Exception("Systemtest build request did not get approved")

    build_id = request_info['builds'][0]['id']
    build_number = request_info['builds'][0]['number']
    print("\nRequest approved!\n" +
          "Assigned build on 'systemtests': {}\n\n".format(build_number))
    job_status = ''
    success_status = ["passed", "canceled"]
    failed_status = ["errored", "failed"]

    print("Job started..")
    while job_status not in (success_status + failed_status):
        job_status = check_job_status(build_id)
        print("Current job status is {}. Be patient...".format(job_status))
        time.sleep(60)

    if job_status in success_status:
        exit(0)
    else:
        exit(1)


def generate_failure_callback():
    """ Generates travis job body, that simply fails without
    running anything
    """

    triggered_by = os.environ["TRAVIS_JOB_WEB_URL"]

    callback_body = {
        "request": {
            "message": "Systemtests failed. Build url:{}".format(triggered_by),
            "branch": "master",
            "config": {
                "merge_mode": "replace",
                "sudo": "true",
                "dist": "trusty",
                "jobs": {
                    "include": {
                        "name": "Systemtest failure callback",
                        "script": "false"
                    }
                }
            }
        }}

    return callback_body


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate and trigger job for systemtests")
    parser.add_argument('--owner', type=str, help="Owner of repository", default='precice')
    parser.add_argument('--adapter', type=str, help="Adapter for which you want to trigger systemtests", required=True,
                        choices=adapters_info.keys())
    parser.add_argument('--failure', help="Whether to trigger normal or failure build", action="store_true")
    parser.add_argument('--wait', help='Whether exit only when the triggered build succeeds', action='store_true')
    parser.add_argument('--test', help='Only print generated job, do not send the request', action='store_true')
    parser.add_argument('--branch', help='Branch of systemtests being used for testing', default='master')
    args = parser.parse_args()

    if args.failure:
        repo = adapters_info[args.adapter].repo
        trigger_travis_build(generate_failure_callback(), args.owner, repo)
    else:
        if args.test:
            job = generate_travis_job(args.adapter, args.owner, trigger_failure=False, branch=args.branch)
            pprint.pprint(job)
        else:
            if args.wait:
                trigger_travis_and_wait_and_respond(generate_travis_job(args.adapter, args.owner, trigger_failure=False,
                                                                        branch=args.branch), args.owner, 'systemtests')
            else:
                trigger_travis_build(generate_travis_job(args.adapter, args.owner, branch=args.branch), args.owner,
                                     'systemtests')
