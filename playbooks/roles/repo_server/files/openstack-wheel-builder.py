#!/usr/bin/env python
# Copyright 2014, Rackspace US, Inc.
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
#
# (c) 2015, Kevin Carter <kevin.carter@rackspace.com>

import os
import traceback

import yaml

from cloudlib import arguments
from cloudlib import shell


REQUIREMENTS_FILE_TYPES = [
    'requirements.txt',
    'global-requirements.txt',
    'test-requirements.txt',
    'dev-requirements.txt'
]


# List of variable names that could be used within the yaml files that
# represent lists of python packages.
BUILT_IN_PIP_PACKAGE_VARS = [
    'service_pip_dependencies',
    'pip_common_packages',
    'pip_container_packages',
    'pip_packages'
]


class DependencyFileProcessor(object):
    def __init__(self, local_path):
        """Find and process dependent files from a local_path.

        :type local_path: ``str``
        :return:
        """
        self.pip = dict()
        self.pip['git_package'] = list()
        self.pip['py_package'] = list()
        self.git_pip_install = 'git+%s@%s'
        self.file_names = self._get_files(path=local_path)

        # Process everything simply by calling the method
        self._process_files(ext=('yaml', 'yml'))

    def _filter_files(self, file_names, ext):
        """Filter the files and return a sorted list.

        :type file_names:
        :type ext: ``str`` or ``tuple``
        :returns: ``list``
        """
        _file_names = list()
        for file_name in file_names:
            if file_name.endswith(ext):
                if '/defaults/' in file_name or '/vars/' in file_name:
                    _file_names.append(file_name)
                else:
                    continue
            elif os.path.basename(file_name) in REQUIREMENTS_FILE_TYPES:
                with open(file_name, 'rb') as f:
                    packages = [
                        i.split()[0] for i in f.read().splitlines()
                        if i
                        if not i.startswith('#')
                    ]
                    self.pip['py_package'].extend(packages)
        else:
            return sorted(_file_names, reverse=True)

    @staticmethod
    def _get_files(path):
        """Return a list of all files in the defaults/repo_packages directory.

        :type path: ``str``
        :returns: ``list``
        """
        paths = os.walk(os.path.abspath(path))
        files = list()
        for fpath, _, afiles in paths:
            for afile in afiles:
                files.append(os.path.join(fpath, afile))
        else:
            return files

    def _check_plugins(self, git_repo_plugins, git_data):
        """Check if the git url is a plugin type.

        :type git_repo_plugins: ``dict``
        :type git_data: ``dict``
        """
        for repo_plugin in git_repo_plugins:
            plugin = '%s/%s' % (
                repo_plugin['path'].strip('/'),
                repo_plugin['package'].lstrip('/')
            )

            package = self.git_pip_install % (
                git_data['repo'],
                '%s#egg=%s&subdirectory=%s' % (
                    git_data['branch'],
                    repo_plugin['package'].strip('/'),
                    plugin
                )
            )

            self.pip['git_package'].append(package)

    def _process_git(self, loaded_yaml, git_item):
        """Process git repos.

        :type loaded_yaml: ``dict``
        :type git_item: ``str``
        """
        git_data = dict()
        if git_item.split('_')[0] == 'git':
            var_name = 'git'
        else:
            var_name = git_item.split('_')[0]

        git_data['repo'] = loaded_yaml.get(git_item)
        git_data['branch'] = loaded_yaml.get(
            '%s_git_install_branch' % var_name.replace('.', '_')
        )
        if not git_data['branch']:
            git_data['branch'] = loaded_yaml.get(
                'git_install_branch',
                'master'
            )

        package = self.git_pip_install % (
            git_data['repo'], git_data['branch']
        )

        self.pip['git_package'].append(package)

        git_repo_plugins = loaded_yaml.get('%s_repo_plugins' % var_name)
        if git_repo_plugins:
            self._check_plugins(
                git_repo_plugins=git_repo_plugins,
                git_data=git_data
            )

    def _process_files(self, ext):
        """Process files.

        :type ext: ``tuple``
        """
        file_names = self._filter_files(
            file_names=self.file_names,
            ext=ext
        )

        for file_name in file_names:
            with open(file_name, 'rb') as f:
                loaded_config = yaml.safe_load(f.read())

            for key, values in loaded_config.items():
                if key.endswith('git_repo'):
                    self._process_git(
                        loaded_yaml=loaded_config,
                        git_item=key
                    )

                if [i for i in BUILT_IN_PIP_PACKAGE_VARS if i in key]:
                    self.pip['py_package'].extend(values)


def _arguments():
    """Return CLI arguments."""

    arguments_dict = {
        'optional_args': {
            'local_path': {
                'commands': [
                    '--local-path'
                ],
                'help': 'Local path to cloned code.',
                'metavar': '[PATH]',
                'required': True
            },
            'report_file': {
                'commands': [
                    '--report-file'
                ],
                'help': 'Full path to write the package report to',
                'metavar': '[FILE_PATH]',
                'required': True
            },
            'storage_pool': {
                'commands': [
                    '--storage-pool'
                ],
                'help': 'Full path to the directory where you want to store'
                        ' built wheels.',
                'metavar': '[PATH]',
                'required': True
            },
            'release_directory': {
                'commands': [
                    '--release-directory'
                ],
                'help': 'Full path to the directory where the releaesed links'
                        ' will be stored.',
                'metavar': '[PATH]',
                'required': True
            },
            'add_on_repos': {
                'commands': [
                    '--add-on-repos'
                ],
                'help': 'Full repo path to require as an additional add on'
                        ' repo. Example:'
                        ' "git+https://github.com/rcbops/other-repo@master"',
                'metavar': '[REPO_NAME]',
                'nargs': '+'
            },
            'link_pool': {
                'commands': [
                    '--link-pool'
                ],
                'help': 'Full path to the directory links are stored.',
                'metavar': '[PATH]',
                'required': True
            }
        }
    }

    return arguments.ArgumentParserator(
        arguments_dict=arguments_dict,
        epilog='Licensed Apache2',
        title='Discover all of the requirements within the'
              ' os-ansible-deployment project.',
        detail='Requirement lookup',
        description='Discover all of the requirements within the'
                    ' os-ansible-deployment project.',
        env_name='OS_ANSIBLE'
    ).arg_parser()


def _abs_path(path):
    return os.path.abspath(
        os.path.expanduser(
            path
        )
    )


def _run_command(command):
    print('Running "%s"' % command[2])
    run_command = shell.ShellCommands(debug=True)
    info, success = run_command.run_command(' '.join(command))
    if not success:
        raise SystemExit(info)
    else:
        print(info)


def main():
    """Run the main application."""
    user_vars = _arguments()
    return_list = list()
    try:
        dfp = DependencyFileProcessor(
            local_path=_abs_path(user_vars['local_path'])
        )
        return_list.extend(dfp.pip['py_package'])
        return_list.extend(dfp.pip['git_package'])
    except Exception as exp:
        raise SystemExit(
            'Execution failure. Path: "%s", Error: "%s", Trace:\n%s' % (
                user_vars['local_path'],
                str(exp),
                traceback.format_exc()
            )
        )
    else:
        return_data = {
            'packages': list(),
            'remote_packages': list()
        }
        for file_name in sorted(set(return_list)):
            is_url = file_name.startswith(('http:', 'https:', 'git+'))
            if is_url:
                if '@' not in file_name:
                    return_data['packages'].append(file_name)
                else:
                    return_data['remote_packages'].append(file_name)
            else:
                return_data['packages'].append(file_name)
        else:
            return_data['packages'] = ' '.join(
                ['"%s"' % i for i in set(return_data['packages'])]
            )

            if user_vars['add_on_repos']:
                return_data['remote_packages'].extend(
                    [i.strip() for i in user_vars['add_on_repos']]
                )

            return_data['remote_packages'] = ' '.join(
                ['"%s"' % i for i in set(return_data['remote_packages'])]
            )

            # Build report
            report_command = [
                'yaprt',
                '--debug',
                'create-report',
                '--report-file',
                _abs_path(user_vars['report_file']),
                '--git-install-repos',
                return_data['remote_packages'],
                '--packages',
                return_data['packages']
            ]
            _run_command(report_command)

            # Build requirements wheels
            requirements_command = [
                'yaprt',
                '--debug',
                'build-wheels',
                '--report-file',
                _abs_path(user_vars['report_file']),
                '--storage-pool',
                _abs_path(user_vars['storage_pool']),
                '--link-dir',
                _abs_path(user_vars['release_directory']),
                '--pip-extra-link-dirs',
                _abs_path(user_vars['link_pool']),
                '--pip-index',
                'http://rpc-repo.rackspace.com/pools',
                '--pip-extra-index',
                'https://pypi.python.org/simple',
                '--pip-bulk-operation',
                '--build-output',
                '/tmp/openstack-wheel-output',
                '--build-dir',
                '/tmp/openstack-builder',
                '--build-requirements',
                '--force-clean'
            ]
            _run_command(requirements_command)

            # Build wheels from git-repos
            requirements_command = [
                'yaprt',
                '--debug',
                'build-wheels',
                '--report-file',
                _abs_path(user_vars['report_file']),
                '--storage-pool',
                _abs_path(user_vars['storage_pool']),
                '--link-dir',
                _abs_path(user_vars['release_directory']),
                '--pip-extra-link-dirs',
                _abs_path(user_vars['link_pool']),
                '--pip-no-deps',
                '--pip-no-index',
                '--build-output',
                '/tmp/openstack-wheel-output',
                '--build-dir',
                '/tmp/openstack-builder',
                '--build-branches',
                '--build-releases',
                '--force-clean'
            ]
            _run_command(requirements_command)

            # Create HTML index for all files in the release directory
            index_command = [
                'yaprt',
                '--debug',
                'create-html-indexes',
                '--repo-dir',
                _abs_path(user_vars['release_directory'])
            ]
            _run_command(index_command)

            # Store the git repositories
            index_command = [
                'yaprt',
                'store-repos',
                '--report-file',
                _abs_path(user_vars['report_file']),
                '--git-repo-path',
                '/var/www/repo/openstackgit'
            ]
            _run_command(index_command)

if __name__ == '__main__':
    main()
