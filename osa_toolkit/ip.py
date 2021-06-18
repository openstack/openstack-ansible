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
#
# (c) 2014, Kevin Carter <kevin.carter@rackspace.com>
# (c) 2016, Nolan Brubaker <nolan.brubaker@rackspace.com>

import copy
import logging
import netaddr
try:
    import Queue
except ImportError:
    import queue as Queue
import random

logger = logging.getLogger('osa-inventory')


USED_IPS = set()


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


def load_ip_q(cidr, ip_q):
    """Load the IP queue with all IP addresses from a given cidr.

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


def load_optional_q(config, cidr_name):
    """Load optional queue with ip addresses.

    :param config: ``dict``  User defined information
    :param cidr_name: ``str``  Name of the cidr name
    """
    cidr = config.get(cidr_name)
    ip_q = None
    if cidr is not None:
        ip_q = Queue.Queue()
        load_ip_q(cidr=cidr, ip_q=ip_q)
    return ip_q


def set_used_ips(user_defined_config, inventory):
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


class NoSuchQueue(Exception):
    pass


class EmptyQueue(Exception):
    pass


class IPBasePlugin(object):
    def load(self, queue_name, cidr):
        """Create and populate a queue with IP addresses

        The network address and broadcast addresses should be excluded from
        the IP addresses loaded into the queue.

        Queue names should associate with their given CIDR. The queue values
        should be a list of all available IP addresses based on CIDR range
        and IP addresses already assigned.

        """
        raise NotImplementedError

    def get(self, queue_name):
        """Reserve an IP address from a given queue.

        Should raise NoSuchQueue when the given queue name is not found,
        and EmptyQueue if the queue is empty.

        Some plugin implementations may be transactional, and require a call to
        ``save`` after reserving an IP.
        """
        raise NotImplementedError

    def release(self, ip):
        """Release an IP back into queues as assignable.

        Some plugin implementations may be transactional, and require a call to
        ``save`` after releasing an IP.
        """
        raise NotImplementedError

    def save(self):
        """Write actions to data store

        This method is optional to implement, and is presented as a hook for
        use with transactional data stores.
        """
        raise NotImplementedError


class IPManager(IPBasePlugin):
    """Class to manage CIDRs and IPs from openstack-ansible inventory config

    CIDRs are managed via queues, which will be named for convenience. All IP
    addresses assigned are saved into the :method:`IPManager.used` set and
    removed from their respective queue.

    IP addresses that are no longer in use may be freed back into the queues
    with the :method:`IPManager.release` method.

    """
    def __init__(self, queues=None, used_ips=None):
        """Create a manager with various queues and a used IP excludelist

        :param queues: ``dict`` A dictionary containing queue names for keys
            and CIDR specifications for values.
        :param used_ips: ``set`` A set of IP addresses which are marked as used
            and unassignable. Any iterable will be coerced into a set to remove
            duplicate entries.
        """

        if queues is None:
            queues = {}

        if used_ips is None:
            used_ips = set()

        # If we receive a set already, this is essentially a no-op,
        # not a wrapper.
        self._used_ips = set(used_ips)
        self._queues = queues

        # The networks will be netaddr.IPNetwork objects for a given CIDR,
        # kept so that if an IP is released from use, it is returned to the
        # associated queue.
        self._networks = {}

        # Populate any queues that were passed in already.
        for name, cidr in queues.items():
            self.load(name, cidr)

    @property
    def used(self):
        """Set of IPs used within the environment

        IP addresses within this set will be masked when requesting a new IP,
        and thus not be returned to callers.

        Set returned is a copy of the internal data structure.

        :return: Set of IP addresses currently in use
        :rtrype: set
        """
        return set(self._used_ips)

    @used.deleter
    def used(self):
        """Empty the used IP set.

        Any IP used will also be released back in to the associated
        queue.
        """
        used_ips = set(self._used_ips)
        for ip in used_ips:
            self.release(ip)
        self._used_ips = set()

    @property
    def queues(self):
        """Dictionary of named queues, populated with IPs for a given CIDR.

        Return values here are copies, to protect the internal structures
        from unintentional changes.
        """
        return copy.deepcopy(self._queues)

    def __getitem__(self, key):
        """Short hand for accessing a named queue

        The list returned is a copy of the internal queue.
        """
        return list(self._queues[key])

    def load(self, queue_name, cidr):
        """Populates a named queue with all IPs in a CIDR

        Queues are implemented as a list, and will be populated by all IP
        addresses within a CIDR, with the following exceptions:
            * The network and broadcast IP addresses
            * Any IP address already in the used_ips set

        :param queue_name: ``str`` Name to apply to a given CIDR
        :param cidr: ``str`` CIDR notation specifying range of IP addresses
            which are available for assignment.
        """
        net = netaddr.IPNetwork(cidr)

        initial_ips = [str(i) for i in list(net)]

        # We will never want to assign these to machines.

        if net.network:
            self._used_ips.update([str(net.network)])
        if net.broadcast:
            self._used_ips.update([str(net.broadcast)])

        all_ips = [ip for ip in initial_ips if ip not in self._used_ips]

        # randomize so that we're not generating the expectation that
        # groups are clustered by IP
        random.shuffle(all_ips)

        self._queues[queue_name] = all_ips
        self._networks[queue_name] = net

    def get(self, queue_name):
        """Returns an usused IP address from a specified queue.

        IPs returned will be marked as used and removed from the associated
        queue.

        :param queue_name: ``str`` Name of the queue from which to retrieve
            an IP.
        :returns: IP address
        :rtype: str
        :raises: ip.NoSuchQueue, ip.EmptyQueue
        """
        if queue_name not in self._queues.keys():
            raise NoSuchQueue("Queue {0} does not exist".format(queue_name))

        try:
            address = self._queues[queue_name].pop(0)
        except IndexError:
            raise EmptyQueue("Queue {0} is empty".format(queue_name))

        self._used_ips.add(address)

        return address

    def release(self, ip):
        """Free an IP from the used list and re-insert it to its queue.

        Any IP freed will also be re-inserted into the associated queue, which
        is calculated at deletion.

        If an IP matches multiple CIDR ranges available, it will be inserted
        to the first one matched.

        :param ip: ``str`` IP address which to release back into the usable
            pool.
        """
        self._used_ips.discard(ip)

        # Use the IP class for membership comparison to the network
        addr = netaddr.IPAddress(ip)

        # TODO(nrb): Should this be ordered somehow to be more determinate?
        # Alphabetical by queue name seems easiest, but not necessarily
        # accurate or relevant.
        for name, network in self._networks.items():
            if addr in network:
                self._queues[name].append(ip)
