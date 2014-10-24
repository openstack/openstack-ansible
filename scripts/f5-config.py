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

import netaddr


PREFIX_NAME = 'RPC'

SNAT_POOL = (
    'create ltm snatpool %(prefix_name)s_SNATPOOL { members replace-all-with {'
    ' %(snat_pool_addresses)s } }'
)

MONITORS = (
    'create ltm monitor mysql %(prefix_name)s_MON_GALERA { count 0 database'
    ' information_schema debug yes defaults-from mysql destination *:*'
    ' interval 30 time-until-up 0 timeout 91 username haproxy }'
)

NODES = (
    'create ltm node %(node_name)s { address %(container_address)s }'
)

PRIORITY_ENTRY = '{ priority-group %(priority_int)s }'

POOL_NODE = {
    'beginning': 'create ltm pool %(pool_name)s {'
                 ' load-balancing-mode fastest-node members replace-all-with'
                 ' { %(nodes)s }',
    'priority': 'min-active-members 1',
    'end': 'monitor %(mon_type)s }'
}

VIRTUAL_ENTRIES = (
    'create ltm virtual %(vs_name)s {'
    ' destination %(internal_lb_vip_address)s:%(port)s'
    ' ip-protocol tcp mask 255.255.255.255'
    ' pool %(pool_name)s profiles replace-all-with { fastL4 { } }'
    ' source 0.0.0.0/0 source-address-translation {'
    ' pool RPC_SNATPOOL type snat } }'
)


# This is a dict of all groups and their respected values / requirements
POOL_PARTS = {
    'galera': {
        'port': 3306,
        'backend_port': 3306,
        'mon_type': 'RPC_MON_GALERA',
        'priority': True,
        'group': 'galera',
        'hosts': []
    },
    'glance_api': {
        'port': 9292,
        'backend_port': 9292,
        'mon_type': 'http',
        'group': 'glance_api',
        'hosts': []
    },
    'glance_registry': {
        'port': 9191,
        'backend_port': 9191,
        'mon_type': 'http',
        'group': 'glance_registry',
        'hosts': []
    },
    'heat_api_cfn': {
        'port': 8000,
        'backend_port': 8000,
        'mon_type': 'http',
        'group': 'heat_api_cfn',
        'hosts': []
    },
    'heat_api_cloudwatch': {
        'port': 8003,
        'backend_port': 8003,
        'mon_type': 'http',
        'group': 'heat_api_cloudwatch',
        'hosts': []
    },
    'heat_api': {
        'port': 8004,
        'backend_port': 8004,
        'mon_type': 'http',
        'group': 'heat_api',
        'hosts': []
    },
    'keystone_admin': {
        'port': 35357,
        'backend_port': 35357,
        'mon_type': 'http',
        'group': 'keystone',
        'hosts': []
    },
    'keystone_service': {
        'port': 5000,
        'backend_port': 5000,
        'mon_type': 'http',
        'group': 'keystone',
        'hosts': []
    },
    'neutron_server': {
        'port': 9696,
        'backend_port': 9696,
        'mon_type': 'http',
        'group': 'neutron_server',
        'hosts': []
    },
    'nova_api_ec2': {
        'port': 8773,
        'backend_port': 8773,
        'mon_type': 'http',
        'group': 'nova_api_ec2',
        'hosts': []
    },
    'nova_api_metadata': {
        'port': 8775,
        'backend_port': 8775,
        'mon_type': 'http',
        'group': 'nova_api_metadata',
        'hosts': []
    },
    'nova_api_os_compute': {
        'port': 8774,
        'backend_port': 8774,
        'mon_type': 'http',
        'group': 'nova_api_os_compute',
        'hosts': []
    },
    'nova_spice_console': {
        'port': 6082,
        'backend_port': 6082,
        'mon_type': 'http',
        'group': 'nova_spice_console',
        'hosts': []
    },
    'cinder_api': {
        'port': 8776,
        'backend_port': 8776,
        'mon_type': 'http',
        'group': 'cinder_api',
        'hosts': []
    },
    'horizon': {
        'port': 80,
        'backend_port': 80,
        'mon_type': 'http',
        'group': 'horizon',
        'hosts': []
    },
    'horizon_ssl': {
        'port': 443,
        'backend_port': 443,
        'mon_type': 'tcp',
        'group': 'horizon',
        'hosts': []
    },
    'elasticsearch': {
        'port': 9200,
        'backend_port': 9200,
        'mon_type': 'tcp',
        'group': 'elasticsearch',
        'hosts': []
    },
    'kibana': {
        'port': 8080,
        'backend_port': 80,
        'mon_type': 'http',
        'group': 'kibana',
        'priority': True,
        'hosts': []
    },
    'kibana_ssl': {
        'port': 8443,
        'backend_port': 443,
        'mon_type': 'tcp',
        'group': 'kibana',
        'priority': True,
        'hosts': []
    }
}


def recursive_host_get(inventory, group_name, host_dict=None):
    if host_dict is None:
        host_dict = {}

    inventory_group = inventory.get(group_name)
    if 'children' in inventory_group and inventory_group['children']:
        for child in inventory_group['children']:
            recursive_host_get(
                inventory=inventory, group_name=child, host_dict=host_dict
            )

    if inventory_group.get('hosts'):
        for host in inventory_group['hosts']:
            if host not in host_dict['hosts']:
                ca = inventory['_meta']['hostvars'][host]['container_address']
                node = {
                    'hostname': host,
                    'container_address': ca
                }
                host_dict['hosts'].append(node)

    return host_dict


def build_pool_parts(inventory):
    for key, value in POOL_PARTS.iteritems():
        recursive_host_get(
            inventory, group_name=value['group'], host_dict=value
        )

    return POOL_PARTS


def file_find(filename, user_file=None, pass_exception=False):
    """Return the path to a file.

    If no file is found the system will exit.
    The file lookup will be done in the following directories:
      /etc/rpc_deploy/
      $HOME/rpc_deploy/
      $(pwd)/rpc_deploy/

    :param filename: ``str``  Name of the file to find
    :param user_file: ``str`` Additional localtion to look in FIRST for a file
    """
    file_check = [
        os.path.join(
            '/etc', 'rpc_deploy', filename
        ),
        os.path.join(
            os.environ.get('HOME'), 'rpc_deploy', filename
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


def args():
    """Setup argument Parsing."""
    parser = argparse.ArgumentParser(
        usage='%(prog)s',
        description='Rackspace Openstack, Inventory Generator',
        epilog='Inventory Generator Licensed "Apache 2.0"')

    parser.add_argument(
        '-f',
        '--file',
        help='Inventory file. Default: [ %(default)s ]',
        required=False,
        default='rpc_inventory.json'
    )

    parser.add_argument(
        '-s',
        '--snat-pool-address',
        help='LB Main SNAT pool address for [ RPC_SNATPOOL ], for'
             ' multiple snat pool addresses comma seperate the ip'
             ' addresses. By default this IP will be .15 from within your'
             ' containers_cidr as found within inventory.',
        required=False,
        default=None
    )

    parser.add_argument(
        '--limit-source',
        help='Limit available connections to the source IP for all source'
             ' limited entries.',
        required=False,
        default=None
    )

    parser.add_argument(
        '-e',
        '--export',
        help='Export the generated F5 configuration script.'
             ' Default: [ %(default)s ]',
        required=False,
        default=os.path.join(
            os.path.expanduser('~/'), 'rpc_f5_config.sh'
        )
    )

    return vars(parser.parse_args())


def main():
    """Run the main application."""
    # Parse user args
    user_args = args()

    # Get the contents of the system environment json
    environment_file = file_find(filename=user_args['file'])
    with open(environment_file, 'rb') as f:
        inventory_json = json.loads(f.read())

    nodes = []
    pools = []
    virts = []

    pool_parts = build_pool_parts(inventory=inventory_json)
    lb_vip_address = inventory_json['all']['vars']['internal_lb_vip_address']

    for key, value in pool_parts.iteritems():
        value['group_name'] = key.upper()
        value['vs_name'] = '%s_VS_%s' % (
            PREFIX_NAME, value['group_name']
        )
        value['pool_name'] = '%s_POOL_%s' % (
            PREFIX_NAME, value['group_name']
        )

        node_data = []
        priority = 100
        for node in value['hosts']:
            node['node_name'] = '%s_NODE_%s' % (PREFIX_NAME, node['hostname'])
            nodes.append('%s\n' % NODES % node)

            virt = (
                '%s\n' % VIRTUAL_ENTRIES % {
                    'port': value['port'],
                    'vs_name': value['vs_name'],
                    'pool_name': value['pool_name'],
                    'internal_lb_vip_address': lb_vip_address
                }
            )
            if virt not in virts:
                virts.append(virt)

            if value.get('priority') is True:
                node_data.append(
                    '%s:%s %s' % (
                        node['node_name'],
                        value['backend_port'],
                        PRIORITY_ENTRY % {'priority_int': priority}
                    )
                )
                priority -= 5
            else:
                node_data.append(
                    '%s:%s' % (
                        node['node_name'],
                        value['backend_port']
                    )
                )


        value['nodes'] = ' '.join(node_data)
        pool_node = [POOL_NODE['beginning'] % value]
        if value.get('priority') is True:
            pool_node.append(POOL_NODE['priority'])

        pool_node.append(POOL_NODE['end'] % value)
        pools.append('%s\n' % ' '.join(pool_node))

    # define the SNAT pool address
    snat_pool_adds = user_args.get('snat_pool_address')
    if snat_pool_adds is None:
        container_cidr = inventory_json['all']['vars']['container_cidr']
        network = netaddr.IPNetwork(container_cidr)
        snat_pool_adds = str(network[15])

    snat_pool_addresses = ' '.join(snat_pool_adds.split(','))
    snat_pool = '%s\n' % SNAT_POOL % {
        'prefix_name': PREFIX_NAME,
        'snat_pool_addresses': snat_pool_addresses
    }

    script = [
        '#!/usr/bin/bash\n',
        snat_pool,
        '%s\n' % MONITORS % {'prefix_name': PREFIX_NAME}
    ]
    script.extend(nodes)
    script.extend(pools)
    script.extend(virts)

    with open(user_args['export'], 'wb') as f:
        f.writelines(script)


if __name__ == "__main__":
    main()
