#!/usr/bin/env bash

# Copyright 2020, VEXXHOST, Inc.
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

export OSA_REPO_PATH=${OSA_REPO_PATH:-"/opt/openstack-ansible"}
export HOSTS=${1:-""}

function define_tasks {

    if [[ ! -z ${PRE_OSA_TASKS} ]]; then
        if [ "${BASH_VERSINFO[0]}" -ge 4 ] && [ "${BASH_VERSINFO[1]}" -ge 4 ]; then
            readarray -td";" PRE_TASKS <<<"$PRE_OSA_TASKS"
        else
            readarray -t PRE_TASKS <<<"$(echo "$PRE_OSA_TASKS" | tr ';' '\n')"
        fi
        for i in ${!PRE_TASKS[@]}; do
            RUN_TASKS+=("${PRE_TASKS[$i]}")
        done
    fi

    RUN_TASKS+=("${OSA_REPO_PATH}/playbooks/setup-hosts.yml --limit ${HOSTS}")
    RUN_TASKS+=("${OSA_REPO_PATH}/playbooks/setup-openstack.yml --limit ${HOSTS}")
    RUN_TASKS+=("${OSA_REPO_PATH}/playbooks/openstack-hosts-setup.yml --tags openstack_hosts-config,openstack-hosts")
    RUN_TASKS+=("${OSA_REPO_PATH}/playbooks/unbound-install.yml --tags unbound-config")
    RUN_TASKS+=("${OSA_REPO_PATH}/playbooks/os-nova-install.yml --tags nova-key --limit nova_compute")

    if [[ ! -z ${POST_OSA_TASKS} ]]; then
        if [ "${BASH_VERSINFO[0]}" -ge 4 ] && [ "${BASH_VERSINFO[1]}" -ge 4 ]; then
            readarray -td";" POST_TASKS <<<"$POST_OSA_TASKS"
        else
            readarray -t POST_TASKS <<<"$(echo "$POST_OSA_TASKS" | tr ';' '\n')"
        fi
        for i in ${!POST_TASKS[@]}; do
            RUN_TASKS+=("${POST_TASKS[$i]}")
        done
    fi
}

function run_tasks {
    set +e
    for item in ${!RUN_TASKS[@]}; do
        eval "openstack-ansible ${RUN_TASKS[$item]}"
        playbook_status="$?"
        if [[ ${playbook_status} -gt 0 ]]; then
            echo "*********************** failure ************************"
            echo "The compute deployment script has encountered a failure."
            echo "Failed on task \"${RUN_TASKS[$item]}\" with status $playbook_status"
            echo "Re-run the script, or execute tasks manually:"
            for item in $(seq $item $((${#RUN_TASKS[@]} - 1))); do
                if [ -n "${RUN_TASKS[$item]}" ]; then
                    echo "openstack-ansible ${RUN_TASKS[$item]}"
                fi
            done
            echo "*********************** failure ************************"
            exit ${playbook_status}
        # else
        #     echo "task ${RUN_TASKS[$item]} ran successfully"
        fi
    done
    set -e
}

function main {
    if [[ -z ${HOSTS} ]]; then
        echo "Hosts to setup are not provided"
        exit 1
    elif [[ ! -d ${OSA_REPO_PATH} ]]; then
        echo "OSA repo is not found: ${OSA_REPO_PATH}. Define OSA_REPO_PATH to set another directory"
        exit 1
    fi

    define_tasks
    run_tasks
}

main
