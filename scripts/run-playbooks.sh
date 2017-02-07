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
PLAYBOOK_LOGS=${PLAYBOOK_LOGS:-"/openstack/log/ansible_playbooks/"}
COMMAND_LOGS=${COMMAND_LOGS:-"/openstack/log/ansible_cmd_logs/"}
ORIG_ANSIBLE_LOG_PATH=${ANSIBLE_LOG_PATH:-"/openstack/log/ansible-logging/ansible.log"}

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

function get_includes {
  /opt/ansible-runtime/bin/python <<EOC
import yaml
with open("${1}") as f:
    yaml_list = yaml.safe_load(f.read())
for item in yaml_list:
    _item = '---\n' + yaml.safe_dump([item], default_flow_style=False, width=1000)
    print(repr(_item).strip("'").strip('"'))
EOC
}

function get_include_file {
  /opt/ansible-runtime/bin/python <<EOC
import yaml
with open("${1}") as f:
    yaml_list = yaml.safe_load(f.read())
print(yaml_list[0]['include'])
EOC
}

function playbook_run {

  # First we gather facts about the hosts to populate the fact cache.
  # We can't gather the facts for all hosts yet because the containers
  # aren't built yet.
  ansible -m setup -a "gather_subset=network,hardware,virtual" hosts

  # Iterate over lines in setup-everything
  IFS=$'\n'
  COUNTER=0
  for root_include in $(get_includes setup-everything.yml); do
    echo -e "${root_include}" > root-include-playbook.yml
    root_include_file_name="$(get_include_file root-include-playbook.yml)"

    # Once setup-hosts is complete, we should gather facts for everything
    # (now including containers) so that the fact cache is complete for the
    # remainder of the run.
    if [[ "${root_include_file_name}" == "setup-infrastructure.yml" ]]; then
      ansible -m setup -a "gather_subset=network,hardware,virtual" all
    fi
    for include in $(get_includes "${root_include_file_name}"); do
      echo -e "${include}" > /tmp/include-playbook.yml
      include_file_name="$(get_include_file /tmp/include-playbook.yml)"
      include_playbook="include-playbook.yml-${include_file_name}"
      mv  /tmp/include-playbook.yml ${include_playbook}
      echo "[Executing \"${include_file_name}\" playbook]"
      # Set the playbook log path so that we can review specific execution later.
      export ANSIBLE_LOG_PATH="${PLAYBOOK_LOGS}/${COUNTER}-${include_file_name}.txt"
      let COUNTER=COUNTER+=1
        install_bits "${include_playbook}"
      # Remove the generate playbook when done with it
      rm "${include_playbook}"
    done
    # Remove the generate playbook when done with it
    rm root-include-playbook.yml
  done
  cat ${PLAYBOOK_LOGS}/* >> "${ORIG_ANSIBLE_LOG_PATH}"
}

trap run_play_book_exit_message EXIT

info_block "Checking for required libraries." 2> /dev/null || source "$(dirname "${0}")/scripts-library.sh"

# Initiate the deployment
pushd "playbooks"
  PLAYBOOK_DIR="$(pwd)"

  # Create playbook log directory
  mkdir -p "${PLAYBOOK_LOGS}"
  mkdir -p "$(dirname ${ORIG_ANSIBLE_LOG_PATH})"

  # Execute setup everything
  playbook_run

    # Log some data about the instance and the rest of the system
    log_instance_info

    # Log repo data
    mkdir -p "${COMMAND_LOGS}/repo_data"
    ansible 'repo_all[0]' -m raw \
                          -a 'find  /var/www/repo/os-releases -type l' \
                          -t "${COMMAND_LOGS}/repo_data"

    print_report
popd
