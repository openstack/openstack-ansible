#!/usr/bin/env python
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
# (c) 2014, Nolan Brubaker <nolan.brubaker@rackspace.com>
import argparse
import os
import sys

from osa_toolkit import tools


def args(arg_list):
    parser = argparse.ArgumentParser(
        usage='%(prog)s',
        description='OpenStack Ansible Configuration Generator',
        epilog='Licensed "Apache2.0"',
    )

    parser.add_argument(
        '--base',
        '-b',
        help="Base file to be used.",
    )

    parser.add_argument(
        '--conf_dir',
        '-c',
        help=("Directory of service-specific configuration files.\n"
              "Only files ending in *.aio will be processed"),
    )

    parser.add_argument(
        '--output',
        '-o',
        help=("Path to combined output file, defaults to "
              "./openstack_user_config.yml"),
        default=os.path.join(os.getcwd(), 'openstack_user_config.yml')
    )

    return vars(parser.parse_args(arg_list))

if __name__ == "__main__":
    script_args = args(sys.argv[1:])

    config = tools.make_example_config(
        script_args['base'],
        script_args['conf_dir']
    )
    tools.write_example_config(script_args['output'], config)
