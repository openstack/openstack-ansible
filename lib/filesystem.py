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
import tarfile

logger = logging.getLogger('osa-inventory')

INVENTORY_FILENAME = 'openstack_inventory.json'


def _get_search_paths(preferred_path=None, suffix=None):
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


def file_find(filename, preferred_path=None, pass_exception=False):
    """Return the path to a file, or False if no file is found.

    If no file is found and pass_exception is True, the system will exit.
    The file lookup will be done in the following directories:
      ``preferred_path`` [Optional]
      /etc/openstack_deploy/
      $(pwd)/openstack_deploy/

    :param filename: ``str``  Name of the file to find
    :param preferred_path: ``str`` Additional directory to look in FIRST
    :param pass_exception: ``bool`` Should a SystemExit be raised if the file
      is not found
    """

    search_paths = _get_search_paths(preferred_path, suffix=filename)

    for file_candidate in search_paths:
        if os.path.isfile(file_candidate):
            return file_candidate
    else:
        if pass_exception is False:
            raise SystemExit('No file found at: {}'.format(search_paths))
        else:
            return False


def make_backup(config_path, inventory_file_path):
    # Create a backup of all previous inventory files as a tar archive
    inventory_backup_file = os.path.join(
        config_path,
        'backup_openstack_inventory.tar'
    )
    with tarfile.open(inventory_backup_file, 'a') as tar:
        basename = os.path.basename(inventory_file_path)
        backup_name = get_backup_name(basename)
        tar.add(inventory_file_path, arcname=backup_name)
    logger.debug("Backup written to {}".format(inventory_backup_file))


def get_backup_name(basename):
    utctime = datetime.datetime.utcnow()
    utctime = utctime.strftime("%Y%m%d_%H%M%S")
    return '{}-{}.json'.format(basename, utctime)


def load_from_json(filename, preferred_path=None, pass_exception=False):
    """Return a dictionary found in a given file

    :param filename: ``str``  Name of the file to read from
    :param preferred_path: ``str``  Path to the json file to try FIRST
    :param pass_exception: ``bool`` Should a SystemExit be raised if the file
        is not found
    :return ``(dict, str)`` Dictionary describing the JSON file contents or
        False, and the fully resolved file name loaded or None
    """

    target_file = file_find(filename, preferred_path, pass_exception)
    dictionary = False
    if target_file is not False:
        with open(target_file, 'rb') as f_handle:
            dictionary = json.loads(f_handle.read())

    return dictionary, target_file


def load_inventory(preferred_path=None, default_inv=None):
    """Create an inventory dictionary from the given source file or a default
        inventory. If an inventory is found then a backup tarball is created
        as well.

    :param preferred_path: ``str`` Path to the inventory directory to try FIRST
    :param default_inv: ``dict`` Default inventory skeleton

    :return: ``dict`` A dictionary found or ``default_inv``
    """

    inventory, file_loaded = load_from_json(INVENTORY_FILENAME, preferred_path,
                                            pass_exception=True)
    if inventory is not False:
        logger.debug("Loaded existing inventory from {}".format(file_loaded))
        make_backup(preferred_path, file_loaded)
    else:
        logger.debug("No existing inventory, created fresh skeleton.")
        inventory = copy.deepcopy(default_inv)

    return inventory


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
        f.write(inventory_json)
        logger.info("Inventory written")
