#!/opt/ansible-runtime/bin/python
#
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
# (c) 2015, Major Hayden <major@mhtx.net>
#
"""Returns data about containers and groups in tabular formats."""
import argparse
import json
import prettytable

from osa_toolkit import dictutils as du
from osa_toolkit import filesystem as filesys


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
        required=False,
        default='openstack_inventory.json'
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
        '-d',
        '--remove-group',
        help='group name to remove from inventory, this can be used multiple'
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
    exclusive_action.add_argument(
        '-g',
        '--list-groups',
        help='List groups and containers in each group',
        action='store_true',
        default=False
    )
    exclusive_action.add_argument(
        '-G',
        '--list-containers',
        help='List containers and their groups',
        action='store_true',
        default=False
    )

    exclusive_action.add_argument(
        '-e',
        '--export',
        help='Export group and variable information per host in JSON.',
        action='store_true',
        default=False
    )

    exclusive_action.add_argument(
        '--clear-ips',
        help='''Clears IPs from the existing inventory, but leaves
              all other information intact. LXC interface files and
              load balancers will *not* be modified.''',
        action='store_true',
        default=False
    )

    return vars(parser.parse_args())


def get_all_groups(inventory):
    """Retrieve all ansible groups.

    Keyword arguments:
    inventory -- inventory dictionary

    Will return a dictionary of containers as keys and corresponding groups
    as values.
    """
    containers = {}
    for container_name in inventory['_meta']['hostvars'].keys():

        # Skip the default group names since they're not helpful (like aio1).
        if '_' not in container_name:
            continue

        groups = get_groups_for_container(inventory, container_name)
        containers[container_name] = groups

    return containers


def get_groups_for_container(inventory, container_name):
    """Return groups for a particular container.

    Keyword arguments:
    inventory -- inventory dictionary
    container_name -- name of a container to lookup

    Will return a list of groups that the container belongs to.
    """
    # Beware, this dictionary comprehension requires Python 2.7, but we should
    # have this on openstack-ansible hosts already.
    groups = {k for (k, v) in inventory.items()
              if ('hosts' in v and container_name in v['hosts'])}
    return groups


def get_containers_for_group(inventory, group):
    """Return containers that belong to a particular group.

    Keyword arguments:
    inventory -- inventory dictionary
    group -- group to use to lookup containers

    Will return a list of containers that belong to a group, or None if no
    containers match the group provided.
    """
    if 'hosts' in inventory[group]:
        containers = inventory[group]['hosts']
    else:
        containers = None
    return containers


def print_groups_per_container(inventory):
    """Return a table of containers and the groups they belong to.

    Keyword arguments:
    inventory -- inventory dictionary
    """
    containers = get_all_groups(inventory)
    required_list = [
        'container_name',
        'groups'
    ]
    table = prettytable.PrettyTable(required_list)

    for container_name, groups in containers.items():
        row = [container_name, ', '.join(sorted(groups))]
        table.add_row(row)

    for tbl in table.align.keys():
        table.align[tbl] = 'l'

    return table


def print_containers_per_group(inventory):
    """Return a table of groups and the containers in each group.

    Keyword arguments:
    inventory -- inventory dictionary
    """
    required_list = [
        'groups',
        'container_name'
    ]
    table = prettytable.PrettyTable(required_list)

    for group_name in inventory.keys():
        containers = get_containers_for_group(inventory, group_name)

        # Don't show a group if it has no containers
        if containers is None or len(containers) < 1:
            continue

        # Don't show default group
        if len(containers) == 1 and '_' not in containers[0]:
            continue

        # Join with newlines here to avoid having a horrific table with tons
        # of line wrapping.
        row = [group_name, '\n'.join(containers)]
        table.add_row(row)

    for tbl in table.align.keys():
        table.align[tbl] = 'l'

    return table


def print_inventory(inventory, sort_key):
    """Return a table of containers with detail about each.

    Keyword arguments:
    inventory -- inventory dictionary
    """
    _meta_data = inventory['_meta']['hostvars']
    required_list = [
        'container_name',
        'is_metal',
        'component',
        'physical_host',
        'tunnel_address',
        'ansible_host',
        'container_types'
    ]
    table = prettytable.PrettyTable(required_list)
    for key, values in _meta_data.items():
        for rl in required_list:
            if rl not in values:
                values[rl] = None
        else:
            row = []
            for _rl in required_list:
                if _rl == 'component':
                    if values.get(_rl) is None:
                        values[_rl] = "-undefined-"
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


def export_host_info(inventory):
    """Pivot variable information to be a per-host dict

    This command is meant for exporting an existing inventory's information.
    The exported data re-arranges variable data so that the keys are the host,
    and the values are hostvars and groups.

    Two top level keys are present: 'hosts' and 'all'. 'hosts' is a dictonary
    of the host information. 'all' represents global data, mostly the load
    balancer and provider network values. It is taken from
    inventory['all']['vars'].
    """
    export_info = {'hosts': {}}
    host_info = export_info['hosts']

    export_info['all'] = inventory['all']['vars']

    for host, hostvars in inventory['_meta']['hostvars'].items():
        host_info[host] = {}
        host_info[host]['hostvars'] = hostvars

    for group_name, group_info in inventory.items():
        if group_name in ('_meta', 'all'):
            continue
        for host in group_info['hosts']:
            if 'groups' not in host_info[host]:
                host_info[host]['groups'] = []
            host_info[host]['groups'].append(group_name)

    return export_info


def remove_ip_addresses(inventory, filepath=None):
    """Removes container IP address information from the inventory dictionary

    Writes the changes into the inventory file in filepath if specified

    All container_networks information for containers will be deleted.
    """
    hostvars = inventory['_meta']['hostvars']

    for host, variables in hostvars.items():
        if variables.get('is_metal', False):
            continue

        ip_vars = ['container_networks', 'container_address',
                   'ansible_host', 'ansible_ssh_host']

        # Don't raise a KeyError if the entries have already been removed.
        for ip_var in ip_vars:
            variables.pop(ip_var, None)

    if filepath is not None:
        inventory_json = json.dumps(inventory, indent=2,
                                    separators=(',', ': '))
        filesys.save_inventory(inventory_json, filepath)


def remove_inventory_group(remove_group, inventory, filepath=None):
    for group in remove_group:
        inventory.pop(group, None)

    if filepath is not None:
        inventory_json = json.dumps(inventory, indent=2,
                                    separators=(',', ': '))
        filesys.save_inventory(inventory_json, filepath)


def remove_inventory_item(remove_item, inventory, filepath=None):
    """Removes inventory item from the inventory dictionary

    Writes the changes into the inventory file in filepath if available

    All container_networks information for containers will be deleted.
    """
    du.recursive_dict_removal(inventory, remove_item)

    if filepath is not None:
        inventory_json = json.dumps(inventory, indent=2,
                                    separators=(',', ': '))
        filesys.save_inventory(inventory_json, filepath)


def main():
    """Run the main application."""
    # Parse user args
    user_args = args()

    # Get the contents of the system inventory
    inventory, filepath = filesys.load_inventory(filename=user_args['file'])

    # Make a table with hosts in the left column and details about each in the
    # columns to the right
    if user_args['list_host'] is True:
        print(print_inventory(inventory, user_args['sort']))

    # Groups in first column, containers in each group on the right
    elif user_args['list_groups'] is True:
        print(print_groups_per_container(inventory))

    # Containers in the first column, groups for each container on the right
    elif user_args['list_containers'] is True:
        print(print_containers_per_group(inventory))
    elif user_args['export'] is True:
        print(json.dumps(export_host_info(inventory), indent=2))
    elif user_args['clear_ips'] is True:
        remove_ip_addresses(inventory, filepath)
        print('Success. . .')
    elif user_args['remove_group']:
        remove_inventory_group(user_args['remove_group'], inventory, filepath)
        print('Success. . .')
    else:
        remove_inventory_item(user_args['remove_item'], inventory, filepath)
        print('Success. . .')


if __name__ == "__main__":
    main()
