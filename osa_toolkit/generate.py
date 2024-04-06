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

import copy
import json
import logging
import netaddr
from osa_toolkit import dictutils as du
from osa_toolkit import filesystem as filesys
from osa_toolkit import ip
import re
import uuid
import warnings


logger = logging.getLogger('osa-inventory')

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
    'physical_host_group',
    'management_address',
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
                     "requires 'is_management_address' "
                     "to be set to True.")

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
        self.message = ("The group 'lxc_hosts' must not"
                        " be defined in config; it will be dynamically "
                        " generated.")

    def __str__(self):
        return self.message


class GroupConflict(Exception):
    pass


def _parse_belongs_to(key, belongs_to, inventory):
    """Parse all items in a `belongs_to` list.

    This function assumes the key defined is a group that has child subgroups,
    *not* a group with hosts defined in the group configuration.

    :param key: ``str``  Name of key to append to a given entry
    :param belongs_to: ``list``  List of items to iterate over
    :param inventory: ``dict``  Living dictionary of inventory
    """
    for item in belongs_to:
        if key not in inventory[item]['children']:
            appended = du.append_if(array=inventory[item]['children'],
                                    item=key)
            if appended:
                logger.debug("Added %s to %s", key, item)


def _build_container_hosts(container_affinity, container_hosts, type_and_name,
                           inventory, host_type, container_host_type,
                           physical_host_type, config, properties, assignment):
    """Add in all of the host associations into inventory.

    This will add in all of the hosts into the inventory based on the given
    affinity for a container component and its subsequent type groups.

    :param container_affinity: ``int`` Set the number of a given container
    :param container_hosts: ``list`` List of containers on an host
    :param type_and_name: ``str`` Combined name of host and container name
    :param inventory: ``dict``  Living dictionary of inventory
    :param host_type: ``str``  Name of the host type
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
            sub_item = re.sub(r'[_-]', '[_-]', f'{type_and_name}-')
            if re.match(sub_item, i):
                du.append_if(array=container_list, item=i)

        existing_count = len(list(set(container_list)))

        if existing_count < container_affinity:
            hostvars = inventory['_meta']['hostvars']
            address = None

            if is_metal is False:
                cuuid = str(uuid.uuid4())
                cuuid = cuuid.split('-')[0]
                container_host_name = '{}-{}'.format(type_and_name, cuuid)
                logger.debug("Generated container name %s",
                             container_host_name)
                hostvars_options = hostvars[container_host_name] = {}
                if container_host_type not in inventory:
                    inventory[container_host_type] = {
                        "hosts": [],
                    }

                appended = du.append_if(
                    array=inventory[container_host_type]["hosts"],
                    item=container_host_name
                )

                if appended:
                    logger.debug("Added container %s to %s",
                                 container_host_name, container_host_type)

                du.append_if(array=container_hosts, item=container_host_name)
            else:
                if host_type not in hostvars:
                    hostvars[host_type] = {}

                hostvars_options = hostvars[host_type]
                container_host_name = host_type
                host_type_config = config[physical_host_type][host_type]
                address = host_type_config.get('ip')

            hostvars_options.update({
                'ansible_host': address,
                'management_address': address,
                'container_name': container_host_name,
                'physical_host': host_type,
                'physical_host_group': physical_host_type,
                'component': assignment
            })
            if 'properties' not in hostvars_options:
                hostvars_options['properties'] = properties


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
    physical_group_type = re.sub(
        r"(?P<group>.*)_(?P<type>.*)$",
        r'\g<group>_all',
        container_type
    )
    if physical_group_type not in inventory:
        logger.debug("Added %s group to inventory", physical_group_type)
        inventory[physical_group_type] = {'hosts': []}

    iph = inventory[physical_group_type]['hosts']
    iah = inventory[assignment]['hosts']
    for hname, hdata in inventory['_meta']['hostvars'].items():
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

                if container.startswith('{}-'.format(type_and_name)):
                    appended = du.append_if(array=iah, item=container)
                    if appended:
                        logger.debug("Added host %s to %s hosts",
                                     container, assignment)
                elif is_metal is True:
                    if component == assignment:
                        appended = du.append_if(array=iah, item=container)
                        if appended:
                            logger.debug("Added is_metal host %s to %s hosts",
                                         container, assignment)
                if container.startswith('{}-'.format(type_and_name)):
                    appended = du.append_if(array=iph, item=container)
                    if appended:
                        logger.debug("Added host %s to %s hosts",
                                     container, physical_group_type)

                elif is_metal is True:
                    if container.startswith(host_type):
                        appended = du.append_if(array=iph, item=container)
                        if appended:
                            logger.debug("Added is_metal host %s to %s hosts",
                                         container, physical_group_type)

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


def _add_container_hosts(assignment, config, container_group, container_type,
                         inventory, properties):
    """Add a given container name and type to the hosts.

    :param assignment: ``str`` Name of container component target
    :param config: ``dict``  User defined information
    :param container_group: ``str``  Name of container group. Used for
                            defining container name
    :param container_type: ``str``  Type of container
    :param inventory: ``dict``  Living dictionary of inventory
    :param properties: ``dict``  Dict of container properties
    """
    physical_host_type = re.sub(
        r"(?P<group>.*)_(?P<type>.*)$",
        r'\g<group>_hosts',
        container_type
    )
    container_name = re.sub(r'_', '-', f'{container_group}')
    # If the physical host type is not in config return
    if physical_host_type not in config:
        return

    for host_type in inventory[physical_host_type]['hosts']:
        container_hosts = inventory[container_group]['hosts']

        # If host_type is not in config do not append containers to it
        if host_type not in config[physical_host_type]:
            continue

        # Get any set host options
        host_options = config[physical_host_type][host_type]
        affinity = host_options.get('affinity', {})
        # Try to get no_containers from host_options and
        # fallback to global_overrides if nothing found
        no_containers = host_options.get(
            'no_containers',
            config['global_overrides'].get('no_containers', False))
        if no_containers:
            properties['is_metal'] = True

        container_affinity = affinity.get(container_group, 1)
        # Ensures that container names are not longer than 63
        # This section will ensure that we are not it by the following bug:
        # https://bugzilla.mindrot.org/show_bug.cgi?id=2239
        type_and_name = '{}-{}'.format(host_type, container_name)
        logger.debug("Generated container name %s", type_and_name)
        max_hostname_len = 52
        is_metal = properties.get('is_metal', False)
        if len(type_and_name) > max_hostname_len and not is_metal:
            raise SystemExit(
                'The resulting combination of [ "{}" + "{}" ] is longer than'
                ' {} characters. This combination will result in a container'
                ' name that is longer than the maximum allowable hostname of'
                ' 63 characters. Before this process can continue please'
                ' adjust the host entries in your "openstack_user_config.yml"'
                ' to use a short hostname. The recommended hostname length is'
                ' < 20 characters long.'.format(
                    host_type, container_name, max_hostname_len
                )
            )
        elif len(host_type) > 63 and is_metal:
            raise SystemExit(
                'The resulting hostname "{0}" is longer than 63 characters.'
                ' This combination may result in a name that is longer than'
                ' the maximum allowable hostname of 63 characters. Before'
                ' this process can continue please adjust the host entries'
                ' in your "openstack_user_config.yml" to use a short hostname'
                '.'.format(host_type)
            )

        physical_host = inventory['_meta']['hostvars'][host_type]
        container_host_type = '{}-host_containers'.format(host_type)
        if 'container_types' not in physical_host:
            physical_host['container_types'] = container_host_type
        elif physical_host['container_types'] != container_host_type:
            physical_host['container_types'] = container_host_type

        # Add all of the containers into the inventory
        logger.debug("Building containers for host %s", container_group)
        _build_container_hosts(
            container_affinity,
            container_hosts,
            type_and_name,
            inventory,
            host_type,
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
    for key, value in config.items():
        if key.endswith('hosts'):
            if key not in inventory:
                logger.debug("Key %s was added to inventory", key)
                inventory[key] = {'hosts': []}

            if value is None:
                logger.debug("Key %s had no value", key)
                return

            for _key, _value in value.items():
                if _key not in hvs:
                    hvs[_key] = {}

                hvs[_key].update({
                    'ansible_host': _value['ip'],
                    'management_address': _value.get(
                        'management_ip', _value['ip']),
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

                ip.USED_IPS.add(_value['ip'])
                appended = du.append_if(array=inventory[key]['hosts'],
                                        item=_key)
                if appended:
                    logger.debug("Added host %s to group %s",
                                 _key, key)


def skel_setup(environment, inventory):
    """Build out the main inventory skeleton as needed.

    :param environment: ``dict`` Known environment information
    :param inventory: ``dict``  Living dictionary of inventory
    """
    for key, value in environment.items():
        if key == 'version':
            continue
        for _key, _value in value.items():
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
    for key, value in skeleton.items():
        _parse_belongs_to(
            key,
            belongs_to=value['belongs_to'],
            inventory=inventory
        )


def network_entry(is_metal, interface,
                  bridge=None, bridge_type=None, net_type=None, net_mtu=None):
    """Return a network entry for a container."""

    # TODO(cloudnull) After a few releases this conditional should be
    # simplified. The container address checking that is ssh address
    # is only being done to support old inventory.

    _network = dict()

    if not is_metal:
        _network['interface'] = interface

    if bridge:
        _network['bridge'] = bridge

    if bridge_type:
        _network['bridge_type'] = bridge_type

    if net_type:
        _network['type'] = net_type

    if net_mtu:
        _network['mtu'] = net_mtu

    return _network


def _add_additional_networks(key, inventory, ip_q, q_name, netmask, interface,
                             bridge, bridge_type, net_type, net_mtu,
                             user_config, is_management_address, static_routes,
                             gateway, reference_group, address_prefix):
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
    :param is_management_address: ``bool`` set address as management_address.
    :param static_routes: ``list`` List containing static route dicts.
    :param gateway: ``str`` gateway address to use in container
    :param reference_group: ``str`` group to filter membership of host against.
    :param address_prefix: ``str`` override prefix of key for network address.
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
                bridge_type,
                net_type,
                net_mtu,
                user_config,
                is_management_address,
                static_routes,
                gateway,
                reference_group,
                address_prefix
            )

    # Make sure the lookup object has a value.
    if lookup:
        hosts = lookup.get('hosts')
        if not hosts:
            return
    else:
        return

    if address_prefix:
        old_address = '%s_address' % address_prefix
    # TODO(cloudnull) after a few releases this should be removed.
    elif q_name:
        old_address = '{}_address'.format(q_name)
    else:
        old_address = '{}_address'.format(interface)

    for container_host in hosts:
        container = base_hosts[container_host]

        physical_host = container.get('physical_host')
        if (reference_group and physical_host
                not in inventory.get(reference_group).get('hosts')):
            continue

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

        _network = network_entry(
            is_metal,
            interface,
            bridge,
            bridge_type,
            net_type,
            net_mtu
        )

        # update values from _network in case they have changed
        if old_address in networks:
            for key in _network.keys():
                networks[old_address][key] = _network[key]

        # This should convert found addresses based on q_name + "_address"
        #  and then build the network if its not found.
        if not is_metal and old_address not in networks:
            network = networks[old_address] = _network
            if old_address in container and container[old_address]:
                network['address'] = container.pop(old_address)
            elif not is_metal:
                address = ip.get_ip_address(name=q_name, ip_q=ip_q)
                if address:
                    network['address'] = address

            ansible_host_address = networks[old_address]['address']
            network['netmask'] = netmask

        elif is_metal:
            network = networks[old_address] = _network
            network['netmask'] = netmask
            if is_management_address:
                # Container physical host group
                cphg = container.get('physical_host_group')

                # user_config data from the container physical host group
                if user_config[cphg].get(container_host) is not None:
                    phg = user_config[cphg][container_host]
                else:
                    phg = user_config[cphg][physical_host]
                ansible_host_address = phg['ip']
                network['address'] = phg.get(
                    'management_ip', ansible_host_address)
        else:
            ansible_host_address = networks[old_address]['address']

        if is_management_address is True:
            container['ansible_host'] = ansible_host_address

        if is_management_address is True:
            container['management_address'] = networks[old_address]['address']

        if gateway:
            # if specified, gateway address will be used for default route in
            # container and routes offered by DHCP will be ignored
            container['gateway'] = gateway
            networks[old_address]['gateway'] = gateway

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

    for key, value in container_skel.items():
        contains_in = value.get('contains', list())
        belongs_to_in = value.get('belongs_to', list())
        properties = value.get('properties', {})

        if belongs_to_in:
            _parse_belongs_to(
                key,
                belongs_to=value['belongs_to'],
                inventory=inventory
            )
        if properties.get('is_nest', False):
            physical_host_type = re.sub(
                r"(?P<group>.*)_(?P<type>.*)$",
                r'\g<group>_hosts',
                key
            )
            for host_type in inventory[physical_host_type]['hosts']:
                container_mapping = inventory[key]['children']
                host_type_containers = '{}-host_containers'.format(host_type)
                if host_type_containers in inventory:
                    du.append_if(array=container_mapping,
                                 item=host_type_containers)

        for assignment in contains_in:
            for container_type in belongs_to_in:
                _add_container_hosts(
                    assignment,
                    config,
                    key,
                    container_type,
                    inventory,
                    properties
                )

    cidr_networks = config.get('cidr_networks')
    provider_queues = {}
    for net_name in cidr_networks:
        ip_q = ip.load_optional_q(
            cidr_networks, cidr_name=net_name
        )
        provider_queues[net_name] = ip_q
        if ip_q is not None:
            net = netaddr.IPNetwork(cidr_networks.get(net_name))
            q_netmask = '{}_netmask'.format(net_name)
            provider_queues[q_netmask] = str(net.netmask)

    overrides = config.get('global_overrides', dict())
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
            netmask = provider_queues['{}_netmask'.format(q_name)]
        else:
            netmask = None

        for group in p_net.get('group_binds', list()):
            _add_additional_networks(
                key=group,
                inventory=inventory,
                ip_q=ip_from_q,
                q_name=q_name,
                netmask=netmask,
                interface=p_net.get('container_interface'),
                bridge=p_net.get('container_bridge'),
                bridge_type=p_net.get('container_bridge_type'),
                net_type=p_net.get('container_type'),
                net_mtu=p_net.get('container_mtu'),
                user_config=config,
                is_management_address=p_net.get(
                    'is_management_address', p_net.get('is_container_address')
                ),
                static_routes=p_net.get('static_routes'),
                gateway=p_net.get('gateway'),
                reference_group=p_net.get('reference_group'),
                address_prefix=p_net.get('address_prefix')
            )

    populate_lxc_hosts(inventory)


def populate_lxc_hosts(inventory):
    """Insert nodes hosting LXC containers into the lxc_hosts group

    The inventory dictionary passed in to this function will be mutated.

    :param inventory: The dictionary containing the Ansible inventory
    """
    lxc_host_nodes = _find_lxc_hosts(inventory)
    inventory['lxc_hosts'] = {'hosts': lxc_host_nodes}
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
    lxc_host_nodes = []
    for host, hostvars in inventory['_meta']['hostvars'].items():
        physical_host = hostvars.get('physical_host', None)
        container_tech = hostvars.get('container_tech', 'lxc')
        hostvars['container_tech'] = container_tech

        # We want this node's "parent", so append the physical host
        if not host == physical_host:
            if container_tech == 'lxc':
                appended = du.append_if(
                    array=lxc_host_nodes,
                    item=physical_host
                )
            else:
                appended = None

            if appended:
                logger.debug("%s added to lxc_hosts group",
                             physical_host)

    return lxc_host_nodes


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
                if 'properties' in type_vars and 'properties' not in container:
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

            # NOTE (palendae): wrapped in a list to support python3,
            # which uses `dict_keys` objects that can't be appended
            kept_vars = list(user_defined_config['global_overrides'].keys())
            kept_vars.append('container_cidr')

            # Remove global overrides that were deleted from inventory, too
            # We use the to_delete list due to Python 3 disallowing dict
            # size mutation during iteration
            to_delete = []
            for key in inventory['all']['vars'].keys():
                if key not in kept_vars:
                    to_delete.append(key)

            for key in to_delete:
                logger.debug("Deleting key %s from inventory", key)
                del inventory['all']['vars'][key]


def _check_same_ip_to_multiple_host(config):
    """Check for IPs assigned to multiple hosts

    : param: config:  ``dict`` User provided configuration
    """

    ips_to_hostnames_mapping = dict()
    for key, value in config.items():
        if key.endswith('hosts'):
            for _key, _value in value.items():
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


def _check_group_branches(config, physical_skel):
    """Ensure that groups have either hosts or child groups, not both

    The inventory skeleton population assumes that groups will either have
    hosts as "leaves", or other groups as children, not both. This function
    ensures this invariant is met by comparing the configuration to the
    physical skeleton definition.

    :param config: ``dict`` The contents of the user configuration file. Keys
        present in this dict are assumed to be groups containing host entries.
    :param config: ``dict`` The physical skeleton tree, defining parent/child
        relationships between groups. Values in the 'belong_to' key are
        assumed to be parents of other groups.
    :raises GroupConflict:
    """
    logging.debug("Checking group branches match expectations")
    for group, relations in physical_skel.items():
        if 'belongs_to' not in relations:
            continue
        parents = relations['belongs_to']
        for parent in parents:
            if parent in config.keys():
                message = (
                    "Group {parent} has a child group {child}, "
                    "but also has host entries in user configuration. "
                    "Hosts cannot be sibling with groups."
                ).format(parent=parent, child=group)
                raise GroupConflict(message)
    logging.debug("Group branches ok.")
    return True


def _check_config_settings(cidr_networks, config, container_skel):
    """check preciseness of config settings

    :param cidr_networks: ``dict`` cidr_networks from config
    :param config: ``dict``  User defined information
    :param container_skel: ``dict`` container skeleton for all known containers
    """

    # search for any container that doesn't have is_metal flag set to true
    is_provider_networks_needed = False
    if 'global_overrides' in config:
        no_containers = config['global_overrides'].get('no_containers', False)
    else:
        no_containers = False
    if not no_containers:
        for key, value in container_skel.items():
            properties = value.get('properties', {})
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
                if (p_net.get('container_bridge') == overrides.get(
                        'management_bridge')):
                    if not p_net.get(
                            'is_management_address',
                            p_net.get('is_container_address')):
                        raise ProviderNetworkMisconfiguration(q_name)

    logger.debug("Provider network information OK")

    # look for same ip address assigned to different hosts
    _check_same_ip_to_multiple_host(config)

    _check_multiple_ips_to_host(config)

    _check_lxc_hosts(config)


def _check_all_conf_groups_present(config, environment):
    """Verifies that all groups defined in the config are in the environment

    If a group is in config but not the environment, a warning will be raised.
    Multiple warnings can be raised, and the return value will be set to False.

    If all groups found are in the environment, the function returns True

    :param config: ``dict`` user's provided configuration
    :param environment: ``dict`` group membership mapping
    :rtype: bool, True if all groups are in environment, False otherwise
    """
    excludes = ('global_overrides', 'cidr_networks', 'used_ips')
    config_groups = [k for k in config.keys() if k not in excludes]
    env_groups = environment['physical_skel'].keys()

    retval = True

    for group in config_groups:
        if group not in env_groups:
            msg = ("Group {} was found in configuration but "
                   "not the environment.".format(group))
            warnings.warn(msg)

            retval = False
    return retval


def _prepare_debug_logger():
    log_fmt = "%(lineno)d - %(funcName)s: %(message)s"
    logging.basicConfig(format=log_fmt, filename='inventory.log')
    logger.setLevel(logging.DEBUG)
    logger.info("Beginning new inventory run")


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
        _prepare_debug_logger()

    try:
        user_defined_config = filesys.load_user_configuration(config)
    except filesys.MissingDataSource as ex:
        raise SystemExit(ex)

    base_env_dir = environment
    base_env = filesys.load_environment(base_env_dir, {})
    environment = filesys.load_environment(config, base_env)

    # Load existing inventory file if found
    inventory, inv_path = filesys.load_inventory(config, INVENTORY_SKEL)

    # Make a deep copy for change comparison
    orig_inventory = copy.deepcopy(inventory)

    # Save the users container cidr as a group variable
    cidr_networks = user_defined_config.get('cidr_networks')
    if not cidr_networks:
        raise SystemExit('No container CIDR specified in user config')

    user_cidr = None
    if 'container' in cidr_networks:
        user_cidr = cidr_networks['container']
    elif 'management' in cidr_networks:
        user_cidr = cidr_networks['management']
    else:
        overrides = user_defined_config.get('global_overrides')
        pns = overrides.get('provider_networks', list())
        for pn in pns:
            p_net = pn.get('network')
            if not p_net:
                continue
            q_name = p_net.get('ip_from_q')
            if q_name and q_name in cidr_networks:
                addr_prefix = p_net.get('address_prefix')
                is_mgmt = p_net.get(
                    'is_management_address', p_net.get('is_container_address')
                )
                if (addr_prefix in ('container', 'management') or is_mgmt):
                    if user_cidr is None:
                        user_cidr = []
                    user_cidr.append(cidr_networks[q_name])

    if user_cidr is None:
        raise SystemExit('No container or management network '
                         'specified in user config.')

    # make sure user_defined config is self contained
    _check_config_settings(
        cidr_networks,
        user_defined_config,
        environment.get('container_skel')
    )

    # Add the container_cidr into the all global ansible group_vars
    _parse_global_variables(user_cidr, inventory, user_defined_config)

    # Load all of the IP addresses that we know are used and set the queue
    ip.set_used_ips(user_defined_config, inventory)
    user_defined_setup(user_defined_config, inventory)
    skel_setup(environment, inventory)

    _check_group_branches(
        user_defined_config,
        environment.get('physical_skel')
    )
    logger.debug("Loading physical skel.")
    skel_load(
        environment.get('physical_skel'),
        inventory
    )
    logger.debug("Loading component skel")
    skel_load(
        environment.get('component_skel'),
        inventory
    )
    container_skel_load(
        environment.get('container_skel'),
        inventory,
        user_defined_config
    )

    # Look at inventory and ensure all entries have all required values.
    _ensure_inventory_uptodate(
        inventory=inventory,
        container_skel=environment.get('container_skel'),
    )

    # Load the inventory json
    inventory_json = json.dumps(
        inventory,
        indent=4,
        separators=(',', ': '),
        sort_keys=True
    )

    if check:
        if _check_all_conf_groups_present(user_defined_config, environment):
            return 'Configuration ok!'

    if logger.isEnabledFor(logging.DEBUG):
        num_hosts = len(inventory['_meta']['hostvars'])
        logger.debug("%d hosts found.", num_hosts)

    # Save new dynamic inventory only if modified
    if orig_inventory != inventory:
        logger.debug("Saving modified inventory")
        filesys.save_inventory(inventory_json, inv_path)

    return inventory_json
