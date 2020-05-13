#!/usr/bin/env python2.7
#
# Copyright 2016, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2016, Jesse Pretorius <jesse.pretorius@rackspace.co.uk>
#


"""Read ansible-role-requirements.yml content from the CLI and output
   yaml content to stdout to be used when submitting release requests."""


from __future__ import print_function
from cStringIO import StringIO

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


import argparse
import re
import yaml


# To ensure that the dicts are always output in the same order
# we setup a representation for dict objects and register it
# with the yaml class.
def represent_dict(self, data):
    def key_function(elem):
        key = elem[0]
        # Prioritizes certain keys when sorting.
        prio = {"version": 0, "projects": 1, "repo": 2, "hash": 3}.get(key, 99)
        return (prio, key)
    items = data.items()
    items.sort(key=key_function)
    return self.represent_mapping(u'tag:yaml.org,2002:map', items)


yaml.add_representer(dict, represent_dict)


# sourced from
# http://stackoverflow.com/questions/25108581/python-yaml-dump-bad-indentation
def yaml_dump(dump, indentSize=2):
    stream = StringIO(dump)
    out = StringIO()
    pat = re.compile(r'(\s*)([^:]*)(:*)')
    last = None

    prefix = 0
    for s in stream:
        indent, key, colon = pat.match(s).groups()
        if indent == "" and key[0] != '-':
            prefix = 0
        if last:
            if len(last[0]) == len(indent) and last[2] == ':':
                if all([
                        not last[1].startswith('-'),
                        s.strip().startswith('-')]):
                    prefix += indentSize
        out.write(" " * prefix + s)
        last = indent, key, colon
    return out.getvalue()


def main():
    """Run the main application."""

    # Setup argument parsing
    parser = argparse.ArgumentParser(
        description='release.yml producer',
        epilog='Licensed "Apache 2.0"')

    parser.add_argument(
        '-f',
        '--file',
        help='<Required> ansible-role-requirements.yml file location',
        default='ansible-role-requirements.yml'
    )

    parser.add_argument(
        '-v',
        '--version',
        help='<Required> The release version to include in the output',
        required=True
    )

    # Parse arguments
    args = parser.parse_args()

    # Read the ansible-role-requirements.yml file into memory
    with open(args.file, "r") as role_req_file:
        reqs = yaml.safe_load(role_req_file)

    # Prepare the vars for output
    version = args.version
    projects = []

    # Prepare the regex match
    regex = re.compile('^.*openstack/(ansible-hardening|openstack-ansible.*)$')

    # Loop through the list of roles
    for role_data in reqs:
        # Only add OpenStack repositories to the release
        if regex.match(role_data['src']):
            # Prepare the repo release dict
            repo_release = {}
            # Figure out the repo from the git source
            repo = urlparse(role_data['src']).path.lstrip('/')
            # Assemble the dict
            repo_release['repo'] = repo
            repo_release['hash'] = role_data['version']
            # Add the dict to the projects list
            projects.append(repo_release.copy())

    # Put the yaml content together
    releases = {'releases': [{'version': version, 'projects': projects}]}

    # Product the YAML output for the resulting releases data
    output = yaml.dump(releases, default_flow_style=False)

    # Print the output, formatted as expected
    print(yaml_dump(output))


if __name__ == "__main__":
    main()
