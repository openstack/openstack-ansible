#!/usr/bin/env bash
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

# Script for running gate tests. Initially very sparse
# additional projects and test types will be added over time.

set -e
set -x

API_TESTS="identity"

pushd /opt/tempest_*
source /root/openrc

for project in $API_TESTS
do
  echo "Running API tests for $project"
  nosetests -v tempest/api/$project
done

popd
echo "GATE PASS"

