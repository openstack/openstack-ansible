#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
import git
import itertools
import multiprocessing
import os
import signal
import time

DOCUMENTATION = """
---
module: git_requirements
short_description: Module to run a multithreaded git clone

options:
  repo_info:
    description:
      - List of repo information dictionaries containing at
        a minimum a key entry "src" with the source git URL
        to clone for each repo. In these dictionaries, one
        can further specify:
        "path" - destination clone location
        "version" - git version to checkout
        "refspec" - git refspec to checkout
        "depth" - clone depth level
        "force" - require git clone uses "--force"
  default_path:
    description:
      Default git clone path (str) in case not
      specified on an individual repo basis in
      repo_info. Defaults to "master". Not
      required.
  default_version:
    description:
      Default git version (str) in case not
      specified on an individual repo basis in
      repo_info. Defaults to "master". Not
      required.
  default_refspec:
    description:
      Default git repo refspec (str) in case not
      specified on an individual repo basis in
      repo_info. Defaults to "". Not required.
  default_depth:
    description:
      Default clone depth (int) in case not specified
      on an individual repo basis. Defaults to 10.
      Not required.
  retries:
     description:
      Integer number of retries allowed in case of git
      clone failure. Defaults to 1. Not required.
  delay:
    description:
      Integer time delay (seconds) between git clone
      retries in case of failure. Defaults to 0. Not
      required.
  force:
    description:
      Boolean. Apply --force flags to git clones wherever
      possible. Defaults to False. Not required.
  core_multiplier:
    description:
      Integer multiplier on the number of cores
      present on the machine to use for
      multithreading. For example, on a 2 core
      machine, a multiplier of 4 would use 8
      threads. Defaults to 4. Not required.
"""

EXAMPLES = r"""

- name: Clone repos
  git_requirements:
    repo_info: "[{'src':'https://github.com/ansible/',
                  'name': 'ansible'
                  'dest': '/etc/opt/ansible'}]"
"""


def init_signal():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def check_out_version(repo, version, pull=False, force=False,
                      refspec=None, tag=False, depth=10):
    try:
        repo.git.fetch(tags=tag, force=force, refspec=refspec, depth=depth)
    except Exception as e:
        return ["Failed to fetch %s\n%s" % (repo.working_dir, str(e))]

    try:
        repo.git.checkout(version, force=force)
    except Exception as e:
        return [
            "Failed to check out version %s for %s\n%s" %
            (version, repo.working_dir, str(e))]

    if repo.is_dirty(untracked_files=True) and force:
        try:
            repo.git.clean(force=force)
        except Exception as e:
            return [
                "Failed to clean up repository% s\n%s" %
                (repo.working_dir, str(e))]

    if pull:
        try:
            repo.git.pull(force=force, refspec=refspec, depth=depth)
        except Exception as e:
            return ["Failed to pull repo %s\n%s" % (repo.working_dir, str(e))]
    return []


def pull_wrapper(info):
    role_info = info
    retries = info[1]["retries"]
    delay = info[1]["delay"]
    for i in range(retries):
        success = pull_role(role_info)
        if success:
            return True
        else:
            time.sleep(delay)
    info[2].append(["Role {0} failed after {1} retries\n".format(role_info[0],
                                                                 retries)])
    return False


def pull_role(info):
    role, config, failures = info

    required_version = role["version"]
    version_hash = False
    if 'version' in role:
        # If the version is the length of a hash then treat is as one
        if len(required_version) == 40:
            version_hash = True

    def get_repo(dest):
        try:
            return git.Repo(dest)
        except Exception:
            failtxt = "Role in {0} is broken/not a git repo.".format(
                role["dest"])
            failtxt += "Please delete or fix it manually"
            failures.append(failtxt)
            return False

    # if repo exists
    if os.path.exists(role["dest"]):
        repo = get_repo(role["dest"])
        if not repo:
            return False  # go to next role
        repo_url = list(repo.remote().urls)[0]
        if repo_url != role["src"]:
            repo.remote().set_url(role["src"])

        # if they want master then fetch, checkout and pull to stay at latest
        # master
        if required_version == "master":
            fail = check_out_version(repo, required_version, pull=True,
                                     force=config["force"],
                                     refspec=role["refspec"],
                                     depth=role["depth"])

        # If we have a hash then reset it to
        elif version_hash:
            fail = check_out_version(repo, required_version,
                                     force=config["force"],
                                     refspec=role["refspec"],
                                     depth=role["depth"])
        else:
            # describe can fail in some cases so be careful:
            try:
                current_version = repo.git.describe(tags=True)
            except Exception:
                current_version = ""
            if current_version == required_version and not config["force"]:
                fail = []
                pass
            else:
                fail = check_out_version(repo, required_version,
                                         force=config["force"],
                                         refspec=role["refspec"],
                                         depth=role["depth"],
                                         tag=True)

    else:
        try:
            # If we have a hash id then treat this a little differently
            if version_hash:
                git.Repo.clone_from(role["src"], role["dest"],
                                    branch='master',
                                    no_single_branch=True,
                                    depth=role["depth"])
                repo = get_repo(role["dest"])
                if not repo:
                    return False  # go to next role
                fail = check_out_version(repo, required_version,
                                         force=config["force"],
                                         refspec=role["refspec"],
                                         depth=role["depth"])
            else:
                git.Repo.clone_from(role["src"], role["dest"],
                                    branch=required_version,
                                    depth=role["depth"],
                                    no_single_branch=True)
                fail = []

        except Exception as e:
            fail = ('Failed cloning repo %s\n%s' % (role["dest"], str(e)))

    if fail == []:
        return True
    else:
        failures.append(fail)
        return False


def set_default(dictionary, key, defaults):
    if key not in dictionary.keys():
        dictionary[key] = defaults[key]


def main():
    # Define variables
    failures = multiprocessing.Manager().list()

    # Data we can pass in to the module
    fields = {
        "repo_info": {"required": True, "type": "list"},
        "default_path": {"required": True,
                         "type": "str"},
        "default_version": {"required": False,
                            "type": "str",
                            "default": "master"},
        "default_refspec": {"required": False,
                            "type": "str",
                            "default": None},
        "default_depth": {"required": False,
                          "type": "int",
                          "default": 10},
        "retries": {"required": False,
                    "type": "int",
                    "default": 1},
        "delay": {"required": False,
                  "type": "int",
                  "default": 0},
        "force": {"required": False,
                  "type": "bool",
                  "default": False},
        "core_multiplier": {"required": False,
                            "type": "int",
                            "default": 4},

    }

    # Pull in module fields and pass into variables
    module = AnsibleModule(argument_spec=fields)

    git_repos = module.params['repo_info']
    defaults = {
        "path": module.params["default_path"],
        "depth": module.params["default_depth"],
        "version": module.params["default_version"],
        "refspec": module.params["default_refspec"]
    }
    config = {
        "retries": module.params["retries"],
        "delay": module.params["delay"],
        "force": module.params["force"],
        "core_multiplier": module.params["core_multiplier"]
    }

    # Set up defaults
    for repo in git_repos:
        for key in ["path", "refspec", "version", "depth"]:
            set_default(repo, key, defaults)
        if "name" not in repo.keys():
            repo["name"] = os.path.basename(repo["src"])
        repo["dest"] = os.path.join(repo["path"], repo["name"])

    # Define varibles
    failures = multiprocessing.Manager().list()
    core_count = multiprocessing.cpu_count() * config["core_multiplier"]

    # Load up process and pass in interrupt and core process count
    p = multiprocessing.Pool(core_count, init_signal)

    clone_success = p.map(pull_wrapper, zip(git_repos,
                                            itertools.repeat(config),
                                            itertools.repeat(failures)),
                          chunksize=1)
    p.close()

    success = all(i for i in clone_success)
    if success:
        module.exit_json(msg=str(git_repos), changed=True)
    else:
        module.fail_json(msg=("Module failed"), meta=failures)


if __name__ == '__main__':
    main()
