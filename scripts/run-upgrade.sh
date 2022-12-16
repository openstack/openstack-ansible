#!/usr/bin/env bash

# Copyright 2015, Rackspace US, Inc.
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

# NOTICE: To run this in an automated fashion run the script via
#   root@HOSTNAME:/opt/openstack-ansible# echo "YES" | bash scripts/run-upgrade.sh


## Shell Opts ----------------------------------------------------------------

set -e -u

## Vars ----------------------------------------------------------------------

# The path from which this script is being run
export SCRIPTS_PATH="$(dirname "$(readlink -f "${0}")")"

# The git checkout root path
export MAIN_PATH="$(dirname "${SCRIPTS_PATH}")"

# The expected source series name
export SOURCE_SERIES="zed"

# The expected target series name
export TARGET_SERIES="2023.1"

# The expected OSA config dir
export OSA_CONFIG_DIR="${OSA_CONFIG_DIR:-/etc/openstack_deploy}"

## Functions -----------------------------------------------------------------

function run_lock {
  set +e
  run_item_index="$1"
  run_item="$2"
  hashed_run_item=($(echo $run_item | md5sum))

  upgrade_marker="${OSA_CONFIG_DIR}/upgrade-${TARGET_SERIES}/$hashed_run_item.complete"

  if [ ! -f "$upgrade_marker" ];then
    # note(sigmavirus24): use eval so that we properly turn strings like
    # "/tmp/fix_container_interfaces.yml || true"
    # into a command, otherwise we'll get an error that there's no playbook
    # named ||
    eval "openstack-ansible $run_item"
    playbook_status="$?"
    echo "ran $run_item"

    if [ "$playbook_status" == "0" ];then
      RUN_TASKS=("${RUN_TASKS[@]/$run_item}")
      echo "$run_item" > "$upgrade_marker"
      echo "$run_item has been marked as success"
    else
      echo "******************** failure ********************"
      echo "The upgrade script has encountered a failure."
      echo "Failed on task \"$run_item\""
      echo "Re-run the run-upgrade.sh script, or"
      echo "execute the remaining tasks manually:"
      # NOTE:
      # List the remaining, incompleted tasks from the tasks array.
      # Using seq to generate a sequence which starts from the spot
      # where previous exception or failures happened.
      # run the tasks in order
      for item in $(seq $run_item_index $((${#RUN_TASKS[@]} - 1))); do
        if [ -n "${RUN_TASKS[$item]}" ]; then
          echo "openstack-ansible ${RUN_TASKS[$item]}"
        fi
      done
      echo "******************** failure ********************"
      exit 99
    fi
  else
    RUN_TASKS=("${RUN_TASKS[@]/$run_item.*}")
  fi
  set -e
}

function check_for_current {
    if [[ ! -d "${OSA_CONFIG_DIR}" ]]; then
      echo "--------------ERROR--------------"
      echo "${OSA_CONFIG_DIR} directory not found."
      echo "It appears you do not have a current environment installed."
      exit 2
    fi
}

function create_working_dir {
    if [ ! -d  "${OSA_CONFIG_DIR}/upgrade-${TARGET_SERIES}" ]; then
        mkdir -p "${OSA_CONFIG_DIR}/upgrade-${TARGET_SERIES}"
    fi
}

function bootstrap_ansible {
    if [ ! -f "${OSA_CONFIG_DIR}/upgrade-${TARGET_SERIES}/bootstrap-ansible.complete" ]; then
      "${SCRIPTS_PATH}/bootstrap-ansible.sh"
      touch ${OSA_CONFIG_DIR}/upgrade-${TARGET_SERIES}/bootstrap-ansible.complete
    else
      echo "Ansible has been bootstrapped for ${TARGET_SERIES} already, skipping..."
    fi
}

function pre_flight {
    ## Library Check -------------------------------------------------------------

    info_block "Checking for required libraries." 2> /dev/null ||
        source ${SCRIPTS_PATH}/scripts-library.sh

    ## Pre-flight Check ----------------------------------------------------------
    # Clear the screen and make sure the user understands whats happening.
    clear

    # Notify the user.
    echo -e "
    This script will perform a ${SOURCE_SERIES^} to ${TARGET_SERIES^} upgrade.
    Once you start the upgrade there is no going back.

    Note that the upgrade targets impacting the data
    plane as little as possible, but assumes that the
    control plane can experience some down time.

    This script executes a one-size-fits-all upgrade,
    and given that the tests implemented for it are
    not monitored as well as those for a greenfield
    environment, the results may vary with each release.

    Please use it against a test environment with your
    configurations to validate whether it suits your
    needs and does a suitable upgrade.

    Are you ready to perform this upgrade now?
    "

    # Confirm the user is ready to upgrade.
    read -p 'Enter "YES" to continue or anything else to quit: ' UPGRADE
    if [ "${UPGRADE}" == "YES" ]; then
      echo "Running Upgrade from ${SOURCE_SERIES^} to ${TARGET_SERIES^}"
    else
      exit 99
    fi
}

## Main ----------------------------------------------------------------------

function main {
    pre_flight
    check_for_current
    create_working_dir

    # Backup source series artifacts
    source_series_backup_file="/openstack/backup-openstack-ansible-${SOURCE_SERIES}.tar.gz"
    if [[ ! -e ${source_series_backup_file} ]]; then
      tar zcf ${source_series_backup_file} ${OSA_CONFIG_DIR} /etc/ansible/ /usr/local/bin/openstack-ansible.rc
    fi

    # Environment variables may be set to a previous/incorrect location.
    # To ensure this is not the case, we unset the environment variable.
    unset ANSIBLE_INVENTORY

    # TODO(noonedeadpunk): Remove after Y release
    source ${SCRIPTS_PATH}/upgrade-utilities/unset-ansible-env.rc

    bootstrap_ansible

    pushd ${MAIN_PATH}/playbooks
        RUN_TASKS+=("${SCRIPTS_PATH}/upgrade-utilities/deploy-config-changes.yml")
        RUN_TASKS+=("${SCRIPTS_PATH}/upgrade-utilities/define-neutron-plugin.yml")
        RUN_TASKS+=("certificate-ssh-authority.yml")
        # we don't want to trigger container restarts for galera and rabbit
        # but as there will be no hosts available for metal deployments,
        # as a fallback option we just run setup-hosts.yml without any arguments
        RUN_TASKS+=("setup-hosts.yml --limit '!galera_all:!rabbitmq_all' -e package_state=latest && \
                     openstack-ansible setup-hosts.yml -e 'lxc_container_allow_restarts=false' --limit 'galera_all:rabbitmq_all' || \
                     openstack-ansible setup-hosts.yml -e package_state=latest")
        # upgrade infrastructure
        RUN_TASKS+=("setup-infrastructure.yml -e 'galera_upgrade=true' -e 'rabbitmq_upgrade=true' -e package_state=latest")
        # explicitly perform controlled galera cluster restart with new lxc config
        RUN_TASKS+=("${SCRIPTS_PATH}/upgrade-utilities/galera-cluster-rolling-restart.yml")
        # upgrade openstack
        RUN_TASKS+=("setup-openstack.yml -e package_state=latest")
        # Run the tasks in order
        for item in ${!RUN_TASKS[@]}; do
          echo "### NOW RUNNING: ${RUN_TASKS[$item]}"
          run_lock $item "${RUN_TASKS[$item]}"
        done
    popd
}

main
