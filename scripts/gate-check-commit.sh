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

## Variables -----------------------------------------------------------------

# Successerator: How many times do we try before failing
export MAX_RETRIES=${MAX_RETRIES:-"2"}

# tempest and testr options, default is to run tempest in serial
export TESTR_OPTS=${TESTR_OPTS:-''}

# Disable the python output buffering so that jenkins gets the output properly
export PYTHONUNBUFFERED=1

# Extra options to pass to the AIO bootstrap process
export BOOTSTRAP_OPTS=${BOOTSTRAP_OPTS:-''}

# Ensure the terminal type is set
export TERM=linux

# Store the clone repo root location
export OSA_CLONE_DIR="$(readlink -f $(dirname ${0})/..)"

# Set the role fetch mode to git-clone to avoid interactions
# with the Ansible galaxy API.
export ANSIBLE_ROLE_FETCH_MODE="git-clone"

# The directory in which the ansible logs will be placed
export ANSIBLE_LOG_DIR="/openstack/log/ansible-logging"

# Set the scenario to execute based on the first CLI parameter
export SCENARIO=${1:-"aio_lxc"}

# Set the action base on the second CLI parameter
# Actions available: [ 'deploy', 'upgrade' ]
export ACTION=${2:-"deploy"}

# Set the source branch for upgrade tests
# Be sure to change this whenever a new stable branch
# is created. The checkout must always be N-1.
export UPGRADE_SOURCE_BRANCH=${UPGRADE_SOURCE_BRANCH:-'stable/pike'}

## Change branch for Upgrades ------------------------------------------------
# If the action is to upgrade, then store the current SHA,
# checkout the source SHA before executing the greenfield
# deployment.
# This needs to be done before the first "source" to ensure
# the correct functions are used for the branch.
# Also, in queens the 'aio' scenario was renamed to aio_lxc
# so we handle ensuring that the pike checkout understands
# which scenario it needs to use.
if [[ "${ACTION}" == "upgrade" ]]; then

    # Convert the scenario from a queens name
    # to a pike name
    if [[ "${SCENARIO}" == "aio_lxc" ]]; then
      export SCENARIO="aio"
    fi

    # Store the target SHA/branch
    export UPGRADE_TARGET_BRANCH=$(git rev-parse HEAD)

    # Now checkout the source SHA/branch
    git checkout ${UPGRADE_SOURCE_BRANCH}
fi

## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source "${OSA_CLONE_DIR}/scripts/scripts-library.sh"

## Main ----------------------------------------------------------------------

# Log some data about the instance and the rest of the system
log_instance_info

run_dstat || true

# Get minimum disk size
DATA_DISK_MIN_SIZE="$((1024**3 * $(awk '/bootstrap_host_data_disk_min_size/{print $2}' "${OSA_CLONE_DIR}/tests/roles/bootstrap-host/defaults/main.yml") ))"

# Determine the largest secondary disk device that meets the minimum size
DATA_DISK_DEVICE=$(lsblk -brndo NAME,TYPE,RO,SIZE | awk '/d[b-z]+ disk 0/{ if ($4>m && $4>='$DATA_DISK_MIN_SIZE'){m=$4; d=$1}}; END{print d}')

# Only set the secondary disk device option if there is one
if [ -n "${DATA_DISK_DEVICE}" ]; then
  export BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_data_disk_device=${DATA_DISK_DEVICE}"
fi

# Bootstrap Ansible
source "${OSA_CLONE_DIR}/scripts/bootstrap-ansible.sh"

# Install and export the ARA callback plugin
setup_ara

# Log some data about the instance and the rest of the system
log_instance_info

# Flush all the iptables rules set by openstack-infra
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# Bootstrap an AIO
unset ANSIBLE_VARS_PLUGINS
unset HOST_VARS_PATH
unset GROUP_VARS_PATH

pushd "${OSA_CLONE_DIR}/tests"
  if [ -z "${BOOTSTRAP_OPTS}" ]; then
    /opt/ansible-runtime/bin/ansible-playbook bootstrap-aio.yml \
                     -i test-inventory.ini \
                     ${ANSIBLE_PARAMETERS}
  else
    /opt/ansible-runtime/bin/ansible-playbook bootstrap-aio.yml \
                     -i test-inventory.ini \
                     -e "${BOOTSTRAP_OPTS}" \
                     ${ANSIBLE_PARAMETERS}
  fi
popd

if [[ "${ACTION}" == "varstest" ]]; then
  pushd "${OSA_CLONE_DIR}/tests"
      openstack-ansible test-vars-overrides.yml
  popd
else
  pushd "${OSA_CLONE_DIR}/playbooks"
    # Disable Ansible color output
    export ANSIBLE_NOCOLOR=1

    # Create ansible logging directory
    mkdir -p ${ANSIBLE_LOG_DIR}

    # Log some data about the instance and the rest of the system
    log_instance_info

    # First we gather facts about the hosts to populate the fact cache.
    # We can't gather the facts for all hosts yet because the containers
    # aren't built yet.
    ansible -m setup -a 'gather_subset=network,hardware,virtual' hosts 2>${ANSIBLE_LOG_DIR}/facts-hosts.log

    # Prepare the hosts
    export ANSIBLE_LOG_PATH="${ANSIBLE_LOG_DIR}/setup-hosts.log"
    openstack-ansible setup-hosts.yml -e osa_gather_facts=False

    # Log some data about the instance and the rest of the system
    log_instance_info

    # Once setup-hosts is complete, we should gather facts for everything
    # (now including containers) so that the fact cache is complete for the
    # remainder of the run.
    ansible -m setup -a 'gather_subset=network,hardware,virtual' all 1>${ANSIBLE_LOG_DIR}/facts-all.log

    # Prepare the infrastructure
    export ANSIBLE_LOG_PATH="${ANSIBLE_LOG_DIR}/setup-infrastructure.log"
    openstack-ansible setup-infrastructure.yml -e osa_gather_facts=False

    # Log some data about the instance and the rest of the system
    log_instance_info

    # Setup OpenStack
    export ANSIBLE_LOG_PATH="${ANSIBLE_LOG_DIR}/setup-openstack.log"
    openstack-ansible setup-openstack.yml -e osa_gather_facts=False

    # Log some data about the instance and the rest of the system
    log_instance_info

  popd
fi

# If the action is to upgrade, then checkout the original SHA for
# the checkout, and execute the upgrade.
if [[ "${ACTION}" == "upgrade" ]]; then

    # Checkout the original HEAD we started with
    git checkout ${UPGRADE_TARGET_BRANCH}

    # Unset environment variables used by the bootstrap-ansible
    # script to allow newer versions of Ansible and global
    # requirements to be installed.
    unset ANSIBLE_PACKAGE
    unset UPPER_CONSTRAINTS_FILE

    # Source the current scripts-library.sh functions
    source "${OSA_CLONE_DIR}/scripts/scripts-library.sh"

    # Kick off the data plane tester
    bash ${OSA_CLONE_DIR}/tests/data-plane-test.sh &> /var/log/data-plane-error.log &

    # Fetch script to execute API availability tests, then
    # background them while the upgrade runs.
    get_bowling_ball_tests
    start_bowling_ball_tests

    # To execute the upgrade script we need to provide
    # an affirmative response to the warning that the
    # upgrade is irreversable.
    echo 'YES' | bash "${OSA_CLONE_DIR}/scripts/run-upgrade.sh"

    # Terminate the API availability tests
    kill_bowling_ball_tests

    # Terminate the data plane tester
    rm -f /var/run/data-plane-test.socket

    # Wait 10s for the tests to complete
    sleep 10

    # Output the API availability test results
    print_bowling_ball_results

    # Check for any data plane failures, and fail if there are
    if ! egrep -q "^FAIL: 0$" /var/log/data-plane-test.log; then
        echo -e "\n\nFAIL: The L3 data plane check failed!\n\n"
        exit 1
    fi

    # Check for any disk access failures, and fail if there are
    if ! egrep -q "^FAIL: 0$" /var/log/disk-access-test.log; then
        echo -e "\n\nFAIL: The disk access data plane check failed!\n\n"
        exit 1
    fi

fi

exit_success
