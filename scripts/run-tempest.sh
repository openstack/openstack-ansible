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

set -e -u -v +x

## Variables -----------------------------------------------------------------

TEMPEST_SCRIPT_PATH=${TEMPEST_SCRIPT_PATH:-/root/rpc_tempest_gate.sh}
TEMPEST_SCRIPT_PARAMETERS=${TEMPEST_SCRIPT_PARAMETERS:-commit_aio}
CONFIG_PREFIX=${CONFIG_PREFIX:-"rpc"}
PLAYBOOK_DIRECTORY_PARENT=${PLAYBOOK_DIRECTORY_PARENT:-"${CONFIG_PREFIX}_deployment"}

## Functions -----------------------------------------------------------------

info_block "Checking for required libraries." || source $(dirname ${0})/scripts-library.sh

## Main ----------------------------------------------------------------------

# Check that ansible has been installed
if ! which ansible > /dev/null 2>&1; then
  info_block "ERROR: Please ensure that ansible is installed."
  exit 1
fi

# Check that we are in the root path of the cloned repo
if [ ! -d "etc" -a ! -d "scripts" -a ! -f "requirements.txt" ]; then
  info_block "ERROR: Please execute this script from the root directory of the cloned source code."
  exit 1
fi

pushd ${PLAYBOOK_DIRECTORY_PARENT}
  # Check that there are utility containers
  if ! ansible 'utility[0]' --list-hosts; then
    info_block "ERROR: No utility containers have been deployed in your environment."
    exit 99
  fi

  # Check that the utility container already has the required tempest script deployed
  if ! ansible 'utility[0]' -m shell -a "ls -al ${TEMPEST_SCRIPT_PATH}"; then
    info_block "ERROR: Please execute the 'os-tempest-install.yml' playbook prior to this script."
    exit 99
  fi

  # Execute the tempest tests
  info_block "Executing tempest tests"
  ansible 'utility[0]' -m shell -a "${TEMPEST_SCRIPT_PATH} ${TEMPEST_SCRIPT_PARAMETERS}"
popd
