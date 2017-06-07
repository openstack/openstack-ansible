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


def merge_dict(base_items, new_items):
    """Recursively merge new_items into some base_items.

    If an empty dictionary is provided as a new value, it will
    completely replace the existing dictionary.

    :param base_items: ``dict``
    :param new_items: ``dict``
    :return dictionary:
    """
    for key, value in new_items.items():
        if isinstance(value, dict) and value:
            base_merge = merge_dict(base_items.get(key, {}), value)
            base_items[key] = base_merge
        else:
            base_items[key] = new_items[key]
    return base_items


def append_if(array, item):
    """Append an ``item`` to an ``array`` if its not already in it.

    :param array: ``list``  List object to append to
    :param item: ``object``  Object to append to the list
    :returns bool:  Flag indicating whether the append happened (True)
        or not (False)
    """
    if item not in array:
        array.append(item)
        return True
    return False


def recursive_list_removal(base_list, purge_list):
    """Remove items from a list.

    If base_list and purge_list resolve to the same list in memory,
    only the first item will be removed due to Python's handling of mutation
    during iteration.

    :param base_list: ``list`` List representing base_list entries
    :param purge_list: ``list`` List of items to remove
    """
    for item in purge_list:
        for _item in base_list:
            if item == _item:
                base_list.pop(base_list.index(item))


# TODO(nrb): this probably needs to be renamed, as it's not really recursive
def recursive_dict_removal(inventory, purge_list):
    """Remove items from a dictionary.

    Only items in child dictionaries and lists are removed.

    Dictionary keys can only be deleted at the 3rd level (e.g in
    inventory['top']['middle']['bottom'], only 'bottom' would be targeted by
    this function)

    :param inventory: ``dict`` Dictionary representing the inventory
    :param purge_list: ``list`` List of items to remove
    """
    for key, value in inventory.items():
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                if isinstance(child_value, dict):
                    for item in purge_list:
                        if item in child_value:
                            del(child_value[item])
                elif isinstance(child_value, list):
                    recursive_list_removal(child_value, purge_list)
        elif isinstance(value, list):
            recursive_list_removal(value, purge_list)
