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

# Rackspace Private Cloud Frozen Repo Tool (Elsa)
# This tool does the following:
#   - Read config file containing ordered list of upstreams and package lists
#   - Create dist containing all the required packages
#
#  TODO:
#  - config file manipulation - add/remove packages
#  - sync to CDN?
#
# Note: I originaly started writing this as a tool that would manually
# read remote repos and generate local repos. However aptly seems to do that
# well already, so I restarted with an aptly wrapper. This reduces the amount
# of new code needed, but is a bit messy as its scraping CLI output.
# I did investigate the python levelsdb interface but the aptly data is
# not transparent.
#
# Requirements:
# - yaml python module
# - aptly tool installed http://www.aptly.info
# - gpg (and a private key already added for repo signing)
# - curl
# - apt_pkg module
# - space for mirrors of potentially large repos
#
# Structure of a debian repo
# /Repo
#    /dists
#        /dist1
#            Release # lists components and architectures
#            /component1
#                /binary-arch
#                    Release # metadat for this particular
#                            # dist/comp/arch/type
#                    Packages.{bz2,gz} # lists all packages in this
#                                      # dist/comp/arch/type
#            /component2
#        /dist2
#    /pool
#        /component1
#            /a
#                /package_name
#                    package_name_version_arch.deb
#            /b
#        /component2
#            /a
#            /b

# Standard Lib Imports
import argparse
import apt_pkg
import logging
import re
import subprocess
import sys

# External imports
import yaml

# Log configuration
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
stdout_channel = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(stdout_channel)


class Aptly(object):
    """Wrapper around the aptly tool"""

    def run(self, cmd_string, insert_aptly=True, shell=False):
        """ execute a single command
        if insert_aptly is true, the path to aptly will be
        inserted as the first argument.

        returns string for stdout
        """

        args = cmd_string.split(' ')
        if insert_aptly:
            args.insert(0, '/usr/bin/aptly')
            # remove spaces and empty args
            args = [i.strip() for i in args if i.strip()]
        if shell:
            args = " ".join(args)
        LOGGER.debug("run args: %s" % args)
        return subprocess.check_output(args, shell=shell)

    def mirror_list(self):
        """List aptly mirrors"""
        return self.run('mirror list -raw').splitlines()

    def mirror_create(self, name, url, architecture, dist="./",
                      component="", key_id=None, key_url=None):
        """Create a repo mirror via aptly.
        These are metadata only, packages arent pulled till update
        """
        # check mirror doesn't exist
        if name in self.mirror_list():
            raise ValueError("a mirror with name %(name)s already exists"
                             % name)

        # check we have a key for the mirror
        if key_id is None and key_url is None:
            raise ValueError("mirror create requires key_id or key_url")

        LOGGER.info("Creating mirror: %s" % name)

        got_key = False
        for attempt in range(3):
            try:
                if key_id is not None:
                    self.run('gpg --no-default-keyring --keyring '
                             'trustedkeys.gpg --recv-keys %(key_id)s'
                             % {'key_id': key_id}, insert_aptly=False)
                else:
                    self.run('curl %(url)s | gpg --no-default-keyring '
                             '--keyring trustedkeys.gpg --import'
                             % {'url': key_url}, insert_aptly=False,
                             shell=True)
                got_key = True
                break
            except Exception as e:
                LOGGER.warning("gpg import failed: %(exception)s "
                               "Attempt: %(attempt)s"
                               % {'exception': e, 'attempt': attempt})
                continue  # try again

        if not got_key:
            raise Exception("Failed to import gpg key for mirror %s"
                            % name)

        self.run("mirror create -architectures %(arch)s %(name)s %(url)s "
                 "%(dist)s %(component)s" % {'arch': architecture,
                                             'name': name,
                                             'url': url,
                                             'dist': dist,
                                             'component': component})

    def mirror_update(self, name):
        """Update (refresh) an aptly mirror"""
        if name not in self.mirror_list():
            raise ValueError("mirror %(name)s not found"
                             % {'name': name})

        LOGGER.info("Updating mirror %s" % name)

        self.run("mirror update %(name)s" % {'name': name})

        self.mirror_get_packages(name)

    def mirror_get_packages(self, name):
        """Git list of package,version tuples from a mirror"""
        lines = self.run("mirror show -with-packages %(name)s"
                         % {'name': name}).splitlines()

        packages = self.parse_aptly_package_list(lines)

        LOGGER.debug("Found %(num_packages)s packages for mirror %(name)s"
                     % {'num_packages': len(packages),
                        'name': name})
        return packages

    def parse_aptly_package_list(self, lines):
        """ Get list of (name,version) tuples from an aptly package list"""

        # match package list from aptly ... show -with-packages name
        line_re = re.compile('\s{2,}(?P<name>[^_]*)_(?P<version>[^_]*)'
                             '_(?P<arch>[^_]*)')
        packages = []
        for line in lines:
            match = line_re.match(line)
            if match:
                packages.append((match.groupdict()['name'],
                                 match.groupdict()['version']))

        return packages

    def repo_list(self):
        """Get list of repos known to aptly"""
        return self.run("-raw repo list").splitlines()

    def repo_create(self, name):
        """Create an aptly repo"""
        self.run("repo create %(name)s" % {'name': name})

    def repo_get_packages(self, name):
        """ get list of name, version tuples from a repo"""
        lines = self.run('repo show -with-packages %(name)s'
                         % {'name': name})

        return self.parse_aptly_package_list(lines)

    def package_query(self, name, version):
        """ return aptly query string for a package name & version """
        return '"%(name)s (=%(version)s)"' % {'name': name,
                                              'version': version}

    def repo_import_package(self, mirror, repo, package_name,
                            package_version):
        """Pull a package from a mirror into a repo"""
        self.run('repo import %(mirror)s %(repo)s %(query)s'
                 % {'mirror': mirror,
                    'repo': repo,
                    'query': self.package_query(
                        package_name, package_version)
                    }, shell=True)

    def repo_import_packages(self, mirror, repo, packages, batch_size=200):
        while packages:
            batch = packages[0:batch_size]
            if not batch:
                break
            packages = packages[batch_size:]
            query_string = " ".join([self.package_query(n, v) for
                                     n, v in batch])
            self.run('repo import %(mirror)s %(repo)s %(query)s'
                     % {'mirror': mirror,
                        'repo': repo,
                        'query': query_string},
                     shell=True)

    def repo_publish(self, name):
        """Create on disk distribution metata for an aptly internal repo"""
        self.run('publish repo -distribution %(name)s %(name)s'
                 % {'name': name})

        LOGGER.info("Published repo %(name)s" % {'name': name})

    def snapshot_list(self):
        """ List reposnapshots known to aptly"""
        self.run("-raw snapshot list").splitlines()

    def snapshot_create(self, name):
        """ Create an empty aptly snapshot"""
        self.run("snapshot create %(name)s empty")


class Config(object):
    """ Class representing YAML config files"""
    def __init__(self, path):
        self.path = path
        self.read(path)

    def read(self, path=None):
        """Read yaml from self.path into self.data"""
        if path is None:
            path = self.path
        self.data = yaml.load(open(path).read())

    def write(self, path=None):
        """Write yaml version of self.data to self.path"""
        if path is None:
            path = self.path
        with open(path, 'w') as f:
            f.write(yaml.dump(self.data, default_flow_style=False))

    def __getitem__(self, key):
        """pass subscript requests to self.data"""
        return self.data.get(key)

    def __setitem__(self, key, value):
        """pass subscript requests to self.data"""
        self.data[key] = value


class AptlyOrechestrator(object):
    """ Class which uses the Aptly wrapper to achieve RPC aims
    This is mostly creating repos from a supplied config file.
    """

    def __init__(self, args):
        self.config_path = args.config_path
        self.args = args
        self.aptly = Aptly()
        self.config = Config(args.config_path)

    def available_versions_for_package(self, name):
        """Find available versions for a package"""
        versions = []
        for mirror, packages in self.mirrors:
            for package_name, version in packages:
                if package_name == name:
                    versions.append(version)
        return versions

    def ensure_mirrors(self, required_mirrors):
        """ Check mirrors list, create any that are missing"""
        current_mirrors = self.aptly.mirror_list()
        self.mirrors = []
        for required_mirror in required_mirrors:
            # Create mirror if necessary
            mirror_name = required_mirror['name']
            if mirror_name not in current_mirrors:
                self.aptly.mirror_create(**required_mirror)

            # Update mirror if created or already existed
            self.aptly.mirror_update(mirror_name)

            # Store list of available packages for each mirror
            self.mirrors.append(
                (mirror_name, self.aptly.mirror_get_packages(mirror_name)))

    def packages_from_config(self):
        """get list of required packages from config
        :returns: list of name,value tuples.
        """
        return [(name, str(version)) for name, version
                in self.config['packages'].iteritems()]

    def ensure_packages(self, dist_name):
        """Add all packages form config file to repo dist_name"""

        # convert name: version dict to [(name,version),..]
        required_packages = self.packages_from_config()
        repo_packages = self.aptly.repo_get_packages(dist_name)

        # packages that aren't in this repo already so need to be added
        missing_packages = [p for p in required_packages
                            if p not in repo_packages]

        LOGGER.debug("missing packages: %s" % missing_packages)

        # list of packages we dont find in any upstreams
        unavailable_packages = []

        # map of mirror to package list for found packages
        package_map = {}
        for package in missing_packages:
            for mirror, packages in self.mirrors:
                if mirror not in package_map:
                    package_map[mirror] = []
                found = False
                if package in packages:
                    package_map[mirror].append(package)
                    found = True
                    LOGGER.debug("Found  %(pname)s in %(mname)s"
                                 % {'pname': package, 'mname': mirror})
                    break
            if not found:
                unavailable_packages.append(package)
                LOGGER.debug("Failed to find package %(name)s %(version)s"
                             % {'name': package[0],
                                'version': package[1]})

        # Batch import all the packages that are known to be available
        for mirror, packages in package_map.iteritems():
            LOGGER.info("importing packages from %s" % mirror)
            self.aptly.repo_import_packages(mirror, dist_name, packages)

        # Return list of packages that were not found
        return unavailable_packages

    def create_dist_from_package_list(self):
        """High level function for creating a dist from
        a supplied config file"""
        dist_name = self.args.dist_name

        if dist_name in self.aptly.repo_list():
            raise ValueError("dist name must be unique, %s already exists"
                             % dist_name)
        LOGGER.info("Creating repo %(name)s" % {'name': dist_name})
        self.ensure_mirrors(self.config['upstream_repos'])
        self.aptly.repo_create(dist_name)
        unavailable_packages = self.ensure_packages(dist_name)

        if unavailable_packages:
            LOGGER.warning("The following packages are not available")
            for name, version in unavailable_packages:
                available_versions_str = ",".join(
                    self.available_versions_for_package(name))
                LOGGER.warning("Not Found: %(name)s version: %(version)s. "
                               "Availble versions: %(avs)s"
                               % {'name': name,
                                  'version': version,
                                  'avs': available_versions_str})

        self.aptly.repo_publish(dist_name)

    def add_package_to_config(self):
        """ Add a package to the supplied config file"""
        self.config['packages'][self.args.name] = self.args.version
        self.config.write()

    def delete_package_from_config(self):
        """ Remove a package from the supplied config file"""
        del self.config['packages'][self.args.name]
        self.config.write()

    def list_upstream_packages(self):
        self.ensure_mirrors(self.config['upstream_repos'])
        for mirror, packages in self.mirrors:
            for package_name, package_version in packages:
                print "%(mirror_name)s,%(package_name)s,%(package_version)s"\
                    % {'mirror_name': mirror,
                        'package_name': package_name,
                        'package_version': package_version}

    def list_available_updates(self):
        self.ensure_mirrors(self.config['upstream_repos'])

        # needed in order to use apt_pkg.version_compare
        apt_pkg.init()

        # Store newest version available for each package with updates
        package_updates = {}

        for package_name, package_version in self.packages_from_config():
            updates = [v for v in self.available_versions_for_package(
                       package_name) if apt_pkg.version_compare(
                       package_version, v) < 0]
            updates = sorted(set(updates),
                             cmp=apt_pkg.version_compare)
            if updates:
                package_updates[package_name] = updates[-1]
                LOGGER.info("Package %(name)s Config Version: %(current)s"
                            " Updates: %(updates)s"
                            % {'name': package_name,
                                'current': package_version,
                                'updates': updates})

        # write new config file with updated versions, if requested
        if package_updates and 'new_config_path' in self.args:
            for package, version in package_updates.iteritems():
                self.config['packages'][package] = version
            self.config.write(self.args.new_config_path)
            LOGGER.info("updated config written to %s"
                        % self.args.new_config_path)


def main(args):
    parser = argparse.ArgumentParser()

    # arguments that are relevant to all subcommands
    parser.add_argument('config_path')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="more logging")

    # Add subparsers for subcommands
    subparsers = parser.add_subparsers()

    # dfc = distribution from config
    parser_dfc = subparsers.add_parser('dist_from_config')
    parser_dfc.add_argument('dist_name', help="must be unique")
    parser_dfc.set_defaults(func="dfc")

    # subcommand to add packages to config
    parser_add_package = subparsers.add_parser('add_package_to_config')
    parser_add_package.add_argument('name')
    parser_add_package.add_argument('version')
    parser_add_package.set_defaults(func="add_package")

    # subcommand to remove packages from config
    parser_del_package = subparsers.add_parser('delete_package_from_config')
    parser_del_package.add_argument('name')
    parser_del_package.set_defaults(func="del_package")

    # List all packages available in configured upstreams
    parser_list_upstream_pkgs = subparsers.add_parser('list_upstream_pkgs')
    parser_list_upstream_pkgs.set_defaults(func='list_upstream')

    # List all packages in the package list that have updates available
    parser_list_upstream_pkgs = subparsers.add_parser('list_pkg_updates')
    parser_list_upstream_pkgs.set_defaults(func='list_updates')

    # Generate new config file with updated package versions
    parser_generate_updated_config = subparsers.add_parser(
        'generate_updated_config',
        help="Generate new config file with package versions "
             "updated to latest available")
    parser_generate_updated_config.add_argument(
        'new_config_path',
        help="New config with updated package verions will be generated"
             " and written to this path")
    parser_generate_updated_config.set_defaults(func='list_updates')

    args = parser.parse_args(args=args[1:])

    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)

    ao = AptlyOrechestrator(args)
    # Each subparser sets the func arg, call the appropriate function
    {'dfc': ao.create_dist_from_package_list,
     'add_package': ao.add_package_to_config,
     'del_package': ao.delete_package_from_config,
     'list_upstream': ao.list_upstream_packages,
     'list_updates': ao.list_available_updates}[args.func]()

if __name__ == "__main__":
    main(sys.argv)
