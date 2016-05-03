#!/usr/bin/env python
# Copyright 2016, Rackspace US, Inc.
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

# This file is used to generate a ReStructured Text table suitable for
# documentating the variable name changes. Its contents are meant to be
# inserted into doc/source/upgrade-guide/scripts.rst.

# As of right now, running this script and inserting the output into
# the file is manual.

from migrate_openstack_vars import VAR_MAPPINGS

# Print old/new values in each row, right aligned.
row_format = "| {:>40} | {:>40} |"

# For the line separators, move the dividing '+' sign over so it's aligned
# with the '|' in the rows.
divider_format = "+-{:->42}---{:->40}"
header_divide_format = "+={:=>42}==={:=>40}"


# Header info
print(divider_format.format('+', '+'))
print(row_format.format('Old Value', 'New Value'))
print(header_divide_format.format('+', '+'))

# If we just used the items method, we'd get an unsorted output.
keys = VAR_MAPPINGS.keys()
keys.sort()

for key in keys:
    print(row_format.format(key, VAR_MAPPINGS[key]))
    print(divider_format.format('+', '+'))
