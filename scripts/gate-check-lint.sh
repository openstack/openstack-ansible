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
set -e -u -x


## Library Check -------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh


## Main ----------------------------------------------------------------------
info_block "Running Basic Ansible Lint Check"

# next, bootstrap Ansible
source $(dirname ${0})/bootstrap-ansible.sh

# Install the development requirements.
if [ -f "dev-requirements.txt" ]; then
  pip2 install -r dev-requirements.txt || pip install -r dev-requirements.txt
else
  pip2 install ansible-lint || pip install ansible-lint
fi

# Create keys if they don't already exist.
ssh_key_create

# Perform our simple sanity checks.
pushd playbooks
  echo -e '[all]\nlocalhost ansible_connection=local' | tee local_only_inventory

  # Do a basic syntax check on all playbooks and roles.
  info_block "Running Syntax Check"
  ansible-playbook -i local_only_inventory --syntax-check *.yml --list-tasks

  # Perform a lint check on all playbooks and roles.
  info_block "Running Lint Check"
  ansible-lint --version
  ansible-lint *.yml
popd
