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

## Pre-flight Check ----------------------------------------------------------
# Clear the screen and make sure the user understands whats happening.
clear

# NOTICE: To run this in an automated fashion run the script via
#   root@HOSTNAME:/opt/openstack-ansible# echo "YES" | bash scripts/run-upgrade.sh

# Notify the user.
echo -e "
This script will perform a v10.x to v11.x upgrade.
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
  echo "Running Upgrade from v10.x to v11.x"
else
  exit 99
fi

## Shell Opts ----------------------------------------------------------------
set -e -u -v

export SCRIPTS_PATH="$(dirname $(readlink -f $0))"
export MAIN_PATH="$(dirname ${SCRIPTS_PATH})"
export UPGRADE_PLAYBOOKS="${SCRIPTS_PATH}/upgrade-utilities/playbooks"
export UPGRADE_SCRIPTS="${SCRIPTS_PATH}/upgrade-utilities/scripts"

## Functions -----------------------------------------------------------------
function run_lock {
  set +e
  run_item="${RUN_TASKS[$1]}"
  file_part="${run_item}"

  # NOTE(sigmavirus24): This handles tasks like:
  # "-e 'rabbitmq_upgrade=true' setup-infrastructure.yml"
  # "/tmp/fix_container_interfaces.yml || true"
  # So we can get the appropriate basename for the upgrade_marker
  for part in $run_item; do
    if [[ "$part" == *.yml ]];then
      file_part="$part"
      break
    fi
  done

  upgrade_marker_file=$(basename ${file_part} .yml)
  upgrade_marker="/etc/openstack_deploy/upgrade-juno/$upgrade_marker_file.complete"

  if [ ! -f "$upgrade_marker" ];then
    # NOTE(sigmavirus24): Use eval so that we properly turn strings like
    # "/tmp/fix_container_interfaces.yml || true"
    # Into a command, otherwise we'll get an error that there's no playbook
    # named ||
    eval "openstack-ansible $2 -e 'pip_install_options=--force-reinstall'"
    playbook_status="$?"
    echo "ran $run_item"

    if [ "$playbook_status" == "0" ];then
      RUN_TASKS=("${RUN_TASKS[@]/$run_item}")
      touch "$upgrade_marker"
      echo "$run_item has been marked as success"
    else
      echo "******************** FAILURE ********************"
      echo "The upgrade script has failed please rerun the following task to continue"
      echo "Failed on task $run_item"
      echo "Do NOT rerun the upgrade script!"
      echo "Please execute the remaining tasks:"
      # Run the tasks in order
      for item in ${!RUN_TASKS[@]}; do
        echo "${RUN_TASKS[$item]}"
      done
      echo "******************** FAILURE ********************"
      exit 99
    fi
  else
    RUN_TASKS=("${RUN_TASKS[@]/$run_item.*}")
  fi
  set -e
}

${UPGRADE_SCRIPTS}/create-new-openstack-deploy-structure.sh

${UPGRADE_SCRIPTS}/bootstrap-new-ansible.sh

${UPGRADE_SCRIPTS}/juno-rpc-extras-create.py

${UPGRADE_SCRIPTS}/new-variable-prep.sh

# Convert LDAP variables if any are found
if grep '^keystone_ldap.*' /etc/openstack_deploy/user_variables.yml;then
  ${UPGRADE_SCRIPTS}/juno-kilo-ldap-conversion.py
fi

# Create the repo servers entries from the same entries found within the infra_hosts group.
if ! grep -r '^repo-infra_hosts\:' /etc/openstack_deploy/openstack_user_config.yml /etc/openstack_deploy/conf.d/;then
  if [ ! -f "/etc/openstack_deploy/conf.d/repo-servers.yml" ];then
    ${UPGRADE_SCRIPTS}/juno-kilo-add-repo-infra.py
  fi
fi

${UPGRADE_SCRIPTS}/juno-is-metal-preserve.py

${UPGRADE_SCRIPTS}/old-variable-remove.sh

## Main ----------------------------------------------------------------------
pushd ${MAIN_PATH}/playbooks
  ${UPGRADE_SCRIPTS}/juno-container-cleanup.sh

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/user-secrets-adjustments.yml")

  RUN_TASKS+=("haproxy-install.yml || true")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/container-network-adjustments.yml || true")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/host-adjustments.yml")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/keystone-adjustments.yml")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/horizon-adjustments.yml")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/cinder-adjustments.yml")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/remove-juno-log-rotate.yml || true")

  RUN_TASKS+=("openstack-hosts-setup.yml")

  RUN_TASKS+=("lxc-hosts-setup.yml --tags rsyslog-client")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/lxc-containers-create-upgrade-step-1.yml --limit '!galera_all:!nova_scheduler:!nova_conductor:!rabbitmq_all:!cinder_scheduler:!neutron_agent'")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/lxc-containers-create-upgrade-step-2.yml --limit 'galera_all[0]:nova_scheduler[0]:nova_conductor[0]:rabbitmq_all[0]:cinder_scheduler[0]:neutron_agent[0]'")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/lxc-containers-create-upgrade-step-3.yml --limit 'galera_all[1-999]:nova_scheduler[1-999]:nova_conductor[1-999]:rabbitmq_all[1-999]:cinder_scheduler[1-999]:neutron_agent[1-999]'")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/container-network-bounce.yml || true")

  RUN_TASKS+=("setup-infrastructure.yml -e 'rabbitmq_upgrade=true' -e 'galera_ignore_cluster_state=true'")

  RUN_TASKS+=("os-keystone-install.yml")

  RUN_TASKS+=("os-glance-install.yml")

  RUN_TASKS+=("os-cinder-install.yml")

  RUN_TASKS+=("os-neutron-install.yml")

  RUN_TASKS+=("os-nova-install.yml")

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/nova-extra-migrations.yml")

  RUN_TASKS+=("os-heat-install.yml")

  RUN_TASKS+=("os-horizon-install.yml")

  RUN_TASKS+=("os-ceilometer-install.yml")

  # Send the swift rings to the first swift host if swift was installed in "v10.x".
  if [ "$(ansible 'swift_hosts' --list-hosts)" != "No hosts matched" ]; then
    RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/swift-ring-adjustments.yml")
  fi

  RUN_TASKS+=("${UPGRADE_PLAYBOOKS}/swift-repo-adjustments.yml")

  RUN_TASKS+=("os-swift-install.yml")

  # Run the tasks in order
  for item in ${!RUN_TASKS[@]}; do
    run_lock $item "${RUN_TASKS[$item]}"
  done
popd

