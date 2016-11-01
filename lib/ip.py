import netaddr
import Queue
import random
import logging

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
