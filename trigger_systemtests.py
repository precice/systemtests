"""
 Generate Travis API V3 request to trigger corresponding systemtests
 based on the adapter type. To adjust it for newly added system test modify
 dictionaries "nm_repo_map" and "np_test_map" below with the name of the
 adapter repository and systemtests that should be run for it.
"""

import json
import os
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


def generate_travis_job(adapter, user):

    job_templates= {
        "name":  Template('[16.04] $TESTNAME <-> $TESTNAME'),
        "script": Template('python system_testing.py -s $TEST') ,
        "after_success":Template('python push.py -s -t $TEST') ,
        "after_failure": Template("python push.py -t $TEST; python trigger_systemtests.py --failure --owner $USER --adapter $ADAPTER")}

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

    job_body["request"]["message"] = adapter + ' systemtest'
    job_body["request"]["config"]["jobs"]["include"] = jobs;

    return job_body


def trigger_travis_build(job_body, user, repo):
    """ Trigger custom travis build using "job_body" as specification
    in the user/repo using Travis API V3
    """

    url = "https://api.{TRAVIS_URL}/repo/{USER}%2F{REPO}/requests".format(TRAVIS_URL="travis-ci.org",
        USER=user,REPO=repo)

    headers = {
      "Content-Type" : "application/json",
      "Accept": "application/json",
      "Travis-API-Version": "3",
      "Authorization": "token {}".format(os.environ['TRAVIS_ACCESS_TOKEN'])
    }

    data = json.dumps(job_body).encode('utf8')
    req = Request(url, headers = headers, data = data)
    response = urlopen(req ).read().decode()


def generate_failure_callback():
    """ Generates travis job body, that simply fails without
    running anything
    """

    callback_body={
    "request": {
      "message": "Systemtests failed",
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
    parser.add_argument('--owner',  type=str, help="Owner of repository", default='precice' )
    parser.add_argument('--adapter', type=str, help="Adapter for which you want to trigger systemtests",
              required=True, choices = ["openfoam", "su2", "calculix"])
    parser.add_argument('--failure', help="Whether to trigger normal or failure build",
              action="store_true")
    args = parser.parse_args()

    if args.failure:
        repo = nm_repo_map[ args.adapter ]
        trigger_travis_build( generate_failure_callback(), args.owner,repo)
    else:
        trigger_travis_build( generate_travis_job(args.adapter, args.owner),
                     args.owner, 'systemtests' )
