"""
 Generate Travis API V3 request to trigger corresponding systemtests
 based on the adapter type. To adjust it for newly added system test modify
 dictionaries "nm_repo_map" and "np_test_map" below with the name of the
 adapter repository and systemtests that should be run for it.
"""

import json
import os
import time
from sys import exit
import argparse
from string import Template
from urllib.parse import urlencode
from urllib.request import Request, urlopen

nm_repo_map = {'openfoam': 'openfoam-adapter',
    'calculix' : 'calculix-adapter',
    'su2': 'su2-adapter'}


nm_test_map = {'openfoam': ['of-of', 'of-ccx'],
        'calculix': ['of-ccx', 'su2-ccx'],
        'su2': ['su2-ccx'] }


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

def generate_travis_job(adapter, user, trigger_failure = True):

    triggered_by = os.environ["TRAVIS_JOB_WEB_URL"] if "TRAVIS_JOB_WEB_URL" in\
         os.environ else "manual script call"

    after_failure_action = "python push.py -t $TEST;"
    if trigger_failure:
        after_failure_action += " python trigger_systemtests.py --failure --owner $USER --adapter $ADAPTER"

    job_templates= {
        "name":  Template('[16.04] $TESTNAME <-> $TESTNAME'),
        "script": Template('python system_testing.py -s $TEST') ,
        "after_success":Template('python push.py -s -t $TEST') ,
        "after_failure": Template(after_failure_action)}

    job_body={
        "request": {
          "message": "{} systemtests".format(adapter),
          "branch": "master",
          "config": {
            # we need to use 'replace' to replace .travis.yml,
            # that is originally present in the repo
            "merge_mode": "replace",
            "sudo": "true",
            "dist": "trusty",
            "language": "python",
            "services": "docker",
            "python": "3.5",
            "jobs":  {
              "include":[
                ]
              }
            }
          }
        }

    # generate jobs body for the request
    jobs = []
    for tests in nm_test_map[adapter]:
        job = {}
        for key,template in job_templates.items():
            job[key] = template.substitute(TESTNAME=tests, USER=user, TEST=tests,
                ADAPTER=adapter)
        jobs.append(job)

    job_body["request"]["message"] = "{} systemtest. Triggered by:{}".format(adapter, triggered_by)
    job_body["request"]["config"]["jobs"]["include"] = jobs;

    return job_body


def trigger_travis_build(job_body, user, repo):
    """ Trigger custom travis build using "job_body" as specification
    in the user/repo using Travis API V3
    """

    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/requests".format(TRAVIS_URL="travis-ci.org",
        USER=user,REPO=repo)

    data = json.dumps(job_body).encode('utf8')

    return get_json_response(url, data = data)

def check_job_status(job_id):
    """ Checks status of the travis job"""
    url = "https://api.{TRAVIS_URL}/build/{JOB_ID}".format(TRAVIS_URL="travis-ci.org", JOB_ID=job_id)

    resp =  get_json_response(url)
    return resp['state']

def get_requests(user, repo):

    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/requests".format(TRAVIS_URL="travis-ci.org",
            USER=user, REPO=repo )
    return get_json_response(url)

def query_request_info(user, repo, req_id):

    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/request/{REQUEST_ID}".format(TRAVIS_URL="travis-ci.org",
            USER=user, REPO=repo, REQUEST_ID=req_id)
    return get_json_response(url)

def trigger_travis_and_wait_and_respond(job_body, user, repo):

    json_response = trigger_travis_build(job_body, user, repo)
    request_id = json_response['request']['id']

    request_info = query_request_info(user, repo, request_id)
    # it case request is being processes slow for whatever reasons
    # (e.g) multiple requests were triggered, we don't yet have
    # info about job_id, so we'll wait until we have it
    print ("Request pending..")
    while request_info.get('state') == 'pending':
        # for ther reference in case of failures
        print ("Current request status is {}".format(request_info['state']))
        request_info = query_request_info(user, repo, request_id)
        time.sleep(60)

    if request_info["result"] != "approved":
        raise Exception("Systemtest build request did not get approved")

    job_id = request_info['builds'][0]['id']

    job_status = ''
    success_status = ["passed", "canceled"]
    failed_status = ["errored", "failed"]

    print ("Job started..")
    while not job_status in (success_status + failed_status):
        job_status = check_job_status(job_id)
        print ("Current job status is {}. Be patient...".format(job_status))
        time.sleep(60)

    if job_status in success_status:
        exit(0)
    else:
        exit(1)


def generate_failure_callback():
    """ Generates travis job body, that simply fails without
    running anything
    """

    triggered_by = os.environ["TRAVIS_JOB_WEB_URL"];

    callback_body={
    "request": {
     "message": "Systemtests failed. Build url:{}".format(triggered_by),
      "branch": "master",
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
    parser.add_argument('--owner',  type=str, help="Owner of repository", default='shkodm' )
    parser.add_argument('--adapter', type=str, help="Adapter for which you want to trigger systemtests",
              required=True, choices = ["openfoam", "su2", "calculix"])
    parser.add_argument('--failure', help="Whether to trigger normal or failure build",
              action="store_true")
    parser.add_argument('--wait', help='Whether exit only when the triggered build succeeds',
              action='store_true')
    args = parser.parse_args()

    if args.failure:
        repo = nm_repo_map[ args.adapter ]
        trigger_travis_build( generate_failure_callback(), args.owner,repo)
    else:
        if args.wait:
            trigger_travis_and_wait_and_respond(generate_travis_job(args.adapter, args.owner, trigger_failure
                = False), args.owner, 'systemtests' )
        else:
            trigger_travis_build( generate_travis_job(args.adapter, args.owner),
                         args.owner, 'systemtests' )
