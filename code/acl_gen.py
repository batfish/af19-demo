import argparse
import os
import shlex
import subprocess
import sys
import tempfile
import yaml
from capirca.lib import naming, policy

from pybatfish.client import capirca

DEFAULT_DENY = {
    "name": "default-deny",
    "clauses": {
        "action": "deny"
    }
}


def get_definitions(networks_file, services_file):
    defs = naming.Naming()
    with open(networks_file, "r") as f:
        defs._ParseFile(f, "networks")
    with open(services_file, "r") as f:
        defs._ParseFile(f, "services")
    return defs


def to_capirca_term(term_dict):
    head = "term {} {{".format(term_dict["name"])
    tail = "}"

    term_clauses = []
    for type, value in term_dict["clauses"].items():
        term_clauses.append("    {}:: {}".format(type.replace('_', '-'), value))

    return "{}\n{}\n{}\n".format(head, "\n".join(term_clauses), tail)


def get_policy_from_capirca(policy_file):
    with open(policy_file, "r") as f:
        return f.read()


def get_policy_from_yaml(policy_file):
    with open(policy_file, "r") as f:
        pol_data = yaml.safe_load(f)

    capirca_header = """
header {{ 
   target:: {}
}}
""".format(pol_data["target"])

    capirca_terms = []
    for term in pol_data["terms"]:
        capirca_terms.append(to_capirca_term(term))

    # append default deny
    capirca_terms.append(to_capirca_term(DEFAULT_DENY))

    return "{}\n{}".format(capirca_header, "\n".join(capirca_terms))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--networks-file', help='Networks file', required=True)
    parser.add_argument('-s', '--services-file', help='Services file', required=True)
    parser.add_argument('-p', '--policy-file', help='Policy file', required=True)
    parser.add_argument('-f', "--input-format", help="Input format", choices=["yaml", "capirca"], default="yaml")

    args = parser.parse_args()

    defs = get_definitions(args.networks_file, args.services_file)

    policy_string = get_policy_from_yaml(args.policy_file) if args.input_format == "yaml" else get_policy_from_capirca(
        args.policy_file)
    pol = policy.ParsePolicy(policy_string, defs)

    acl_text = capirca._get_acl_text(pol, "juniper-srx")

    print(acl_text.replace("replace: ", ""))