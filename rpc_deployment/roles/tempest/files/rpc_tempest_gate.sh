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
testr_ouput_lines=${testr_output_lines:-100}
RUN_TEMPEST_OPTS=${RUN_TEMPEST_OPTS:-''}
TESTR_OPTS=${TESTR_OPTS:-''}


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

exit_msg(){
  echo $1
  exit $2
}


# -------------------- Main -------------------------

available_test_lists=$(compgen -A function|sed -n '/^gen_test_list_/s/gen_test_list_//p')

grep $test_list_name <<<$available_test_lists ||\
  exit_msg "$test_list_name is not a valid test list, available test lists: $available_test_lists" 1

# work in tempest directory
pushd /opt/tempest_*

# read creds into environment
source /root/openrc

# create testr repo - required for testr to do anything
testr init &>/dev/null ||:

# Get list of available tests.
# lines 1-$testr_ouput_lines are output to stdout, all lines are written to
# full_test_list.
set -o pipefail
testr list-tests |tee >(sed -n 1,${testr_ouput_lines}p) >full_test_list ||\
  exit_msg "Failed to generate test list" $?
set +o pipefail

# Check the full test list is not empty
[[ -s full_test_list ]] || exit_msg "No tests found" 1

# Write filter test list using selected function. The full test list is
# pre-filtered to only include test lines, this saves adding that filter to
# every test list function.
grep '^tempest\.' < full_test_list | gen_test_list_${test_list_name} > test_list

# Check the filtered test list is not empty
[[ -s test_list ]] || exit_msg "No tests remain after filtering" 1

test_list_summary="${test_list_name} ($(wc -l <test_list) tests)"

echo "Using test list $test_list_summary"

# execute chosen tests with pretty output
./run_tempest.sh --no-virtual-env ${RUN_TEMPEST_OPTS} -- --load-list test_list ${TESTR_OPTS};
result=$?
popd

if [[ $result == 0 ]]; then
  echo "TEMPEST PASS $test_list_summary"
else
  echo "TEMPEST FAIL $test_list_summary"
fi

exit $result
