import io
import unittest
from unittest.mock import patch
from osa_toolkit import releasing
from datetime import datetime
from prettytable import PrettyTable
from ruamel.yaml import YAML
from packaging import requirements

class TestReleasing(unittest.TestCase):
    """
    Test suite for the 'releasing' module
    """

    def test_parse_requirements(self):
        """
        Tests the `parse_requirements` function.
        """
        req = list(releasing.parse_requirements("pip==18.0"))[0]
        self.assertEqual(req.name, "pip")
        self.assertEqual(req.specifier, requirements.SpecifierSet("==18.0"))
        self.assertEqual(req.extras, set())

    def test_discover_requirements_sha(self):
        """
        Tests the `discover_requirements_sha` function.
        """
        expected_sha = "4425ce22fda513fb7a20e77f28685004296731d0"
        actual_sha = releasing.discover_requirements_sha(
            path="tests/fixtures/repo_packages/openstack_services.yml"
        )
        self.assertEqual(actual_sha, expected_sha)

    def test_print_requirements_state_not_in_uc(self):
        """
        Tests `print_requirements_state` when a package is not in the
        upper constraints. This test uses a context manager to capture
        stdout, which is the equivalent of the `capsys` pytest fixture.
        """
        pins = {"pip": "==18.0"}
        latest_versions = {"pip": "18.0"}
        constraints_versions = {}

        # Capture the output of the function
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            releasing.print_requirements_state(pins, latest_versions, constraints_versions)
            captured_output = fake_stdout.getvalue()

        # Generate the expected output string for comparison
        reftable = PrettyTable(
            ["Package", "Current Version Spec", "Latest version on PyPI", "Constrained to"]
        )
        reftable.add_row(["pip", "==18.0", "18.0", "None"])
        expected_output = str(reftable) + "\n" # PrettyTable adds a newline

        self.assertEqual(captured_output, expected_output)

    def test_print_requirements_state_in_uc(self):
        """
        Tests `print_requirements_state` when a package is in the
        upper constraints.
        """
        pins = {"pip": "==18.0"}
        latest_versions = {"pip": "18.0"}
        constraints_versions = {"pip": "==30.3.0"}

        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            releasing.print_requirements_state(pins, latest_versions, constraints_versions)
            captured_output = fake_stdout.getvalue()

        reftable = PrettyTable(
            ["Package", "Current Version Spec", "Latest version on PyPI", "Constrained to"]
        )
        reftable.add_row(["pip", "==18.0", "18.0", "==30.3.0"])
        expected_output = str(reftable) + "\n"

        self.assertEqual(captured_output, expected_output)

    def test_find_yaml_files(self):
        """
        Tests the `find_yaml_files` function.
        """
        self.assertEqual(len(releasing.find_yaml_files(["tests/fixtures/repo_packages/*.yaml"])), 0)
        self.assertEqual(len(releasing.find_yaml_files(["tests/fixtures/notexistingfolder/"])), 0)
        self.assertEqual(
            len(releasing.find_yaml_files([
                "tests/fixtures/notexistingfolder/",
                "tests/fixtures/repo_packages/*"
            ])), 2
        )
        self.assertEqual(len(releasing.find_yaml_files(["tests/fixtures/repo_packages/*"])), 2)

    def test_build_repos_dict(self):
        """
        Tests the `build_repos_dict` function.
        """
        yaml = YAML()
        with open("tests/fixtures/repo_packages/gnocchi.yml", "r") as fd:
            repofiledata = yaml.load(fd)
        repos = releasing.build_repos_dict(repofiledata)

        self.assertEqual(repos["gnocchi"]["url"], "https://github.com/gnocchixyz/gnocchi")
        self.assertEqual(repos["gnocchi"]["sha"], "711e51f706dcc5bc97ad14ddc8108e501befee23")
        self.assertEqual(repos["gnocchi"]["trackbranch"], "stable/4.3")

    def test_get_sha_from_ref(self):
        """
        Tests the `get_sha_from_ref` function.
        """
        sha = releasing.get_sha_from_ref(
            "https://github.com/openstack/openstack-ansible.git", "newton-eol"
        )
        self.assertEqual(sha, "bf565c6ae34bb4343b4d6b486bd9b514de370b0a")

    @patch('osa_toolkit.releasing.get_sha_from_ref')
    @patch('osa_toolkit.releasing.j2_template')
    def test_process_upstream_repos(self, mock_j2_template, mock_get_sha):
        """
        Tests the `_process_upstream_repos` generator.
        """
        # Mock the Jinja2 template rendering
        mock_template = unittest.mock.Mock()
        mock_template.render.return_value = 'http://example.com/repo.git'
        mock_j2_template.return_value = mock_template

        mock_get_sha.return_value = 'new_sha_123'
        repos = {
            'project1': {
                'url': '{{ openstack_opendev_base_url }}/project1',
                'trackbranch': 'master'
            },
            'project2': {
                'url': '{{ openstack_opendev_base_url }}/project2',
                'trackbranch': 'None'
            }
        }

        results = list(releasing._process_upstream_repos(repos))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ('project1', 'new_sha_123'))
        mock_get_sha.assert_called_once_with('http://example.com/repo.git', 'master')

    @patch('osa_toolkit.releasing.copy_role_releasenotes')
    @patch('osa_toolkit.releasing.clone_role')
    @patch('osa_toolkit.releasing.get_sha_from_ref')
    def test_process_roles(self, mock_get_sha, mock_clone_role, mock_copy_reno):
        """
        Tests the `_process_roles` generator.
        """
        mock_get_sha.return_value = 'new_sha_for_role'

        mock_commit_datetime = datetime(2024, 1, 10)
        mock_repo = unittest.mock.Mock()
        mock_repo.head.object.committed_datetime = mock_commit_datetime
        mock_repo.working_dir = '/tmp/somedir'
        mock_clone_role.return_value = mock_repo

        all_roles = [
            {
                'name': 'role1',
                'src': 'http://example.com/role1.git',
                'version': 'old_sha',
                'trackbranch': 'master',
                'shallow_since': '2024-01-01'
            },
            {
                'name': 'role2',
                'src': 'http://example.com/role2.git',
                'version': 'master',
                'trackbranch': 'master'
            },
            {
                'name': 'role3',
                'src': 'http://example.com/role3.git',
                'version': 'fixed_sha',
                'trackbranch': 'None'
            }
        ]
        openstack_roles = [all_roles[0]]

        clone_path = '/tmp/fake_clone_path'
        # Test a standard bump
        results = list(releasing._process_ansible_role_requirements(all_roles, openstack_roles, False, False, clone_path))
        self.assertEqual(results[0]['version'], 'new_sha_for_role')
        self.assertEqual(results[0]['shallow_since'], '2024-01-09')
        self.assertEqual(results[1]['version'], 'master')
        self.assertEqual(results[2]['version'], 'fixed_sha')
        mock_clone_role.assert_called()
        mock_copy_reno.assert_called()

        # Test milestone freeze
        mock_get_sha.reset_mock()
        results = list(releasing._process_ansible_role_requirements(all_roles, openstack_roles, True, False, clone_path))
        self.assertEqual(results[0]['version'], 'new_sha_for_role')
        self.assertEqual(results[0]['shallow_since'], '2024-01-09')
        self.assertEqual(mock_get_sha.call_count, 2)

        # Test milestone unfreeze
        results = list(releasing._process_ansible_role_requirements(all_roles, openstack_roles, False, True, clone_path))
        self.assertEqual(results[0]['version'], 'master')
        self.assertEqual(results[1]['version'], 'master')

    @patch('osa_toolkit.releasing.clone_role')
    def test_process_collections(self, mock_clone_role):
        """
        Tests the `_process_collections` generator.
        """
        mock_tag1 = unittest.mock.Mock()
        mock_tag1.name = '1.0.0'
        mock_tag2 = unittest.mock.Mock()
        mock_tag2.name = '2.1.0'
        mock_tag3 = unittest.mock.Mock()
        mock_tag3.name = '2.0.0'
        mock_invalid_tag = unittest.mock.Mock()
        mock_invalid_tag.name = 'not-a-version'

        mock_repo = unittest.mock.Mock()
        mock_repo.tags = [mock_tag1, mock_tag2, mock_tag3, mock_invalid_tag]
        mock_clone_role.return_value = mock_repo

        collections = [
            {'source': 'http://example.com/collection1.git', 'type': 'git', 'version': '1.0.0'},
            {'source': 'community.general', 'type': 'galaxy', 'version': '3.0.0'}
        ]

        clone_path = '/tmp/fake_clone_path'
        results = list(releasing._process_collection_requirements(collections, clone_path))

        self.assertEqual(len(results), 2)
        # First collection should be updated to the highest tag version
        self.assertEqual(results[0]['version'], '2.1.0')
        # Second collection should be unchanged
        self.assertEqual(results[1]['version'], '3.0.0')
        mock_clone_role.assert_called_once_with('http://example.com/collection1.git', unittest.mock.ANY)


if __name__ == '__main__':
    unittest.main()
