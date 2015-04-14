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


# Install the development requirements.
if [ -f "dev-requirements.txt" ]; then
  pip2 install -r dev-requirements.txt || pip install -r dev-requirements.txt
else
  pip2 install ansible-lint || pip install ansible-lint
fi

# Run hacking/flake8 check for all python files
# Ignores the following rules due to how ansible modules work in general
#     F403 'from ansible.module_utils.basic import *' used; unable to detect undefined names
#     H303  No wildcard (*) import.
flake8 --ignore=F403,H303 $(grep -rln -e '^#!/usr/bin/env python' -e '^#!/bin/python' * )


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
