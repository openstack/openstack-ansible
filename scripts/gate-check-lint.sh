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

BOOTSTRAP_ANSIBLE=${BOOTSTRAP_ANSIBLE:-"yes"}
PLAYBOOK_PATH=${PLAYBOOK_PATH:-"rpc_deployment/playbooks"}

## Functions -----------------------------------------------------------------

info_block "Checking for required libraries." || source $(dirname ${0})/scripts-library.sh

## Main ----------------------------------------------------------------------

# Enable logging of all commands executed
set -x

# Bootstrap ansible if required
if [ "${BOOTSTRAP_ANSIBLE}" == "yes" ]; then
  source $(dirname ${0})/bootstrap-ansible.sh
fi

# Check whether pip or pip2 is available
if ! ( which pip > /dev/null && which pip2 > /dev/null ); then
  info_block "ERROR: Please install pip before proceeding."
  exit 1
fi

# Check whether ansible-playbook is available
if ! which ansible-playbook > /dev/null; then
  info_block "ERROR: Please install ansible before proceeding."
  exit 1
fi

# Install the development requirements
if [ -f dev-requirements.txt ]; then
  pip2 install -r dev-requirements.txt || pip install -r dev-requirements.txt
else
  pip2 install ansible-lint || pip install ansible-lint
fi

# Perform our simple sanity checks
echo -e '[all]\nlocalhost ansible_connection=local' | tee local_only_inventory

# Do a basic syntax check on all playbooks and roles
info_block "Running Syntax Check"
ansible-playbook -i local_only_inventory --syntax-check \
                 $(find ${PLAYBOOK_PATH} -type f -name "*.yml" \
                        ! -name "os-service-config-update.yml" \
                        ! -name "host-network-setup.yml")

# Perform a lint check on all playbooks and roles
info_block "Running Lint Check"
ansible-lint --version
ansible-lint $(find ${PLAYBOOK_PATH} -type f -name "*.yml" \
                    ! -name "os-service-config-update.yml" \
                    ! -name "host-network-setup.yml")
