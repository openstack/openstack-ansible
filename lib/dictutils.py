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


def recursive_list_removal(inventory, purge_list):
    """Remove items from a list.

    Keyword arguments:
    inventory -- inventory dictionary
    purge_list -- list of items to remove
    """
    for item in purge_list:
        for _item in inventory:
            if item == _item:
                inventory.pop(inventory.index(item))


def recursive_dict_removal(inventory, purge_list):
    """Remove items from a dictionary.

    Keyword arguments:
    inventory -- inventory dictionary
    purge_list -- list of items to remove
    """
    for key, value in inventory.iteritems():
        if isinstance(value, dict):
            for _key, _value in value.iteritems():
                if isinstance(_value, dict):
                    for item in purge_list:
                        if item in _value:
                            del(_value[item])
                elif isinstance(_value, list):
                    recursive_list_removal(_value, purge_list)
        elif isinstance(value, list):
            recursive_list_removal(value, purge_list)
