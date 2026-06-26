# Copyright 2026, Cleura AB
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

import importlib.util
import os
import sys
import unittest
from unittest import mock

# Load the custom Ansible module by path
module_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'roles/bootstrap-host/library/override_git_branches.py'
    )
)
spec = importlib.util.spec_from_file_location("override_git_branches",
                                              module_path)
ogb = importlib.util.module_from_spec(spec)
sys.modules["override_git_branches"] = ogb
spec.loader.exec_module(ogb)


class TestOverrideGitBranches(unittest.TestCase):
    def test_extract_projects(self):
        zuul_items = [
            {'project': {'name': 'openstack/octavia'}, 'commit_id': 'hash1'},
            {'project': {'name': 'openstack/neutron'}}
        ]
        projects = list(ogb.extract_projects(zuul_items))
        self.assertEqual(
            set(projects),
            {("openstack/octavia", "hash1"), ("openstack/neutron", "HEAD")}
        )

    @mock.patch('override_git_branches.AnsibleModule')
    def test_main_no_projects(self, mock_module_cls):
        mock_module = mock.MagicMock()
        mock_module.params = {
            'repo_path': '/dummy/repo',
            'zuul_job_vars_file': '/dummy/job_vars.yml',
            'zuul_items': None
        }
        mock_module.exit_json.side_effect = SystemExit
        mock_module.fail_json.side_effect = SystemExit
        mock_module.check_mode = False
        mock_module_cls.return_value = mock_module

        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch('os.path.exists', return_value=False):

            with self.assertRaises(SystemExit):
                ogb.main()
            mock_module.exit_json.assert_called_once_with(
                changed=False, overrides={}, msg="No dependent projects found."
            )

    @mock.patch('override_git_branches.AnsibleModule')
    def test_main_with_overrides(self, mock_module_cls):
        mock_module = mock.MagicMock()
        mock_module.params = {
            'repo_path': '/dummy/repo',
            'zuul_job_vars_file': '/dummy/job_vars.yml',
            'zuul_items': None
        }
        mock_module.exit_json.side_effect = SystemExit
        mock_module.fail_json.side_effect = SystemExit
        mock_module.check_mode = False
        mock_module_cls.return_value = mock_module

        # We will mock file reading
        file_contents = {
            '/dummy/repo/inventory/group_vars/octavia_all/source_git.yml': (
                "octavia_git_repo: \"{{ openstack_opendev_base_url }}"
                "/openstack/octavia\"\n"
                "octavia_git_install_branch: "
                "9ff4683c8212e4c043af69f1b5ebadc21651dc58\n"
            ),
            '/dummy/job_vars.yml': (
                "zuul:\n"
                "  items:\n"
                "    - project:\n"
                "        name: openstack/octavia\n"
                "      commit_id: \"some_speculative_sha\"\n"
            )
        }

        # Mock functions/paths
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.walk') as mock_walk, \
             mock.patch('builtins.open') as mock_open:

            mock_walk.return_value = [
                ('/dummy/repo/inventory/group_vars/octavia_all',
                 [],
                 ['source_git.yml'])
            ]

            def side_effect(path, mode='r', *args, **kwargs):
                content = file_contents.get(path, "")
                m = mock.mock_open(read_data=content)
                return m(path, mode, *args, **kwargs)

            mock_open.side_effect = side_effect

            with self.assertRaises(SystemExit):
                ogb.main()

            # Verify changes
            mock_module.exit_json.assert_called_once()
            args, kwargs = mock_module.exit_json.call_args
            self.assertFalse(kwargs.get('changed'))
            expected_overrides = {
                'octavia_git_install_branch': 'some_speculative_sha'
            }
            self.assertEqual(kwargs.get('overrides'), expected_overrides)

    @mock.patch('override_git_branches.AnsibleModule')
    def test_main_invalid_yaml(self, mock_module_cls):
        mock_module = mock.MagicMock()
        mock_module.params = {
            'repo_path': '/dummy/repo',
            'zuul_job_vars_file': '/dummy/job_vars.yml',
            'zuul_items': None
        }
        mock_module.exit_json.side_effect = SystemExit
        mock_module.fail_json.side_effect = SystemExit
        mock_module_cls.return_value = mock_module

        open_mock = mock.mock_open(read_data="invalid: [yaml: syntax")
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('builtins.open', open_mock):

            with self.assertRaises(SystemExit):
                ogb.main()
            mock_module.fail_json.assert_called_once()
            args, kwargs = mock_module.fail_json.call_args
            err_msg = kwargs.get('msg') or (args[0] if args else '')
            self.assertIn("Failed to parse job vars file", err_msg)

    @mock.patch('override_git_branches.AnsibleModule')
    def test_main_missing_keys(self, mock_module_cls):
        mock_module = mock.MagicMock()
        mock_module.params = {
            'repo_path': '/dummy/repo',
            'zuul_job_vars_file': '/dummy/job_vars.yml',
            'zuul_items': None
        }
        mock_module.exit_json.side_effect = SystemExit
        mock_module.fail_json.side_effect = SystemExit
        mock_module_cls.return_value = mock_module

        open_mock = mock.mock_open(read_data="some_other_key: values")
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('builtins.open', open_mock):

            with self.assertRaises(SystemExit):
                ogb.main()
            mock_module.exit_json.assert_called_once_with(
                changed=False, overrides={}, msg="No dependent projects found."
            )

    @mock.patch('override_git_branches.AnsibleModule')
    def test_main_excludes_roles_and_osa(self, mock_module_cls):
        mock_module = mock.MagicMock()
        mock_module.params = {
            'repo_path': '/dummy/repo',
            'zuul_job_vars_file': '/dummy/job_vars.yml',
            'zuul_items': None
        }
        mock_module.exit_json.side_effect = SystemExit
        mock_module.fail_json.side_effect = SystemExit
        mock_module.check_mode = False
        mock_module_cls.return_value = mock_module

        file_contents = {
            '/dummy/job_vars.yml': (
                "zuul:\n"
                "  items:\n"
                "    - project:\n"
                "        name: openstack/openstack-ansible\n"
                "    - project:\n"
                "        name: openstack/ansible-role-zookeeper\n"
            )
        }

        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('builtins.open') as mock_open:

            def side_effect(path, mode='r', *args, **kwargs):
                content = file_contents.get(path, "")
                m = mock.mock_open(read_data=content)
                return m(path, mode, *args, **kwargs)

            mock_open.side_effect = side_effect

            with self.assertRaises(SystemExit):
                ogb.main()

            mock_module.exit_json.assert_called_once_with(
                changed=False, overrides={}, msg="No dependent projects found."
            )

    @mock.patch('override_git_branches.AnsibleModule')
    def test_main_matching_precision_and_git_suffix(self, mock_module_cls):
        mock_module = mock.MagicMock()
        mock_module.params = {
            'repo_path': '/dummy/repo',
            'zuul_job_vars_file': '/dummy/job_vars.yml',
            'zuul_items': None
        }
        mock_module.exit_json.side_effect = SystemExit
        mock_module.fail_json.side_effect = SystemExit
        mock_module.check_mode = False
        mock_module_cls.return_value = mock_module

        file_contents = {
            '/dummy/repo/inventory/group_vars/octavia_all/source_git.yml': (
                "octavia_git_repo: \"{{ openstack_opendev_base_url }}"
                "/openstack/octavia.git\"\n"
                "octavia_dashboard_git_repo: \"{{ "
                "openstack_opendev_base_url }}/openstack/octavia-dashboard\"\n"
            ),
            '/dummy/job_vars.yml': (
                "zuul:\n"
                "  items:\n"
                "    - project:\n"
                "        name: openstack/octavia\n"
                "      commit_id: \"some_sha\"\n"
            )
        }

        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.walk') as mock_walk, \
             mock.patch('builtins.open') as mock_open:

            mock_walk.return_value = [
                ('/dummy/repo/inventory/group_vars/octavia_all',
                 [],
                 ['source_git.yml'])
            ]

            def side_effect(path, mode='r', *args, **kwargs):
                content = file_contents.get(path, "")
                m = mock.mock_open(read_data=content)
                return m(path, mode, *args, **kwargs)

            mock_open.side_effect = side_effect

            with self.assertRaises(SystemExit):
                ogb.main()

            mock_module.exit_json.assert_called_once()
            args, kwargs = mock_module.exit_json.call_args
            expected_overrides = {
                'octavia_git_install_branch': 'some_sha'
            }
            self.assertEqual(kwargs.get('overrides'), expected_overrides)

    @mock.patch('override_git_branches.AnsibleModule')
    def test_main_with_zuul_items(self, mock_module_cls):
        mock_module = mock.MagicMock()
        mock_module.params = {
            'repo_path': '/dummy/repo',
            'zuul_job_vars_file': '/dummy/job_vars.yml',
            'zuul_items': [
                {
                    'project': {
                        'name': 'openstack/octavia'
                    },
                    'commit_id': 'some_speculative_sha_from_param'
                }
            ]
        }
        mock_module.exit_json.side_effect = SystemExit
        mock_module.fail_json.side_effect = SystemExit
        mock_module.check_mode = False
        mock_module_cls.return_value = mock_module

        file_contents = {
            '/dummy/repo/inventory/group_vars/octavia_all/source_git.yml': (
                "octavia_git_repo: \"{{ openstack_opendev_base_url }}"
                "/openstack/octavia\"\n"
                "octavia_git_install_branch: "
                "9ff4683c8212e4c043af69f1b5ebadc21651dc58\n"
            )
        }

        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch('os.path.isdir', return_value=True), \
             mock.patch('os.path.exists', return_value=True), \
             mock.patch('os.walk') as mock_walk, \
             mock.patch('builtins.open') as mock_open:

            mock_walk.return_value = [
                ('/dummy/repo/inventory/group_vars/octavia_all',
                 [],
                 ['source_git.yml'])
            ]

            def side_effect(path, mode='r', *args, **kwargs):
                content = file_contents.get(path, "")
                m = mock.mock_open(read_data=content)
                return m(path, mode, *args, **kwargs)

            mock_open.side_effect = side_effect

            with self.assertRaises(SystemExit):
                ogb.main()

            mock_module.exit_json.assert_called_once()
            args, kwargs = mock_module.exit_json.call_args
            expected_overrides = {
                'octavia_git_install_branch': 'some_speculative_sha_from_param'
            }
            self.assertEqual(kwargs.get('overrides'), expected_overrides)

    @mock.patch('override_git_branches.AnsibleModule')
    def test_main_no_yaml(self, mock_module_cls):
        mock_module = mock.MagicMock()
        mock_module.params = {
            'repo_path': '/dummy/repo',
            'zuul_job_vars_file': '/dummy/job_vars.yml',
            'zuul_items': None
        }
        mock_module.exit_json.side_effect = SystemExit
        mock_module.fail_json.side_effect = SystemExit
        mock_module_cls.return_value = mock_module

        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.dict(sys.modules, {'yaml': None}), \
             mock.patch('os.path.exists', return_value=True):

            with self.assertRaises(SystemExit):
                ogb.main()
            mock_module.fail_json.assert_called_once_with(
                msg=(
                    "The python yaml module (PyYAML) is "
                    "required to read the job vars file."
                )
            )
