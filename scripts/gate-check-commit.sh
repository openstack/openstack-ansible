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
export MAX_RETRIES=${MAX_RETRIES:-"2"}
# tempest and testr options, default is to run tempest in serial
export TESTR_OPTS=${TESTR_OPTS:-''}
# Disable the python output buffering so that jenkins gets the output properly
export PYTHONUNBUFFERED=1
# Extra options to pass to the AIO bootstrap process
export BOOTSTRAP_OPTS=${BOOTSTRAP_OPTS:-''}
# This variable is being added to ensure the gate job executes an exit
#  function at the end of the run.
export OSA_GATE_JOB=true
# Set the role fetch mode to any option [galaxy, git-clone]
export ANSIBLE_ROLE_FETCH_MODE="git-clone"
# Set the scenario to execute based on the first CLI parameter
export SCENARIO=${1:-"aio"}

# TODO(sc68cal) update the job configs to have the stable branch
# So we have job names like:
# gate-openstack-ansible-openstack-ansible-upgrade-newton-ubuntu-xenial-nv
export UPGRADE_BASEBRANCH=${2:-"ocata"}
export SCENARIO_BACKUP=${SCENARIO_BACKUP:-''}

## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source "$(dirname "${0}")/scripts-library.sh"

## Main ----------------------------------------------------------------------
# Set gate job exit traps, this is run regardless of exit state when the job finishes.
trap gate_job_exit_tasks EXIT

# Log some data about the instance and the rest of the system
log_instance_info


if [[ "$SCENARIO" == "upgrade" ]]; then
    # First, check out the base branch and build an AIO
    git checkout origin/stable/$UPGRADE_BASEBRANCH

    # Do a quick swap of SCENARIO since the newton branch doesn't know about the upgrade scenario
    export SCENARIO_BACKUP=$SCENARIO
    SCENARIO="aio"
fi

# Get minimum disk size
DATA_DISK_MIN_SIZE="$((1024**3 * $(awk '/bootstrap_host_data_disk_min_size/{print $2}' "$(dirname "${0}")/../tests/roles/bootstrap-host/defaults/main.yml") ))"

# Determine the largest secondary disk device that meets the minimum size
DATA_DISK_DEVICE=$(lsblk -brndo NAME,TYPE,RO,SIZE | awk '/d[b-z]+ disk 0/{ if ($4>m && $4>='$DATA_DISK_MIN_SIZE'){m=$4; d=$1}}; END{print d}')

# Only set the secondary disk device option if there is one
if [ -n "${DATA_DISK_DEVICE}" ]; then
  export BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_data_disk_device=${DATA_DISK_DEVICE}"
fi

# Bootstrap Ansible
source "$(dirname "${0}")/bootstrap-ansible.sh"

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
pushd "$(dirname "${0}")/../tests"
  if [ -z "${BOOTSTRAP_OPTS}" ]; then
    ansible-playbook bootstrap-aio.yml \
                     -i test-inventory.ini \
                     ${ANSIBLE_PARAMETERS}
  else
    ansible-playbook bootstrap-aio.yml \
                     -i test-inventory.ini \
                     -e "${BOOTSTRAP_OPTS}" \
                     ${ANSIBLE_PARAMETERS}
  fi
popd

# Implement the log directory
mkdir -p /openstack/log

pushd "$(dirname "${0}")/../playbooks"
  # Disable Ansible color output
  export ANSIBLE_NOCOLOR=1

  # Create ansible logging directory and add in a log file export
  mkdir -p /openstack/log/ansible-logging
  export ANSIBLE_LOG_PATH="/openstack/log/ansible-logging/ansible.log"
popd

# Log some data about the instance and the rest of the system
log_instance_info

# Execute the Playbooks
bash "$(dirname "${0}")/run-playbooks.sh"

# Log some data about the instance and the rest of the system
log_instance_info

if [ ! -z $SCENARIO_BACKUP ]; then
    # Restore the scenario from L56
    SCENARIO=$SCENARIO_BACKUP
fi

if [[ "$SCENARIO" == "upgrade" ]]; then
    # Hopefully we can re-check out the patch from Zuul.
    git checkout FETCH_HEAD
    export I_REALLY_KNOW_WHAT_I_AM_DOING=true
    bash "$(dirname "${0}")/run-upgrade.sh"
fi

exit_success
