#!/usr/bin/env python
#
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
#

import os
from os import path
from osa_toolkit import filesystem as fs
import sys
import unittest
from unittest import mock

from test_inventory import cleanup
from test_inventory import get_inventory
from test_inventory import make_config

INV_DIR = 'inventory'

sys.path.append(path.join(os.getcwd(), INV_DIR))

TARGET_DIR = path.join(os.getcwd(), 'tests', 'inventory')
USER_CONFIG_FILE = path.join(TARGET_DIR, 'openstack_user_config.yml')


def setUpModule():
    # The setUpModule function is used by the unittest framework.
    make_config()


def tearDownModule():
    # This file should only be removed after all tests are run,
    # thus it is excluded from cleanup.
    os.remove(USER_CONFIG_FILE)


class TestMultipleRuns(unittest.TestCase):
    def test_creating_backup_file(self):
        inventory_file_path = os.path.join(TARGET_DIR,
                                           'openstack_inventory.json')
        get_backup_name_path = 'osa_toolkit.filesystem._get_backup_name'
        backup_name = 'openstack_inventory.json-20160531_171804.json'

        tar_file = mock.MagicMock()
        tar_file.__enter__.return_value = tar_file

        # run make backup with faked tarfiles and date
        with mock.patch('osa_toolkit.filesystem.tarfile.open') as tar_open:
            tar_open.return_value = tar_file
            with mock.patch(get_backup_name_path) as backup_mock:
                backup_mock.return_value = backup_name
                fs._make_backup(TARGET_DIR, inventory_file_path)

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

        inv, path = fs.load_inventory(TARGET_DIR)
        self.assertIsInstance(inv, dict)
        self.assertIn('_meta', inv)
        # This test is basically just making sure we get more than
        # INVENTORY_SKEL populated, so we're not going to do deep testing
        self.assertIn('dashboard_hosts', inv)

    def tearDown(self):
        # Clean up here since get_inventory will not do it by design in
        # this test.
        cleanup()


if __name__ == '__main__':
    unittest.main(catchbreak=True)
