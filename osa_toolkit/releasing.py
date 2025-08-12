import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from datetime import datetime, timedelta

try:
    from git import Repo
    from jinja2 import Template as j2_template
    from packaging import requirements as pyrequirements
    from packaging import version
    from prettytable import PrettyTable  # prettytable
    from ruamel.yaml import YAML  # ruamel.yaml
except ImportError as err:
    raise SystemExit(
        'Required dependencies are missing for this script! '
        'Please, make sure that OpenStack-Ansible is installed with '
        '`releases` extras.\n'
        'Check docs for more details: https://docs.openstack.org/openstack-ansible/latest/contributors/periodic-work.html#osa-cli-tooling \n\n'
        f'Error: {err}'
    )

BASE_URI_MAPPING = {
        'openstack_opendev_base_url': 'https://opendev.org',
        'openstack_github_base_url': 'https://github.com',
    }


def _update_head_date(data):
    """Parse data and update date of last bump in it
    :param data: String to parse for
    :returns: string with current date instead of old one
    """
    return re.sub(
        r'### HEAD as of [0-9.]{10} ###',
        "### HEAD as of {:%d.%m.%Y} ###".format(datetime.now()),
        data)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tooling for releasing OpenStack-Ansible"
    )
    subparsers = parser.add_subparsers(help='subcommand help')

    # check_pins
    check_pins_parser = subparsers.add_parser(
        'check_pins',
        help='Sha used for fetching the upper constraints file in requirements'
    )
    check_pins_parser.add_argument(
        "--requirements_sha",
        help="Sha used for fetching the upper constraints file in requirements",
    )
    check_pins_parser.add_argument(
        "--file",
        help="path to global requirements pin file",
        default="global-requirement-pins.txt",
    )
    check_pins_parser.set_defaults(func=analyse_global_requirement_pins)

    # bump_upstream_shas
    bump_upstream_shas_parser = subparsers.add_parser(
        'bump_upstream_shas',
        help='Bump SHAs of OpenStack services'
    )

    bump_upstream_shas_parser.add_argument(
        "--path",
        action='append',
        help="glob expressions for finding files that contain SHAs",
        default=["playbooks/defaults/repo_packages/*.yml",
                 "inventory/group_vars/*all/*_git.yml"],
    )
    bump_upstream_shas_parser.set_defaults(func=bump_ushas)

    # bump_collections
    bump_collections_parser = subparsers.add_parser(
        'bump_collections',
        help='Bump version of Ansible collections'
    )
    bump_collections_parser.add_argument(
        "--file",
        help="path to ansible-collection-requirements.yml file",
        default="ansible-collection-requirements.yml",
    )
    bump_collections_parser.set_defaults(func=bump_acr)

    # bump_roles
    bump_roles_parser = subparsers.add_parser(
        'bump_roles',
        help='Bump roles SHA and copies releases notes from the openstack roles.'
    )
    bump_roles_parser.add_argument(
        "--file",
        help="path to ansible-role-requirements.yml file",
        default="ansible-role-requirements.yml",
    )
    bump_roles_parser.set_defaults(func=bump_arr)

    # freeze_roles_for_milestone
    freeze_roles_parser = subparsers.add_parser(
        'freeze_roles_for_milestone',
        help='Freeze all roles shas for milestone releases and copy release notes'
    )
    freeze_roles_parser.add_argument(
        "--file",
        help="path to ansible-role-requirements.yml file",
        default="ansible-role-requirements.yml",
    )
    freeze_roles_parser.set_defaults(func=freeze_arr)

    # unfreeze_roles_from_milestone
    unfreeze_roles_parser = subparsers.add_parser(
        'unfreeze_roles_from_milestone',
        help=' Unfreeze all roles shas after milestone release'
    )
    unfreeze_roles_parser.add_argument(
        "--file",
        help="path to ansible-role-requirements.yml file",
        default="ansible-role-requirements.yml",
    )
    freeze_roles_parser.set_defaults(func=unfreeze_arr)

    return parser.parse_args()


def analyse_global_requirement_pins(args):
    """Check a package list file for updates on PyPI or on upper constraints"""

    with open(args.file, "r") as global_req_file:
        pins = {
            pin.name: pin.specifier
            for pin in parse_requirements(global_req_file.read())
        }

    latest_versions = get_pypi_versions(pins.keys())

    if not args.requirements_sha:
        sha = discover_requirements_sha()
    else:
        sha = args.requirements_sha

    url = f"https://raw.githubusercontent.com/openstack/requirements/{sha}/upper-constraints.txt"
    with urllib.request.urlopen(url) as response:
        constraints_versions = {
            pin.name: pin.specifier for pin in parse_requirements(response.read().decode('utf-8'))
        }

    print_requirements_state(pins, latest_versions, constraints_versions)


def parse_requirements(requirements):
    """Parse requirement file contents into name, constraints specs, and extra data
    :param pin: Complete string containing a requirement
    :returns: A detailed requirement, each requirement being a tuple containing:
                 - package 'name' (string)
                 - package 'specs' (list of tuples)
                 - package 'extras' (list)
    """
    for req in requirements.split('\n'):
        if re.match(r'^#\s*\w.*', req):
            continue
        try:
            yield pyrequirements.Requirement(req)
        except pyrequirements.InvalidRequirement:
            continue


def get_pypi_versions(pins):
    """ Display package metadata on PyPI
    :param pins: this is a list of packages to check on PyPI
    :returns: dict whose keys are package names and value is latest package version)
    """
    versions = {}
    for pkgname in pins:
        versions[pkgname] = get_pypi_version(pkgname)
    return versions


def get_pypi_version(name):
    """ Return latest version of a package on PyPI
    :param name: This is the project name on PyPI
    :returns: String containing latest version of package
    """
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json") as url:
        data = json.load(url)
    return data["info"]["version"]


def discover_requirements_sha(
    path="inventory/group_vars/all/source_git.yml"
):
    """ Finds in openstack-ansible repos the current SHA for the requirements repo
    :param path: Location of the YAML file containing requirements_git_install_branch
    :returns: String containing the SHA of the requirements repo.
    """
    yaml = YAML()  # use ruamel.yaml to keep comments
    with open(path, "r") as os_repos_yaml:
        repos = yaml.load(os_repos_yaml)
    return repos["requirements_git_install_branch"]


def print_requirements_state(pins, latest_versions, constraints_versions):
    """ Shows current status of global-requirement-pins.txt
    :param pins: A dict containing requirements of the current global-requirement-pins file
    :param latest_versions: A dict containing the latest version of each requirement in pypi
    :param constraints_version: A dict containing the current version of all constraints from requirements repo
    :returns: Nothing
    """
    table = PrettyTable(
        ["Package", "Current Version Spec", "Latest version on PyPI", "Constrained to"]
    )
    for pkgname in pins.keys():
        table.add_row(
            [
                pkgname,
                pins[pkgname],
                latest_versions[pkgname],
                constraints_versions.get(pkgname, "None"),
            ]
        )
    print(table)


def bump_upstream_repos_shas(path):
    """ Processes all the yaml files in the path by updating their upstream repos shas
    :param path: String containing the location of the yaml files to update
    :returns: None
    """
    filelist = find_yaml_files(path)
    for filename in filelist:
        print("Working on %s" % filename)
        bump_upstream_repos_sha_file(filename)


def find_yaml_files(paths):
    """ Lists all the files in a provided paths
    :param paths: Folder location
    :returns: List of files matching the glob
    """
    found_files = [
        file
        for path in paths
        for file in glob.glob(path)
    ]
    return found_files


def bump_upstream_repos_sha_file(filename):
    yaml = YAML()  # use ruamel.yaml to keep comments
    yaml.preserve_quotes = True
    with open(filename, "r") as ossyml:
        yml_data = ossyml.read()
    repofiledata = yaml.load(_update_head_date(yml_data))

    repos = build_repos_dict(repofiledata)
    changed = False
    for project, projectdata in repos.items():
        # a _git_track_branch string of "None" means no tracking, which means
        # do not update (as there is no branch to track)
        project_url = j2_template(projectdata["url"]).render(BASE_URI_MAPPING)
        if projectdata["trackbranch"] != "None":
            print(
                "Bumping project %s on its %s branch"
                % (project_url, projectdata["trackbranch"])
            )
            sha = get_sha_from_ref(project_url, projectdata["trackbranch"])
            if repofiledata[project + "_git_install_branch"] != sha:
                repofiledata[project + "_git_install_branch"] = sha
                changed = True
        else:
            print(
                "Skipping project %s branch %s"
                % (project_url, projectdata["trackbranch"])
            )

    if changed:
        with open(filename, "w") as fw:
            # Temporarily revert the explicit start to add --- into first line
            yaml.explicit_start = True
            yaml.dump(repofiledata, fw)
            yaml.explicit_start = False


# def parse_repos_info(filename):
#    """ Take a file consisting of ordered entries
#    *_git_repo, followed by *_git_install_branch, with a comment the branch to track,
#    returns information about each repos.
#    :param filename: String containing path to file to analyse
#    :returns: YAMLMap object, an ordered dict keeping the comments.
#    """
#    yaml = YAML() # use ruamel.yaml to keep comments
#    with open(filename,'r') as ossyml:
#        y = yaml.load(ossyml)
#    return y


def build_repos_dict(repofiledict):
    """ Returns a structured dict of repos data
    :param repofiledict:
    :returns: Dict of repos, whose values are dicts containing shas and branches.
    """
    repos = dict()
    reponames = [
        key.replace("_git_repo", "")
        for key in repofiledict.keys()
        if key.endswith("_git_repo")
    ]
    for reponame in reponames:
        repos[reponame] = {
            "url": repofiledict[reponame + "_git_repo"],
            "sha": repofiledict[reponame + "_git_install_branch"],
            "trackbranch": repofiledict[reponame + "_git_track_branch"],
        }
    return repos


def get_sha_from_ref(repo_url, reference):
    """ Returns the sha corresponding to the reference for a repo
    :param repo_url: location of the git repository
    :param reference: reference of the branch
    :returns: utf-8 encoded string of the SHA found by the git command
    """
    # Using subprocess instead of convoluted git libraries.
    # Any rc != 0 will be throwing an exception, so we don't have to care
    out = subprocess.check_output(
        ["git", "ls-remote", "--exit-code", repo_url, reference]
    )
    # out is a b'' type string always finishing up with a newline
    # construct list of (ref,sha)
    refs = [
        (line.split(b"\t")[1], line.split(b"\t")[0])
        for line in out.split(b"\n")
        if line != b"" and b"^{}" not in line
    ]
    if len(refs) > 1:
        raise ValueError(
            "More than one ref for reference %s, please be more explicit %s"
            % (reference, refs)
        )
    return refs[0][1].decode("utf-8")


def freeze_ansible_role_requirements_file(filename=""):
    """ Freezes a-r-r for master"""
    update_ansible_role_requirements_file(
        filename, milestone_freeze=True
    )


def unfreeze_ansible_role_requirements_file(filename=""):
    """ Freezes a-r-r for master"""
    update_ansible_role_requirements_file(
        filename, milestone_unfreeze=True
    )


def update_ansible_role_requirements_file(
    filename="", milestone_freeze=False, milestone_unfreeze=False
):
    """ Updates the SHA of each of the ansible roles based on branch given in argument
    Do not do anything on master except if milestone_freeze.
    In that case, freeze by using the branch present in version.
    Else, stable branches only get openstack roles bumped.
    Copies all the release notes of the roles at the same time.
    """

    openstack_roles, external_roles, all_roles = sort_roles(filename)

    clone_root_path = tempfile.mkdtemp()

    for role in all_roles:
        trackbranch = role.get("trackbranch")
        if not trackbranch or trackbranch.lower() == "none":
            print(
                "Skipping role %s branch" % role["name"]
            )
            continue

        copyreleasenotes = False

        shallow_since = role.get("shallow_since")

        # We don't want to copy config_template renos even if it's an openstack
        # role, as it's not branched the same way.
        if role in openstack_roles and (not role["src"].endswith("config_template")):
            copyreleasenotes = True

        # Freeze sha by checking its trackbranch value
        # Do not freeze sha if trackbranch is None
        if trackbranch:
            try:
                role_repo = clone_role(
                   role["src"], clone_root_path, branch=trackbranch, depth="1"
                )
                if milestone_unfreeze:
                    print(f"Unfreeze {trackbranch} role")
                    role["version"] = trackbranch
                # Do nothing when trackbranch and version are same and not freezing
                elif trackbranch == role.get("version") and not milestone_freeze:
                    print("Version and trackbranch equal, skipping...")
                    pass
                # Freeze or Bump
                else:
                    role_head = role_repo.head.object
                    role["version"] = str(role_head)
                    print(f"Bumped role {role['name']} to sha {role['version']}")

                    if shallow_since:
                        head_timestamp = role_head.committed_datetime
                        head_datetime = head_timestamp - timedelta(days=1)
                        role["shallow_since"] = head_datetime.strftime('%Y-%m-%d')

                # Copy the release notes `Also handle the release notes
                # If frozen, no need to copy release notes.
                if copyreleasenotes:
                    print("Copying %s's release notes" % role["name"])
                    copy_role_releasenotes(role_repo.working_dir, "./")
            finally:
                shutil.rmtree(role_repo.working_dir)

    shutil.rmtree(clone_root_path)
    print("Overwriting ansible-role-requirements")
    with open(filename, "w") as arryml:
        yaml = YAML()  # use ruamel.yaml to keep comments that could appear
        yaml.explicit_start = True
        yaml.dump(all_roles, arryml)
        yaml.explicit_start = False


def update_ansible_collection_requirements(filename=''):
    clone_root_path = tempfile.mkdtemp()
    yaml = YAML()  # use ruamel.yaml to keep comments
    with open(filename, "r") as arryml:
        yaml_data = arryml.read()

    all_requirements = yaml.load(_update_head_date(yaml_data))
    all_collections = all_requirements.get('collections')

    for collection in all_collections:
        collection_type = collection.get('type')
        if collection_type == 'git' and collection["version"] != 'master':
            collection_repo = clone_role(
                collection["source"], clone_root_path
            )
            collection_tags = collection_repo.tags
            collection_versions = list()
            for tag in collection_tags:
                try:
                    collection_versions.append(version.parse(tag.name))
                except version.InvalidVersion:
                    continue
            collection['version'] = str(max(collection_versions))

    all_requirements['collections'] = all_collections
    print("Overwriting ansible-collection-requirements")
    with open(filename, "w") as arryml:
        yaml = YAML()  # use ruamel.yaml to keep comments that could appear
        yaml.explicit_start = True
        yaml.dump(all_requirements, arryml)
        yaml.explicit_start = False


def sort_roles(ansible_role_requirements_file):
    """ Separate the openstack roles from the external roles
    :param ansible_role_requirements_file: Path to the a-r-r file
    :returns: 3-tuple: (list of openstack roles, list of external roles, list of all roles)
    """
    yaml = YAML()  # use ruamel.yaml to keep comments
    with open(ansible_role_requirements_file, "r") as arryml:
        yaml_data = arryml.read()
    all_roles = yaml.load(_update_head_date(yaml_data))
    external_roles = []
    openstack_roles = []
    for role in all_roles:
        if role["src"].startswith("https://git.openstack.org/") or (
            role["src"].startswith("https://opendev.org/openstack/")
        ):
            openstack_roles.append(role)
        else:
            external_roles.append(role)
    return openstack_roles, external_roles, all_roles


def clone_role(url, clone_root_path, branch=None, clone_folder=None, depth=None):
    """ Git clone
    :param url: Source of the git repo
    :param branch: Branch of the git repo
    :param clone_root_path: The main folder in which the repo will be cloned.
    :param clone_folder: The relative folder name of the git clone to the clone_root_path
    :param depth(str): The git shallow clone depth
    :returns: dulwich repository object
    """
    gitargs = {}

    if depth and depth.isdigit():
        gitargs.update({"depth": depth, "no-single-branch": True})

    if branch:
        gitargs.update({"branch": branch})

    if not clone_folder:
        clone_folder = url.split("/")[-1]
    dirpath = os.path.join(clone_root_path, clone_folder)

    print(f'Clonning {url} to {dirpath}')
    repo = Repo.clone_from(url, dirpath, **gitargs)
    return repo


def copy_role_releasenotes(src_path, dest_path):
    """ Copy release notes from src to dest
    """
    renos = glob.glob("{}/releasenotes/notes/*.yaml".format(src_path))
    for reno in renos:
        subprocess.call(
            ["rsync", "-aq", reno, "{}/releasenotes/notes/".format(dest_path)]
        )


def find_release_number():
    """ Find a release version amongst usual OSA files
    :returns: version (str),  filename containing version (string)
    """
    yaml = YAML()  # use ruamel.yaml to keep comments
    oa_version_files = [
        "inventory/group_vars/all/all.yml",
        "group_vars/all/all.yml",
        "playbooks/inventory/group_vars/all.yml",
    ]
    for filename in oa_version_files:
        try:
            with open(filename, "r") as vf:
                version = yaml.load(vf)["openstack_release"]
                found_file = filename
                break
        except FileNotFoundError:
            pass
    else:
        raise FileNotFoundError("No file found matching the list of files")
    return version, found_file


def next_release_number(current_version, releasetype):
    version = current_version.split(".")
    if releasetype in ("milestone", "rc"):
        return increment_milestone_version(version, releasetype)
    else:
        increment = {"bugfix": (0, 0, 1), "feature": (0, 1, 0)}[releasetype]
        return increment_version(version, increment)


# THis is taken from releases repo
def increment_version(old_version, increment):
    """Compute the new version based on the previous value.
    :param old_version: Parts of the version string for the last
                        release.
    :type old_version: list(str)
    :param increment: Which positions to increment.
    :type increment: tuple(int)
    """
    new_version_parts = []
    clear = False
    for cur, inc in zip(old_version, increment):
        if clear:
            new_version_parts.append("0")
        else:
            new_version_parts.append(str(int(cur) + inc))
            if inc:
                clear = True
    return new_version_parts


# THis is taken from releases repo
def increment_milestone_version(old_version, release_type):
    """Increment a version using the rules for milestone projects.
    :param old_version: Parts of the version string for the last
                        release.
    :type old_version: list(str)
    :param release_type: Either ``'milestone'`` or ``'rc'``.
    :type release_type: str
    """
    if release_type == "milestone":
        if "b" in old_version[-1]:
            # Not the first milestone
            new_version_parts = old_version[:-1]
            next_milestone = int(old_version[-1][2:]) + 1
            new_version_parts.append("0b{}".format(next_milestone))
        else:
            new_version_parts = increment_version(old_version, (1, 0, 0))
            new_version_parts.append("0b1")
    elif release_type == "rc":
        new_version_parts = old_version[:-1]
        if "b" in old_version[-1]:
            # First RC
            new_version_parts.append("0rc1")
        else:
            next_rc = int(old_version[-1][3:]) + 1
            new_version_parts.append("0rc{}".format(next_rc))
    else:
        raise ValueError("Unknown release type {!r}".format(release_type))
    return new_version_parts


def bump_ushas(args):
    """ Bump upstream projects SHAs.
    :param path: String containing the path of the YAML files formatted for updates
    """

    bump_upstream_repos_shas(args.path)


def bump_acr(args):
    """ Bump collection versions.
    """

    update_ansible_collection_requirements(filename=args.file)


def bump_arr(args):
    """ Bump roles SHA and copies releases notes from the openstack roles.
    Also bumps roles from external sources when the branch to bump is master.
    """

    update_ansible_role_requirements_file(filename=args.file)


def freeze_arr(args):
    """ Freeze all roles shas for milestone releases.
    Bump roles SHA and copies releases notes from the openstack roles.
    Also freezes roles from external sources.
    """

    freeze_ansible_role_requirements_file(filename=args.file)


def unfreeze_arr(args):
    """ Unfreeze all roles shas for milestone releases.
    Also unfreezes roles from external sources.
    """

    unfreeze_ansible_role_requirements_file(filename=args.file)


def main():
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
