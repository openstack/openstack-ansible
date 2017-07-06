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

from osa_toolkit import dictutils as du


class TestMergeDictUnit(unittest.TestCase):
    def test_merging_dict(self):
        base = {'key1': 'value1'}
        target = {'key2': 'value2'}

        new = du.merge_dict(base, target)

        self.assertIn('key2', new.keys())
        self.assertEqual('value2', new['key2'])

    def test_base_dict_is_modified(self):
        base = {'key1': 'value1'}
        target = {'key2': 'value2'}

        new = du.merge_dict(base, target)

        self.assertIs(base, new)

    def test_merging_nested_dicts(self):
        base = {'key1': 'value1'}
        target = {'key2': {'key2.1': 'value2'}}

        new = du.merge_dict(base, target)

        self.assertIn('key2', new.keys())
        self.assertIn('key2.1', new['key2'].keys())


class TestAppendIfUnit(unittest.TestCase):
    def test_appending_not_present(self):
        base = ['foo', 'bar']
        target = 'baz'

        retval = du.append_if(base, target)

        self.assertIn(target, base)
        self.assertTrue(retval)

    def test_appending_present(self):
        base = ['foo', 'bar', 'baz']
        target = 'baz'

        retval = du.append_if(base, target)

        self.assertFalse(retval)


class TestListRemovalUnit(unittest.TestCase):
    def setUp(self):
        # Can't just use a member list, since it remains changed after each
        # test
        self.base = ['foo', 'bar']

    def test_removing_one_target(self):
        target = ['bar']

        du.recursive_list_removal(self.base, target)

        self.assertNotIn('bar', self.base)

    def test_removing_entire_list(self):
        # Use a copy so we're not hitting the exact same object in memory.
        target = list(self.base)

        du.recursive_list_removal(self.base, target)

        self.assertEqual(0, len(self.base))

    def test_using_base_as_target(self):
        target = self.base

        du.recursive_list_removal(self.base, target)

        self.assertEqual(1, len(self.base))
        self.assertEqual(1, len(target))
        self.assertIn('bar', self.base)

    def test_using_bare_string(self):
        target = 'foo'

        du.recursive_list_removal(self.base, target)

        self.assertEqual(2, len(self.base))


class TestDictRemovalUnit(unittest.TestCase):
    def test_deleting_single_item_in_single_level_noop(self):
        """The function only operates on nested dictionaries"""
        base = {'key1': 'value1'}
        target = ['value1']

        du.recursive_dict_removal(base, target)

        self.assertEqual('value1', base['key1'])

    def test_deleting_single_item(self):
        base = {'key1': {'key1.1': 'value1'}}
        target = ['value1']

        du.recursive_dict_removal(base, target)

        self.assertEqual('value1', base['key1']['key1.1'])

    def test_deleting_single_item_from_list(self):
        base = {'key1': {'key1.1': ['value1']}}
        target = ['value1']

        du.recursive_dict_removal(base, target)

        self.assertEqual(0, len(base['key1']['key1.1']))
        self.assertNotIn('value1', base['key1']['key1.1'])

    def test_deleting_single_item_from_nested_list(self):
        """The function only operates on the 2nd level dictionary"""
        base = {'key1': {'key1.1': {'key1.1.1': ['value1']}}}
        target = ['value1']

        du.recursive_dict_removal(base, target)

        self.assertEqual(1, len(base['key1']['key1.1']['key1.1.1']))
        self.assertIn('value1', base['key1']['key1.1']['key1.1.1'])

    def test_deleting_single_item_top_level_list(self):
        base = {'key1': ['value1']}
        target = ['value1']

        du.recursive_dict_removal(base, target)

        self.assertEqual(0, len(base['key1']))

    def test_deleting_single_nested_key(self):
        base = {'key1': {'key1.1': {'key1.1.1': ['value1']}}}
        target = ['key1.1.1']

        du.recursive_dict_removal(base, target)

        self.assertNotIn('key1.1.1', base['key1']['key1.1'])


if __name__ == '__main__':
    unittest.main()
