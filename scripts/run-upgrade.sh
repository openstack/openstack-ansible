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

# The path to find all the upgrade playbooks
export UPGRADE_PLAYBOOKS="${SCRIPTS_PATH}/upgrade-utilities/playbooks"

# The expected source series name
export SOURCE_SERIES="queens"

# The expected target series name
export TARGET_SERIES="rocky"

## Functions -----------------------------------------------------------------

function run_lock {
  set +e
  run_item="${RUN_TASKS[$1]}"
  file_part="${run_item}"

  # note(sigmavirus24): this handles tasks like:
  # "-e 'rabbitmq_upgrade=true' setup-infrastructure.yml"
  # "/tmp/fix_container_interfaces.yml || true"
  # so we can get the appropriate basename for the upgrade_marker
  for part in $run_item; do
    if [[ "$part" == *.yml ]];then
      file_part="$part"
      break
    fi
  done

  if [ ! -d  "/etc/openstack_deploy/upgrade-${TARGET_SERIES}" ]; then
      mkdir -p "/etc/openstack_deploy/upgrade-${TARGET_SERIES}"
  fi

  upgrade_marker_file=$(basename ${file_part} .yml)
  upgrade_marker="/etc/openstack_deploy/upgrade-${TARGET_SERIES}/$upgrade_marker_file.complete"

  if [ ! -f "$upgrade_marker" ];then
    # note(sigmavirus24): use eval so that we properly turn strings like
    # "/tmp/fix_container_interfaces.yml || true"
    # into a command, otherwise we'll get an error that there's no playbook
    # named ||
    eval "openstack-ansible $2"
    playbook_status="$?"
    echo "ran $run_item"

    if [ "$playbook_status" == "0" ];then
      RUN_TASKS=("${RUN_TASKS[@]/$run_item}")
      touch "$upgrade_marker"
      echo "$run_item has been marked as success"
    else
      echo "******************** failure ********************"
      echo "The upgrade script has encountered a failure."
      echo "Failed on task \"$run_item\""
      echo "Re-run the run-upgrade.sh script, or"
      echo "execute the remaining tasks manually:"
      # NOTE:
      # List the remaining, incompleted tasks from the tasks array.
      # Using seq to genertate a sequence which starts from the spot
      # where previous exception or failures happened.
      # run the tasks in order
      for item in $(seq $1 $((${#RUN_TASKS[@]} - 1))); do
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
    if [[ ! -d "/etc/openstack_deploy" ]]; then
      echo "--------------ERROR--------------"
      echo "/etc/openstack_deploy directory not found."
      echo "It appears you do not have a current environment installed."
      exit 2
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

    # ANSIBLE_INVENTORY location has changed between P and Q, so we ensure
    # we don't point to previous inventory.
    unset ANSIBLE_INVENTORY

    # Archive previous version artifacts
    tar zcf /openstack/previous-ansible_`date +%F_%H%M`.tar.gz /etc/openstack_deploy /etc/ansible/ /usr/local/bin/openstack-ansible.rc

    "${SCRIPTS_PATH}/bootstrap-ansible.sh"

    pushd ${MAIN_PATH}/playbooks
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/ansible_fact_cleanup.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/user-secrets-adjustment.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/pip-conf-removal.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/ceph-galaxy-removal.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/molteniron-role-removal.yml")
        # we don't want to trigger container restarts for these groups yet
        RUN_TASKS+=("setup-hosts.yml --limit '!galera_all:!rabbitmq_all'")
        # add new container config to containers but don't restart
        RUN_TASKS+=("lxc-containers-create.yml -e 'lxc_container_allow_restarts=false' --limit 'galera_all:rabbitmq_all'")
        # setup infra
        RUN_TASKS+=("unbound-install.yml")
        RUN_TASKS+=("repo-install.yml")
        RUN_TASKS+=("haproxy-install.yml")
        RUN_TASKS+=("repo-use.yml")
        # explicitly perform mariadb upgrade
        RUN_TASKS+=("galera-install.yml -e 'galera_upgrade=true'")
        # explicitly perform controlled galera cluster restart
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/galera-cluster-rolling-restart.yml")
        # individually run each of the remaining plays from setup-infrastructure
        RUN_TASKS+=("memcached-install.yml")
        RUN_TASKS+=("rabbitmq-install.yml -e 'rabbitmq_upgrade=true'")
        RUN_TASKS+=("etcd-install.yml")
        RUN_TASKS+=("utility-install.yml")
        RUN_TASKS+=("rsyslog-install.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/memcached-flush.yml")
        RUN_TASKS+=("setup-openstack.yml")
        # Run the tasks in order
        for item in ${!RUN_TASKS[@]}; do
          run_lock $item "${RUN_TASKS[$item]}"
        done
    popd
}

main
