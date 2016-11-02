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
set -e -u -v

export SCRIPTS_PATH="$(dirname $(readlink -f $0))"
export MAIN_PATH="$(dirname ${SCRIPTS_PATH})"
export UPGRADE_PLAYBOOKS="${SCRIPTS_PATH}/upgrade-utilities/playbooks"
export I_REALLY_KNOW_WHAT_I_AM_DOING=${I_REALLY_KNOW_WHAT_I_AM_DOING:-"false"}

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

  if [ ! -d  "/etc/openstack_deploy/upgrade-mitaka" ]; then
      mkdir -p "/etc/openstack_deploy/upgrade-mitaka"
  fi

  upgrade_marker_file=$(basename ${file_part} .yml)
  upgrade_marker="/etc/openstack_deploy/upgrade-mitaka/$upgrade_marker_file.complete"

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
    echo "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh
    ## Pre-flight Check ----------------------------------------------------------
    # Clear the screen and make sure the user understands whats happening.
    clear

    # Notify the user.
    echo -e "
    This script will perform a v12.x to v13.x upgrade.
    Once you start the upgrade there's no going back.

    Note, this is an online upgrade and while the
    in progress running VMs will not be impacted.
    However, you can expect some hiccups with OpenStack
    API services while the upgrade is running.

    Are you ready to perform this upgrade now?
    "

    # Confirm the user is ready to upgrade.
    read -p 'Enter "YES" to continue or anything else to quit: ' UPGRADE
    if [ "${UPGRADE}" == "YES" ]; then
      echo "Running Upgrade from v12.x to v13.x"
    else
      exit 99
    fi
}

function exit_early {
    echo -e "
    The upgrade script is still under active development and should not be
    run at this time. For test environments the early exit of the script can
    skipped by executing ``export I_REALLY_KNOW_WHAT_I_AM_DOING=true`` before
    ``run-upgrade.sh``.
    "
    exit 99
}

## Main ----------------------------------------------------------------------

function main {
    pre_flight
    check_for_current

    "${SCRIPTS_PATH}/bootstrap-ansible.sh"

    pushd ${MAIN_PATH}/playbooks
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/disable_hatool.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/01_ansible_fact_cleanup.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/deploy-config-changes.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/user-secrets-adjustment.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/pip-conf-removal.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/old-hostname-compatibility.yml")
        # we don't want to trigger galera container restarts yet
        RUN_TASKS+=("setup-hosts.yml --limit '!galera_all'")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/restart-rabbitmq-containers.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/02_ansible_fact_cleanup.yml")
        # add new container config to galera containers but don't restart
        RUN_TASKS+=("lxc-containers-create.yml -e 'lxc_container_allow_restarts=false' --limit galera_all")
	# rebuild the repo servers
        RUN_TASKS+=("repo-install.yml")
        # explicitly perform mariadb upgrade
        RUN_TASKS+=("galera-install.yml -e 'galera_upgrade=true'")
        # explicitly perform controlled galera cluster restart
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/galera-cluster-rolling-restart.yml")
        # individually run each of the remaining plays from setup-infrastructure
        RUN_TASKS+=("haproxy-install.yml")
        RUN_TASKS+=("memcached-install.yml")
        RUN_TASKS+=("rabbitmq-install.yml -e 'rabbitmq_upgrade=true'")
        RUN_TASKS+=("utility-install.yml")
        RUN_TASKS+=("rsyslog-install.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/memcached-flush.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/neutron-mtu-migration.yml")
        RUN_TASKS+=("setup-openstack.yml")
        RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/rfc1034_1035-cleanup.yml -e 'destroy_ok=yes'")
        # Run the tasks in order
        for item in ${!RUN_TASKS[@]}; do
          run_lock $item "${RUN_TASKS[$item]}"
        done
    popd
}

main
