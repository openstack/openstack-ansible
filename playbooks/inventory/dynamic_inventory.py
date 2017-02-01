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
import copy
import datetime
import json
import logging
import netaddr
import os
import Queue
import random
import sys
import tarfile
import uuid
import yaml

logger = logging.getLogger('osa-inventory')

USED_IPS = set()
INVENTORY_SKEL = {
    '_meta': {
        'hostvars': {}
    }
}

# This is a list of items that all hosts should have at all times.
# Any new item added to inventory that will used as a default argument in the
# inventory setup should be added to this list.
REQUIRED_HOSTVARS = [
    'properties',
    'ansible_host',
    'ansible_ssh_host',
    'physical_host_group',
    'container_address',
    'container_name',
    'container_networks',
    'physical_host',
    'component'
]


class MultipleHostsWithOneIPError(Exception):
    def __init__(self, ip, assigned_host, new_host):
        self.ip = ip
        self.assigned_host = assigned_host
        self.new_host = new_host

        # Order the hostnames for predictable testing.
        host_list = [assigned_host, new_host]
        host_list.sort()
        error_msg = ("Both host:{} and host:{} have "
                     "address:{} assigned.  Cannot "
                     "assign same ip to both hosts")

        self.message = error_msg.format(host_list[0], host_list[1], ip)

    def __str__(self):
        return self.message


class ProviderNetworkMisconfiguration(Exception):
    def __init__(self, queue_name):
        self.queue_name = queue_name

        error_msg = ("Provider network with queue '{queue}' "
                     "requires 'is_container_address' and "
                     "'is_ssh_address' to be set to True.")

        self.message = error_msg.format(queue=self.queue_name)

    def __str__(self):
        return self.message


class MultipleIpForHostError(Exception):
    def __init__(self, hostname, current_ip, new_ip):
        self.hostname = hostname
        self.current_ip = current_ip
        self.new_ip = new_ip

        # Sort the IPs for our error message so we're always consistent.
        ips = [current_ip, new_ip]
        ips.sort()

        error_msg = "Host {hostname} has both {ips[0]} and {ips[1]} assigned"

        self.message = error_msg.format(hostname=hostname, ips=ips)

    def __str__(self):
        return self.message


class MissingStaticRouteInfo(Exception):
    def __init__(self, queue_name):
        self.queue_name = queue_name

        error_msg = ("Static route provider network with queue '{queue}' "
                     "needs both 'cidr' and 'gateway' values.")

        self.message = error_msg.format(queue=self.queue_name)

    def __str__(self):
        return self.message


class LxcHostsDefined(Exception):
    def __init__(self):
        self.message = ("The group 'lxc_hosts' must not be defined in config;"
                        " it will be dynamically generated.")


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
        default=None
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
              'Defaults to <OSA_ROOT>/playbooks/inventory/.'),
        required=False,
        default=os.path.dirname(__file__),
    )

    return vars(parser.parse_args(arg_list))


def get_ip_address(name, ip_q):
    """Return an IP address from our IP Address queue."""
    try:
        ip_addr = ip_q.get(timeout=1)
        while ip_addr in USED_IPS:
            ip_addr = ip_q.get(timeout=1)
        else:
            USED_IPS.add(ip_addr)
            return str(ip_addr)
    except AttributeError:
        return None
    except Queue.Empty:
        raise SystemExit(
            'Cannot retrieve requested amount of IP addresses. Increase the %s'
            ' range in your openstack_user_config.yml.' % name
        )


def _load_ip_q(cidr, ip_q):
    """Load the IP queue with all IP address from a given cidr.

    :param cidr: ``str``  IP address with cidr notation
    """
    _all_ips = [str(i) for i in list(netaddr.IPNetwork(cidr))]
    base_exclude = [
        str(netaddr.IPNetwork(cidr).network),
        str(netaddr.IPNetwork(cidr).broadcast)
    ]
    USED_IPS.update(base_exclude)
    for ip in random.sample(_all_ips, len(_all_ips)):
        if ip not in USED_IPS:
            ip_q.put(ip)


def _parse_belongs_to(key, belongs_to, inventory):
    """Parse all items in a `belongs_to` list.

    :param key: ``str``  Name of key to append to a given entry
    :param belongs_to: ``list``  List of items to iterate over
    :param inventory: ``dict``  Living dictionary of inventory
    """
    for item in belongs_to:
        if key not in inventory[item]['children']:
            logger.debug("Adding %s to %s", key, item)
            append_if(array=inventory[item]['children'], item=key)


def _build_container_hosts(container_affinity, container_hosts, type_and_name,
                           inventory, host_type, container_type,
                           container_host_type, physical_host_type, config,
                           properties, assignment):
    """Add in all of the host associations into inventory.

    This will add in all of the hosts into the inventory based on the given
    affinity for a container component and its subsequent type groups.

    :param container_affinity: ``int`` Set the number of a given container
    :param container_hosts: ``list`` List of containers on an host
    :param type_and_name: ``str`` Combined name of host and container name
    :param inventory: ``dict``  Living dictionary of inventory
    :param host_type: ``str``  Name of the host type
    :param container_type: ``str``  Type of container
    :param container_host_type: ``str`` Type of host
    :param physical_host_type: ``str``  Name of physical host group
    :param config: ``dict``  User defined information
    :param properties: ``dict``  Container properties
    :param assignment: ``str`` Name of container component target
    """
    container_list = []
    is_metal = False
    if properties:
        is_metal = properties.get('is_metal', False)

    for make_container in range(container_affinity):
        for i in container_hosts:
            if '%s-' % type_and_name in i:
                append_if(array=container_list, item=i)

        existing_count = len(list(set(container_list)))

        if existing_count < container_affinity:
            hostvars = inventory['_meta']['hostvars']
            container_mapping = inventory[container_type]['children']
            address = None

            if is_metal is False:
                cuuid = '%s' % uuid.uuid4()
                cuuid = cuuid.split('-')[0]
                container_host_name = '%s-%s' % (type_and_name, cuuid)
                logger.debug("Generated container name %s",
                             container_host_name)
                hostvars_options = hostvars[container_host_name] = {}
                if container_host_type not in inventory:
                    inventory[container_host_type] = {
                        "hosts": [],
                    }

                logger.debug("Adding container %s to %s",
                             container_host_name, container_host_type)

                append_if(
                    array=inventory[container_host_type]["hosts"],
                    item=container_host_name
                )

                append_if(array=container_hosts, item=container_host_name)

            else:
                if host_type not in hostvars:
                    hostvars[host_type] = {}

                hostvars_options = hostvars[host_type]
                container_host_name = host_type
                host_type_config = config[physical_host_type][host_type]
                address = host_type_config.get('ip')

            # Create a host types containers group and append it to inventory
            host_type_containers = '%s-host_containers' % host_type
            append_if(array=container_mapping, item=host_type_containers)

            hostvars_options.update({
                'properties': properties,
                'ansible_host': address,
                'ansible_ssh_host': address,
                'container_address': address,
                'container_name': container_host_name,
                'physical_host': host_type,
                'physical_host_group': physical_host_type,
                'component': assignment
            })


def _append_container_types(inventory, host_type):
    """Append the "physical_host" type to all containers.

    :param inventory: ``dict``  Living dictionary of inventory
    :param host_type: ``str``  Name of the host type
    """
    for _host in inventory['_meta']['hostvars'].keys():
        hdata = inventory['_meta']['hostvars'][_host]
        if 'container_name' in hdata:
            if hdata['container_name'].startswith(host_type):
                if 'physical_host' not in hdata:
                    logger.debug("Set physical host for %s to %s",
                                 _host, host_type)
                    hdata['physical_host'] = host_type


def _append_to_host_groups(inventory, container_type, assignment, host_type,
                           type_and_name, host_options):
    """Append all containers to physical (logical) groups based on host types.

    :param inventory: ``dict``  Living dictionary of inventory

    :param container_type: ``str``  Type of container
    :param assignment: ``str`` Name of container component target
    :param host_type: ``str``  Name of the host type
    :param type_and_name: ``str`` Combined name of host and container name
    """
    physical_group_type = '%s_all' % container_type.split('_')[0]
    if physical_group_type not in inventory:
        logger.debug("Added %s group to inventory", physical_group_type)
        inventory[physical_group_type] = {'hosts': []}

    iph = inventory[physical_group_type]['hosts']
    iah = inventory[assignment]['hosts']
    for hname, hdata in inventory['_meta']['hostvars'].iteritems():
        is_metal = False
        properties = hdata.get('properties')
        if properties:
            is_metal = properties.get('is_metal', False)

        if 'container_types' in hdata or 'container_name' in hdata:
            if 'container_name' not in hdata:
                container = hdata['container_name'] = hname
            else:
                container = hdata['container_name']

            component = hdata.get('component')
            if container.startswith(host_type):
                if 'physical_host' not in hdata:
                    hdata['physical_host'] = host_type

                if container.startswith('%s-' % type_and_name):
                    logger.debug("Added host %s to %s hosts",
                                 container, assignment)
                    append_if(array=iah, item=container)
                elif is_metal is True:
                    if component == assignment:
                        logger.debug("Added is_metal host %s to %s hosts",
                                     container, assignment)
                        append_if(array=iah, item=container)

                if container.startswith('%s-' % type_and_name):
                    logger.debug("Added host %s to %s hosts",
                                 container, physical_group_type)
                    append_if(array=iph, item=container)
                elif is_metal is True:
                    if container.startswith(host_type):
                        logger.debug("Added is_metal host %s to %s hosts",
                                     container, physical_group_type)
                        append_if(array=iph, item=container)

                # Append any options in config to the host_vars of a container
                container_vars = host_options.get('container_vars')
                if isinstance(container_vars, dict):
                    for _keys, _vars in container_vars.items():
                        # Copy the options dictionary for manipulation
                        if isinstance(_vars, dict):
                            options = _vars.copy()
                        else:
                            options = _vars

                        limit = None
                        # If a limit is set use the limit string as a filter
                        # for the container name and see if it matches.
                        if isinstance(options, (str, dict, list)):
                            if 'limit_container_types' in options:
                                limit = options.pop(
                                    'limit_container_types', None
                                )

                        if limit is None or (component and limit in component):
                            logger.debug("Set options for %s", hname)
                            hdata[_keys] = options


def _add_container_hosts(assignment, config, container_name, container_type,
                         inventory, properties):
    """Add a given container name and type to the hosts.

    :param assignment: ``str`` Name of container component target
    :param config: ``dict``  User defined information
    :param container_name: ``str``  Name fo container
    :param container_type: ``str``  Type of container
    :param inventory: ``dict``  Living dictionary of inventory
    :param properties: ``dict``  Dict of container properties
    """
    physical_host_type = '%s_hosts' % container_type.split('_')[0]
    # If the physical host type is not in config return
    if physical_host_type not in config:
        return

    for host_type in inventory[physical_host_type]['hosts']:
        container_hosts = inventory[container_name]['hosts']

        # If host_type is not in config do not append containers to it
        if host_type not in config[physical_host_type]:
            continue

        # Get any set host options
        host_options = config[physical_host_type][host_type]
        affinity = host_options.get('affinity', {})

        container_affinity = affinity.get(container_name, 1)
        # Ensures that container names are not longer than 63
        # This section will ensure that we are not it by the following bug:
        # https://bugzilla.mindrot.org/show_bug.cgi?id=2239
        type_and_name = '%s_%s' % (host_type, container_name)
        logger.debug("Generated container name %s", type_and_name)
        max_hostname_len = 52
        if len(type_and_name) > max_hostname_len:
            raise SystemExit(
                'The resulting combination of [ "%s" + "%s" ] is longer than'
                ' 52 characters. This combination will result in a container'
                ' name that is longer than the maximum allowable hostname of'
                ' 63 characters. Before this process can continue please'
                ' adjust the host entries in your "openstack_user_config.yml"'
                ' to use a short hostname. The recommended hostname length is'
                ' < 20 characters long.' % (host_type, container_name)
            )

        physical_host = inventory['_meta']['hostvars'][host_type]
        container_host_type = '%s-host_containers' % host_type
        if 'container_types' not in physical_host:
            physical_host['container_types'] = container_host_type
        elif physical_host['container_types'] != container_host_type:
            physical_host['container_types'] = container_host_type

        # Add all of the containers into the inventory
        logger.debug("Building containers for host %s", container_name)
        _build_container_hosts(
            container_affinity,
            container_hosts,
            type_and_name,
            inventory,
            host_type,
            container_type,
            container_host_type,
            physical_host_type,
            config,
            properties,
            assignment,
        )

        # Add the physical host type to all containers from the built inventory
        _append_container_types(inventory, host_type)
        _append_to_host_groups(
            inventory,
            container_type,
            assignment,
            host_type,
            type_and_name,
            host_options
        )


def user_defined_setup(config, inventory):
    """Apply user defined entries from config into inventory.

    :param config: ``dict``  User defined information
    :param inventory: ``dict``  Living dictionary of inventory
    """
    hvs = inventory['_meta']['hostvars']
    for key, value in config.iteritems():
        if key.endswith('hosts'):
            if key not in inventory:
                logger.debug("Key %s was added to inventory", key)
                inventory[key] = {'hosts': []}

            if value is None:
                logger.debug("Key %s had no value", key)
                return

            for _key, _value in value.iteritems():
                if _key not in hvs:
                    hvs[_key] = {}

                hvs[_key].update({
                    'ansible_host': _value['ip'],
                    'ansible_ssh_host': _value['ip'],
                    'container_address': _value['ip'],
                    'is_metal': True,
                    'physical_host_group': key
                })
                logger.debug("Hostvars info updated for %s", key)

                # If the entry is missing the properties key add it.
                properties = hvs[_key].get('properties')
                if not properties or not isinstance(properties, dict):
                    hvs[_key]['properties'] = dict()

                hvs[_key]['properties'].update({'is_metal': True})

                if 'host_vars' in _value:
                    for _k, _v in _value['host_vars'].items():
                        hvs[_key][_k] = _v

                USED_IPS.add(_value['ip'])
                logger.debug("Attempting to add host %s to group %s",
                             _key, key)
                append_if(array=inventory[key]['hosts'], item=_key)


def skel_setup(environment, inventory):
    """Build out the main inventory skeleton as needed.

    :param environment: ``dict`` Known environment information
    :param inventory: ``dict``  Living dictionary of inventory
    """
    for key, value in environment.iteritems():
        if key == 'version':
            continue
        for _key, _value in value.iteritems():
            if _key not in inventory:
                logger.debug("Key %s added to inventory", _key)
                inventory[_key] = {}
                if _key.endswith('container'):
                    if 'hosts' not in inventory[_key]:
                        inventory[_key]['hosts'] = []
                else:
                    if 'children' not in inventory[_key]:
                        inventory[_key]['children'] = []
                    # TODO(nrb): This line is duplicated above;
                    # is that necessary?
                    if 'hosts' not in inventory[_key]:
                        inventory[_key]['hosts'] = []

            if 'belongs_to' in _value:
                for assignment in _value['belongs_to']:
                    if assignment not in inventory:
                        logger.debug("Created group %s", assignment)
                        inventory[assignment] = {}
                        if 'children' not in inventory[assignment]:
                            inventory[assignment]['children'] = []
                        if 'hosts' not in inventory[assignment]:
                            inventory[assignment]['hosts'] = []


def skel_load(skeleton, inventory):
    """Build out data as provided from the defined `skel` dictionary.

    :param skeleton: ``dict`` Dictionary defining group and component
        memberships for the inventory.
    :param inventory: ``dict``  Living dictionary of inventory
    """
    for key, value in skeleton.iteritems():
        _parse_belongs_to(
            key,
            belongs_to=value['belongs_to'],
            inventory=inventory
        )


def _load_optional_q(config, cidr_name):
    """Load optional queue with ip addresses.

    :param config: ``dict``  User defined information
    :param cidr_name: ``str``  Name of the cidr name
    """
    cidr = config.get(cidr_name)
    ip_q = None
    if cidr is not None:
        ip_q = Queue.Queue()
        _load_ip_q(cidr=cidr, ip_q=ip_q)
    return ip_q


def network_entry(is_metal, interface,
                  bridge=None, net_type=None, net_mtu=None):
    """Return a network entry for a container."""

    # TODO(cloudnull) After a few releases this conditional should be
    # simplified. The container address checking that is ssh address
    # is only being done to support old inventory.

    if is_metal:
        _network = dict()
    else:
        _network = {'interface': interface}

    if bridge:
        _network['bridge'] = bridge

    if net_type:
        _network['type'] = net_type

    if net_mtu:
        _network['mtu'] = net_mtu

    return _network


def _add_additional_networks(key, inventory, ip_q, q_name, netmask, interface,
                             bridge, net_type, net_mtu, user_config,
                             is_ssh_address, is_container_address,
                             static_routes):
    """Process additional ip adds and append then to hosts as needed.

    If the host is found to be "is_metal" it will be marked as "on_metal"
    and will not have an additionally assigned IP address.

    :param key: ``str`` Component key name. This could be a group or a host
        name
    :param inventory: ``dict``  Living dictionary of inventory.
    :param ip_q: ``object`` build queue of IP addresses.
    :param q_name: ``str`` key to use in host vars for storage. May be blank.
    :param netmask: ``str`` netmask to use.
    :param interface: ``str`` interface name to set for the network.
    :param user_config: ``dict`` user defined configuration details.
    :param is_ssh_address: ``bol`` set this address as ansible_ssh_host.
    :param is_container_address: ``bol`` set this address to container_address.
    :param static_routes: ``list`` List containing static route dicts.
    """

    base_hosts = inventory['_meta']['hostvars']
    lookup = inventory.get(key, list())

    if 'children' in lookup and lookup['children']:
        for group in lookup['children']:
            _add_additional_networks(
                group,
                inventory,
                ip_q,
                q_name,
                netmask,
                interface,
                bridge,
                net_type,
                net_mtu,
                user_config,
                is_ssh_address,
                is_container_address,
                static_routes
            )

    # Make sure the lookup object has a value.
    if lookup:
        hosts = lookup.get('hosts')
        if not hosts:
            return
    else:
        return

    # TODO(cloudnull) after a few releases this should be removed.
    if q_name:
        old_address = '%s_address' % q_name
    else:
        old_address = '%s_address' % interface

    for container_host in hosts:
        container = base_hosts[container_host]

        # TODO(cloudnull) after a few releases this should be removed.
        # This removes the old container network value that now serves purpose.
        container.pop('container_network', None)

        if 'container_networks' in container:
            networks = container['container_networks']
        else:
            networks = container['container_networks'] = dict()

        is_metal = False
        properties = container.get('properties')
        if properties:
            is_metal = properties.get('is_metal', False)

        # This should convert found addresses based on q_name + "_address"
        #  and then build the network if its not found.
        if not is_metal and old_address not in networks:
            network = networks[old_address] = network_entry(
                is_metal,
                interface,
                bridge,
                net_type,
                net_mtu
            )
            if old_address in container and container[old_address]:
                network['address'] = container.pop(old_address)
            elif not is_metal:
                address = get_ip_address(name=q_name, ip_q=ip_q)
                if address:
                    network['address'] = address

            network['netmask'] = netmask
        elif is_metal:
            network = networks[old_address] = network_entry(
                is_metal,
                interface,
                bridge,
                net_type,
                net_mtu
            )
            network['netmask'] = netmask
            if is_ssh_address or is_container_address:
                # Container physical host group
                cphg = container.get('physical_host_group')

                # user_config data from the container physical host group
                phg = user_config[cphg][container_host]
                network['address'] = phg['ip']

        if is_ssh_address is True:
            container['ansible_host'] = networks[old_address]['address']
            container['ansible_ssh_host'] = networks[old_address]['address']

        if is_container_address is True:
            container['container_address'] = networks[old_address]['address']

        if static_routes:
            # NOTE: networks[old_address]['static_routes'] will get
            #       regenerated on each run
            networks[old_address]['static_routes'] = []
            for route in static_routes:
                # only add static routes if they are specified correctly;
                # that is, the key and a value must be present. This doesn't
                # ensure that the values provided are routable, just that
                # they are not empty.
                cidr_present = route.get('cidr', False)
                gateway_present = route.get('gateway', False)

                if not (cidr_present and gateway_present):
                    raise MissingStaticRouteInfo(q_name)
                networks[old_address]['static_routes'].append(route)


def container_skel_load(container_skel, inventory, config):
    """Build out all containers as defined in the environment file.

    :param container_skel: ``dict`` container skeleton for all known containers
    :param inventory: ``dict``  Living dictionary of inventory
    :param config: ``dict``  User defined information
    """
    logger.debug("Loading container skeleton")
    if 'lxc_hosts' not in inventory.keys():
        logger.debug("Created lxc_hosts group.")
        inventory['lxc_hosts'] = {'hosts': []}
    for key, value in container_skel.iteritems():
        contains_in = value.get('contains', False)
        belongs_to_in = value.get('belongs_to', False)
        if contains_in or belongs_to_in:
            for assignment in value['contains']:
                for container_type in value['belongs_to']:
                    _add_container_hosts(
                        assignment,
                        config,
                        key,
                        container_type,
                        inventory,
                        value.get('properties')
                    )
    else:
        cidr_networks = config.get('cidr_networks')
        provider_queues = {}
        for net_name in cidr_networks:
            ip_q = _load_optional_q(
                cidr_networks, cidr_name=net_name
            )
            provider_queues[net_name] = ip_q
            if ip_q is not None:
                net = netaddr.IPNetwork(cidr_networks.get(net_name))
                provider_queues['%s_netmask' % net_name] = str(net.netmask)

        overrides = config['global_overrides']
        # iterate over a list of provider_networks, var=pn
        pns = overrides.get('provider_networks', list())
        for pn in pns:
            # p_net are the provider_network values
            p_net = pn.get('network')
            if not p_net:
                continue

            q_name = p_net.get('ip_from_q')
            ip_from_q = provider_queues.get(q_name)
            if ip_from_q:
                netmask = provider_queues['%s_netmask' % q_name]
            else:
                netmask = None

            for group in p_net.get('group_binds', list()):
                _add_additional_networks(
                    key=group,
                    inventory=inventory,
                    ip_q=ip_from_q,
                    q_name=q_name,
                    netmask=netmask,
                    interface=p_net['container_interface'],
                    bridge=p_net['container_bridge'],
                    net_type=p_net.get('container_type'),
                    net_mtu=p_net.get('container_mtu'),
                    user_config=config,
                    is_ssh_address=p_net.get('is_ssh_address'),
                    is_container_address=p_net.get('is_container_address'),
                    static_routes=p_net.get('static_routes')
                )

    populate_lxc_hosts(inventory)


def populate_lxc_hosts(inventory):
    """Insert nodes hosting LXC containers into the lxc_hosts group

    The inventory dictionary passed in to this function will be mutated.

    :param inventory: The dictionary containing the Ansible inventory
    """
    host_nodes = _find_lxc_hosts(inventory)
    inventory['lxc_hosts'] = {'hosts': host_nodes}
    logger.debug("Created lxc_hosts group.")


def _find_lxc_hosts(inventory):
    """Build the lxc_hosts dynamic group

    Inspect the generated inventory for nodes that host LXC containers.
    Return a list of those that match for insertion into the inventory.
    Populate the 'lxc_hosts' group with any node that matches.

    This and the populate_lxc_hosts function are split in order to be less
    coupled and more testable.

    :param inventory: The dictionary containing the Ansible inventory
    :returns: List of hostnames that are LXC hosts
    :rtype: list
    """
    host_nodes = []
    for host, hostvars in inventory['_meta']['hostvars'].items():
        physical_host = hostvars.get('physical_host', None)

        # We want this node's "parent", so append the physical host
        if not host == physical_host:
            appended = append_if(array=host_nodes, item=physical_host)
            if appended:
                logger.debug("%s added to lxc_hosts group", physical_host)
    return host_nodes


def find_config_path(user_config_path=None):
    """Return the path to the user configuration files.

    If no directory is found the system will exit.

    The lookup will be done in the following directories:

      * user_config_path
      * ``/etc/openstack_deploy/``

    :param user_config_path: ``str`` Location to look in FIRST for a file
    """
    path_check = [
        os.path.join('/etc', 'openstack_deploy'),
    ]

    if user_config_path is not None:
        path_check.insert(0, os.path.expanduser(user_config_path))

    for f in path_check:
        if os.path.isdir(f):
            return f
    else:
        raise SystemExit('No config found at: %s' % path_check)


def _set_used_ips(user_defined_config, inventory):
    """Set all of the used ips into a global list.

    :param user_defined_config: ``dict`` User defined configuration
    :param inventory: ``dict`` Living inventory of containers and hosts
    """
    used_ips = user_defined_config.get('used_ips')
    if isinstance(used_ips, list):
        for ip in used_ips:
            split_ip = ip.split(',')
            if len(split_ip) >= 2:
                ip_range = list(
                    netaddr.iter_iprange(
                        split_ip[0],
                        split_ip[-1]
                    )
                )
                USED_IPS.update([str(i) for i in ip_range])
            else:
                logger.debug("IP %s set as used", split_ip[0])
                USED_IPS.add(split_ip[0])

    # Find all used IP addresses and ensure that they are not used again
    for host_entry in inventory['_meta']['hostvars'].values():
        networks = host_entry.get('container_networks', dict())
        for network_entry in networks.values():
            address = network_entry.get('address')
            if address:
                logger.debug("IP %s set as used", address)
                USED_IPS.add(address)


def _ensure_inventory_uptodate(inventory, container_skel):
    """Update inventory if needed.

    Inspect the current inventory and ensure that all host items have all of
    the required entries.

    :param inventory: ``dict`` Living inventory of containers and hosts
    """
    host_vars = inventory['_meta']['hostvars']
    for hostname, _vars in host_vars.items():
        if 'container_name' not in _vars:
            _vars['container_name'] = hostname

        for rh in REQUIRED_HOSTVARS:
            if rh not in _vars:
                _vars[rh] = None
                if rh == 'container_networks':
                    _vars[rh] = {}

    # For each of the various properties in the container skeleton,
    # copy them into the host's properties dictionary
    for container_type, type_vars in container_skel.items():
        item = inventory.get(container_type)
        # Note: this creates an implicit dependency on skel_setup which
        # adds the hosts entries.
        hosts = item.get('hosts')
        if hosts:
            for host in hosts:
                container = host_vars[host]
                if 'properties' in type_vars:
                    logger.debug("Copied propeties for %s from skeleton",
                                 container)
                    container['properties'] = type_vars['properties']


def _parse_global_variables(user_cidr, inventory, user_defined_config):
    """Add any extra variables that may have been set in config.

    :param user_cidr: ``str`` IP address range in CIDR notation
    :param inventory: ``dict`` Living inventory of containers and hosts
    :param user_defined_config: ``dict`` User defined variables
    """
    if 'all' not in inventory:
        inventory['all'] = {}

    if 'vars' not in inventory['all']:
        inventory['all']['vars'] = {}

    # Write the users defined cidr into global variables.
    inventory['all']['vars']['container_cidr'] = user_cidr

    if 'global_overrides' in user_defined_config:
        if isinstance(user_defined_config['global_overrides'], dict):
            inventory['all']['vars'].update(
                user_defined_config['global_overrides']
            )
            logger.debug("Applied global_overrides")
            kept_vars = user_defined_config['global_overrides'].keys()
            kept_vars.append('container_cidr')

            # Remove global overrides that were deleted from inventory, too
            for key in inventory['all']['vars'].keys():
                if key not in kept_vars:
                    logger.debug("Deleting key %s from inventory", key)
                    del inventory['all']['vars'][key]


def append_if(array, item):
    """Append an ``item`` to an ``array`` if its not already in it.

    :param array: ``list``  List object to append to
    :param item: ``object``  Object to append to the list
    :returns array:  returns the amended list.
    """
    if item not in array:
        array.append(item)
    # TODO(nrb): Would be nice to change this to return true/false
    # for logging purposes.
    return array


def _merge_dict(base_items, new_items):
    """Recursively merge new_items into some base_items.

    If an empty dictionary is provided as a new value, it will
    completely replace the existing dictionary.

    :param base_items: ``dict``
    :param new_items: ``dict``
    :return dictionary:
    """
    for key, value in new_items.iteritems():
        if isinstance(value, dict) and value:
            base_merge = _merge_dict(base_items.get(key, {}), value)
            base_items[key] = base_merge
        else:
            base_items[key] = new_items[key]
    return base_items


def _extra_config(user_defined_config, base_dir):
    """Discover new items in any extra directories and add the new values.

    :param user_defined_config: ``dict``
    :param base_dir: ``str``
    """
    for root_dir, _, files in os.walk(base_dir):
        for name in files:
            if name.endswith(('.yml', '.yaml')):
                with open(os.path.join(root_dir, name), 'rb') as f:
                    _merge_dict(
                        user_defined_config,
                        yaml.safe_load(f.read()) or {}
                    )
                    logger.debug("Merged overrides from file %s", name)


def _check_same_ip_to_multiple_host(config):
    """Check for IPs assigned to multiple hosts

    : param: config:  ``dict`` User provided configuration
    """

    ips_to_hostnames_mapping = dict()
    for key, value in config.iteritems():
        if key.endswith('hosts'):
            for _key, _value in value.iteritems():
                hostname = _key
                ip = _value['ip']
                if not (ip in ips_to_hostnames_mapping):
                    ips_to_hostnames_mapping[ip] = hostname
                else:
                    if ips_to_hostnames_mapping[ip] != hostname:
                        info = (ip, ips_to_hostnames_mapping[ip], hostname)
                        raise MultipleHostsWithOneIPError(*info)
    logger.debug("No hosts with duplicated IPs found")


def _check_multiple_ips_to_host(config):
    """Check for multiple IPs assigned to a single hostname

    :param: config: ``dict`` User provided configuration
    """

    # Extract only the dictionaries in the host groups.
    host_ip_map = {}
    for groupnames, group in config.items():
        if '_hosts' in groupnames:
            for hostname, entries in group.items():
                if hostname not in host_ip_map:
                    host_ip_map[hostname] = entries['ip']
                else:
                    current_ip = host_ip_map[hostname]
                    new_ip = entries['ip']
                    if not current_ip == new_ip:
                        raise MultipleIpForHostError(hostname, current_ip,
                                                     new_ip)
    logger.debug("No hosts with multiple IPs found.")
    return True


def _check_lxc_hosts(config):
    if 'lxc_hosts' in config.keys():
        raise LxcHostsDefined()
    logger.debug("lxc_hosts group not defined")


def _check_config_settings(cidr_networks, config, container_skel):
    """check preciseness of config settings

    :param cidr_networks: ``dict`` cidr_networks from config
    :param config: ``dict``  User defined information
    :param container_skel: ``dict`` container skeleton for all known containers
    """

    # search for any container that doesn't have is_metal flag set to true
    is_provider_networks_needed = False
    for key, value in container_skel.iteritems():
        properties = value.get('properties')
        is_metal = properties.get('is_metal', False)
        if not is_metal:
            is_provider_networks_needed = True
            break

    if is_provider_networks_needed:
        if ('global_overrides' not in config):
            raise SystemExit(
                "global_overrides can't be found in user config"
            )

        elif ('provider_networks' not in config['global_overrides']):
            raise SystemExit(
                "provider networks can't be found under "
                "global_overrides in user config"
            )
        else:
            # make sure that provider network's ip_from_q is valid
            overrides = config['global_overrides']
            pns = overrides.get('provider_networks', list())
            for pn in pns:
                p_net = pn.get('network')
                if not p_net:
                    continue
                q_name = p_net.get('ip_from_q')
                if q_name and q_name not in cidr_networks:
                    raise SystemExit(
                        "can't find " + q_name + " in cidr_networks"
                    )
                if (p_net.get('container_bridge') ==
                        overrides.get('management_bridge')):
                    if (not p_net.get('is_ssh_address') or
                            not p_net.get('is_container_address')):
                        raise ProviderNetworkMisconfiguration(q_name)

    logger.debug("Provider network information OK")

    # look for same ip address assigned to different hosts
    _check_same_ip_to_multiple_host(config)

    _check_multiple_ips_to_host(config)

    _check_lxc_hosts(config)


def load_environment(config_path, environment):
    """Create an environment dictionary from config files

    :param config_path: ``str`` path where the environment files are kept
    :param environment: ``dict`` dictionary to populate with environment data
    """

    # Load all YAML files found in the env.d directory
    env_plugins = os.path.join(config_path, 'env.d')

    if os.path.isdir(env_plugins):
        _extra_config(user_defined_config=environment, base_dir=env_plugins)
    logger.debug("Loaded environment from %s", config_path)
    return environment


def load_user_configuration(config_path):
    """Create a user configuration dictionary from config files

    :param config_path: ``str`` path where the configuration files are kept
    """

    user_defined_config = dict()

    # Load the user defined configuration file
    user_config_file = os.path.join(config_path, 'openstack_user_config.yml')
    if os.path.isfile(user_config_file):
        with open(user_config_file, 'rb') as f:
            user_defined_config.update(yaml.safe_load(f.read()) or {})

    # Load anything in a conf.d directory if found
    base_dir = os.path.join(config_path, 'conf.d')
    if os.path.isdir(base_dir):
        _extra_config(user_defined_config, base_dir)

    # Exit if no user_config was found and loaded
    if not user_defined_config:
        raise SystemExit(
            'No user config loaded\n'
            'No openstack_user_config files are available in either \n%s'
            '\nor \n%s/conf.d directory' % (config_path, config_path)
        )
    logger.debug("User configuration loaded from: %s", user_config_file)
    return user_defined_config


def make_backup(config_path, inventory_file_path):
    # Create a backup of all previous inventory files as a tar archive
    inventory_backup_file = os.path.join(
        config_path,
        'backup_openstack_inventory.tar'
    )
    with tarfile.open(inventory_backup_file, 'a') as tar:
        basename = os.path.basename(inventory_file_path)
        backup_name = get_backup_name(basename)
        tar.add(inventory_file_path, arcname=backup_name)
    logger.debug("Backup written to %s", inventory_backup_file)


def get_backup_name(basename):
    utctime = datetime.datetime.utcnow()
    utctime = utctime.strftime("%Y%m%d_%H%M%S")
    return '%s-%s.json' % (basename, utctime)


def get_inventory(config_path, inventory_file_path):
    if os.path.isfile(inventory_file_path):
        with open(inventory_file_path, 'rb') as f:
            dynamic_inventory = json.loads(f.read())
            logger.debug("Loaded existing inventory from %s",
                         inventory_file_path)

        make_backup(config_path, inventory_file_path)
    else:
        dynamic_inventory = copy.deepcopy(INVENTORY_SKEL)
        logger.debug("No existing inventory, created fresh skeleton.")

    return dynamic_inventory


def main(config=None, check=False, debug=False, environment=None, **kwargs):
    """Run the main application.

    :param config: ``str`` Directory from which to pull configs and overrides
    :param check: ``bool`` Flag to enable check mode
    :param debug: ``bool`` Flag to enable debug logging
    :param kwargs: ``dict`` Dictionary of arbitrary arguments; mostly for
        catching Ansible's required `--list` parameter without name shadowing
        the `list` built-in.
    :param environment: ``str`` Directory containing the base env.d
    """
    if debug:
        log_fmt = "%(lineno)d - %(funcName)s: %(message)s"
        logging.basicConfig(format=log_fmt, filename='inventory.log')
        logger.setLevel(logging.DEBUG)
        logger.info("Beginning new inventory run")

    # Get the path to the user configuration files
    config_path = find_config_path(
        user_config_path=config
    )

    user_defined_config = load_user_configuration(config_path)
    base_env_dir = environment
    base_env = load_environment(base_env_dir, {})
    environment = load_environment(config_path, base_env)

    # Load existing inventory file if found
    dynamic_inventory_file = os.path.join(
        config_path, 'openstack_inventory.json'
    )

    dynamic_inventory = get_inventory(config_path, dynamic_inventory_file)

    # Save the users container cidr as a group variable
    cidr_networks = user_defined_config.get('cidr_networks')
    if not cidr_networks:
        raise SystemExit('No container CIDR specified in user config')

    if 'container' in cidr_networks:
        user_cidr = cidr_networks['container']
    elif 'management' in cidr_networks:
        user_cidr = cidr_networks['management']
    else:
        raise SystemExit('No container or management network '
                         'specified in user config.')

    # make sure user_defined config is self contained
    _check_config_settings(
        cidr_networks,
        user_defined_config,
        environment.get('container_skel')
    )

    # Add the container_cidr into the all global ansible group_vars
    _parse_global_variables(user_cidr, dynamic_inventory, user_defined_config)

    # Load all of the IP addresses that we know are used and set the queue
    _set_used_ips(user_defined_config, dynamic_inventory)
    user_defined_setup(user_defined_config, dynamic_inventory)
    skel_setup(environment, dynamic_inventory)
    logger.debug("Loading physical skel.")
    skel_load(
        environment.get('physical_skel'),
        dynamic_inventory
    )
    logger.debug("Loading component skel")
    skel_load(
        environment.get('component_skel'),
        dynamic_inventory
    )
    container_skel_load(
        environment.get('container_skel'),
        dynamic_inventory,
        user_defined_config
    )

    # Look at inventory and ensure all entries have all required values.
    _ensure_inventory_uptodate(
        inventory=dynamic_inventory,
        container_skel=environment.get('container_skel'),
    )

    # Load the inventory json
    dynamic_inventory_json = json.dumps(
        dynamic_inventory,
        indent=4,
        sort_keys=True
    )

    if check:
        return 'Configuration ok!'

    # Generate a list of all hosts and their used IP addresses
    hostnames_ips = {}
    for _host, _vars in dynamic_inventory['_meta']['hostvars'].iteritems():
        host_hash = hostnames_ips[_host] = {}
        for _key, _value in _vars.iteritems():
            if _key.endswith('address') or _key == 'ansible_ssh_host':
                host_hash[_key] = _value

    # Save a list of all hosts and their given IP addresses
    hostnames_ip_file = os.path.join(
        config_path, 'openstack_hostnames_ips.yml')
    with open(hostnames_ip_file, 'wb') as f:
        f.write(
            json.dumps(
                hostnames_ips,
                indent=4,
                sort_keys=True
            )
        )

    if logger.isEnabledFor(logging.DEBUG):
        num_hosts = len(dynamic_inventory['_meta']['hostvars'])
        logger.debug("%d hosts found." % num_hosts)

    # Save new dynamic inventory
    with open(dynamic_inventory_file, 'wb') as f:
        f.write(dynamic_inventory_json)
        logger.info("Inventory written")

    return dynamic_inventory_json

if __name__ == '__main__':
    all_args = args(sys.argv[1:])
    output = main(**all_args)
    print(output)
