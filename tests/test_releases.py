import io
import unittest
from unittest.mock import patch
from osa_toolkit import releasing
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


if __name__ == '__main__':
    unittest.main()
