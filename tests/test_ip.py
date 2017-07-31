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

import unittest

from osa_toolkit import ip


class TestIPManager(unittest.TestCase):
    def test_basic_instantiation(self):
        manager = ip.IPManager()

        self.assertEqual({}, manager.queues)
        self.assertEqual(set(), manager.used)

    def test_verbose_instantiation(self):
        manager = ip.IPManager(queues={'test': '192.168.0.0/24'},
                               used_ips=set(['192.168.0.0', '192.168.0.255']))
        self.assertEqual(2, len(manager.used))
        self.assertEqual(254, len(manager.queues['test']))

    def test_instantiation_with_used_list(self):
        manager = ip.IPManager(used_ips=['192.168.0.0', '192.168.0.255'])

        self.assertEqual(2, len(manager.used))

    def test_verbose_instantiation_duplicated_ips(self):
        manager = ip.IPManager(used_ips=['192.168.0.0', '192.168.0.0'])

        self.assertEqual(1, len(manager.used))

    def test_deleting_used(self):
        manager = ip.IPManager(used_ips=set(['192.168.1.1']))

        del manager.used

        self.assertEqual(set(), manager.used)

    def test_getitem(self):
        manager = ip.IPManager(queues={'test': '192.168.0.0/24'})

        self.assertEqual(manager.queues['test'], manager['test'])

    def test_loading_queue(self):
        manager = ip.IPManager()
        manager.load('test', '192.168.0.0/24')
        self.assertEqual(254, len(manager.queues['test']))

    def test_loading_network_excludes(self):
        manager = ip.IPManager()
        manager.load('test', '192.168.0.0/24')
        self.assertNotIn('192.168.0.0', manager.queues['test'])
        self.assertNotIn('192.168.0.255', manager.queues['test'])

    def test_loading_used_ips(self):
        manager = ip.IPManager()
        manager.load('test', '192.168.0.0/24')

        self.assertEqual(2, len(manager.used))
        self.assertIn('192.168.0.0', manager.used)
        self.assertIn('192.168.0.255', manager.used)

    def test_load_creates_networks(self):
        manager = ip.IPManager()
        manager.load('test', '192.168.0.0/24')

        self.assertIn('test', manager._networks)

    def test_loaded_randomly(self):
        manager = ip.IPManager()
        manager.load('test', '192.168.0.0/24')

        self.assertNotEqual(['192.168.0.1', '192.168.0.2', '192.168.0.3'],
                            manager.queues['test'][0:3])

    def test_getting_ip(self):
        manager = ip.IPManager(queues={'test': '192.168.0.0/24'})
        my_ip = manager.get('test')

        self.assertTrue(my_ip.startswith('192.168.0'))
        self.assertIn(my_ip, manager.used)
        self.assertNotIn(my_ip, manager.queues['test'])

    def test_getting_ip_from_empty_queue(self):
        manager = ip.IPManager(queues={'test': '192.168.0.0/31'})
        # There will only be 1 usable IP address in this range.
        manager.get('test')

        with self.assertRaises(ip.EmptyQueue):
            manager.get('test')

    def test_get_ip_from_missing_queue(self):
        manager = ip.IPManager()

        with self.assertRaises(ip.NoSuchQueue):
            manager.get('management')

    def test_release_used_ip(self):
        target_ip = '192.168.0.1'
        manager = ip.IPManager(queues={'test': '192.168.0.0/31'},
                               used_ips=[target_ip])

        manager.release(target_ip)

        # No broadcast address on this network, so only the network addr left
        self.assertEqual(1, len(manager.used))
        self.assertNotIn(target_ip, manager.used)
        self.assertIn(target_ip, manager['test'])

    def test_save_not_implemented(self):
        manager = ip.IPManager()

        with self.assertRaises(NotImplementedError):
            manager.save()

    def test_queue_dict_copied(self):
        manager = ip.IPManager(queues={'test': '192.168.0.0/31'})
        external = manager.queues
        self.assertIsNot(manager.queues, external)
        self.assertIsNot(manager.queues['test'], external['test'])

    def test_queue_list_copied(self):
        manager = ip.IPManager(queues={'test': '192.168.0.0/31'})
        external = manager['test']
        # test against the internal structure since .queues should
        # itself be making copies
        self.assertIsNot(manager._queues['test'], external)

    def test_used_ips_copies(self):
        manager = ip.IPManager(used_ips=['192.168.0.1'])
        external = manager.used
        self.assertIsNot(manager._used_ips, external)

    def test_deleting_used_ips_releases_to_queues(self):
        target_ip = '192.168.0.1'
        manager = ip.IPManager(queues={'test': '192.168.0.0/31'},
                               used_ips=[target_ip])

        del manager.used

        self.assertIn(target_ip, manager['test'])


if __name__ == "__main__":
    unittest.main()
