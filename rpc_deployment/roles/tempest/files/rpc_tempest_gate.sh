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


# -------------------- Shell Options -------------------------
set -x


# -------------------- Parameters -------------------------
# The only parameter this script takes is the name of a test list to use:
# ./$0 <test_list_name>
#
# If a name is not supplied commit_multinode will be used.

test_list_name=${1:-commit_multinode}


# -------------------- Functions -------------------------
# Test list functions. Each tempest test scenario (eg commit gate, nightly,
# pre release) should have a function here to generate the list of tests that
# should be run. Each function takes in the full list of tempest tests and
# should output a filtered list.

gen_test_list_commit_multinode(){
  # filter test list to produce list of tests to use.
  egrep 'tempest\.api\.(identity|image|volume)'\
    |grep -vi xml \
    |grep -v compute \
    |grep -v VolumesV.ActionsTest
}

# Run smoke tests
gen_test_list_commit_aio(){
  egrep 'tempest\.scenario\.test_(minimum|swift|server)_basic(_ops)?'
}

# Run smoke tests
gen_test_list_nightly_heat_multinode(){
  grep smoke
}

# Run all tests
gen_test_list_all(){
  cat
}


# -------------------- Main -------------------------

available_test_lists=$(compgen -A function|sed -n '/^gen_test_list_/s/gen_test_list_//p')

grep $test_list_name <<<$available_test_lists || {
  echo "$test_list_name is not a valid test list, available test lists: "
  echo $available_test_lists
  exit 1
}

# work in tempest directory
pushd /opt/tempest_*

# read creds into environment
source /root/openrc

# create testr repo - required for testr to do anything
testr init &>/dev/null ||:

# Get list of available tests
testr list-tests > full_test_list

# Write filter test list using selected function
gen_test_list_$test_list_name <full_test_list >test_list

test_list_summary="${test_list_name} ($(wc -l <test_list) tests)"

echo "Using test list $test_list_summary"

# execute chosen tests with pretty output
./run_tempest.sh --no-virtual-env -- --load-list test_list;
result=$?
popd

if [[ $result == 0 ]]; then
  echo "TEMPEST PASS $test_list_summary"
else
  echo "TEMPEST FAIL $test_list_summary"
fi

exit $result
