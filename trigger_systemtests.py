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

adapter_info = namedtuple('adapter_info', 'repo tests base install_mode')

adapters_info = {"openfoam": adapter_info('openfoam-adapter', ['of-of', 'of-ccx'],  'Ubuntu1804.package', 'clone'),
                "calculix":  adapter_info('calculix-adapter', ['of-ccx','su2-ccx'], 'Ubuntu1804.package', 'clone'),
                "su2":       adapter_info('su2-adapter',      ['su2-ccx'],          'Ubuntu1804.package', 'clone'),
                "dealii":    adapter_info('dealii-adapter',   ['dealii-of'],        'Ubuntu1804.package', 'clone'),
                "fenics":    adapter_info('fenics-adapter',   ['fe-fe'],            'Ubuntu1804.package', 'pip')}

class msg_color:
    green = "\033[92m"
    bold = "\033[1m"
    end = "\033[0m"


def get_json_response(url, **kwargs):

    headers = {
      "Content-Type" : "application/json",
      "Accept": "application/json",
      "Travis-API-Version": "3",
      "Authorization": "token {}".format(os.environ['TRAVIS_ACCESS_TOKEN'])
    }

    req = Request(url, headers = headers, **kwargs )
    response = urlopen( req ).read().decode()
    json_response = json.loads( response )


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
    if (branch or pull_req not in [None, "false"]) and adapters_info[adapter].install_mode == 'clone':
        preprocess_cmd = "grep -rl --include=\*Dockerfile\* github.com/{user}/{adapter} |\
        xargs sed -i 's|\(github.com/{user}/{adapter}.*\)|\\1 \&\& cd \
        {adapter} \&\& {post_clone_cmd} \&\& cd .. |g'".format(user = user, adapter =
                adapters_info[adapter].repo,
                post_clone_cmd = post_clone_cmd)
    elif (branch or pull_req not in [None, "false"]) and adapters_info[adapter].install_mode == 'pip':
        adapter_branch = os.environ.get("TRAVIS_PULL_REQUEST_BRANCH")
        if adapter_branch == "":
            adapter_branch = branch
        preprocess_cmd = "grep -rl --include=\*Dockerfile\* github.com/{user}/{adapter} |\
        xargs sed -i 's|\(ARG adapter_branch=.+\)|ARG adapter_branch={adapter_branch}|g'".format(user = user, adapter =
                adapters_info[adapter].repo, adapter_branch = adapter_branch, post_clone_cmd = post_clone_cmd)


    main_script = " && ".join(filter(None, ([ preprocess_cmd, script ])))

    return main_script


def determine_image_tag():

    """ Generates tag information based on the branch and pull request names """

    branch = os.environ.get("TRAVIS_BRANCH", "latest")
    pull_req = os.environ.get("TRAVIS_PULL_REQUEST")
    if pull_req and pull_req != 'false':
        return ".pr".join([branch, pull_req])
    else:
        return branch

def generate_travis_job(adapter, user, enable_output = False, trigger_failure = True, st_branch='develop'):

    triggered_by = os.environ["TRAVIS_JOB_WEB_URL"] if "TRAVIS_JOB_WEB_URL" in\
         os.environ else "manual script call"

    base = adapters_info[adapter].base

    after_failure_action = ""
    main_test_script = "python system_testing.py -s {TEST} --base {BASE} -v"

    base_remote = "precice/precice-{base}-develop".format(base = base.lower())
    main_build_script = "docker build -f adapters/Dockerfile.{adapter} -t \
        {user}/{adapter}-{base}-develop:{tag} --build-arg from={base_remote}  .".format(adapter =
                adapters_info[adapter].repo, user = user, base_remote =
                base_remote, tag = determine_image_tag(), base=base.lower())

    if trigger_failure:
        after_failure_action += " python trigger_systemtests.py --failure --owner {USER} --adapter {ADAPTER}"


    # template for building this particular adapter
    build_template = {
        "stage": "Building adapter",
        "name": adapters_info[adapter].repo,
        "script": adjust_travis_script(main_build_script, user, adapter),
        "after_success":
            [  'echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin',
                'docker push {user}/{adapter}-{base}-develop:{tag}'.format(adapter =
                    adapters_info[adapter].repo, user = user,tag = determine_image_tag(), base=base.lower()) ]
        }

    # template for actually runnig an adapter in combination with other
    # adapters
    systest_templates = {
        "stage": "Running tests",
        "name":          "[{BASE}] {TESTNAME}",
        # force docker-compose to consider an image with a particular tag
        "script":      ["export {adapter_tag}={tag}; ".format(adapter_tag = adapter.upper() + "_TAG", tag = determine_image_tag()),
                        main_test_script,
                        "python push.py" + (" -o" if enable_output else "")],
        "after_failure": after_failure_action
    };

    job_body={
        "request": {
          "message": "{} systemtest".format(adapter),
          "branch": "{}".format(st_branch),
          "config": {
            # we need to use 'replace' to replace .travis.yml,
            # that is originally present in the repo
            "merge_mode": "replace",
            "sudo": "true",
            "dist": "bionic",
            "language": "python",
            "services": "docker",
            "python": "3.8",
            "install": "pip install Jinja2",
            "jobs":  {
              "include":[
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
        for key,systest_template in systest_templates.items():
            if key is not 'script':
                job[key] = systest_template.format(TESTNAME=tests, USER=user, TEST=tests,
                    ADAPTER=adapter, BASE=base)
            else:
                job[key] = [element.format(TESTNAME=tests, USER=user, TEST=tests,
                    ADAPTER=adapter, BASE=base) for element in systest_template]
        jobs.append(job)

    job_body["request"]["message"] = "{} systemtest. Triggered by: {}".format(adapter, triggered_by)
    job_body["request"]["config"]["jobs"]["include"] = jobs;

    return job_body


def trigger_travis_build(job_body, user, repo):
    """ Trigger custom travis build using "job_body" as specification
    in the user/repo using Travis API V3
    """

    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/requests".format(TRAVIS_URL="travis-ci.com",
        USER=user,REPO=repo)

    data = json.dumps(job_body).encode('utf8')

    return get_json_response(url, data = data)

def check_job_status(job_id):
    """ Checks status of the travis job"""
    url = "https://api.{TRAVIS_URL}/build/{JOB_ID}".format(TRAVIS_URL="travis-ci.com", JOB_ID=job_id)

    resp =  get_json_response(url)
    return resp['state']

def get_requests(user, repo):

    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/requests".format(TRAVIS_URL="travis-ci.com",
            USER=user, REPO=repo )
    return get_json_response(url)

def query_request_info(user, repo, req_id):

    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/request/{REQUEST_ID}".format(TRAVIS_URL="travis-ci.com",
            USER=user, REPO=repo, REQUEST_ID=req_id)
    return get_json_response(url)

def trigger_travis_and_wait_and_respond(job_body, user, repo):

    json_response = trigger_travis_build(job_body, user, repo)
    request_id = json_response['request']['id']

    request_info = query_request_info(user, repo, request_id)
    # it case request is being processes slow for whatever reasons
    # (e.g) multiple requests were triggered, we don't yet have
    # info about job_id, so we'll wait until we have it
    print("Request pending...", flush=True)
    while request_info.get('state') == 'pending':
        # for ther reference in case of failures
        print("Current request status is '{}'.".format(request_info['state']), flush=True)
        request_info = query_request_info(user, repo, request_id)
        time.sleep(120)

    if request_info["result"] != "approved":
        raise Exception("Systemtest build request did not get approved.")

    build_id = request_info['builds'][0]['id']
    build_number = request_info['builds'][0]['number']
    print(msg_color.green +
          "###############################\n" +
          "Request approved!\n" +
          "Assigned build number on 'systemtests': {}\n\n".format(build_number) +
          "Link to build page:\n" +
          "https://travis-ci.com/github/precice/systemtests/builds/{}\n".format(build_id) +
          "###############################\n" +
          msg_color.end)
    job_status = ''
    success_status = ["passed", "canceled"]
    failed_status = ["errored", "failed"]

    print("Job started!", flush=True)
    while not job_status in (success_status + failed_status):
        time.sleep(20)
        job_status = check_job_status(build_id)
        print("Current job status is '{}'. Please wait...".format(job_status), flush=True)

    if job_status in success_status:
        print("Systemtest succeeded!")
        exit(0)
    else:
        print("Systemtest failed!\n" +
              "For more information, view the associated systemtest build.\n")
        exit(1)


def generate_failure_callback():
    """ Generates travis job body, that simply fails without
    running anything
    """

    triggered_by = os.environ["TRAVIS_JOB_WEB_URL"];

    callback_body={
    "request": {
     "message": "Systemtests failed! Build url: {}".format(triggered_by),
      "branch": "develop",
        "config": {
          "merge_mode": "replace",
          "sudo": "true",
          "dist": "trusty",
          "jobs": {
          "include":{
              "name": "Systemtest failure callback",
              "script": "false"
            }
          }
        }
    }}

    return callback_body


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Generate and trigger job for systemtests")
    parser.add_argument('--owner',  type=str, help="Owner of repository", default='precice' )
    parser.add_argument('--st-branch',  type=str, help="Used branch of systemtests", default='develop' )
    parser.add_argument('--adapter', type=str, help="Adapter for which you want to trigger systemtests",
              required=True, choices = adapters_info.keys() )
    parser.add_argument('-o', '--output', help="Enable output for the triggered tests", action='store_true')
    parser.add_argument('--failure', help="Whether to trigger normal or failure build",
              action="store_true")
    parser.add_argument('--wait', help='Whether exit only when the triggered build succeeds',
              action='store_true')
    parser.add_argument('--test', help='Only print generated job, do not send the request',
            action='store_true')
    args = parser.parse_args()

    if args.failure:
        repo = adapters_info[ args.adapter ].repo
        trigger_travis_build( generate_failure_callback(), args.owner,repo)
    else:
        if args.test:
            job = generate_travis_job(args.adapter, args.owner, enable_output=args.output,
                trigger_failure=False, st_branch=args.st_branch)
            pprint.pprint(job)
        else:
            if args.wait:
                trigger_travis_and_wait_and_respond(generate_travis_job(args.adapter, args.owner,
                    enable_output=args.output, trigger_failure=False, st_branch=args.st_branch), args.owner, 'systemtests' )
            else:
                trigger_travis_build( generate_travis_job(args.adapter, args.owner,
                    enable_output=args.output, trigger_failure=False, st_branch=args.st_branch), args.owner, 'systemtests' )
