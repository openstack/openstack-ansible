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

## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh

## Main ----------------------------------------------------------------------
# Set gate job exit traps, this is run regardless of exit state when the job finishes.
trap gate_job_exit_tasks EXIT

# Log some data about the instance and the rest of the system
log_instance_info

# Get minimum disk size
DATA_DISK_MIN_SIZE="$((1024**3 * $(awk '/bootstrap_host_data_disk_min_size/{print $2}' $(dirname ${0})/../tests/roles/bootstrap-host/defaults/main.yml) ))"

# Determine the largest secondary disk device that meets the minimum size
DATA_DISK_DEVICE=$(lsblk -brndo NAME,TYPE,RO,SIZE | awk '/d[b-z]+ disk 0/{ if ($4>m && $4>='$DATA_DISK_MIN_SIZE'){m=$4; d=$1}}; END{print d}')

# Only set the secondary disk device option if there is one
if [ -n "${DATA_DISK_DEVICE}" ]; then
  export BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_data_disk_device=${DATA_DISK_DEVICE}"
fi

# Bootstrap Ansible
source $(dirname ${0})/bootstrap-ansible.sh

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

# Adjust settings based on the Cloud Provider info in OpenStack-CI
if [ -f /etc/nodepool/provider -a -s /etc/nodepool/provider ]; then
  source /etc/nodepool/provider

  # Update the libvirt cpu map with a gate64 cpu model. This enables nova
  # live migration for 64bit guest OSes on heterogenous cloud "hardware".
  export BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_libvirt_config=yes"

fi

# Bootstrap an AIO
pushd $(dirname ${0})/../tests
  sed -i '/\[defaults\]/a nocolor = 1/' ansible.cfg
  ansible-playbook -i "localhost ansible-connection=local," \
                   -e "${BOOTSTRAP_OPTS}" \
                   ${ANSIBLE_PARAMETERS} \
                   bootstrap-aio.yml
popd

# Implement the log directory
mkdir -p /openstack/log

# Implement the log directory link for openstack-infra log publishing
ln -sf /openstack/log $(dirname ${0})/../logs

pushd $(dirname ${0})/../playbooks
  # Disable Ansible color output
  sed -i 's/nocolor.*/nocolor = 1/' ansible.cfg

  # Create ansible logging directory and add in a log file entry into ansible.cfg
  mkdir -p /openstack/log/ansible-logging
  sed -i '/\[defaults\]/a log_path = /openstack/log/ansible-logging/ansible.log' ansible.cfg

  # This plugin makes the output easier to read
  wget -O /etc/ansible/plugins/callback/human_log.py https://gist.githubusercontent.com/cliffano/9868180/raw/f360f306b3c6d689734a6aa8773a00edf16a0054/human_log.py

  # Enable callback plugins
  sed -i '/\[defaults\]/a callback_plugins = /etc/ansible/plugins/callback' ansible.cfg
popd

# Log some data about the instance and the rest of the system
log_instance_info

# Execute the Playbooks
bash $(dirname ${0})/run-playbooks.sh

# Log some data about the instance and the rest of the system
log_instance_info

# Run the tempest tests
source $(dirname ${0})/run-tempest.sh

# Log some data about the instance and the rest of the system
log_instance_info

exit_success
