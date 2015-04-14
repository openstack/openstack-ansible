#!/usr/bin/env python
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
import json
import os
import prettytable


def file_find(filename, user_file=None, pass_exception=False):
    """Return the path to a file.

    If no file is found the system will exit.
    The file lookup will be done in the following directories:
      /etc/openstack_deploy/
      $(pwd)/openstack_deploy/

    :param filename: ``str``  Name of the file to find
    :param user_file: ``str`` Additional localtion to look in FIRST for a file
    """
    file_check = [
        os.path.join(
            '/etc', 'openstack_deploy', filename
        ),
        os.path.join(
            os.getcwd(), filename
        )
    ]

    if user_file is not None:
        file_check.insert(0, os.path.expanduser(user_file))

    for f in file_check:
        if os.path.isfile(f):
            return f
    else:
        if pass_exception is False:
            raise SystemExit('No file found at: %s' % file_check)
        else:
            return False


def recursive_list_removal(inventory, purge_list):
    for item in purge_list:
        for _item in inventory:
            if item == _item:
                inventory.pop(inventory.index(item))


def recursive_dict_removal(inventory, purge_list):
    for key, value in inventory.iteritems():
        if isinstance(value, dict):
            for _key, _value in value.iteritems():
                if isinstance(_value, dict):
                    for item in purge_list:
                        if item in _value:
                            del(_value[item])
                elif isinstance(_value, list):
                    recursive_list_removal(_value, purge_list)
        elif isinstance(value, list):
            recursive_list_removal(value, purge_list)


def args():
    """Setup argument Parsing."""
    parser = argparse.ArgumentParser(
        usage='%(prog)s',
        description='OpenStack Inventory Generator',
        epilog='Inventory Generator Licensed "Apache 2.0"')

    parser.add_argument(
        '-f',
        '--file',
        help='Inventory file.',
        required=True,
        default=None
    )
    parser.add_argument(
        '-s',
        '--sort',
        help='Sort items based on given key i.e. physical_host',
        required=False,
        default='component'
    )

    exclusive_action = parser.add_mutually_exclusive_group(required=True)
    exclusive_action.add_argument(
        '-r',
        '--remove-item',
        help='host name to remove from inventory, this can be used multiple'
             ' times.',
        action='append',
        default=[]
    )
    exclusive_action.add_argument(
        '-l',
        '--list-host',
        help='',
        action='store_true',
        default=False
    )

    return vars(parser.parse_args())


def print_inventory(inventory, sort_key):
    _meta_data = inventory['_meta']['hostvars']
    required_list = [
        'container_name',
        'is_metal',
        'component',
        'physical_host',
        'tunnel_address',
        'ansible_ssh_host',
        'container_types'
    ]
    table = prettytable.PrettyTable(required_list)
    for key, values in _meta_data.iteritems():
        for rl in required_list:
            if rl not in values:
                values[rl] = None
        else:
            row = []
            for _rl in required_list:
                if _rl == 'container_name':
                    if values.get(_rl) is None:
                        values[_rl] = key

                row.append(values.get(_rl))
            else:
                table.add_row(row)
    for tbl in table.align.keys():
        table.align[tbl] = 'l'
    table.sortby = sort_key
    return table


def main():
    """Run the main application."""
    # Parse user args
    user_args = args()

    # Get the contents of the system environment json
    environment_file = file_find(filename=user_args['file'])
    with open(environment_file, 'rb') as f:
        inventory = json.loads(f.read())

    if user_args['list_host'] is True:
        print(print_inventory(inventory, user_args['sort']))
    else:
        recursive_dict_removal(inventory, user_args['remove_item'])
        with open(environment_file, 'wb') as f:
            f.write(json.dumps(inventory, indent=2))
        print('Success. . .')

if __name__ == "__main__":
    main()
