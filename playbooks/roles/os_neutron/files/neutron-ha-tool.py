#! /usr/bin/env python

# Copyright 2013 AT&T Services, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import logging
import os
import sys
import argparse
import random
import time
from logging.handlers import SysLogHandler
from collections import OrderedDict
from neutronclient.neutron import client


LOG = logging.getLogger('neutron-ha-tool')
LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
LOG_DATE = '%m-%d %H:%M'
DESCRIPTION = "neutron High Availability Tool"
TAKEOVER_DELAY = int(random.random()*30+30)


def parse_args():

    # ensure environment has necessary items to authenticate
    for key in ['OS_TENANT_NAME', 'OS_USERNAME', 'OS_PASSWORD',
                'OS_AUTH_URL']:
        if key not in os.environ.keys():
            LOG.exception("Your environment is missing '%s'")

    ap = argparse.ArgumentParser(description=DESCRIPTION)
    ap.add_argument('-d', '--debug', action='store_true',
                    default=False, help='Show debugging output')
    ap.add_argument('-q', '--quiet', action='store_true', default=False,
                    help='Only show error and warning messages')
    ap.add_argument('-n', '--noop', action='store_true', default=False,
                    help='Do not do any modifying operations (dry-run)')
    ap.add_argument('--l3-agent-check', action='store_true', default=False,
                    help='Show routers associated with offline l3 agents')
    ap.add_argument('--l3-agent-migrate', action='store_true', default=False,
                    help='Migrate routers away from offline l3 agents')
    ap.add_argument('--l3-agent-rebalance', action='store_true', default=False,
                    help='Rebalance router count on all l3 agents')
    ap.add_argument('--replicate-dhcp', action='store_true', default=False,
                    help='Replicate DHCP configuration to all agents')
    ap.add_argument('--now', action='store_true', default=False,
                    help='Migrate Routers immediately without a delay.')
    ap.add_argument('--insecure', action='store_true', default=False,
                    help='Explicitly allow neutron-ha-tool to perform '
                         '"insecure" SSL (https) requests. The server\'s '
                         'certificate will not be verified against any '
                         'certificate authorities. This option should be used '
                         'with caution.')
    return ap.parse_args()


def setup_logging(args):
    level = logging.INFO
    if args.quiet:
        level = logging.WARN
    if args.debug:
        level = logging.DEBUG
    logging.basicConfig(level=level, format=LOG_FORMAT, date_fmt=LOG_DATE)
    handler = SysLogHandler(address='/dev/log')
    syslog_formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
    handler.setFormatter(syslog_formatter)
    LOG.addHandler(handler)


def run(args):
    try:
        ca = os.environ['OS_CACERT']
    except KeyError:
        ca = None

    # instantiate client
    qclient = client.Client('2.0', auth_url=os.environ['OS_AUTH_URL'],
                            username=os.environ['OS_USERNAME'],
                            tenant_name=os.environ['OS_TENANT_NAME'],
                            password=os.environ['OS_PASSWORD'],
                            endpoint_type='internalURL',
                            insecure=args.insecure,
                            ca_cert=ca)

    # set json return type
    qclient.format = 'json'

    if args.l3_agent_check:
        LOG.info("Performing L3 Agent Health Check")
        l3_agent_check(qclient)

    if args.l3_agent_migrate:
        LOG.info("Performing L3 Agent Migration for Offline L3 Agents")
        l3_agent_migrate(qclient, args.noop, args.now)

    if args.l3_agent_rebalance:
        LOG.info("Rebalancing L3 Agent Router Count")
        l3_agent_rebalance(qclient, args.noop)

    if args.replicate_dhcp:
        LOG.info("Performing DHCP Replication of Networks to Agents")
        replicate_dhcp(qclient, args.noop)


def l3_agent_rebalance(qclient, noop=False):
    """
    Rebalance l3 agent router count across agents.  The number of routers
    on each l3 agent will be as close as possible which should help
    distribute load as new l3 agents come online.

    :param qclient: A neutronclient
    :param noop: Optional noop flag
    """

    # {u'binary': u'neutron-l3-agent',
    #  u'description': None,
    #  u'admin_state_up': True,
    #  u'heartbeat_timestamp': u'2013-07-02 22:20:23',
    #  u'alive': True,
    #  u'topic': u'l3_agent',
    #  u'host': u'o3r3.int.san3.attcompute.com',
    #  u'agent_type': u'L3 agent',
    #  u'created_at': u'2013-07-02 14:50:58',
    #  u'started_at': u'2013-07-02 18:00:55',
    #  u'id': u'6efe494a-616c-41ea-9c8f-2c592f4d46ff',
    #  u'configurations': {
    #      u'router_id': u'',
    #      u'gateway_external_network_id': u'',
    #      u'handle_internal_only_routers': True,
    #      u'use_namespaces': True,
    #      u'routers': 5,
    #      u'interfaces': 3,
    #      u'floating_ips': 9,
    #      u'interface_driver':
    #           u'neutron.agent.linux.interface.OVSInterfaceDriver',
    #      u'ex_gw_ports': 3}
    #  }

    l3_agent_dict = {}
    agents = list_agents(qclient, agent_type='L3 agent')
    num_agents = len(agents)
    if num_agents <= 1:
        LOG.info("No rebalancing required for 1 or fewer agents")
        return

    for l3_agent in agents:
        l3_agent_dict[l3_agent['id']] = \
            list_routers_on_l3_agent(qclient, l3_agent['id'])

    ordered_l3_agent_dict = OrderedDict(sorted(l3_agent_dict.items(),
                                               key=lambda t: len(t[0])))
    ordered_l3_agent_list = list(ordered_l3_agent_dict)
    num_agents = len(ordered_l3_agent_list)
    LOG.info("Agent list: %s", ordered_l3_agent_list[0:(num_agents-1/2)+1])
    i = 0
    for agent in ordered_l3_agent_list[0:num_agents-1/2]:
        low_agent_id = ordered_l3_agent_list[i]
        hgh_agent_id = ordered_l3_agent_list[-(i+1)]

        # do nothing if we end up comparing the same router
        if low_agent_id == hgh_agent_id:
            continue

        LOG.info("Examining low_agent=%s, high_agent=%s",
                 low_agent_id, hgh_agent_id)

        low_agent_router_count = len(l3_agent_dict[low_agent_id])
        hgh_agent_router_count = len(l3_agent_dict[hgh_agent_id])

        LOG.info("Low Count=%s, High Count=%s",
                 low_agent_router_count, hgh_agent_router_count)

        for router_id in l3_agent_dict[hgh_agent_id]:
            if low_agent_router_count >= hgh_agent_router_count:
                break
            else:
                LOG.info("Migrating router=%s from agent=%s to agent=%s",
                         router_id, hgh_agent_id, low_agent_id)
                try:
                    if not noop:
                        migrate_router(qclient, router_id, hgh_agent_id,
                                       low_agent_id)
                    low_agent_router_count += 1
                    hgh_agent_router_count -= 1
                except:
                    LOG.exception("Failed to migrate router=%s from agent=%s "
                                  "to agent=%s", router_id, hgh_agent_id,
                                  low_agent_id)
                    continue
        i += 1


def l3_agent_check(qclient):
    """
    Walk the l3 agents searching for agents that are offline.  Show routers
    that are offline and where we would migrate them to.

    :param qclient: A neutronclient

    """

    migration_count = 0
    agent_list = list_agents(qclient)
    agent_dead_list = agent_dead_id_list(agent_list, 'L3 agent')
    agent_alive_list = agent_alive_id_list(agent_list, 'L3 agent')
    LOG.info("There are %s offline L3 agents and %s online L3 agents",
             len(agent_dead_list), len(agent_alive_list))

    if len(agent_dead_list) > 0:
        for agent_id in agent_dead_list:
            LOG.info("Querying agent_id=%s for routers to migrate", agent_id)
            router_id_list = list_routers_on_l3_agent(qclient, agent_id)

            for router_id in router_id_list:
                try:
                    target_id = random.choice(agent_alive_list)
                except IndexError:
                    LOG.warn("There are no l3 agents alive we could "
                             "migrate routers onto.")
                    target_id = None

                migration_count += 1
                LOG.warn("Would like to migrate router=%s to agent=%s",
                         router_id, target_id)

        if migration_count > 0:
            sys.exit(2)


def l3_agent_migrate(qclient, noop=False, now=False):
    """
    Walk the l3 agents searching for agents that are offline.  For those that
    are offline, we will retrieve a list of routers on them and migrate them to
    a random l3 agent that is online.

    :param qclient: A neutronclient
    :param noop: Optional noop flag
    :param now: Optional. If false (the default), we'll wait for a random
                amount of time (between 30 and 60 seconds) before migration. If
                true, routers are migrated immediately.

    """

    migration_count = 0
    agent_list = list_agents(qclient)
    agent_dead_list = agent_dead_id_list(agent_list, 'L3 agent')
    agent_alive_list = agent_alive_id_list(agent_list, 'L3 agent')
    LOG.info("There are %s offline L3 agents and %s online L3 agents",
             len(agent_dead_list), len(agent_alive_list))

    if len(agent_dead_list) > 0:
        if len(agent_alive_list) < 1:
            LOG.exception("There are no l3 agents alive to migrate "
                          "routers onto")

        timeout = 0
        if not now:
            while timeout < TAKEOVER_DELAY:

                agent_list_new = list_agents(qclient)
                agent_dead_list_new = agent_dead_id_list(agent_list_new,
                                                         'L3 agent')
                if len(agent_dead_list_new) < len(agent_dead_list):
                    LOG.info("Skipping router failover since an agent came "
                             "online while ensuring agents offline for %s "
                             "seconds", TAKEOVER_DELAY)
                    sys.exit(0)

                LOG.info("Agent found offline for seconds=%s but waiting "
                         "seconds=%s before migration",
                         timeout, TAKEOVER_DELAY)
                timeout += 1
                time.sleep(1)

        for agent_id in agent_dead_list:
            LOG.info("Querying agent_id=%s for routers to migrate", agent_id)
            router_id_list = list_routers_on_l3_agent(qclient, agent_id)

            for router_id in router_id_list:

                target_id = random.choice(agent_alive_list)
                LOG.info("Migrating router=%s to agent=%s",
                         router_id, target_id)

                try:
                    if not noop:
                        migrate_router(qclient, router_id, agent_id, target_id)
                        migration_count += 1
                except:
                    LOG.exception("There was an error migrating a router")
                    continue

        LOG.info("%s routers required migration from offline L3 agents",
                 migration_count)


def replicate_dhcp(qclient, noop=False):
    """
    Retrieve a network list and then probe each DHCP agent to ensure
    they have that network assigned.

    :param qclient: A neutronclient
    :param noop: Optional noop flag

    """

    added = 0
    networks = list_networks(qclient)
    network_id_list = [n['id'] for n in networks]
    agents = list_agents(qclient, agent_type='DHCP agent')
    LOG.info("Replicating %s networks to %s DHCP agents", len(networks),
             len(agents))
    for dhcp_agent_id in [a['id'] for a in agents]:
        networks_on_agent = \
            qclient.list_networks_on_dhcp_agent(dhcp_agent_id)['networks']
        network_id_on_agent = [n['id'] for n in networks_on_agent]
        for network_id in network_id_list:
            if network_id not in network_id_on_agent:
                try:
                    dhcp_body = {'network_id': network_id}
                    if not noop:
                        qclient.add_network_to_dhcp_agent(dhcp_agent_id,
                                                          dhcp_body)
                    LOG.info("Added missing network=%s to dhcp agent=%s",
                             network_id, dhcp_agent_id)
                    added += 1
                except:
                    LOG.exception("Failed to add network_id=%s to"
                                  "dhcp_agent=%s", network_id, dhcp_agent_id)
                    continue

    LOG.info("Added %s networks to DHCP agents", added)


def migrate_router(qclient, router_id, agent_id, target_id):
    """
    Returns nothing, and raises on exception

    :param qclient: A neutronclient
    :param router_id: The id of the router to migrate
    :param agent_id: The id of the l3 agent to migrate from
    :param target_id: The id of the l3 agent to migrate to
    """

    # N.B. The neutron API will return "success" even when there is a
    # subsequent failure during the add or remove process so we must check to
    # ensure the router has been added or removed

    # remove the router from the dead agent
    qclient.remove_router_from_l3_agent(agent_id, router_id)

    # ensure it is removed or log an error
    if router_id in list_routers_on_l3_agent(qclient, agent_id):
        LOG.exception("Failed to remove router_id=%s from agent_id=%s",
                      router_id, agent_id)

    # add the router id to a live agent
    router_body = {'router_id': router_id}
    qclient.add_router_to_l3_agent(target_id, router_body)

    # ensure it is removed or log an error
    if router_id not in list_routers_on_l3_agent(qclient, target_id):
        LOG.exception("Failed to add router_id=%s from agent_id=%s",
                      router_id, agent_id)


def list_networks(qclient):
    """
    Return a list of network objects

    :param qclient: A neutronclient
    """

    resp = qclient.list_networks()
    LOG.debug("list_networks: %s", resp)
    return resp['networks']


def list_dhcp_agent_networks(qclient, agent_id):
    """
    Return a list of network ids assigned to a particular DHCP agent

    :param qclient: A neutronclient
    :param agent_id: A DHCP agent id
    """

    resp = qclient.list_networks_on_dhcp_agent(agent_id)
    LOG.debug("list_networks_on_dhcp_agent: %s", resp)
    return [s['id'] for s in resp['networks']]


def list_routers(qclient):
    """
    Return a list of router objects

    :param qclient: A neutronclient

    # {'routers': [
    #    {u'status': u'ACTIVE',
    #     u'external_gateway_info':
    #        {u'network_id': u'b970297c-d80e-4527-86d7-e49d2da9fdef'},
    #     u'name': u'router1',
    #     u'admin_state_up': True,
    #     u'tenant_id': u'5603b97ee7f047ea999e25492c7fcb23',
    #     u'routes': [],
    #     u'id': u'0a122e5c-1623-412e-8c53-a1e21d1daff8'}
    # ]}

    """

    resp = qclient.list_routers()
    LOG.debug("list_routers: %s", resp)
    return resp['routers']


def list_routers_on_l3_agent(qclient, agent_id):
    """
    Return a list of router ids on an agent

    :param qclient: A neutronclient
    """

    resp = qclient.list_routers_on_l3_agent(agent_id)
    LOG.debug("list_routers_on_l3_agent: %s", resp)
    return [r['id'] for r in resp['routers']]


def list_agents(qclient, agent_type=None):
    """Return a list of agent objects

    :param qclient: A neutronclient


    # {u'agents': [

    #   {u'binary': u'neutron-openvswitch-agent',
    #    u'description': None,
    #    u'admin_state_up': True,
    #    u'heartbeat_timestamp': u'2013-07-02 22:20:25',
    #    u'alive': True,
    #    u'topic': u'N/A',
    #    u'host': u'o3r3.int.san3.attcompute.com',
    #    u'agent_type': u'Open vSwitch agent',
    #    u'created_at': u'2013-07-02 14:50:57',
    #    u'started_at': u'2013-07-02 14:50:57',
    #    u'id': u'3a577f1d-d86e-4f1a-a395-8d4c8e4df1e2',
    #    u'configurations': {u'devices': 10}},

    #   {u'binary': u'neutron-dhcp-agent',
    #    u'description': None,
    #    u'admin_state_up': True,
    #    u'heartbeat_timestamp': u'2013-07-02 22:20:23',
    #    u'alive': True,
    #    u'topic': u'dhcp_agent',
    #    u'host': u'o5r4.int.san3.attcompute.com',
    #    u'agent_type': u'DHCP agent',
    #    u'created_at': u'2013-06-26 16:21:02',
    #    u'started_at': u'2013-06-28 13:32:52',
    #    u'id': u'3e8be28e-05a0-472b-9288-a59f8d8d2271',
    #    u'configurations': {
    #         u'subnets': 4,
    #         u'use_namespaces': True,
    #         u'dhcp_driver': u'neutron.agent.linux.dhcp.Dnsmasq',
    #         u'networks': 4,
    #         u'dhcp_lease_time': 120,
    #         u'ports': 38}},


    #   {u'binary': u'neutron-l3-agent',
    #    u'description': None,
    #    u'admin_state_up': True,
    #    u'heartbeat_timestamp': u'2013-07-02 22:20:23',
    #    u'alive': True,
    #    u'topic': u'l3_agent',
    #    u'host': u'o3r3.int.san3.attcompute.com',
    #    u'agent_type': u'L3 agent',
    #    u'created_at': u'2013-07-02 14:50:58',
    #    u'started_at': u'2013-07-02 18:00:55',
    #    u'id': u'6efe494a-616c-41ea-9c8f-2c592f4d46ff',
    #    u'configurations': {
    #         u'router_id': u'',
    #         u'gateway_external_network_id': u'',
    #         u'handle_internal_only_routers': True,
    #         u'use_namespaces': True,
    #         u'routers': 5,
    #         u'interfaces': 3,
    #         u'floating_ips': 9,
    #         u'interface_driver':
    #             u'neutron.agent.linux.interface.OVSInterfaceDriver',
    #         u'ex_gw_ports': 3}},

    """

    resp = qclient.list_agents()
    LOG.debug("list_agents: %s", resp)
    if agent_type:
        return [agent for agent in resp['agents']
                if agent['agent_type'] == agent_type]
    return resp['agents']


def agent_alive_id_list(agent_list, agent_type):
    """
    Return a list of agents that are alive from an API list of agents

    :param agent_list: API response for list_agents()

    """
    return [agent['id'] for agent in agent_list
            if agent['agent_type'] == agent_type and agent['alive'] is True]


def agent_dead_id_list(agent_list, agent_type):
    """
    Return a list of agents that are dead from an API list of agents

    :param agent_list: API response for list_agents()

    """
    return [agent['id'] for agent in agent_list
            if agent['agent_type'] == agent_type and agent['alive'] is False]


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args)

    try:
        run(args)
        sys.exit(0)
    except Exception as err:
        LOG.error(err)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
