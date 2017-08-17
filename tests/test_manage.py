#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
from os import path
import test_inventory
import unittest

TARGET_DIR = path.join(os.getcwd(), 'tests', 'inventory')

from osa_toolkit import manage as mi


def setUpModule():
    test_inventory.make_config()


def tearDownModule():
    os.remove(test_inventory.USER_CONFIG_FILE)


class TestExportFunction(unittest.TestCase):
    def setUp(self):
        self.inv = test_inventory.get_inventory()

    def tearDown(self):
        test_inventory.cleanup()

    def test_host_is_present(self):
        host_inv = mi.export_host_info(self.inv)['hosts']
        self.assertIn('aio1', host_inv.keys())

    def test_groups_added(self):
        host_inv = mi.export_host_info(self.inv)['hosts']
        self.assertIn('groups', host_inv['aio1'].keys())

    def test_variables_added(self):
        host_inv = mi.export_host_info(self.inv)['hosts']
        self.assertIn('hostvars', host_inv['aio1'].keys())

    def test_number_of_hosts(self):
        host_inv = mi.export_host_info(self.inv)['hosts']

        self.assertEqual(len(self.inv['_meta']['hostvars']),
                         len(host_inv))

    def test_all_information_added(self):
        all_info = mi.export_host_info(self.inv)['all']
        self.assertIn('provider_networks', all_info)

    def test_all_lb_information(self):
        all_info = mi.export_host_info(self.inv)['all']
        inv_all = self.inv['all']['vars']
        self.assertEqual(inv_all['internal_lb_vip_address'],
                         all_info['internal_lb_vip_address'])


class TestRemoveIpfunction(unittest.TestCase):
    def setUp(self):
        self.inv = test_inventory.get_inventory()

    def tearDown(self):
        test_inventory.cleanup()

    def test_ips_removed(self):
        mi.remove_ip_addresses(self.inv)
        mi.remove_ip_addresses(self.inv, TARGET_DIR)
        hostvars = self.inv['_meta']['hostvars']

        for host, variables in hostvars.items():
            has_networks = 'container_networks' in variables
            if variables.get('is_metal', False):
                continue
            self.assertFalse(has_networks)

    def test_inventory_item_removed(self):
        inventory = self.inv

        # Make sure we have log_hosts in the original inventory
        self.assertIn('log_hosts', inventory)

        mi.remove_inventory_item("log_hosts", inventory)
        mi.remove_inventory_item("log_hosts", inventory, TARGET_DIR)

        # Now make sure it's gone
        self.assertIn('log_hosts', inventory)

    def test_metal_ips_kept(self):
        mi.remove_ip_addresses(self.inv)
        hostvars = self.inv['_meta']['hostvars']

        for host, variables in hostvars.items():
            has_networks = 'container_networks' in variables
            if not variables.get('is_metal', False):
                continue
            self.assertTrue(has_networks)

    def test_ansible_host_vars_removed(self):
        mi.remove_ip_addresses(self.inv)
        hostvars = self.inv['_meta']['hostvars']

        for host, variables in hostvars.items():
            has_host = 'ansible_host' in variables
            if variables.get('is_metal', False):
                continue
            self.assertFalse(has_host)

    def test_multiple_calls(self):
        """Removal should fail silently if keys are absent."""
        mi.remove_ip_addresses(self.inv)
        mi.remove_ip_addresses(self.inv)


if __name__ == '__main__':
    unittest.main(catchbreak=True)
