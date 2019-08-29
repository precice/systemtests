import subprocess

def call(cmd, **kwargs):
    """ Runs cmd in a shell, returns its return code. """
    print("EXECUTING:", cmd)
    cp = subprocess.run(cmd, shell=True, **kwargs)
    return cp.returncode

def ccall(cmd,  **kwargs):
    """ Runs cmd in a shell, returns its return code. Raises exception on error """
    return call(cmd, check = True, **kwargs)

def capture_output(cmd, **kwargs):
    """ Runs cmd in a shell and captures output """
    return subprocess.run(cmd, stdout=subprocess.PIPE, **kwargs).stdout.decode('utf-8')

import os


def determine_test_name(test):
    return test.split('.')[0]


def get_tests(root = os.path.join(os.getcwd(), 'tests')):
    """ List of all available system tests """
    prefixes = ["Test_", "TestCompose_"]
    tests = list(set([determine_test_name(s[len(prefix ):]) for prefix in prefixes for s in
        os.listdir(root) if s.startswith(prefix)]))
    return tests


def get_test_variants(test_name, root = os.path.join(os.getcwd(), 'tests')):
    """ List of all available system tests """
    prefixes = ["Test_", "TestCompose_"]
    test_variants = [s[len(prefix):]  for prefix in prefixes for s in os.listdir(root)
            if s.startswith(prefix + test_name)]
    # filter cases with same participants
    if test_name and not "_" in test_name:
        test_variants = [t for t in test_variants if not "_" in t]

    return test_variants


def get_test_participants(test_name):
    """ Returns solvers that participate in the test """
    solvers_abbr = {"ccx": "calculix-adapter", "su2": "su2-adapter", "of": "openfoam-adapter", 
            "dealii":"dealii-adapter", "bindings": "bindings", "fe":"fenics-adapter"}

    return [solvers_abbr[abbr] for abbr in  test_name.lower().split('_')[0].split('-')]


from contextlib import contextmanager

@contextmanager
def chdir(path):
    """ Changes and restores the current working directory. """
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)

def get_diff_files(dcmp):
    """ Given a filecmp.dircmp object, recursively compares files.
    Returns three lists: files that differ and files that exist only in left/right directory. """
    diff_files = dcmp.diff_files
    left_only = dcmp.left_only
    right_only = dcmp.right_only

    for sub_dcmp in dcmp.subdirs.values():
        ret = get_diff_files(sub_dcmp)
        diff_files += ret[0]
        left_only += ret[1]
        right_only += ret[2]

    return diff_files, left_only, right_only


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
    return len(test.split('.'))

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
