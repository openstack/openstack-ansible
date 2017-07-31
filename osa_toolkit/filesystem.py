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
# (c) 2015, Major Hayden <major@mhtx.net>
#

import copy
import datetime
import json
import logging
import os
from osa_toolkit import dictutils as du
import tarfile
import yaml


logger = logging.getLogger('osa-inventory')

INVENTORY_FILENAME = 'openstack_inventory.json'


class MissingDataSource(Exception):
    def __init__(self, *sources):
        self.sources = sources

        error_msg = "Could not read data sources: '{sources}'."
        self.message = error_msg.format(sources=self.sources)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


def _get_search_paths(preferred_path=None, suffix=None):
    """Return a list of search paths, including the standard location

    :param preferred_path: A search path to prefer to a standard location
    :param suffix: Appended to the search paths, e.g. subdirectory or filename
    :return: ``(list)`` Path strings to search
    """

    search_paths = [
        os.path.join(
            '/etc', 'openstack_deploy'
        ),
    ]
    if preferred_path is not None:
        search_paths.insert(0, os.path.expanduser(preferred_path))

    if suffix:
        search_paths = [os.path.join(p, suffix) for p in search_paths]

    return search_paths


def file_find(filename, preferred_path=None, raise_if_missing=True):
    """Return the path to an existing file, or False if no file is found.

    If no file is found and raise_if_missing is True, MissingDataSource
        will be raised.

    The file lookup will be done in the following directories:
      * ``preferred_path`` [Optional]
      * ``/etc/openstack_deploy/``

    :param filename: ``str``  Name of the file to find
    :param preferred_path: ``str`` Additional directory to look in FIRST
    :param raise_if_missing: ``bool`` Should a MissingDataSource be raised if
        the file is not found
    """

    search_paths = _get_search_paths(preferred_path, suffix=filename)

    for file_candidate in search_paths:
        if os.path.isfile(file_candidate):
            return file_candidate

    # The file was not found
    if raise_if_missing:
        raise MissingDataSource(search_paths)
    else:
        return False


def dir_find(preferred_path=None, suffix=None, raise_if_missing=True):
    """Return the path to the user configuration files.

    If no directory is found the system will exit.

    The lookup will be done in the following directories:

      * ``preferred_path`` [Optional]
      * ``/etc/openstack_deploy/``

    :param preferred_path: ``str`` Additional directory to look in FIRST
    :param suffix: ``str`` Name of a subdirectory to find under standard paths
    :param raise_if_missing: ``bool`` Should a MissingDataSource be raised if
        the directory is not found.
    """
    search_paths = _get_search_paths(preferred_path, suffix)

    for f in search_paths:
        if os.path.isdir(f):
            return f

    # The directory was not found
    if raise_if_missing:
        raise MissingDataSource(search_paths)
    else:
        return False


def _extra_config(user_defined_config, base_dir):
    """Discover new items in any extra directories and add the new values.

    :param user_defined_config: ``dict``
    :param base_dir: ``str``
    """
    for root_dir, _, files in os.walk(base_dir):
        for name in files:
            if name.endswith(('.yml', '.yaml')):
                with open(os.path.join(root_dir, name), 'rb') as f:
                    du.merge_dict(
                        user_defined_config,
                        yaml.safe_load(f.read()) or {}
                    )
                    logger.debug("Merged overrides from file {}".format(name))


def _make_backup(backup_path, source_file_path):
    """Create a backup of all previous inventory files as a tar archive

    :param backup_path: where to store the backup file
    :param source_file_path: path of file to backup
    :return:
    """

    inventory_backup_file = os.path.join(
        backup_path,
        'backup_openstack_inventory.tar'
    )
    with tarfile.open(inventory_backup_file, 'a') as tar:
        basename = os.path.basename(source_file_path)
        backup_name = _get_backup_name(basename)
        tar.add(source_file_path, arcname=backup_name)
    logger.debug("Backup written to {}".format(inventory_backup_file))


def _get_backup_name(basename):
    """Return a name for a backup file based on the time

    :param basename: serves as prefix for the return value
    :return: a name for a backup file based on current time
    """

    utctime = datetime.datetime.utcnow()
    utctime = utctime.strftime("%Y%m%d_%H%M%S")
    return '{}-{}.json'.format(basename, utctime)


def write_hostnames(save_path, hostnames_ips):
    """Write a list of all hosts and their given IP addresses

    NOTE: the file is saved in json format to a file with the name
    ``openstack_hostnames_ips.yml``

    :param save_path: path to save the file to, will use default location if
        None or an invalid path is provided
    :param hostnames_ips: the list of all hosts and their IP addresses
    """

    file_path = dir_find(save_path)
    hostnames_ip_file = os.path.join(file_path, 'openstack_hostnames_ips.yml')

    with open(hostnames_ip_file, 'wb') as f:
        f.write(
            json.dumps(
                hostnames_ips,
                indent=4,
                separators=(',', ': '),
                sort_keys=True
            ).encode('ascii')
        )


def _load_from_json(filename, preferred_path=None, raise_if_missing=True):
    """Return a dictionary found in json format in a given file

    :param filename: ``str``  Name of the file to read from
    :param preferred_path: ``str``  Path to the json file to try FIRST
    :param raise_if_missing: ``bool`` Should a MissingDataSource be raised if
        the file is not found
    :return ``(dict, str)`` Dictionary describing the JSON file contents or
        False, and the fully resolved file name loaded or None
    """

    target_file = file_find(filename, preferred_path, raise_if_missing)
    dictionary = False
    if target_file is not False:
        with open(target_file, 'rb') as f_handle:
            dictionary = json.loads(f_handle.read().decode('ascii'))

    return dictionary, target_file


def load_inventory(preferred_path=None, default_inv=None, filename=None):
    """Create an inventory dictionary from the given source file or a default
        inventory. If an inventory is found then a backup tarball is created
        as well.

    :param preferred_path: ``str`` Path to the inventory directory to try FIRST
    :param default_inv: ``dict`` Default inventory skeleton

    :return: ``(dict, str)`` Dictionary describing the JSON file contents or
        ``default_inv``, and the directory from which the inventory was loaded
        or should have been loaded from.
    """

    if filename:
        inv_fn = filename
    else:
        inv_fn = INVENTORY_FILENAME

    inventory, file_loaded = _load_from_json(inv_fn, preferred_path,
                                            raise_if_missing=False)
    if file_loaded is not False:
        load_path = os.path.dirname(file_loaded)
    else:
        load_path = dir_find(preferred_path)

    if inventory is not False:
        logger.debug("Loaded existing inventory from {}".format(file_loaded))
        _make_backup(load_path, file_loaded)
    else:
        logger.debug("No existing inventory, created fresh skeleton.")
        inventory = copy.deepcopy(default_inv)

    return inventory, load_path


def save_inventory(inventory_json, save_path):
    """Save an inventory dictionary

    :param inventory_json: ``str`` String of JSON formatted inventory to store
    :param save_path: ``str`` Path of the directory to save to
    """

    if INVENTORY_FILENAME == save_path:
        inventory_file = file_find(save_path)
    else:
        inventory_file = os.path.join(save_path, INVENTORY_FILENAME)
    with open(inventory_file, 'wb') as f:
        f.write(inventory_json.encode('ascii'))
        logger.info("Inventory written")


def load_environment(config_path, environment):
    """Create an environment dictionary from config files

    :param config_path: ``str`` path where the environment files are kept
    :param environment: ``dict`` dictionary to populate with environment data
    """

    # Load all YAML files found in the env.d directory
    env_plugins = dir_find(config_path, 'env.d', raise_if_missing=False)

    if env_plugins is not False:
        _extra_config(user_defined_config=environment, base_dir=env_plugins)
        logger.debug("Loaded environment from {}".format(config_path))

    return environment


def load_user_configuration(config_path=None):
    """Create a user configuration dictionary from config files

    :param config_path: ``str`` path where the configuration files are kept
    """

    user_defined_config = dict()

    # Load the user defined configuration file
    user_config_file = file_find('openstack_user_config.yml',
                                 preferred_path=config_path,
                                 raise_if_missing=False)
    if user_config_file is not False:
        with open(user_config_file, 'rb') as f:
            user_defined_config.update(yaml.safe_load(f.read()) or {})

    # Load anything in a conf.d directory if found
    base_dir = dir_find(config_path, 'conf.d', raise_if_missing=False)
    if base_dir is not False:
        _extra_config(user_defined_config, base_dir)

    # Exit if no user_config was found and loaded
    if not user_defined_config:
        raise MissingDataSource(_get_search_paths(config_path) +
                                _get_search_paths(config_path, 'conf.d'))

    logger.debug("User configuration loaded from: {}".format(user_config_file))
    return user_defined_config
