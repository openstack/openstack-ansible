#!/usr/bin/env python

import collections
import json
import os
from os import path
import subprocess
import unittest
import yaml

INV_DIR = 'playbooks/inventory'
SCRIPT_FILENAME = 'dynamic_inventory.py'
INV_SCRIPT = path.join(os.getcwd(), INV_DIR, SCRIPT_FILENAME)

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
        cmd = [INV_SCRIPT, '--config', TARGET_DIR]
        inventory_string = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT
        )
        inventory = json.loads(inventory_string)
        return inventory
    finally:
        # Remove the file system artifacts since we want to force fresh runs
        cleanup()


class TestDuplicateIps(unittest.TestCase):
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


class TestConfigChecks(unittest.TestCase):

    def setUp(self):
        self.user_defined_config = dict()
        with open(USER_CONFIG_FILE, 'rb') as f:
            self.user_defined_config.update(yaml.safe_load(f.read()) or {})

    def setup_config_file(self, user_defined_config, key):
        try:
            if key in user_defined_config:
                del user_defined_config[key]
            elif key in user_defined_config['global_overrides']:
                del user_defined_config['global_overrides'][key]
            else:
                raise KeyError("can't find specified key in user config")
        finally:
            # rename temporarily our user_config_file so we can use the new one
            os.rename(USER_CONFIG_FILE, USER_CONFIG_FILE + ".tmp")
            # Save new user_config_file
            with open(USER_CONFIG_FILE, 'wb') as f:
                f.write(yaml.dump(user_defined_config))

    def test_provider_networks_check(self):
        # create config file without provider networks
        self.setup_config_file(self.user_defined_config, 'provider_networks')
        # check if provider networks absence is Caught
        with self.assertRaises(subprocess.CalledProcessError) as context:
            get_inventory()
        expectedLog = "provider networks can't be found under global_overrides"
        self.assertTrue(expectedLog in context.exception.output)

    def test_global_overrides_check(self):
        # create config file without global_overrides
        self.setup_config_file(self.user_defined_config, 'global_overrides')
        # check if global_overrides absence is Caught
        with self.assertRaises(subprocess.CalledProcessError) as context:
            get_inventory()
        expectedLog = "global_overrides can't be found in user config\n"
        self.assertEqual(context.exception.output, expectedLog)

    def tearDown(self):
        # get back our initial user config file
        os.remove(USER_CONFIG_FILE)
        os.rename(USER_CONFIG_FILE + ".tmp", USER_CONFIG_FILE)


if __name__ == '__main__':
    unittest.main()
