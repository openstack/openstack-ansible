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

set -x

# work in tempest directory
pushd /opt/tempest_*

# read creds into environment
source /root/openrc

# create testr trepo - required for testr to do anything
testr init &>/dev/null ||:

# Get list of available tests
testr list-tests > full_test_list

# filter test list to produce list of tests to use.
egrep 'tempest\.api\.(identity|image|volume)' < full_test_list \
  |grep -vi xml \
  > test_list

# execute chosen tests with pretty output
./run_tempest.sh --no-virtual-env -- --load-list test_list;
result=$?
popd

if [[ $result == 0 ]]; then
  echo "GATE PASS"
else
  echo "GATE FAIL"
fi

exit $result

