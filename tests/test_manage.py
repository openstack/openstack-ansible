#!/usr/bin/env python

import os
from os import path
import sys
import test_inventory
import unittest

MANAGE_DIR = path.join(os.getcwd(), 'lib')

sys.path.append(MANAGE_DIR)

import manage as mi


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
        hostvars = self.inv['_meta']['hostvars']

        for host, variables in hostvars.items():
            has_networks = 'container_networks' in variables
            if variables.get('is_metal', False):
                continue
            self.assertFalse(has_networks)

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
    unittest.main()
