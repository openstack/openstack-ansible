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

import json
import os


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


def save_to_json(filename, dictionary):
    """Write out the given dictionary

    :param filename: ``str``  Name of the file to write to
    :param dictionary: ``dict`` A dictionary to write
    """
    target_file = file_find(filename)
    with open(target_file, 'wb') as f_handle:
        inventory_json = json.dumps(dictionary, indent=2)
        f_handle.write(inventory_json)


def load_from_json(filename):
    """Return a dictionary found in a given file

    :param filename: ``str``  Name of the file to read from
    """
    target_file = file_find(filename)
    with open(target_file, 'rb') as f_handle:
        dictionary = json.loads(f_handle.read())

    return dictionary
