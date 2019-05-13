#!/usr/bin/env bash
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

## Shell Opts ----------------------------------------------------------------
set -e -u -x

## Variables -----------------------------------------------------------------
# Extra options to pass to the AIO bootstrap process
export BOOTSTRAP_OPTS=${BOOTSTRAP_OPTS:-''}

# Store the clone repo root location
export OSA_CLONE_DIR="${OSA_CLONE_DIR:-$(readlink -f $(dirname $0)/..)}"

# This script should be executed from the root directory of the cloned repo
cd "$(dirname "${0}")/.."

## Main ----------------------------------------------------------------------

# When running in the gate, enable data device detection in the bootstrap
# role. This is needed on RAX nodepool instances because the root data disk
# is too small for an OSA AIO, and a second data disk is attached which must
# be formatted and used.
if [[ -d '/etc/nodepool' ]]; then
  export BOOTSTRAP_HOST_DETECT_DATA_DISK=true
fi

# Ensure that some of the wrapper options are overridden
# to prevent interference with the AIO bootstrap.
export ANSIBLE_INVENTORY="${OSA_CLONE_DIR}/tests/test-inventory.ini"
export ANSIBLE_VARS_PLUGINS="/dev/null"
export HOST_VARS_PATH="/dev/null"
export GROUP_VARS_PATH="/dev/null"

# Run AIO bootstrap playbook
pushd tests
  if [ -z "${BOOTSTRAP_OPTS}" ]; then
    ansible-playbook bootstrap-aio.yml
  else
    export BOOTSTRAP_OPTS_ITEMS=''
    for BOOTSTRAP_OPT in ${BOOTSTRAP_OPTS}; do
      BOOTSTRAP_OPTS_ITEMS=${BOOTSTRAP_OPTS_ITEMS}"-e "${BOOTSTRAP_OPT}" "
    done
    ansible-playbook bootstrap-aio.yml \
                     ${BOOTSTRAP_OPTS_ITEMS}
  fi
popd

# Now unset the env var overrides so that the defaults work again
unset ANSIBLE_INVENTORY
unset ANSIBLE_VARS_PLUGINS
unset HOST_VARS_PATH
unset GROUP_VARS_PATH

