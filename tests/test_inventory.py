#!/usr/bin/env python

import collections
import copy
import glob
import json
import mock
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
BASE_ENV_DIR = INV_DIR
CONFIGS_DIR = path.join(os.getcwd(), 'etc', 'openstack_deploy')
CONFD = os.path.join(CONFIGS_DIR, 'conf.d')
AIO_CONFIG_FILE = path.join(CONFIGS_DIR, 'openstack_user_config.yml.aio')
USER_CONFIG_FILE = path.join(TARGET_DIR, 'openstack_user_config.yml')

# These files will be placed in TARGET_DIR by INV_SCRIPT.
# They should be cleaned up between each test.
CLEANUP = [
    'openstack_inventory.json',
    'openstack_hostnames_ips.yml',
    'backup_openstack_inventory.tar'
]

# Base config is a global configuration accessible for convenience.
# It should *not* be mutated outside of setUpModule, which populates it.
_BASE_CONFIG = {}


def get_config():
    """Return a copy of the original config so original isn't modified."""
    global _BASE_CONFIG
    return copy.deepcopy(_BASE_CONFIG)


def make_config():
    """Build an inventory configuration from the sample AIO files.

    Take any files specified as '.aio' and load their keys into a
    configuration dict  and write them out to a file for consumption by
    the tests.
    """
    # Allow access here so we can populate the dictionary.
    global _BASE_CONFIG
    config = _BASE_CONFIG

    files = glob.glob(os.path.join(CONFD, '*.aio'))
    for file_name in files:
        with open(file_name, 'r') as f:
            config.update(yaml.safe_load(f.read()))

    with open(AIO_CONFIG_FILE, 'r') as f:
        config.update(yaml.safe_load(f.read()))

    with open(USER_CONFIG_FILE, 'w') as f:
        f.write(yaml.dump(config))


def setUpModule():
    # The setUpModule function is used by the unittest framework.
    make_config()


def tearDownModule():
    # This file should only be removed after all tests are run,
    # thus it is excluded from cleanup.
    os.remove(USER_CONFIG_FILE)


def cleanup():
    for f_name in CLEANUP:
        f_file = path.join(TARGET_DIR, f_name)
        if os.path.exists(f_file):
            os.remove(f_file)


def get_inventory(clean=True, extra_args=None):
    "Return the inventory mapping in a dict."
    # Use the list argument to more closely mirror
    # Ansible's use of the callable.
    args = {'config': TARGET_DIR, 'list': True,
            'environment': BASE_ENV_DIR}
    if extra_args:
        args.update(extra_args)
    try:
        inventory_string = di.main(**args)
        inventory = json.loads(inventory_string)
        return inventory
    finally:
        if clean:
            # Remove the file system artifacts since we want to force
            # fresh runs
            cleanup()


class TestArgParser(unittest.TestCase):
    def test_no_args(self):
        arg_dict = di.args([])
        self.assertEqual(arg_dict['config'], None)
        self.assertEqual(arg_dict['list'], False)

    def test_list_arg(self):
        arg_dict = di.args(['--list'])
        self.assertEqual(arg_dict['list'], True)

    def test_config_arg(self):
        arg_dict = di.args(['--config', '/etc/openstack_deploy'])
        self.assertEqual(arg_dict['config'], '/etc/openstack_deploy')


class TestAnsibleInventoryFormatConstraints(unittest.TestCase):
    inventory = None

    expected_groups = [
        'aio1-host_containers',
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
        'compute-infra_all',
        'compute-infra_containers',
        'compute-infra_hosts',
        'compute_all',
        'compute_containers',
        'compute_hosts',
        'dashboard_all',
        'dashboard_containers',
        'dashboard_hosts',
        'database_containers',
        'database_hosts',
        'galera',
        'galera_all',
        'galera_container',
        'glance_all',
        'glance_api',
        'glance_container',
        'glance_registry',
        'gnocchi_all',
        'gnocchi_api',
        'gnocchi_container',
        'gnocchi_metricd',
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
        'image_all',
        'image_containers',
        'image_hosts',
        'ironic-infra_all',
        'ironic-infra_containers',
        'ironic-infra_hosts',
        'ironic-server_containers',
        'ironic-server_hosts',
        'ironic_all',
        'ironic_api',
        'ironic_api_container',
        'ironic_conductor',
        'ironic_conductor_container',
        'ironic_server',
        'ironic_server_container',
        'ironic_servers',
        'ironic_compute',
        'ironic_compute_container',
        'ironic-compute_containers',
        'ironic-compute_all',
        'ironic-compute_hosts',
        'keystone',
        'keystone_all',
        'keystone_container',
        'log_all',
        'log_containers',
        'log_hosts',
        'lxc_hosts',
        'magnum',
        'magnum-infra_all',
        'magnum-infra_containers',
        'magnum-infra_hosts',
        'magnum_all',
        'magnum_container',
        'memcached',
        'memcached_all',
        'memcached_container',
        'memcaching_containers',
        'memcaching_hosts',
        'metering-alarm_all',
        'metering-alarm_containers',
        'metering-alarm_hosts',
        'metering-compute_all',
        'metering-compute_container',
        'metering-compute_containers',
        'metering-compute_hosts',
        'metering-infra_all',
        'metering-infra_containers',
        'metering-infra_hosts',
        'metrics_all',
        'metrics_containers',
        'metrics_hosts',
        'mq_containers',
        'mq_hosts',
        'network_all',
        'network_containers',
        'network_hosts',
        'neutron_agent',
        'neutron_agents_container',
        'neutron_all',
        'neutron_bgp_dragent',
        'neutron_dhcp_agent',
        'neutron_l3_agent',
        'neutron_lbaas_agent',
        'neutron_linuxbridge_agent',
        'neutron_metadata_agent',
        'neutron_metering_agent',
        'neutron_openvswitch_agent',
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
        'operator_containers',
        'operator_hosts',
        'orchestration_all',
        'orchestration_containers',
        'orchestration_hosts',
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
        'sahara-infra_all',
        'sahara-infra_containers',
        'sahara-infra_hosts',
        'sahara_all',
        'sahara_api',
        'sahara_container',
        'sahara_engine',
        'shared-infra_all',
        'shared-infra_containers',
        'shared-infra_hosts',
        'storage-infra_all',
        'storage-infra_containers',
        'storage-infra_hosts',
        'storage_all',
        'storage_containers',
        'storage_hosts',
        'swift-proxy_all',
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
        'unbound',
        'unbound_all',
        'unbound_container',
        'unbound_containers',
        'unbound_hosts',
        'utility',
        'utility_all',
        'utility_container'
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

    def test_configured_groups_have_hosts(self):
        config = get_config()
        groups = self.inventory.keys()
        for group in groups:
            if group in config.keys():
                self.assertTrue(0 < len(self.inventory[group]['hosts']))


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
        self.loaded_environment = di.load_environment(BASE_ENV_DIR, {})

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

    @mock.patch('dynamic_inventory.load_environment')
    @mock.patch('dynamic_inventory.load_user_configuration')
    def test_duplicates(self, mock_load_config, mock_load_env):
        """Test that no duplicate IPs are made on any network."""

        # Grab our values read from the file system just once.
        mock_load_config.return_value = get_config()
        mock_load_env.return_value = di.load_environment(BASE_ENV_DIR, {})

        mock_open = mock.mock_open()

        for i in xrange(0, 99):
            # tearDown is ineffective for this loop, so clean the USED_IPs
            # on each run
            inventory = None
            di.USED_IPS = set()

            # Mock out the context manager being used to write files.
            # We don't need to hit the file system for this test.
            with mock.patch('__main__.open', mock_open):
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
        di.USED_IPS = set()


class TestConfigCheckBase(unittest.TestCase):
    def setUp(self):
        self.config_changed = False
        self.user_defined_config = get_config()

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

    def add_config_key(self, key, value):
        self.user_defined_config[key] = value
        self.write_config()

    def delete_provider_network(self, net_name):
        del self.user_defined_config['cidr_networks'][net_name]
        self.write_config()

    def delete_provider_network_key(self, net_name, key):
        pns = self.user_defined_config['global_overrides']['provider_networks']
        for net in pns:
            if 'ip_from_q' in net['network']:
                if net['network']['ip_from_q'] == net_name:
                    if key in net['network']:
                        del net['network'][key]

    def write_config(self):
        self.config_changed = True
        # Save new user_config_file
        with open(USER_CONFIG_FILE, 'wb') as f:
            f.write(yaml.dump(self.user_defined_config))

    def restore_config(self):
        # get back our initial user config file
        self.user_defined_config = get_config()
        self.write_config()

    def set_new_hostname(self, user_defined_config, group,
                         old_hostname, new_hostname):
        # set a new name for the specified hostname
        old_hostname_settings = user_defined_config[group].pop(old_hostname)
        user_defined_config[group][new_hostname] = old_hostname_settings
        self.write_config()

    def set_new_ip(self, user_defined_config, group, hostname, ip):
        # Sets an IP address for a specified host.
        user_defined_config[group][hostname]['ip'] = ip
        self.write_config()

    def add_host(self, group, host_name, ip):
        self.user_defined_config[group][host_name] = {'ip': ip}
        self.write_config()

    def tearDown(self):
        if self.config_changed:
            self.restore_config()


class TestConfigChecks(TestConfigCheckBase):
    def test_missing_container_cidr_network(self):
        self.delete_provider_network('container')
        with self.assertRaises(SystemExit) as context:
            get_inventory()
        expectedLog = ("No container or management network specified in "
                       "user config.")
        self.assertEqual(context.exception.message, expectedLog)

    def test_management_network_malformed(self):
        self.delete_provider_network_key('container', 'is_container_address')
        self.delete_provider_network_key('container', 'is_ssh_address')
        self.write_config()

        with self.assertRaises(di.ProviderNetworkMisconfiguration) as context:
            get_inventory()
        expectedLog = ("Provider network with queue 'container' "
                       "requires 'is_container_address' and "
                       "'is_ssh_address' to be set to True.")
        self.assertEqual(context.exception.message, expectedLog)
        self.restore_config()

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
        self.assertIn(expectedLog, context.exception.message)

    def test_global_overrides_check(self):
        # create config file without global_overrides
        self.delete_config_key(self.user_defined_config, 'global_overrides')
        # check if global_overrides absence is Caught
        with self.assertRaises(SystemExit) as context:
            get_inventory()
        expectedLog = "global_overrides can't be found in user config"
        self.assertEqual(context.exception.message, expectedLog)

    def test_two_hosts_same_ip(self):
        # Use an OrderedDict to be certain our testing order is preserved
        # Even with the same hash seed, different OSes get different results,
        # eg. local OS X vs gate's Linux
        config = collections.OrderedDict()
        config['shared-infra_hosts'] = {
            'host1': {
                'ip': '192.168.1.1'
            }
        }
        config['compute_hosts'] = {
            'host2': {
                'ip': '192.168.1.1'
            }
        }

        with self.assertRaises(di.MultipleHostsWithOneIPError) as context:
            di._check_same_ip_to_multiple_host(config)
        self.assertEqual(context.exception.ip, '192.168.1.1')
        self.assertEqual(context.exception.assigned_host, 'host1')
        self.assertEqual(context.exception.new_host, 'host2')

    def test_two_hosts_same_ip_externally(self):
        self.set_new_hostname(self.user_defined_config, "haproxy_hosts",
                              "aio1", "hap")
        with self.assertRaises(di.MultipleHostsWithOneIPError) as context:
            get_inventory()
        expectedLog = ("Both host:aio1 and host:hap have "
                       "address:172.29.236.100 assigned.  Cannot "
                       "assign same ip to both hosts")
        self.assertEqual(context.exception.message, expectedLog)

    def test_one_host_two_ips_externally(self):
        # haproxy chosen because it was last in the config file as of
        # writing
        self.set_new_ip(self.user_defined_config, 'haproxy_hosts', 'aio1',
                        '172.29.236.101')
        with self.assertRaises(di.MultipleIpForHostError) as context:
            get_inventory()
        expectedLog = ("Host aio1 has both 172.29.236.100 and 172.29.236.101 "
                       "assigned")
        self.assertEqual(context.exception.message, expectedLog)

    def test_two_ips(self):
        # Use an OrderedDict to be certain our testing order is preserved
        # Even with the same hash seed, different OSes get different results,
        # eg. local OS X vs gate's Linux
        config = collections.OrderedDict()
        config['shared-infra_hosts'] = {
            'host1': {
                'ip': '192.168.1.1'
            }
        }
        config['compute_hosts'] = {
            'host1': {
                'ip': '192.168.1.2'
            }
        }

        with self.assertRaises(di.MultipleIpForHostError) as context:
            di._check_multiple_ips_to_host(config)
        self.assertEqual(context.exception.current_ip, '192.168.1.1')
        self.assertEqual(context.exception.new_ip, '192.168.1.2')
        self.assertEqual(context.exception.hostname, 'host1')

    def test_correct_hostname_ip_map(self):
        config = {
            'shared-infra_hosts': {
                'host1': {
                    'ip': '192.168.1.1'
                }
            },
            'compute_hosts': {
                'host2': {
                    'ip': '192.168.1.2'
                }
            },
        }
        ret = di._check_multiple_ips_to_host(config)
        self.assertTrue(ret)


class TestStaticRouteConfig(TestConfigCheckBase):
    def setUp(self):
        super(TestStaticRouteConfig, self).setUp()
        self.expectedMsg = ("Static route provider network with queue "
                            "'container' needs both 'cidr' and 'gateway' "
                            "values.")

    def add_static_route(self, q_name, route_dict):
        """Adds a static route to a provider network."""
        pn = self.user_defined_config['global_overrides']['provider_networks']
        for net in pn:
            net_dict = net['network']
            q = net_dict.get('ip_from_q', None)
            if q == q_name:
                net_dict['static_routes'] = [route_dict]
        self.write_config()

    def test_setting_static_route(self):
        route_dict = {'cidr': '10.176.0.0/12',
                      'gateway': '172.29.248.1'}
        self.add_static_route('container', route_dict)
        inventory = get_inventory()

        # Use aio1 and 'container_address' since they're known keys.
        hostvars = inventory['_meta']['hostvars']['aio1']
        cont_add = hostvars['container_networks']['container_address']

        self.assertIn('static_routes', cont_add)

        first_route = cont_add['static_routes'][0]
        self.assertIn('cidr', first_route)
        self.assertIn('gateway', first_route)

    def test_setting_bad_static_route_only_cidr(self):
        route_dict = {'cidr': '10.176.0.0/12'}
        self.add_static_route('container', route_dict)

        with self.assertRaises(di.MissingStaticRouteInfo) as context:
            get_inventory()

        exception = context.exception

        self.assertEqual(str(exception), self.expectedMsg)

    def test_setting_bad_static_route_only_gateway(self):
        route_dict = {'gateway': '172.29.248.1'}
        self.add_static_route('container', route_dict)

        with self.assertRaises(di.MissingStaticRouteInfo) as context:
            get_inventory()

        exception = context.exception

        self.assertEqual(exception.message, self.expectedMsg)

    def test_setting_bad_gateway_value(self):
        route_dict = {'cidr': '10.176.0.0/12',
                      'gateway': None}
        self.add_static_route('container', route_dict)

        with self.assertRaises(di.MissingStaticRouteInfo) as context:
            get_inventory()

        exception = context.exception

        self.assertEqual(exception.message, self.expectedMsg)

    def test_setting_bad_cidr_value(self):
        route_dict = {'cidr': None,
                      'gateway': '172.29.248.1'}
        self.add_static_route('container', route_dict)

        with self.assertRaises(di.MissingStaticRouteInfo) as context:
            get_inventory()

        exception = context.exception

        self.assertEqual(exception.message, self.expectedMsg)

    def test_setting_bad_cidr_gateway_value(self):
        route_dict = {'cidr': None,
                      'gateway': None}
        self.add_static_route('container', route_dict)

        with self.assertRaises(di.MissingStaticRouteInfo) as context:
            get_inventory()

        exception = context.exception

        self.assertEqual(exception.message, self.expectedMsg)


class TestGlobalOverridesConfigDeletion(TestConfigCheckBase):
    def setUp(self):
        super(TestGlobalOverridesConfigDeletion, self).setUp()
        self.inventory = get_inventory()

    def add_global_override(self, var_name, var_value):
        """Adds an arbitrary name and value to the global_overrides dict."""
        overrides = self.user_defined_config['global_overrides']
        overrides[var_name] = var_value

    def remove_global_override(self, var_name):
        """Removes target key from the global_overrides dict."""
        overrides = self.user_defined_config['global_overrides']
        del overrides[var_name]

    def test_global_overrides_delete_when_merge(self):
        """Vars removed from global overrides are removed from inventory"""
        self.add_global_override('foo', 'bar')

        di._parse_global_variables({}, self.inventory,
                                   self.user_defined_config)

        self.remove_global_override('foo')

        di._parse_global_variables({}, self.inventory,
                                   self.user_defined_config)

        self.assertNotIn('foo', self.inventory['all']['vars'],
                         "foo var not removed from group_vars_all")

    def test_global_overrides_merge(self):
        self.add_global_override('foo', 'bar')

        di._parse_global_variables({}, self.inventory,
                                   self.user_defined_config)

        self.assertEqual('bar', self.inventory['all']['vars']['foo'])

    def test_container_cidr_key_retained(self):
        user_cidr = self.user_defined_config['cidr_networks']['container']
        di._parse_global_variables(user_cidr, self.inventory,
                                   self.user_defined_config)
        self.assertIn('container_cidr', self.inventory['all']['vars'])
        self.assertEqual(self.inventory['all']['vars']['container_cidr'],
                         user_cidr)

    def test_only_old_vars_deleted(self):
        self.inventory['all']['vars']['foo'] = 'bar'

        di._parse_global_variables('', self.inventory,
                                   self.user_defined_config)

        self.assertNotIn('foo', self.inventory['all']['vars'])

    def test_empty_vars(self):
        del self.inventory['all']

        di._parse_global_variables('', self.inventory,
                                   self.user_defined_config)

        self.assertIn('container_cidr', self.inventory['all']['vars'])

        for key in self.user_defined_config['global_overrides']:
            self.assertIn(key, self.inventory['all']['vars'])


class TestMultipleRuns(unittest.TestCase):
    def test_creating_backup_file(self):
        inventory_file_path = os.path.join(TARGET_DIR,
                                           'openstack_inventory.json')
        get_backup_name_path = 'dynamic_inventory.get_backup_name'
        backup_name = 'openstack_inventory.json-20160531_171804.json'

        tar_file = mock.MagicMock()
        tar_file.__enter__.return_value = tar_file

        # run make backup with faked tarfiles and date
        with mock.patch('dynamic_inventory.tarfile.open') as tar_open:
            tar_open.return_value = tar_file
            with mock.patch(get_backup_name_path) as backup_mock:
                backup_mock.return_value = backup_name
                di.make_backup(TARGET_DIR, inventory_file_path)

        backup_path = path.join(TARGET_DIR, 'backup_openstack_inventory.tar')

        tar_open.assert_called_with(backup_path, 'a')

        # This chain is present because of how tarfile.open is called to
        # make a context manager inside the make_backup function.

        tar_file.add.assert_called_with(inventory_file_path,
                                        arcname=backup_name)

    def test_recreating_files(self):
        # Deleting the files after the first run should cause the files to be
        # completely remade
        get_inventory()

        get_inventory()

        backup_path = path.join(TARGET_DIR, 'backup_openstack_inventory.tar')

        self.assertFalse(os.path.exists(backup_path))

    def test_rereading_files(self):
        # Generate the initial inventory files
        get_inventory(clean=False)

        inventory_file_path = os.path.join(TARGET_DIR,
                                           'openstack_inventory.json')
        inv = di.get_inventory(TARGET_DIR, inventory_file_path)
        self.assertIsInstance(inv, dict)
        self.assertIn('_meta', inv)
        # This test is basically just making sure we get more than
        # INVENTORY_SKEL populated, so we're not going to do deep testing
        self.assertIn('log_hosts', inv)

    def tearDown(self):
        # Clean up here since get_inventory will not do it by design in
        # this test.
        cleanup()


class TestEnsureInventoryUptoDate(unittest.TestCase):
    def setUp(self):
        self.env = di.load_environment(BASE_ENV_DIR, {})
        # Copy because we manipulate the structure in each test;
        # not copying would modify the global var in the target code
        self.inv = copy.deepcopy(di.INVENTORY_SKEL)
        # Since we're not running skel_setup, add necessary keys
        self.host_vars = self.inv['_meta']['hostvars']

        # The _ensure_inventory_uptodate function depends on values inserted
        # by the skel_setup function
        di.skel_setup(self.env, self.inv)

    def test_missing_required_host_vars(self):
        self.host_vars['host1'] = {}

        di._ensure_inventory_uptodate(self.inv, self.env['container_skel'])

        for required_key in di.REQUIRED_HOSTVARS:
            self.assertIn(required_key, self.host_vars['host1'])

    def test_missing_container_name(self):
        self.host_vars['host1'] = {}

        di._ensure_inventory_uptodate(self.inv, self.env['container_skel'])

        self.assertIn('container_name', self.host_vars['host1'])
        self.assertEqual(self.host_vars['host1']['container_name'], 'host1')

    def test_inserting_container_networks_is_dict(self):
        self.host_vars['host1'] = {}

        di._ensure_inventory_uptodate(self.inv, self.env['container_skel'])

        self.assertIsInstance(self.host_vars['host1']['container_networks'],
                              dict)

    def test_populating_inventory_info(self):
        skel = self.env['container_skel']

        di._ensure_inventory_uptodate(self.inv, skel)

        for container_type, type_vars in skel.items():
            hosts = self.inv[container_type]['hosts']
            if hosts:
                for host in hosts:
                    host_var_entries = self.inv['_meta']['hostvars'][host]
                    if 'properties' in type_vars:
                        self.assertEqual(host_var_entries['properties'],
                                         type_vars['properties'])

    def tearDown(self):
        self.env = None
        self.host_vars = None
        self.inv = None


class OverridingEnvBase(unittest.TestCase):
    def setUp(self):
        self.base_env = di.load_environment(BASE_ENV_DIR, {})

        # Use the cinder configuration as our sample for override testing
        with open(path.join(BASE_ENV_DIR, 'env.d', 'cinder.yml'), 'r') as f:
            self.cinder_config = yaml.safe_load(f.read())

        self.override_path = path.join(TARGET_DIR, 'env.d')
        os.mkdir(self.override_path)

    def write_override_env(self):
        with open(path.join(self.override_path, 'cinder.yml'), 'w') as f:
            f.write(yaml.safe_dump(self.cinder_config))

    def tearDown(self):
        os.remove(path.join(self.override_path, 'cinder.yml'))
        os.rmdir(self.override_path)


class TestOverridingEnvVars(OverridingEnvBase):

    def test_cinder_metal_override(self):
        vol = self.cinder_config['container_skel']['cinder_volumes_container']
        vol['properties']['is_metal'] = False

        self.write_override_env()

        di.load_environment(TARGET_DIR, self.base_env)

        test_vol = self.base_env['container_skel']['cinder_volumes_container']
        self.assertFalse(test_vol['properties']['is_metal'])

    def test_deleting_elements(self):
        # Leave only the 'properties' dictionary attached to simulate writing
        # a partial override file

        vol = self.cinder_config['container_skel']['cinder_volumes_container']
        for key in vol.keys():
            if not key == 'properties':
                del vol[key]

        self.write_override_env()

        di.load_environment(TARGET_DIR, self.base_env)

        test_vol = self.base_env['container_skel']['cinder_volumes_container']

        self.assertIn('belongs_to', test_vol)

    def test_adding_new_keys(self):
        vol = self.cinder_config['container_skel']['cinder_volumes_container']
        vol['a_new_key'] = 'Added'

        self.write_override_env()

        di.load_environment(TARGET_DIR, self.base_env)

        test_vol = self.base_env['container_skel']['cinder_volumes_container']

        self.assertIn('a_new_key', test_vol)
        self.assertEqual(test_vol['a_new_key'], 'Added')

    def test_emptying_dictionaries(self):
        self.cinder_config['container_skel']['cinder_volumes_container'] = {}

        self.write_override_env()

        di.load_environment(TARGET_DIR, self.base_env)

        test_vol = self.base_env['container_skel']['cinder_volumes_container']

        self.assertNotIn('belongs_to', test_vol)

    def test_emptying_lists(self):
        vol = self.cinder_config['container_skel']['cinder_volumes_container']
        vol['belongs_to'] = []

        self.write_override_env()

        di.load_environment(TARGET_DIR, self.base_env)

        test_vol = self.base_env['container_skel']['cinder_volumes_container']

        self.assertEqual(test_vol['belongs_to'], [])


class TestOverridingEnvIntegration(OverridingEnvBase):
    def setUp(self):
        super(TestOverridingEnvIntegration, self).setUp()
        self.user_defined_config = get_config()

        # Inventory is necessary since keys are assumed present
        self.inv = di.get_inventory(TARGET_DIR, '')

    def skel_setup(self):
        self.environment = di.load_environment(TARGET_DIR, self.base_env)

        di.skel_setup(self.environment, self.inv)

        di.skel_load(
            self.environment.get('physical_skel'),
            self.inv
        )

    def test_emptying_container_integration(self):
        self.cinder_config = {}
        self.cinder_config['container_skel'] = {'cinder_volumes_container': {}}

        self.write_override_env()
        self.skel_setup()

        di.container_skel_load(
            self.environment.get('container_skel'),
            self.inv,
            self.user_defined_config
        )

        test_vol = self.base_env['container_skel']['cinder_volumes_container']

        self.assertNotIn('belongs_to', test_vol)
        self.assertNotIn('contains', test_vol)

    def test_empty_contains(self):
        vol = self.cinder_config['container_skel']['cinder_volumes_container']
        vol['contains'] = []

        self.write_override_env()
        self.skel_setup()

        di.container_skel_load(
            self.environment.get('container_skel'),
            self.inv,
            self.user_defined_config
        )

        test_vol = self.base_env['container_skel']['cinder_volumes_container']

        self.assertEqual(test_vol['contains'], [])

    def test_empty_belongs_to(self):
        vol = self.cinder_config['container_skel']['cinder_volumes_container']
        vol['belongs_to'] = []

        self.write_override_env()
        self.skel_setup()

        di.container_skel_load(
            self.environment.get('container_skel'),
            self.inv,
            self.user_defined_config
        )

        test_vol = self.base_env['container_skel']['cinder_volumes_container']

        self.assertEqual(test_vol['belongs_to'], [])

    def tearDown(self):
        super(TestOverridingEnvIntegration, self).tearDown()
        self.user_defined_config = None
        self.inv = None


class TestSetUsedIPS(unittest.TestCase):
    def setUp(self):
        # Clean up the used ips in case other tests didn't.
        di.USED_IPS = set()

        # Create a fake inventory just for this test.
        self.inventory = {'_meta': {'hostvars': {
            'host1': {'container_networks': {
                'net': {'address': '172.12.1.1'}
            }},
            'host2': {'container_networks': {
                'net': {'address': '172.12.1.2'}
            }},
        }}}

    def test_adding_inventory_used_ips(self):
        config = {'used_ips': None}

        di._set_used_ips(config, self.inventory)

        self.assertEqual(len(di.USED_IPS), 2)
        self.assertIn('172.12.1.1', di.USED_IPS)
        self.assertIn('172.12.1.2', di.USED_IPS)

    def tearDown(self):
        di.USED_IPS = set()


class TestConfigCheckFunctional(TestConfigCheckBase):
    def duplicate_ip(self):
        ip = self.user_defined_config['log_hosts']['aio1']
        self.user_defined_config['log_hosts']['bogus'] = ip

    def test_checking_good_config(self):
        output = di.main(config=TARGET_DIR, check=True,
                         environment=BASE_ENV_DIR)
        self.assertEqual(output, 'Configuration ok!')

    def test_duplicated_ip(self):
        self.duplicate_ip()
        self.write_config()
        with self.assertRaises(di.MultipleHostsWithOneIPError) as context:
            di.main(config=TARGET_DIR, check=True, environment=BASE_ENV_DIR)
        self.assertEqual(context.exception.ip, '172.29.236.100')


class TestNetworkEntry(unittest.TestCase):
    def test_all_args_filled(self):
        entry = di.network_entry(True, 'eth1', 'br-mgmt', 'my_type', '1700')

        self.assertNotIn('interface', entry.keys())
        self.assertEqual(entry['bridge'], 'br-mgmt')
        self.assertEqual(entry['type'], 'my_type')
        self.assertEqual(entry['mtu'], '1700')

    def test_container_dict(self):
        entry = di.network_entry(False, 'eth1', 'br-mgmt', 'my_type', '1700')

        self.assertEqual(entry['interface'], 'eth1')


class TestDebugLogging(unittest.TestCase):
    @mock.patch('dynamic_inventory.logging')
    @mock.patch('dynamic_inventory.logger')
    def test_logging_enabled(self, mock_logger, mock_logging):
        # Shadow the real value so tests don't complain about it
        mock_logging.DEBUG = 10

        get_inventory(extra_args={"debug": True})

        self.assertTrue(mock_logging.basicConfig.called)
        self.assertTrue(mock_logger.info.called)
        self.assertTrue(mock_logger.debug.called)

    @mock.patch('dynamic_inventory.logging')
    @mock.patch('dynamic_inventory.logger')
    def test_logging_disabled(self, mock_logger, mock_logging):
        get_inventory(extra_args={"debug": False})

        self.assertFalse(mock_logging.basicConfig.called)
        # Even though logging is disabled, we still call these
        # all over the place; they just choose not to do anything.
        self.assertTrue(mock_logger.info.called)
        self.assertTrue(mock_logger.debug.called)


class TestLxcHosts(TestConfigCheckBase):

    def test_lxc_hosts_group_present(self):
        inventory = get_inventory()
        self.assertIn('lxc_hosts', inventory)

    def test_lxc_hosts_only_inserted_once(self):
        inventory = get_inventory()
        self.assertEqual(1, len(inventory['lxc_hosts']['hosts']))

    def test_lxc_hosts_members(self):
        self.add_host('shared-infra_hosts', 'aio2', '172.29.236.101')
        inventory = get_inventory()
        self.assertIn('aio2', inventory['lxc_hosts']['hosts'])
        self.assertIn('aio1', inventory['lxc_hosts']['hosts'])

    def test_lxc_hosts_in_config_raises_error(self):
        self.add_config_key('lxc_hosts', {})
        with self.assertRaises(di.LxcHostsDefined):
            get_inventory()


if __name__ == '__main__':
    unittest.main()
