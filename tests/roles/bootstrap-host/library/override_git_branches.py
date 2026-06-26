# Copyright 2026, Cleura AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r'''
---
module: override_git_branches
short_description: >-
  Override git install branch to HEAD for dependent projects in Zuul CI
description:
  - This module parses Zuul job vars of openstack-ansible to detect
    cross-project dependencies and return their overrides.
options:
  repo_path:
    description: Path to the openstack-ansible clone.
    required: false
    default: /openstack/src/opendev.org/openstack/openstack-ansible
    type: path
  zuul_job_vars_file:
    description: >-
      Path to the osa-job-vars.yml file written by pre-gate-scenario.
    required: false
    default: /home/zuul/osa-job-vars.yml
    type: path
  zuul_items:
    description: >-
      List of speculative changes from zuul.items directly passed from
      the playbook.
    required: false
    type: list
'''

EXAMPLES = r'''
- name: Generate overrides for git install branches based on Depends-On
  override_git_branches:
    zuul_items: "{{ zuul.items | default([]) }}"
  register: branch_overrides
'''


def extract_projects(zuul_items):
    if zuul_items:
        for item in zuul_items:
            if (isinstance(item, dict)
                    and 'project' in item
                    and 'name' in item['project']):
                proj_name = item['project']['name']
                commit_id = item.get('commit_id') or 'HEAD'
                yield proj_name, commit_id


def main():
    module = AnsibleModule(
        argument_spec=dict(
            repo_path=dict(
                type='path',
                default=(
                    '/openstack/src/opendev.org'
                    '/openstack/openstack-ansible'
                )
            ),
            zuul_job_vars_file=dict(
                type='path',
                default='/home/zuul/osa-job-vars.yml'
            ),
            zuul_items=dict(
                type='list',
                default=None
            ),
        ),
        supports_check_mode=True,
    )

    repo_path = module.params['repo_path']
    job_vars_path = module.params['zuul_job_vars_file']
    zuul_items = module.params['zuul_items']

    if zuul_items is None:
        try:
            import yaml
        except ImportError:
            module.fail_json(
                msg=(
                    "The python yaml module (PyYAML) is "
                    "required to read the job vars file."
                )
            )
        if os.path.exists(job_vars_path):
            try:
                with open(job_vars_path, 'r') as f:
                    data = yaml.safe_load(f)
                if data and 'zuul' in data:
                    zuul_data = data['zuul']
                    if 'items' in zuul_data:
                        zuul_items = zuul_data['items']
            except Exception as e:
                module.fail_json(
                    msg=(
                        "Failed to parse job vars file at "
                        f"{job_vars_path}: {str(e)}"
                    )
                )

    if zuul_items is None:
        zuul_items = []

    # Ignore openstack-ansible and ansible roles from being overridden
    project_to_commit = {}

    for project, commit in extract_projects(zuul_items):
        if ('openstack-ansible' not in project
                and 'ansible-role-' not in project):
            project_to_commit[project] = commit

    if not project_to_commit:
        module.exit_json(
            changed=False,
            overrides={},
            msg="No dependent projects found."
        )

    # Locate source_git.yml files in group_vars
    group_vars_path = os.path.join(repo_path, 'inventory/group_vars')
    if not os.path.isdir(group_vars_path):
        module.fail_json(
            msg=f"Group vars path {group_vars_path} does not exist."
        )

    source_git_files = []
    for root, dirs, files in os.walk(group_vars_path):
        for file in files:
            if file == 'source_git.yml':
                source_git_files.append(os.path.join(root, file))

    # Map variable names to repository URLs
    var_to_repo = {}
    for filepath in source_git_files:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(':', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    if var_name.endswith('_git_repo'):
                        val = parts[1].strip().strip('"\'')
                        var_to_repo[var_name] = val
        except Exception as e:
            module.fail_json(msg=f"Error reading {filepath}: {str(e)}")

    # Check matches and compute overrides
    overrides = {}
    for var_name, repo_url in var_to_repo.items():
        clean_url = repo_url.strip().strip('"\'').lower()
        if clean_url.endswith('.git'):
            clean_url = clean_url[:-4]
        for project, commit in project_to_commit.items():
            proj_lower = project.lower()
            if clean_url.endswith('/' + proj_lower) or clean_url == proj_lower:
                install_branch_var = var_name.replace(
                    '_git_repo', '_git_install_branch'
                )
                overrides[install_branch_var] = commit

    if not overrides:
        module.exit_json(
            changed=False,
            overrides={},
            msg="No matching service repositories found for the "
                "dependent projects."
        )

    module.exit_json(
        changed=False,
        overrides=overrides
    )


if __name__ == '__main__':
    main()
