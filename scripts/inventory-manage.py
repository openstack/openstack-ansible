#!/usr/bin/env python
#
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
"""Returns data about containers and groups in tabular formats."""

# NOTE(nrb/palendae): The contents of this file were moved
# to manage.py in order to facilitate importing of the python code

# This file remains for backwards compatibility
import os
import sys

cwd = os.path.abspath(os.path.dirname(__file__))
import_path = os.path.join(cwd, '..', 'osa_toolkit')
sys.path.append(import_path)

import manage

if __name__ == "__main__":
        manage.main()
