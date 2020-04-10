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


"""Read/write ansible-role-requirements.yml content from the CLI."""


from __future__ import print_function

import argparse
import yaml


# To ensure that the dicts are always output in the same order
# we setup a representation for dict objects and register it
# with the yaml class.
def represent_dict(self, data):
    def key_function(elem):
        key = elem[0]
        # Prioritizes certain keys when sorting.
        prio = {"model": 0, "pk": 1, "fields": 2}.get(key, 99)
        return (prio, key)
    items = data.items()
    items.sort(key=key_function)
    return self.represent_mapping(u'tag:yaml.org,2002:map', items)


yaml.add_representer(dict, represent_dict)


def main():
    """Run the main application."""

    # Setup argument parsing
    parser = argparse.ArgumentParser(
        description='ansible-role-requirements.yml CLI editor',
        epilog='Licensed "Apache 2.0"')

    parser.add_argument(
        '-f',
        '--file',
        help='<Required> ansible-role-requirements.yml file location',
        required=True
    )

    parser.add_argument(
        '-n',
        '--name',
        help='<Required> The name of the Ansible role to edit',
        required=True
    )

    parser.add_argument(
        '-v',
        '--version',
        help='<Required> The version to set for the Ansible role',
        required=True
    )

    parser.add_argument(
        '-s',
        '--src',
        help='<Optional> The source URL to set for the Ansible role',
        required=False
    )

    # Parse arguments
    args = parser.parse_args()

    # Read the ansible-role-requirements.yml file into memory
    with open(args.file, "r") as role_req_file:
        reqs = yaml.safe_load(role_req_file)

    # Loop through the list to find the applicable role
    for role_data in reqs:
        if role_data['name'] == args.name:
            # Change the specified role data
            role_data['version'] = args.version
            if args.src:
                role_data['src'] = args.src

    # Write out the resulting file
    with open(args.file, "w") as role_req_file:
        try:
            yaml.dump(reqs, role_req_file, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == "__main__":
    main()
