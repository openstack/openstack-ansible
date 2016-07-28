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
set -e -u

## Variables -----------------------------------------------------------------
DEPLOY_AIO=${DEPLOY_AIO:-false}
COMMAND_LOGS=${COMMAND_LOGS:-"/openstack/log/ansible_cmd_logs/"}

## Main ----------------------------------------------------------------------
function run_play_book_exit_message {
echo -e "\e[1;5;97m*** NOTICE ***\e[0m

The \"\e[1;31m${0}\e[0m\" script has exited. This script is no longer needed from now on.
If you need to re-run parts of the stack, adding new nodes to the environment,
or have encountered an error you will no longer need this application to
interact with the environment. All jobs should be executed out of the
\"\e[1;33m${PLAYBOOK_DIR}\e[0m\" directory using the \"\e[1;32mopenstack-ansible\e[0m\"
command line wrapper.

For more information about OpenStack-Ansible please review our documentation at:
  \e[1;36mhttp://docs.openstack.org/developer/openstack-ansible\e[0m

Additionally if there's ever a need for information on common operational tasks please
see the following information:
  \e[1;36mhttp://docs.openstack.org/developer/openstack-ansible/developer-docs/ops.html\e[0m


If you ever have any questions please join the community conversation on IRC at
#openstack-ansible on freenode.
"
}

function playbook_run {
  for root_include in $(awk -F'include:' '{print $2}' setup-everything.yml); do
    for include in $(awk -F'include:' '{print $2}' "${root_include}"); do
      echo "[Executing \"${include}\" playbook]"
      if [[ "${DEPLOY_AIO}" = true ]] && [[ "${include}" == "security-hardening.yml" ]]; then
        # NOTE(mattt): We have to skip V-38462 as openstack-infra are now building
        #              images with apt config Apt::Get::AllowUnauthenticated set
        #              to true.
        # NOTE(mhayden): Skipping V-38660 since it breaks the Xenial gate. The
        #                CI Xenial image has non-SNMPv3 configurations.
        install_bits "${include}" --skip-tag V-38462,V-38660
      else
        install_bits "${include}"
      fi
    done
  done
}

trap run_play_book_exit_message EXIT

info_block "Checking for required libraries." 2> /dev/null || source "$(dirname "${0}")/scripts-library.sh"

# Initiate the deployment
pushd "playbooks"
  PLAYBOOK_DIR="$(pwd)"

  # Execute setup everything
  playbook_run

  if [[ "${DEPLOY_AIO}" = true ]]; then
    # Log some data about the instance and the rest of the system
    log_instance_info

    # Log repo data
    mkdir -p "${COMMAND_LOGS}/repo_data"
    ansible 'repo_all[0]' -m raw \
                          -a 'find  /var/www/repo/os-releases -type l' \
                          -t "${COMMAND_LOGS}/repo_data"

    openstack-ansible os-tempest-install.yml
    print_report
  fi
popd
