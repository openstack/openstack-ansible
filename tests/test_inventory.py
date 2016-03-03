#!/usr/bin/env python

import collections
import json
import os
from os import path
import subprocess
import unittest


INV_DIR = '../playbooks/inventory'
SCRIPT_FILENAME = 'dynamic_inventory.py'
INV_SCRIPT = path.join(INV_DIR, SCRIPT_FILENAME)

# We'll use the test directory, and have tox do the cd command for us.
TARGET_DIR = path.join(os.getcwd(), 'inventory')

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
        cmd = [INV_SCRIPT, '--file', TARGET_DIR]
        inventory_string = subprocess.check_output(cmd)
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


if __name__ == '__main__':
    unittest.main()
