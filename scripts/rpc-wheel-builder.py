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
# (c) 2014, Kevin Carter <kevin.carter@rackspace.com>

import argparse
import datetime
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
import time
import urlparse

from distutils import version

import requests
import yaml

from cloudlib import logger


PYTHON_PACKAGES = {
    'base_release': dict(),
    'known_release': dict(),
    'from_git': dict(),
    'required_packages': dict()
}

GIT_REPOS = []

GIT_REQUIREMENTS_MAP = {
    'github.com': 'https://raw.githubusercontent.com/%(path)s/%(branch)s'
                  '/%(file)s',
    'openstack.org': 'https://git.openstack.org/cgit/%(path)s/plain'
                     '/%(file)s?id=%(branch)s'
}

VERSION_DESCRIPTORS = [
    '>=', '<=', '==', '!=', '<', '>'
]


class IndicatorThread(object):
    """Creates a visual indicator while normally performing actions."""

    def __init__(self, work_q=None, system=True, debug=False):
        """System Operations Available on Load.

        :param work_q:
        :param system:
        """

        self.debug = debug
        self.work_q = work_q
        self.system = system
        self.job = None

    def __enter__(self):
        if self.debug is False:
            self.indicator_thread()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug is False:
            print('Done.')
            self.job.terminate()

    def indicator(self):
        """Produce the spinner."""

        while self.system:
            busy_chars = ['|', '/', '-', '\\']
            for bc in busy_chars:
                note = 'Please Wait... '
                sys.stdout.write('\rProcessing - [ %s ] - %s' % (bc, note))
                sys.stdout.flush()
                time.sleep(.1)
                self.system = self.system

    def indicator_thread(self):
        """indicate that we are performing work in a thread."""

        self.job = multiprocessing.Process(target=self.indicator)
        self.job.start()
        return self.job


class LoggerWriter(object):
    @property
    def fileno(self):
        return LOG.handlers[0].stream.fileno


def get_file_names(path, ext=None):
    """Return a list of all files in the vars/repo_packages directory.

    :param path: ``str``  $PATH to search for files
    :param ext: ``str`` extension filter for specific files.
    """

    paths = os.walk(os.path.abspath(path))
    files = []
    for fpath, _, afiles in paths:
        for afile in afiles:
            if ext is not None:
                if afile.endswith(ext):
                    files.append(os.path.join(fpath, afile))
            else:
                files.append(os.path.join(fpath, afile))
    else:
        return files


def requirements_parse(pkgs):
    """Parse all requirements.

    :param pkgs: ``list`` list of all requirements to parse.
    """
    for pkg in pkgs:
        LOG.debug('Parsing python dependencies: %s', pkg)
        if '==' in pkg:
            required_packages = PYTHON_PACKAGES['required_packages']
            pkg_name = '-'.join(pkg.split('=='))
            if pkg_name not in required_packages:
                required_packages[pkg_name] = pkg

        split_pkg = pkg.split(',')
        for version_descriptor in VERSION_DESCRIPTORS:
            if version_descriptor in split_pkg[0]:
                name, ver = split_pkg[0].split(version_descriptor)
                ver = '%s%s' % (version_descriptor, ver)
                if len(split_pkg) > 1:
                    versions = split_pkg[1:]
                    versions.insert(0, ver)
                else:
                    versions = [ver]

                break
        else:
            name = split_pkg[0]
            versions = None

        base_release = PYTHON_PACKAGES['base_release']
        if name in base_release:
            saved_versions = base_release[name]
            if versions is not None:
                if '==' in versions:
                    _lv = version.LooseVersion
                    if _lv(versions) < _lv(saved_versions):
                        versions = saved_versions
                        LOG.debug(
                            'New version found for replacement: [ %s ]',
                            versions
                        )

        if isinstance(versions, list):
            base_release[name.lower()] = '%s%s' % (name, ','.join(versions))
        elif versions is not None:
            base_release[name.lower()] = '%s%s' % (name, versions)
        else:
            base_release[name.lower()] = name


def package_dict(var_file):
    """Process variable file for Python requirements.

    :param var_file: ``str`` path to yaml file.
    """
    LOG.debug('Opening [ %s ]', var_file)
    with open(var_file, 'rb') as f:
        package_vars = yaml.safe_load(f.read())

    pip_pkgs = package_vars.get('service_pip_dependencies')
    if pip_pkgs:
        requirements_parse(pkgs=pip_pkgs)

    git_repo = package_vars.get('git_repo')
    if git_repo:
        if git_repo not in GIT_REPOS:
            GIT_REPOS.append(git_repo)

        LOG.debug('Building git type package [ %s ]', git_repo)
        git_url = urlparse.urlsplit(git_repo)
        repo_name = os.path.basename(git_url.path)
        repo = PYTHON_PACKAGES['from_git'][repo_name] = {}
        repo['branch'] = package_vars.get('git_install_branch', 'master')
        repo['full_url'] = git_repo
        repo['project'] = repo_name

        setup_file = None
        for k, v in GIT_REQUIREMENTS_MAP.iteritems():
            if k in git_repo:
                requirements_request = v % {
                    'path': git_url.path.lstrip('/'),
                    'file': package_vars.get(
                        'requirements_file', 'requirements.txt'
                    ),
                    'branch': repo['branch']
                }
                req = requests.get(requirements_request)
                if req.status_code == 200:
                    requirements = [
                        i.split()[0] for i in req.text.splitlines()
                        if i
                        if not i.startswith('#')
                    ]
                    repo['requirements'] = requirements
                    requirements_parse(pkgs=requirements)

                setup_request = v % {
                    'path': git_url.path.lstrip('/'),
                    'file': 'setup.py',
                    'branch': repo['branch']
                }
                setup = requests.head(setup_request)
                if setup.status_code == 200:
                    setup_file = True
                break

        git_req = 'git+%s@%s'
        known_release = PYTHON_PACKAGES['known_release']
        if setup_file is True:
            known_release[repo_name] = git_req % (
                repo['full_url'], repo['branch']
            )

        git_repo_plugins = package_vars.get('git_repo_plugins')
        if git_repo_plugins:
            for grp in git_repo_plugins:
                LOG.debug(
                    'Building git type package with plugins [ %s ]',
                    git_repo_plugins
                )
                plugin = '%s/%s' % (
                    grp['path'].strip('/'),
                    grp['package'].lstrip('/')
                )
                known_release[grp['package']] = git_req % (
                    git_url.geturl(),
                    '%s#egg=%s&subdirectory=%s' % (
                        repo['branch'],
                        grp['package'].strip('/'),
                        plugin
                    )
                )


def retryloop(attempts, timeout=None, delay=None, backoff=1, obj=None):
    """Enter the amount of retries you want to perform.

    The timeout allows the application to quit on "X".
    delay allows the loop to wait on fail. Useful for making REST calls.

    Example:
        Function for retring an action.
        for retry in retryloop(attempts=10, timeout=30, delay=1, backoff=1):
            something
            if somecondition:
                retry()

    :param attempts:
    :param timeout:
    :param delay:
    :param backoff:
    """

    starttime = time.time()
    success = set()
    for _ in range(attempts):
        success.add(True)
        yield success.clear
        if success:
            return
        duration = time.time() - starttime
        if timeout is not None and duration > timeout:
            break
        if delay:
            time.sleep(delay)
            delay *= backoff

    error = (
        'RetryError: FAILED TO PROCESS [ %s ] after [ %s ] Attempts' % (
            obj,
            attempts
        )
    )
    _error_handler(msg=error)


def build_wheel(wheel_dir, build_dir, dist=None, pkg_name=None, quiet=False,
                make_opts=None):
    """Execute python wheel build command.

    :param wheel_dir: ``str`` $PATH to local save directory
    :param build_dir: ``str`` $PATH to temp build directory
    :param dist: ``str`` $PATH to requirements file
    :param pkg_name: ``str`` name of package to build
    """
    command = [
        'pip',
        'wheel',
        '--find-links',
        wheel_dir,
        '--timeout',
        '120',
        '--wheel-dir',
        wheel_dir,
        '--allow-all-external',
        '--build',
        build_dir
    ]

    if make_opts is not None:
        for make_opt in make_opts:
            command.append(make_opt)

    if dist is not None:
        command.extend(['--requirement', dist])
    elif pkg_name is not None:
        command.append(pkg_name)
    else:
        raise SyntaxError('neither "dist" or "pkg_name" was specified')

    build_command = ' '.join(command)
    LOG.info('Command: %s' % build_command)
    for retry in retryloop(3, obj=build_command, delay=2, backoff=1):
        try:
            with IndicatorThread(debug=quiet):
                ret_data = subprocess.check_call(
                    command,
                    stdout=LoggerWriter(),
                    stderr=LoggerWriter()
                )

            LOG.info('Command return code: [ %s ]', ret_data)
            if ret_data:
                raise subprocess.CalledProcessError(ret_data, build_command)
        except subprocess.CalledProcessError as exp:
            LOG.warn(
                'Process failure. Error: [ %s ]. Removing build directory'
                ' for retry. Check log for more detauls.', str(exp)
            )
            retry()


def remove_dirs(directory):
    """Delete a directory recursively.

    :param directory: ``str`` $PATH to directory.
    """
    LOG.info('Removing directory [ %s ]', directory)
    for file_name in get_file_names(path=directory):
        LOG.debug('Removing file [ %s ]', file_name)
        os.remove(file_name)

    dir_names = []
    for dir_name, _, _ in os.walk(directory):
        dir_names.append(dir_name)

    dir_names = sorted(dir_names, reverse=True)
    for dir_name in dir_names:
        try:
            LOG.debug('Removing subdirectory [ %s ]', dir_name)
            os.removedirs(dir_name)
        except OSError:
            pass


def _requirements_maker(name, wheel_dir, release, build_dir, quiet, make_opts,
                        iterate=False):
    requirements_file_lines = []
    for value in sorted(release.values()):
        requirements_file_lines.append('%s\n' % value)

    requirements_file = os.path.join(wheel_dir, name)
    with open(requirements_file, 'wb') as f:
        f.writelines(requirements_file_lines)

    if iterate is True:
        for pkg in sorted(release.values()):
            build_wheel(
                wheel_dir=wheel_dir,
                build_dir=build_dir,
                dist=None,
                pkg_name=pkg,
                quiet=quiet,
                make_opts=make_opts
            )
            remove_dirs(directory=build_dir)
    else:
        build_wheel(
            wheel_dir=wheel_dir,
            build_dir=build_dir,
            dist=requirements_file,
            quiet=quiet,
            make_opts=make_opts
        )
        remove_dirs(directory=build_dir)


def make_wheels(wheel_dir, build_dir, quiet):
    """Build wheels of all installed packages that don't already have one.

    :param wheel_dir: ``str`` $PATH to local save directory
    :param build_dir: ``str`` $PATH to temp build directory
    """

    _requirements_maker(
        name='rpc_base_requirements.txt',
        wheel_dir=wheel_dir,
        release=PYTHON_PACKAGES['base_release'],
        build_dir=build_dir,
        quiet=quiet,
        make_opts=None
    )

    _requirements_maker(
        name='rpc_required_requirements.txt',
        wheel_dir=wheel_dir,
        release=PYTHON_PACKAGES['required_packages'],
        build_dir=build_dir,
        quiet=quiet,
        make_opts=None,
        iterate=True
    )

    _requirements_maker(
        name='rpc_known_requirements.txt',
        wheel_dir=wheel_dir,
        release=PYTHON_PACKAGES['known_release'],
        build_dir=build_dir,
        quiet=quiet,
        make_opts=['--no-deps']
    )

    remove_dirs(
        directory=os.path.join(
            tempfile.gettempdir(),
            'pip_build_root'
        )
    )


def ensure_consistency():
    """Iterate through the known data set and remove duplicates."""

    LOG.info('Ensuring the package list is consistent')
    for key in PYTHON_PACKAGES['known_release'].keys():
        PYTHON_PACKAGES['base_release'].pop(key, None)


def new_setup(user_args, input_path, output_path, quiet):
    """Discover all yaml files in the input directory."""

    LOG.info('Discovering input file(s)')
    var_files = None
    if os.path.isdir(user_args['input']):
        var_files = get_file_names(path=input_path, ext='.yml')
    else:
        if not input_path.endswith(('.yml', '.yaml')):
            error = (
                'The file you specified, [ %s ] does not have a valid yaml'
                ' extension. Please check your file and try again.'
                % input_path
            )
            _error_handler(msg=error)
        else:
            var_files = [input_path]

    # Populate the package dict
    LOG.info('Building the package list')
    with IndicatorThread(debug=quiet):
        for var_file in var_files:
            package_dict(var_file=var_file)

    # Ensure no general packages take precedence over the explicit ones
    ensure_consistency()

    # Get a timestamp and create a report file
    utctime = datetime.datetime.utcnow()
    utctime = utctime.strftime("%Y%m%d_%H%M%S")
    backup_name = 'python-build-report-%s.json' % utctime
    output_report_file = os.path.join(
        output_path,
        'json-reports',
        backup_name
    )
    _mkdirs(os.path.dirname(output_report_file))

    # Generate a timestamped report file
    LOG.info('Generating packaging report [ %s ]', output_report_file)
    with open(output_report_file, 'wb') as f:
        f.write(
            json.dumps(
                PYTHON_PACKAGES,
                indent=2,
                sort_keys=True
            )
        )


def _error_handler(msg, system_exit=True):
    """Handle and error logging and exit the application if needed.

    :param msg: ``str`` message to log
    :param system_exit: ``bol`` if true the system will exit with an error.
    """
    LOG.error(msg)
    if system_exit is True:
        raise SystemExit(msg)


def _user_args():
    """Setup argument Parsing."""

    parser = argparse.ArgumentParser(
        usage='%(prog)s',
        description='Rackspace Openstack, Python wheel builder',
        epilog='Python package builder Licensed "Apache 2.0"'
    )
    file_input = parser.add_mutually_exclusive_group(required=True)
    file_input.add_argument(
        '-i',
        '--input',
        help='Path to the directory where the repo_packages/ file or filess'
             ' are. This can be set to a directory or a file. If the path is'
             ' a directory all .yml files will be scanned for python packages'
             ' and git repositories.',
        default=None
    )
    file_input.add_argument(
        '--pre-input',
        help='Path to a already built json file which contains the python'
             ' packages and git repositories required.',
        default=None
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Path to the location where the built Python package files will'
             ' be stored.',
        required=True,
        default=None
    )
    parser.add_argument(
        '-g',
        '--git-repos',
        help='Path to where to store all of the git repositories.',
        required=False,
        default=None
    )
    parser.add_argument(
        '--build-dir',
        help='Path to temporary build directory. If unset a auto generated'
             ' temporary directory will be used.',
        required=False,
        default=None
    )
    opts = parser.add_mutually_exclusive_group()
    opts.add_argument(
        '--debug',
        help='Enable debug mode',
        action='store_true',
        default=False
    )
    opts.add_argument(
        '--quiet',
        help='Enables quiet mode, this disables all stdout',
        action='store_true',
        default=False
    )

    return vars(parser.parse_args())


def _get_abs_path(path):
    """Return the absolute path for a given path.

    :param path: ``str``  $PATH to be created
    :returns: ``str``
    """
    return os.path.abspath(
        os.path.expanduser(
            path
        )
    )


def _mkdirs(path):
    """Create a directory.

    :param path: ``str``  $PATH to be created
    """
    if not os.path.exists(path):
        LOG.info('Creating directory [ %s ]' % path)
        os.makedirs(path)
    else:
        if not os.path.isdir(path):
            error = (
                'Path [ %s ] can not be created, it exists and is not already'
                ' a directory.' % path
            )
            _error_handler(msg=error)


def _store_git_repos(git_repos_path, quiet):
    """Clone and or update all git repos.

    :param git_repos_path: ``str`` Path to where to store the git repos
    :param quiet: ``bol`` Enable quiet mode.
    """
    _mkdirs(git_repos_path)
    for retry in retryloop(3, delay=2, backoff=1):
        for git_repo in GIT_REPOS:
            with IndicatorThread(debug=quiet):
                repo_name = os.path.basename(git_repo)
                if repo_name.endswith('.git'):
                    repo_name = repo_name.rstrip('git')

                repo_path_name = os.path.join(git_repos_path, repo_name)
                if os.path.isdir(repo_path_name):
                    os.chdir(repo_path_name)
                    LOG.debug('Updating git repo [ %s ]', repo_path_name)
                    commands = [
                        ['git', 'fetch', '-p', 'origin'],
                        ['git', 'pull']
                    ]
                else:
                    LOG.debug('Cloning into git repo [ %s ]', repo_path_name)
                    commands = [
                        ['git', 'clone', git_repo, repo_path_name]
                    ]

                for command in commands:
                    try:
                        ret_data = subprocess.check_call(
                            command,
                            stdout=LoggerWriter(),
                            stderr=LoggerWriter()
                        )
                        if ret_data:
                            raise subprocess.CalledProcessError(
                                ret_data, command
                            )
                    except subprocess.CalledProcessError as exp:
                        LOG.warn('Process failure. Error: [ %s ]', str(exp))
                        retry()
                    else:
                        LOG.debug('Command return code: [ %s ]', ret_data)


def main():
    """Run the main app.

    This application will create all Python wheel files from within an
    environment.  The purpose is to create pre-compiled python wheels from
    the RPC playbooks.
    """

    # Parse input arguments
    user_args = _user_args()

    # Load the logging
    _logging = logger.LogSetup(debug_logging=user_args['debug'])
    if user_args['quiet'] is True or user_args['debug'] is False:
        stream = False
    else:
        stream = True

    _logging.default_logger(
        name='rpc_wheel_builder',
        enable_stream=stream
    )

    global LOG
    LOG = logger.getLogger(name='rpc_wheel_builder')

    # Create the output path
    output_path = _get_abs_path(path=user_args['output'])
    LOG.info('Getting output path')
    _mkdirs(path=output_path)

    # Create the build path
    LOG.info('Getting build path')
    if user_args['build_dir'] is not None:
        build_path = _get_abs_path(path=user_args['build_dir'])
        _mkdirs(path=build_path)
    else:
        build_path = tempfile.mkdtemp(prefix='rpc_wheels_build_')
        pre_input = user_args['pre_input']
        if pre_input:
            pre_input_path = _get_abs_path(path=user_args['pre_input'])
            with open(pre_input_path, 'rb') as f:
                global PYTHON_PACKAGES
                PYTHON_PACKAGES = json.loads(f.read())
        else:
            # Get the input path
            LOG.info('Getting input path')
            input_path = _get_abs_path(path=user_args['input'])
            new_setup(
                user_args=user_args,
                input_path=input_path,
                output_path=output_path,
                quiet=stream
            )

        # Create all of the python package wheels
        make_wheels(
            wheel_dir=output_path,
            build_dir=build_path,
            quiet=stream
        )

    # if git_repos was defined save all of the sources to the defined location
    git_repos_path = user_args.get('git_repos')
    if git_repos_path:
        _store_git_repos(git_repos_path, quiet=stream)



if __name__ == "__main__":
    main()
