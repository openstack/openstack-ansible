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
# (c) 2014, Kevin Carter <kevin.carter@rackspace.com>

import os
import traceback

from ansible import errors
from ansible import utils
import yaml


VERSION_DESCRIPTORS = ['>=', '<=', '==', '!=', '<', '>']


REQUIREMENTS_FILE_TYPES = [
    'global-requirements.txt',
    'test-requirements.txt',
    'dev-requirements.txt',
    'global-requirement-pins.txt'
]


# List of variable names that could be used within the yaml files that
# represent lists of python packages.
BUILT_IN_PIP_PACKAGE_VARS = [
    'service_pip_dependencies',
    'pip_common_packages',
    'pip_container_packages',
    'pip_packages'
]


def git_pip_link_parse(repo):
    """Return a tuple containing the parts of a git repository.

    Example parsing a standard git repo:
      >>> git_pip_link_parse('git+https://github.com/username/repo@tag')
      ('repo',
       'tag',
       None,
       'https://github.com/username/repo',
       'git+https://github.com/username/repo@tag')

    Example parsing a git repo that uses an installable from a subdirectory:
      >>> git_pip_link_parse(
      ...     'git+https://github.com/username/repo@tag#egg=plugin.name'
      ...     '&subdirectory=remote_path/plugin.name'
      ... )
      ('repo',
       'tag',
       'remote_path/plugin.name',
       'https://github.com/username/repo',
       'git+https://github.com/username/repo@tag#egg=plugin.name&'
       'subdirectory=remote_path/plugin.name')

    :param repo: git repo string to parse.
    :type repo: ``str``
    :returns: ``tuple``
    """

    _git_url = repo.split('+')
    if len(_git_url) >= 2:
        _git_url = _git_url[1]
    else:
        _git_url = _git_url[0]

    git_branch_sha = _git_url.split('@')
    if len(git_branch_sha) > 1:
        url, branch = git_branch_sha
    else:
        url = git_branch_sha[0]
        branch = 'master'

    name = os.path.basename(url.rstrip('/'))
    _branch = branch.split('#')
    branch = _branch[0]

    plugin_path = None
    # Determine if the package is a plugin type
    if len(_branch) > 1:
        if 'subdirectory' in _branch[-1]:
            plugin_path = _branch[1].split('subdirectory=')[1].split('&')[0]

    return name.lower(), branch, plugin_path, url, repo


class DependencyFileProcessor(object):
    def __init__(self, local_path):
        """Find required files.

        :type local_path: ``str``
        :return:
        """
        self.pip = dict()
        self.pip['git_package'] = list()
        self.pip['py_package'] = list()
        self.pip['role_packages'] = dict()
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

            if git_data['fragments']:
                package = '%s&%s' % (package, git_data['fragments'])

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
            var_name = git_item.split('_git_repo')[0]

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
        package = '%s#egg=%s' % (package, git_pip_link_parse(package)[0].replace('-', '_'))
        git_data['fragments'] = loaded_yaml.get(
            '%s_git_install_fragments' % var_name.replace('.', '_')
        )
        if git_data['fragments']:
            package = '%s#%s' % (package, git_data['fragments'])

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

        role_name = None
        for file_name in file_names:
            with open(file_name, 'rb') as f:
                # If there is an exception loading the file continue
                #  and if the loaded_config is None continue. This makes
                #  no bad config gets passed to the rest of the process.
                try:
                    loaded_config = yaml.safe_load(f.read())
                except Exception:  # Broad exception so everything is caught
                    continue
                else:
                    if not loaded_config:
                        continue

                    if 'roles' in file_name:
                        _role_name = file_name.split('roles%s' % os.sep)[-1]
                        role_name = _role_name.split(os.sep)[0]


            for key, values in loaded_config.items():
                # This conditional is set to ensure we're not processes git repos
                #  from the defaults file which may conflict with what is being set
                #  in the repo_packages files.
                if not '/defaults/main' in file_name:
                    if key.endswith('git_repo'):
                        self._process_git(
                            loaded_yaml=loaded_config,
                            git_item=key
                        )

                if [i for i in BUILT_IN_PIP_PACKAGE_VARS if i in key]:
                    self.pip['py_package'].extend(values)

                    if role_name:
                        if not role_name in self.pip['role_packages']:
                            self.pip['role_packages'][role_name] = values
                        else:
                            self.pip['role_packages'][role_name].extend(values)
                            self.pip['role_packages'][role_name] = list(
                                set(
                                    self.pip['role_packages'][role_name]
                                )
                            )


def _abs_path(path):
    return os.path.abspath(
        os.path.expanduser(
            path
        )
    )


class LookupModule(object):

    def __init__(self, basedir=None, **kwargs):
        """Run the lookup module.

        :type basedir:
        :type kwargs:
        """
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):
        """Run the main application.

        :type terms: ``str``
        :type inject: ``str``
        :type kwargs: ``dict``
        :returns: ``list``
        """
        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject)
        if isinstance(terms, basestring):
            terms = [terms]

        return_data = {
            'packages': list(),
            'remote_packages': list()
        }
        return_list = list()
        for term in terms:
            try:
                dfp = DependencyFileProcessor(
                    local_path=_abs_path(str(term))
                )
                return_list.extend(dfp.pip['py_package'])
                return_list.extend(dfp.pip['git_package'])
            except Exception as exp:
                raise errors.AnsibleError(
                    'lookup_plugin.py_pkgs(%s) returned "%s" error "%s"' % (
                        term,
                        str(exp),
                        traceback.format_exc()
                    )
                )

            for item in sorted(set(return_list)):
                if item.startswith(('http:', 'https:', 'git+')):
                    if '@' not in item:
                        return_data['packages'].append(item)
                    else:
                        return_data['remote_packages'].append(item)
                else:
                    return_data['packages'].append(item)
            else:
                return_data['packages'] = list(
                    set([i.lower() for i in return_data['packages']])
                )
                return_data['remote_packages'] = list(
                    set(return_data['remote_packages'])
                )
                keys = ['name', 'version', 'fragment', 'url', 'original']
                remote_package_parts = [
                    dict(
                        zip(
                            keys, git_pip_link_parse(i)
                        )
                    ) for i in return_data['remote_packages']
                ]
                return_data['remote_package_parts'] = remote_package_parts
                return_data['role_packages'] = dfp.pip['role_packages']

                return [return_data]
