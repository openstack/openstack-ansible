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

## Shell Opts ----------------------------------------------------------------
set -e -u +x


## Vars ----------------------------------------------------------------------
export TEMPEST_SCRIPT_PATH=${TEMPEST_SCRIPT_PATH:-/opt/openstack_tempest_gate.sh}
## TODO(someone) this needs to be changed back to the normal tests once someone
## is able to dig into tempest/the updated/deprecated config(s). This test should
## go back to being the scenario tests.
export TEMPEST_SCRIPT_PARAMETERS=${TEMPEST_SCRIPT_PARAMETERS:-"scenario heat_api cinder_backup"}
export RUN_TEMPEST_OPTS=${RUN_TEMPEST_OPTS:-''}
export TESTR_OPTS=${TESTR_OPTS:-''}

## Library Check -------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh


## Main ----------------------------------------------------------------------
info_block "Running OpenStack Smoke Tests"

pushd playbooks
  # Check that there are utility containers
  if ! ansible 'utility[0]' --list-hosts;then
    echo -e "\nERROR: No utility containers have been deployed in your environment\n"
    exit_state 99
  fi

  # Check that the utility container already has the required tempest script deployed
  if ! ansible 'utility[0]' -m shell -a "ls -al ${TEMPEST_SCRIPT_PATH}";then
    echo -e "\nERROR: Please execute the 'os-tempest-install.yml' playbook prior to this script.\n"
    exit_state 99
  fi

  # Execute the tempest tests
  ansible 'utility[0]' -m shell -a "export RUN_TEMPEST_OPTS=${RUN_TEMPEST_OPTS}; \
                                    export TESTR_OPTS=${TESTR_OPTS}; \
                                    ${TEMPEST_SCRIPT_PATH} ${TEMPEST_SCRIPT_PARAMETERS}"
popd
