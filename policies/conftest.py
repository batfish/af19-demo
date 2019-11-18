import logging
import os
import uuid

import pandas as pd
import pytest
import yaml

# from output import build_tag
from pybatfish.client.session import Session
from pybatfish.datamodel import AddressGroup, ReferenceBook

BF_NETWORK = os.environ["BF_NETWORK"]
BF_SNAPSHOT = os.environ["BF_SNAPSHOT"]
BF_INIT_SNAPSHOT = os.environ.get("BF_INIT_SNAPSHOT", "yes")

BF_SNAPSHOT_DIR = '{}/'.format(os.environ.get("BF_SNAPSHOT_DIR", "."))
BF_DASHBOARD = os.environ.get("BF_DASHBOARD", "http://localhost:3000/dashboard")

NETWORK_FIXTURES = ['demonet']

ADDRESS_GROUPS_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "address-groups.yml")

####################
# Set pandas options
####################
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

#######################
# Set pybatfish options
#######################
logging.getLogger('pybatfish').setLevel(logging.WARN)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[39;49m'


def pytest_addoption(parser):
    parser.addoption("--min-severity", action="store", default=0, type=int,
                     help="Minimal FindIssues severity to care about")


@pytest.fixture(scope="session")
def bf():

    try:
        bf = Session.get('bfe')
        os.environ["SESSION_TYPE"] = 'bfe'
    except:
        bf = Session.get('bf')
        os.environ["SESSION_TYPE"] = 'bf'

    session_type = os.environ.get('SESSION_TYPE')

    bf.enable_diagnostics = False
    bf.set_network(BF_NETWORK)
    if BF_INIT_SNAPSHOT == "yes":
        bf.init_snapshot(BF_SNAPSHOT_DIR, name=BF_SNAPSHOT, overwrite=True)
    else:
        bf.set_snapshot(BF_SNAPSHOT)
    if session_type == 'bfe':
        bf.get_node_roles()

    add_address_groups(bf)

    return bf

@pytest.fixture
def min_severity(request):
    return request.config.getoption("--min-severity")


def pytest_report_header(config):
    return [
        bcolors.BOLD + bcolors.OKBLUE + "Running Intentionet CI tests" + bcolors.RESET]


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if exitstatus != 0 and BF_DASHBOARD is not None:
        url = "{BF_DASHBOARD}/{BF_NETWORK}/{BF_SNAPSHOT}/policies".format(
            BF_DASHBOARD=BF_DASHBOARD, BF_NETWORK=BF_NETWORK, BF_SNAPSHOT=BF_SNAPSHOT)
        terminalreporter.write_line(
            "\n\n"
            + bcolors.BOLD + bcolors.FAIL
            + "There have been failures, explore more using Intentionet Dashboard at {}".format(
                url)
            + "  "  # saves URL
        )


def pytest_sessionstart(session):
    os.environ['bf_policy_name'] = session.name


p_id = uuid.uuid4().hex


def pytest_runtest_setup(item):
    # Get test file name
    test_file_name = os.path.basename(item.parent.name)
    test_name = item.name
    os.environ['bf_policy_name'] = test_file_name
    os.environ['bf_policy_id'] = p_id
    os.environ['bf_test_name'] = test_name


def subdict(d, keys):
    return {k: d.get(k) for k in keys}


def add_address_groups(bf):
    with open(ADDRESS_GROUPS_FILE, "r") as f:
        groups = yaml.safe_load(f)
    address_groups = [AddressGroup(g["name"], g["addresses"]) for g in groups["metadata"]]
    bf.put_reference_book(ReferenceBook(name="metadata", addressGroups=address_groups))
