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
from migrate_openstack_vars import main
from migrate_openstack_vars import VAR_MAPPINGS

import os
import sys


FILE_NAME = 'test_user_variables.yml'


def set_up():
    # Create an example file with key/value pairs, as well as a comment
    # The old to new value mappings are written to a file, then later the
    # file is inspected to ensure no old values remain.
    var_lines = ["{}: {}".format(key, val) for
                 key, val in VAR_MAPPINGS.items()]
    var_lines.append('# A test comment')
    sample = VAR_MAPPINGS.items()[0]
    var_lines.append('# {} / {}'.format(*sample))
    with open(FILE_NAME, 'w') as f:
        f.write('\n'.join(var_lines))


def teardown():
    # Remove files so they don't pollute the directories.
    os.remove(FILE_NAME)

def test():
    main(FILE_NAME)

    with open(FILE_NAME, 'r') as f:
        contents = f.readlines()

    for line in contents:
        # only split lines that look like a key/value pair.
        if ':' in line:
            var, value = line.split(':', 1)
            value = value.strip()
        elif '/' in line:
            # For the comment containing a variable, clean up the list
            # contents before assigning the parts we want to test.
            parts = line.split()
            parts.remove('#')
            parts.remove('/')
            var, value = parts
        else:
            var = value = line


        # Once run through the 'main' function, the keys and values should
        # match
        if not value == var:
            import pdb; pdb.set_trace()  # NOQA
            print("Var and value don't match.")
            print("Var: {}, Value: {}".format(var, value))
            sys.exit()

        invalid_variable = var not in VAR_MAPPINGS.values()
        # Comments aren't in our test mapping, so make sure we ignore them
        is_comment = line.startswith('#')

        if invalid_variable and not is_comment:
            err = "Variable {} doesn't appear to be a valid new name."
            sys.exit(err.format(var))


    print("Tests passed")


if __name__ == '__main__':
    set_up()
    test()
    teardown()
