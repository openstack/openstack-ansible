#!/usr/bin/env python

import collections
import json
import os
from os import path
import Queue
import sys
import unittest
import yaml

INV_DIR = 'playbooks/inventory'
SCRIPT_FILENAME = 'dynamic_inventory.py'
INV_SCRIPT = path.join(os.getcwd(), INV_DIR, SCRIPT_FILENAME)

sys.path.append(path.join(os.getcwd(), INV_DIR))

import dynamic_inventory as di

TARGET_DIR = path.join(os.getcwd(), 'tests', 'inventory')
USER_CONFIG_FILE = path.join(TARGET_DIR, "openstack_user_config.yml")

# These files will be placed in TARGET_DIR by INV_SCRIPT.
# They should be cleaned up between each test.
CLEANUP = [
    'openstack_inventory.json',
    'openstack_hostnames_ips.yml',
    'backup_openstack_inventory.tar'
]


def cleanup():
    for f_name in CLEANUP:
        f_file = path.join(TARGET_DIR, f_name)
        if os.path.exists(f_file):
            os.remove(f_file)


def get_inventory():
    "Return the inventory mapping in a dict."
    try:
        inventory_string = di.main({'config': TARGET_DIR})
        inventory = json.loads(inventory_string)
        return inventory
    finally:
        # Remove the file system artifacts since we want to force fresh runs
        cleanup()


class TestAnsibleInventoryFormatConstraints(unittest.TestCase):
    inventory = None

    expected_groups = [
        'aio1_containers',
        'all',
        'all_containers',
        'aodh_alarm_evaluator',
        'aodh_alarm_notifier',
        'aodh_all',
        'aodh_api',
        'aodh_container',
        'aodh_listener',
        'ceilometer_agent_central',
        'ceilometer_agent_compute',
        'ceilometer_agent_notification',
        'ceilometer_all',
        'ceilometer_api',
        'ceilometer_api_container',
        'ceilometer_collector',
        'ceilometer_collector_container',
        'cinder_all',
        'cinder_api',
        'cinder_api_container',
        'cinder_backup',
        'cinder_scheduler',
        'cinder_scheduler_container',
        'cinder_volume',
        'cinder_volumes_container',
        'compute_all',
        'compute_containers',
        'compute_hosts',
        'galera',
        'galera_all',
        'galera_container',
        'glance_all',
        'glance_api',
        'glance_container',
        'glance_registry',
        'haproxy',
        'haproxy_all',
        'haproxy_container',
        'haproxy_containers',
        'haproxy_hosts',
        'heat_all',
        'heat_api',
        'heat_api_cfn',
        'heat_api_cloudwatch',
        'heat_apis_container',
        'heat_engine',
        'heat_engine_container',
        'horizon',
        'horizon_all',
        'horizon_container',
        'hosts',
        'identity_all',
        'identity_containers',
        'identity_hosts',
        'infra_containers',
        'infra_hosts',
        'ironic-server_hosts',
        'ironic_conductor_container',
        'ironic_api_container',
        'ironic_conductor',
        'ironic-infra_containers',
        'ironic-infra_hosts',
        'ironic_servers',
        'ironic-server_containers',
        'ironic_all',
        'ironic_server',
        'ironic_server_container',
        'ironic_api',
        'keystone',
        'keystone_all',
        'keystone_container',
        'log_all',
        'log_containers',
        'log_hosts',
        'memcached',
        'memcached_all',
        'memcached_container',
        'metering-alarm_containers',
        'metering-alarm_hosts',
        'metering-compute_container',
        'metering-compute_containers',
        'metering-compute_hosts',
        'metering-infra_containers',
        'metering-infra_hosts',
        'network_all',
        'network_containers',
        'network_hosts',
        'neutron_agent',
        'neutron_agents_container',
        'neutron_all',
        'neutron_dhcp_agent',
        'neutron_l3_agent',
        'neutron_lbaas_agent',
        'neutron_linuxbridge_agent',
        'neutron_metadata_agent',
        'neutron_metering_agent',
        'neutron_server',
        'neutron_server_container',
        'nova_all',
        'nova_api_metadata',
        'nova_api_metadata_container',
        'nova_api_os_compute',
        'nova_api_os_compute_container',
        'nova_cert',
        'nova_cert_container',
        'nova_compute',
        'nova_compute_container',
        'nova_conductor',
        'nova_conductor_container',
        'nova_console',
        'nova_console_container',
        'nova_scheduler',
        'nova_scheduler_container',
        'os-infra_all',
        'os-infra_containers',
        'os-infra_hosts',
        'pkg_repo',
        'rabbit_mq_container',
        'rabbitmq',
        'rabbitmq_all',
        'remote',
        'remote_containers',
        'repo-infra_all',
        'repo-infra_containers',
        'repo-infra_hosts',
        'repo_all',
        'repo_container',
        'rsyslog',
        'rsyslog_all',
        'rsyslog_container',
        'shared-infra_all',
        'shared-infra_containers',
        'shared-infra_hosts',
        'storage-infra_all',
        'storage-infra_containers',
        'storage-infra_hosts',
        'storage_all',
        'storage_containers',
        'storage_hosts',
        'swift-proxy_containers',
        'swift-proxy_hosts',
        'swift-remote_containers',
        'swift-remote_hosts',
        'swift_acc',
        'swift_acc_container',
        'swift_all',
        'swift_cont',
        'swift_cont_container',
        'swift_containers',
        'swift_hosts',
        'swift_obj',
        'swift_obj_container',
        'swift_proxy',
        'swift_proxy_container',
        'swift_remote',
        'swift_remote_all',
        'swift_remote_container',
        'utility',
        'utility_all',
        'utility_container',
    ]

    @classmethod
    def setUpClass(cls):
        cls.inventory = get_inventory()

    def test_meta(self):
        meta = self.inventory['_meta']
        self.assertIsNotNone(meta, "_meta missing from inventory")
        self.assertIsInstance(meta, dict, "_meta is not a dict")

    def test_hostvars(self):
        hostvars = self.inventory['_meta']['hostvars']
        self.assertIsNotNone(hostvars, "hostvars missing from _meta")
        self.assertIsInstance(hostvars, dict, "hostvars is not a dict")

    def test_group_vars_all(self):
        group_vars_all = self.inventory['all']
        self.assertIsNotNone(group_vars_all,
                             "group vars all missing from inventory")
        self.assertIsInstance(group_vars_all, dict,
                              "group vars all is not a dict")

        the_vars = group_vars_all['vars']
        self.assertIsNotNone(the_vars,
                             "vars missing from group vars all")
        self.assertIsInstance(the_vars, dict,
                              "vars in group vars all is not a dict")

    def test_expected_host_groups_present(self):

        for group in self.expected_groups:
            the_group = self.inventory[group]
            self.assertIsNotNone(the_group,
                                 "Required host group: %s is missing "
                                 "from inventory" % group)
            self.assertIsInstance(the_group, dict)

            if group != 'all':
                self.assertIn('hosts', the_group)
                self.assertIsInstance(the_group['hosts'], list)

    def test_only_expected_host_groups_present(self):
        all_keys = list(self.expected_groups)
        all_keys.append('_meta')
        self.assertEqual(set(all_keys), set(self.inventory.keys()))


class TestUserConfiguration(unittest.TestCase):
    def setUp(self):
        self.longMessage = True
        self.loaded_user_configuration = di.load_user_configuration(TARGET_DIR)

    def test_loading_user_configuration(self):
        """Test that the user configuration can be loaded"""
        self.assertIsInstance(self.loaded_user_configuration, dict)


class TestEnvironments(unittest.TestCase):
    def setUp(self):
        self.longMessage = True
        self.loaded_environment = di.load_environment(TARGET_DIR)

    def test_loading_environment(self):
        """Test that the environment can be loaded"""
        self.assertIsInstance(self.loaded_environment, dict)

    def test_envd_read(self):
        """Test that the env.d contents are inserted into the environment"""
        expected_keys = [
            'component_skel',
            'container_skel',
            'physical_skel',
        ]
        for key in expected_keys:
            self.assertIn(key, self.loaded_environment)


class TestIps(unittest.TestCase):
    def setUp(self):
        # Allow custom assertion errors.
        self.longMessage = True

    def test_duplicates(self):
        """Test that no duplicate IPs are made on any network."""

        for i in xrange(0, 99):
            inventory = get_inventory()
            ips = collections.defaultdict(int)
            hostvars = inventory['_meta']['hostvars']

            for host, var_dict in hostvars.items():
                nets = var_dict['container_networks']
                for net, vals in nets.items():
                    if 'address' in vals.keys():

                        addr = vals['address']
                        ips[addr] += 1

                        self.assertEqual(1, ips[addr],
                                         msg="IP %s duplicated." % addr)

    def test_empty_ip_queue(self):
        q = Queue.Queue()
        with self.assertRaises(SystemExit) as context:
            di.get_ip_address('test', q)
        expectedLog = ("Cannot retrieve requested amount of IP addresses. "
                       "Increase the test range in your "
                       "openstack_user_config.yml.")
        self.assertEqual(context.exception.message, expectedLog)

    def tearDown(self):
        # Since the get_ip_address function touches USED_IPS,
        # and USED_IPS is currently a global var, make sure we clean it out
        di.USED_IPS = []


class TestConfigChecks(unittest.TestCase):

    def setUp(self):
        self.user_defined_config = dict()
        with open(USER_CONFIG_FILE, 'rb') as f:
            self.user_defined_config.update(yaml.safe_load(f.read()) or {})

    def delete_config_key(self, user_defined_config, key):
        try:
            if key in user_defined_config:
                del user_defined_config[key]
            elif key in user_defined_config['global_overrides']:
                del user_defined_config['global_overrides'][key]
            else:
                raise KeyError("can't find specified key in user config")
        finally:
            self.write_config()

    def delete_provider_network(self, net_name):
        del self.user_defined_config['cidr_networks'][net_name]
        self.write_config()

    def write_config(self):
        # rename temporarily our user_config_file so we can use the new one
        os.rename(USER_CONFIG_FILE, USER_CONFIG_FILE + ".tmp")
        # Save new user_config_file
        with open(USER_CONFIG_FILE, 'wb') as f:
            f.write(yaml.dump(self.user_defined_config))

    def test_missing_container_cidr_network(self):
        self.delete_provider_network('container')
        with self.assertRaises(SystemExit) as context:
            get_inventory()
        expectedLog = ("No container or management network specified in "
                       "user config.")
        self.assertEqual(context.exception.message, expectedLog)

    def test_missing_cidr_network_present_in_provider(self):
        self.delete_provider_network('storage')
        with self.assertRaises(SystemExit) as context:
            get_inventory()
        expectedLog = "can't find storage in cidr_networks"
        self.assertEqual(context.exception.message, expectedLog)

    def test_missing_cidr_networks_key(self):
        del self.user_defined_config['cidr_networks']
        self.write_config()
        with self.assertRaises(SystemExit) as context:
            get_inventory()
        expectedLog = "No container CIDR specified in user config"
        self.assertEqual(context.exception.message, expectedLog)

    def test_provider_networks_check(self):
        # create config file without provider networks
        self.delete_config_key(self.user_defined_config, 'provider_networks')
        # check if provider networks absence is Caught
        with self.assertRaises(SystemExit) as context:
            get_inventory()
        expectedLog = "provider networks can't be found under global_overrides"
        self.assertTrue(expectedLog in context.exception.message)

    def test_global_overrides_check(self):
        # create config file without global_overrides
        self.delete_config_key(self.user_defined_config, 'global_overrides')
        # check if global_overrides absence is Caught
        with self.assertRaises(SystemExit) as context:
            get_inventory()
        expectedLog = "global_overrides can't be found in user config"
        self.assertEqual(context.exception.message, expectedLog)

    def tearDown(self):
        # get back our initial user config file
        os.remove(USER_CONFIG_FILE)
        os.rename(USER_CONFIG_FILE + ".tmp", USER_CONFIG_FILE)


if __name__ == '__main__':
    unittest.main()
