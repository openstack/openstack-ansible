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


# ---------------------------------------------------------------------------


# Rackspace Private Cloud Frozen Repo Tool (Elsa)
# This tool does the following:
#   - Create dist containing all the required packages at specific versions
#       Example: python elsa_repo.py config.yml dist_from_config repo-123
#   - Check for new/updated packages and generate a new config file
#       Example: python elsa_repo.py config.yml\
#                generate_updated_config --add-new newconfig.yml
#
# Requirements:
#   - Pip:
#       * python-apt
#       * pyyaml
#   - OS tools:
#       * curl (apt/curl)
#       * aptly http://www.aptly.info/download/
#   - Lots of space for mirrors of potentially large repos.
#     The repo mirrors will be stored in ~/.aptly.
#
# Example YAML Config File:
#    ---
#    config:
#      # only packages matching this arch or 'all' will be imported
#      architecture: amd64
#    # hash of package name: version
#    packages:
#      compat-libstdc: 5-1
#      libargtable2-0: 12-1
#      ...
#    # list of upstreams to search for packages
#    upstream_repos:
#    - component: main
#      dist: testing
#      key_url: http://www.rabbitmq.com/rabbitmq-signing-key-public.asc
#      name: rabbit
#      url: http://www.rabbitmq.com/debian/

#    - component: main
#      dist: stable
#      key_url: http://packages.elasticsearch.org/GPG-KEY-elasticsearch
#      name: elasticsearch
#      url: http://packages.elasticsearch.org/logstash/1.4/debian

#    - key_id: 5234BF2B
#      name: rsyslog_ppa_v8
#      ppa: adiscon/v8-stable

#    - key_id: 1285491434D8786F
#      name: openmanage
#      url: http://linux.dell.com/repo/community/deb/latest/

#    - component: main
#      dist: cloudmonitoring
#      key_url: https://monitoring.api.rackspacecloud.com/pki/agent/linux.asc
#      name: cloud_monitoring_agent
#      url: >
#        http://stable.packages.cloudmonitoring.rackspace.com/
#        ubuntu-14.04-x86_64

# Notes: to generate a full mirror set packages: {} in config then use
#        generate_updated_config --add-new

# Standard Lib Imports
import argparse
import copy
import logging
import re
import subprocess
import sys

# External imports
import apt_pkg
import yaml

# Log configuration
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
stdout_channel = logging.StreamHandler(sys.stdout)
LOGGER.addHandler(stdout_channel)


class PackageStore(object):
    """Store a list of PackageLists and provide search"""

    def __init__(self):
        self.package_lists = {}

    def __iter__(self):
        return self.package_lists.values().__iter__()

    def __contains__(self, list_name):
        return list_name in self.package_lists

    def __getitem__(self, item):
        return self.package_lists.get(item)

    def __setitem__(self, key, value):
        self.package_lists[key] = value

    def package_query(self, package, newer_only=False):
        """Search for a package in all package lists"""
        results = []
        for pl in self.package_lists.values():
            results.extend(pl.package_query(package, newer_only))
        return sorted(set(results))

    def all_packages(self):
        """return all packages in a flat list"""
        results = PackageList('all_packages')
        for pl in self.package_lists.values():
            for package in pl.all_packages():
                results.add_package(package)
        return results

    def distinct_packages(self):
        """return newest version for each package in flat list"""
        results = PackageList('all_packages')
        for pl in self.package_lists.values():
            for package in pl.distinct_packages():
                results.add_package(package)
        return results


class PackageList(object):
    """Store packages and versions from a single source"""
    def __init__(self, name):
        # data contains a hash for fast lookup
        self.data = {}
        self.name = name

    def __iter__(self):
        return self.all_packages().__iter__()

    def __len__(self):
        return len(self.all_packages())

    def __contains__(self, other):
        return other.name in self.data

    def __sub__(self, other):
        """subtract another package list from this one
           returns a new package list with the result"""
        result_packages = set(self) - set(other)
        new_list = PackageList("%s - %s" % (self.name, other.name))
        for package in result_packages:
            new_list.add_package(package)
        return new_list

    def __add__(self, other):
        """Add two package lists, return a new list"""
        new_list = PackageList("%s + %s" % (self.name, other.name))
        new_packages = set(self) + set(other)
        for package in new_packages:
            new_list.add_package(package)

    def add_package(self, package):
        """Add a package to this package list, if its not already present"""
        if package.name not in self.data:
            self.data[package.name] = {}
        versions = self.data[package.name]

        if package.version not in versions:
            versions[package.version] = package

        package.last_list = self.name
        LOGGER.debug('adding %s to %s' % (package, self.name))

    def package_query(self, package, newer_only=False):
        """Search for a package in this package list
           if package.version is None, multiple versions may be returned
           if newer_only is true, then only versions newer than the specified
                version will be returned
           Always returns a list.
        """

        if package.name not in self.data:
            return []

        versions = sorted(set(self.data[package.name].values()))
        if package.version is None:
            return versions
        else:
            if not newer_only:
                if package.version in self.data[package.name]:
                    return [self.data[package.name].get(package.version)]
                else:
                    return []
            else:
                return [p for p in versions if p > package]

    def all_packages(self):
        """return flat list of all packages"""
        packages = []
        for versions in self.data.values():
            packages.extend(versions.values())
        return list(set(packages))

    def distinct_packages(self):
        """return flat list of newest version of each package"""
        packages = []
        for versions in self.data.values():
            packages.append(sorted(versions.values())[-1])
        return list(set(packages))


class Package(object):
    """Represents a single package"""

    def __init__(self, name, version=None, source=None):
        self.name = name
        self.version = version
        self.source = source

    def __eq__(self, other):
        """Packages are 'equal' if there name is the same"""
        return self.name == other.name and self.version == other.version

    def __hash__(self):
        """hash matches equality by hashing name and version"""
        return hash(self.name) ^ hash(str(self.version))

    def __cmp__(self, other):
        """ packages are sorted by name then version """
        if self.name == other.name:
            return apt_pkg.version_compare(self.version, other.version)
        else:
            return self.name.__cmp__(other.name)

    def __repr__(self):
        return "Package: %s, Version: %s" % (self.name, self.version)


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

    def mirror_create(self, name, architecture, dist="./",
                      component="", url=None, key_id=None, key_url=None,
                      ppa=None):
        """Create a repo mirror via aptly.
        These are metadata only, packages arent pulled till update
        """
        # check mirror doesn't exist
        if name in self.mirror_list():
            raise ValueError("a mirror with name %(name)s already exists"
                             % name)

        # check we have a key for the mirror
        if key_id is None and key_url is None:
            raise ValueError("mirror create requires key_id, key_url")

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

        if ppa:
            self.run("mirror create -architectures %(arch)s %(name)s "
                     "ppa:%(ppa)s" % {'arch': architecture,
                                      'name': name,
                                      'ppa': ppa})
        else:
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

    def mirror_get_packages(self, name, arch):
        """Get list of packages from a mirror"""
        lines = self.run("mirror show -with-packages %(name)s"
                         % {'name': name}).splitlines()

        packages = self.parse_aptly_package_list(lines, source=name,
                                                 arch=arch)

        LOGGER.debug("Found %(num_packages)s packages for mirror %(name)s"
                     % {'num_packages': len(packages),
                        'name': name})
        return packages

    def parse_aptly_package_list(self, lines, source=None, arch=None):
        """Generate a PackageList() from aptly package list output"""

        # match package list from aptly ... show -with-packages name
        line_re = re.compile('\s{2,}(?P<name>[^_]*)_(?P<version>[^_]*)'
                             '_(?P<arch>[^_]*)')

        package_list = PackageList(name=source)
        for line in lines:
            match = line_re.match(line)
            if match:
                gd = match.groupdict()
                if gd['arch'] in [arch, 'all', None]:
                    package_list.add_package(Package(name=gd['name'],
                                             version=gd['version'],
                                             source=source))
                else:
                    LOGGER.debug('rejecting package %s %s due to invalid '
                                 'architecture %s' % (gd['name'],
                                                      gd['version'],
                                                      gd['arch']))
        return package_list

    def repo_list(self):
        """Get list of repos known to aptly"""
        return self.run("-raw repo list").splitlines()

    def repo_create(self, name):
        """Create an aptly repo"""
        self.run("repo create %(name)s" % {'name': name})

    def repo_get_packages(self, name):
        """Generate PackageList representing an atply repo"""
        lines = self.run('repo show -with-packages %(name)s'
                         % {'name': name})

        return self.parse_aptly_package_list(lines, source=name)

    def package_query(self, package):
        """return aptly query string for a package name & version"""
        return '"%(name)s (=%(version)s)"' % {'name': package.name,
                                              'version': package.version}

    def repo_import_package(self, mirror, repo, package):
        """Pull a package from a mirror into a repo"""
        self.run('repo import %(mirror)s %(repo)s %(query)s'
                 % {'mirror': mirror,
                    'repo': repo,
                    'query': self.package_query(
                        package.name, package.version)
                    }, shell=True)

    def repo_import_packages(self, repo, package_list, batch_size=200):
        """Batch import packages from a mirror into a repo"""
        packages = package_list.all_packages()
        packages_copy = copy.deepcopy(packages)
        packages_reconstruct = []
        LOGGER.info('importing %s packages from %s' % (len(packages),
                                                       package_list.name))
        while packages:
            batch = packages[:batch_size]
            packages_reconstruct.extend(batch)
            if not batch:
                break
            packages = packages[batch_size:]
            query_string = " ".join([self.package_query(p) for p in batch])
            self.run('repo import %(mirror)s %(repo)s %(query)s'
                     % {'mirror': package_list.name,
                        'repo': repo,
                        'query': query_string},
                     shell=True)

        assert packages_reconstruct == packages_copy

    def repo_publish(self, name):
        """Create on disk distribution metata for an aptly internal repo"""
        self.run('publish repo -distribution %(name)s %(name)s'
                 % {'name': name})

        LOGGER.info("Published repo %(name)s" % {'name': name})

    def snapshot_list(self):
        """List reposnapshots known to aptly"""
        self.run("-raw snapshot list").splitlines()

    def snapshot_create(self, name):
        """Create an empty aptly snapshot"""
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
        # needed in order to use apt_pkg.version_compare
        apt_pkg.init()

    def ensure_mirrors(self, required_mirrors):
        """ Check mirrors list, create any that are missing"""
        current_mirrors = self.aptly.mirror_list()
        self.mirrors = PackageStore()
        for required_mirror in required_mirrors:
            # Create mirror if necessary
            mirror_name = required_mirror['name']
            if mirror_name not in current_mirrors:
                required_mirror['architecture'] =\
                    self.config['config']['architecture']
                self.aptly.mirror_create(**required_mirror)

            # Store list of available packages for each mirror
            self.aptly.mirror_update(mirror_name)
            self.mirrors[mirror_name] = \
                self.aptly.mirror_get_packages(
                    mirror_name,
                    self.config['config']['architecture'])

    def packages_from_config(self):
        """get list of required packages from config
        """
        pl = PackageList(name='config')
        for name, version in self.config['packages'].iteritems():
            pl.add_package(Package(name=name, version=version,
                                   source='config'))
        return pl

    def ensure_packages(self, dist_name):
        """Add all packages from config file to repo dist_name"""

        # convert name: version dict to [(name,version),..]
        required_packages = self.packages_from_config()
        repo_packages = self.aptly.repo_get_packages(dist_name)

        # packages that aren't in this repo already so need to be added
        missing_packages = required_packages - repo_packages

        LOGGER.debug("Packages to add: %s" % missing_packages)

        # list of packages we don't find in any upstreams
        unavailable_packages = PackageList('unavailable')

        # map of mirror to package list for found packages
        packages_to_import = PackageStore()
        for package in missing_packages:

            result = self.mirrors.package_query(package)
            if not result:
                unavailable_packages.add_package(package)
                LOGGER.debug("Failed to find package %(name)s %(version)s"
                             % {'name': package.name,
                                'version': package.version})
            else:
                package = result[0]
                if package.source not in packages_to_import:
                    packages_to_import[package.source] = \
                        PackageList(package.source)
                packages_to_import[package.source].add_package(package)
                LOGGER.debug("Found  %(pname)s in %(mname)s"
                             % {'pname': package, 'mname': package.source})

        # Batch import all the packages that are known to be available
        for package_list in packages_to_import:
            self.aptly.repo_import_packages(dist_name, package_list)

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
        self.ensure_mirrors(copy.deepcopy(self.config['upstream_repos']))
        self.aptly.repo_create(dist_name)
        unavailable_packages = self.ensure_packages(dist_name)

        if unavailable_packages:
            LOGGER.warning("The following packages are not available")
            for package in unavailable_packages:
                LOGGER.warning("Not Found: %(package)s"
                               % {'package': package})

        self.aptly.repo_publish(dist_name)

    def add_package_to_config(self):
        """ Add a package to the supplied config file"""
        self.config['packages'][self.args.name] = self.args.version

    def delete_package_from_config(self):
        """ Remove a package from the supplied config file"""
        del self.config['packages'][self.args.name]

    def list_upstream_packages(self):
        self.ensure_mirrors(self.config['upstream_repos'])
        for package in self.mirrors.all_packages():
            print "%(mirror_name)s,%(package)s"\
                % {'mirror_name': package.source,
                   'package_name': package}

    def check_for_new_and_updated(self):
        """Check for new and updated packages print them and optionally
           generate a new config file"""
        self.ensure_mirrors(self.config['upstream_repos'])

        # Count updated packages
        package_updates = 0
        config_packages = self.packages_from_config()

        # Itterate over packages in config and check for newer versions.
        for package in config_packages:
            updates = self.mirrors.package_query(package, newer_only=True)
            if updates:
                self.config['packages'][package.name] = updates[-1].version
                package_updates += 1
                LOGGER.info("Package %(name)s Config Version: %(current)s"
                            " Updates: %(updates)s"
                            % {'name': package.name,
                                'current': package.version,
                                'updates': [p.version for p in updates]})

        # Find packages that are available upstream but not in the config file
        all_upstream_packages = self.mirrors.all_packages()
        new_packages = PackageList('new_packages')
        for package in all_upstream_packages:
            if package not in config_packages:
                new_packages.add_package(package)
                LOGGER.info("New %s" % (package))
                self.config['packages'][package.name] = package.version

        # write new config file with updated versions and new packages
        # if requested
        if 'new_config_path' in self.args:
            self.config.write(self.args.new_config_path)
            LOGGER.info("updated config containing %s packages written to %s"
                        % (len(self.config['packages']),
                           self.args.new_config_path))

        LOGGER.info("Input Config Packages: %s, Upstream Packages: %s, "
                    "New Packages: %s, Package Updates: %s" %
                    (len(config_packages),
                     len(self.mirrors.distinct_packages()),
                     len(new_packages.distinct_packages()), package_updates))


def main(args):
    parser = argparse.ArgumentParser()

    # arguments that are relevant to all subcommands
    parser.add_argument('config_path')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="more logging")

    # Add subparsers for subcommands
    subparsers = parser.add_subparsers()

    # dfc = distribution from config
    parser_dfc = subparsers.add_parser(
        'dist_from_config',
        help="Create distribution from config file")
    parser_dfc.add_argument('dist_name', help="must be unique")
    parser_dfc.set_defaults(func="dfc")

    # subcommand to add packages to config
    parser_add_package = subparsers.add_parser(
        'add_package_to_config',
        help="Add a package to the config file")
    parser_add_package.add_argument('name')
    parser_add_package.add_argument('version')
    parser_add_package.set_defaults(func="add_package")

    # subcommand to remove packages from config
    parser_del_package = subparsers.add_parser(
        'delete_package_from_config',
        help="Delete package from config file")
    parser_del_package.add_argument('name')
    parser_del_package.set_defaults(func="del_package")

    # List all packages available in configured upstreams
    parser_list_upstream_pkgs = subparsers.add_parser(
        'list_upstream_packages',
        help="List all packages from upstreams in config file")
    parser_list_upstream_pkgs.set_defaults(func='list_upstream')

    # List all packages in the package list that have updates available
    parser_list_upstream_pkgs = subparsers.add_parser(
        'list_package_updates',
        help="List packages which have newer versions available upstream"
             " than listed in the config file")
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
    parser_generate_updated_config.add_argument(
        '--add-new', dest="add_new", action='store_true',
        help="Add packages available upstream but not listed in"
        " the specified config file to the new config file")
    parser_generate_updated_config.set_defaults(func='list_updates')

    args = parser.parse_args(args=args[1:])

    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)

    apt_pkg.init()  # Only needs to be done once to read the apt configs
    ao = AptlyOrechestrator(args)
    # Each subparser sets the func arg, call the appropriate function
    {'dfc': ao.create_dist_from_package_list,
     'add_package': ao.add_package_to_config,
     'del_package': ao.delete_package_from_config,
     'list_upstream': ao.list_upstream_packages,
     'list_updates': ao.check_for_new_and_updated}[args.func]()

if __name__ == "__main__":
    main(sys.argv)
