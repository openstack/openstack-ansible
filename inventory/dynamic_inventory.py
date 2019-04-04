#!/opt/ansible-runtime/bin/python
# Copyright 2014, Rackspace US, Inc.
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
# (c) 2014, Kevin Carter <kevin.carter@rackspace.com>

import argparse
import os
import sys

try:
    from osa_toolkit import generate
except ImportError:
    current_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    lib_path = os.path.join(current_path, '..')
    sys.path.append(lib_path)
    from osa_toolkit import generate


# Function kept in order to use relative pathing for the env.d directory
def args(arg_list):
    """Setup argument Parsing."""
    parser = argparse.ArgumentParser(
        usage='%(prog)s',
        description='OpenStack Inventory Generator',
        epilog='Inventory Generator Licensed "Apache 2.0"')

    parser.add_argument(
        '--config',
        help='Path containing the user defined configuration files',
        required=False,
        default=os.getenv('OSA_CONFIG_DIR', None)
    )
    parser.add_argument(
        '--list',
        help='List all entries',
        action='store_true'
    )

    parser.add_argument(
        '--check',
        help="Configuration check only, don't generate inventory",
        action='store_true',
    )

    parser.add_argument(
        '-d',
        '--debug',
        help=('Output debug messages to log file. '
              'File is appended to, not overwritten'),
        action='store_true',
        default=False,
    )

    parser.add_argument(
        '-e',
        '--environment',
        help=('Directory that contains the base env.d directory.\n'
              'Defaults to <OSA_ROOT>/inventory/.'),
        required=False,
        default=os.path.dirname(__file__),
    )

    return vars(parser.parse_args(arg_list))


if __name__ == '__main__':
    all_args = args(sys.argv[1:])
    output = generate.main(**all_args)
    print(output)
