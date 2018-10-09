#!/usr/bin/env python
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

# This could probably be made more generic, since the biggest change per
# service is the variable mappings
import sys

VAR_MAPPINGS = {
    # Add mapped items here
    'test-old': 'test-new'
}


def update_variables(old_contents):
    """Replace all references to old variables.

    This includes comments and references within values for other variables.
    """
    new_contents = []

    for line in old_contents:
        words = line.split()

        for word in words:
            # Using the whitespace split above, the keys in the yaml file will
            # have a : at the end, so we need to strip that off before
            # replacing
            if word.endswith(':'):
                word = word[:-1]

            if word in VAR_MAPPINGS.keys():
                line = line.replace(word, VAR_MAPPINGS[word])

        new_contents.append(line)

    return new_contents


def main(filename):
    with open(filename, 'r') as f:
        contents = f.readlines()

    new_contents = update_variables(contents)

    with open(filename, 'w') as f:
        f.write(''.join(new_contents))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("Filename and flag file reference required.")

    filename = sys.argv[1]
    flag_ref = sys.argv[2]
    main(filename)

    flag_file = '/etc/openstack_deploy.ROCKY/VARS_MIGRATED_%s' % flag_ref
    with open(flag_file, 'w') as f:
        f.write('OpenStack-Ansible variables migrated.')
