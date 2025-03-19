#!/opt/ansible-runtime/bin/python
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

import os
import sys

try:
    from osa_toolkit import generate
except ImportError:
    current_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    lib_path = os.path.join(current_path, '..')
    sys.path.append(lib_path)
    from osa_toolkit import generate


def main():
    generate.main()


if __name__ == '__main__':
    main()
