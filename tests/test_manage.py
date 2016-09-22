#!/usr/bin/env python

import os
from os import path
import sys
import test_inventory
import unittest

MANAGE_DIR = path.join(os.getcwd(), 'scripts')

sys.path.append(MANAGE_DIR)

import manage_inventory as mi


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


if __name__ == '__main__':
    unittest.main()
