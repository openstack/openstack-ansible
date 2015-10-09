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
export BOOTSTRAP_ANSIBLE=${BOOTSTRAP_ANSIBLE:-"yes"}
export BOOTSTRAP_AIO=${BOOTSTRAP_AIO:-"yes"}
export RUN_PLAYBOOKS=${RUN_PLAYBOOKS:-"yes"}
export RUN_TEMPEST=${RUN_TEMPEST:-"yes"}
# Ansible options
export ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-"-v"}
# Deployment options
export DEPLOY_HOST=${DEPLOY_HOST:-"yes"}
export DEPLOY_LB=${DEPLOY_LB:-"yes"}
export DEPLOY_INFRASTRUCTURE=${DEPLOY_INFRASTRUCTURE:-"yes"}
export DEPLOY_LOGGING=${DEPLOY_LOGGING:-"yes"}
export DEPLOY_OPENSTACK=${DEPLOY_OPENSTACK:-"yes"}
export DEPLOY_SWIFT=${DEPLOY_SWIFT:-"yes"}
export DEPLOY_TEMPEST=${DEPLOY_TEMPEST:-"yes"}
# Limit the gate check to only performing one attempt, unless already set
export MAX_RETRIES=${MAX_RETRIES:-"2"}
# tempest and testr options, default is to run tempest in serial
export RUN_TEMPEST_OPTS=${RUN_TEMPEST_OPTS:-'--serial'}
export TESTR_OPTS=${TESTR_OPTS:-''}

## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh

## Main ----------------------------------------------------------------------

# Disable Ansible color output
sed -i 's/nocolor.*/nocolor = 1/' $(dirname ${0})/../playbooks/ansible.cfg

# Make the /openstack/log directory for openstack-infra gate check log publishing
mkdir -p /openstack/log

# Implement the log directory link for openstack-infra log publishing
ln -sf /openstack/log $(dirname ${0})/../logs

# Create ansible logging directory and add in a log file entry into ansible.cfg
mkdir -p /openstack/log/ansible-logging
sed -i '/\[defaults\]/a log_path = /openstack/log/ansible-logging/ansible.log' $(dirname ${0})/../playbooks/ansible.cfg

# Adjust settings based on the Cloud Provider info in OpenStack-CI
if [ -f /etc/nodepool/provider -a -s /etc/nodepool/provider ]; then
  source /etc/nodepool/provider
  if [[ ${NODEPOOL_PROVIDER} == "rax"* ]]; then
    export UBUNTU_REPO="http://mirror.rackspace.com/ubuntu"
    export UBUNTU_SEC_REPO="${UBUNTU_REPO}"
  elif [[ ${NODEPOOL_PROVIDER} == "hpcloud"* ]]; then
    export UBUNTU_REPO="http://${NODEPOOL_AZ}.clouds.archive.ubuntu.com/ubuntu"
    export UBUNTU_SEC_REPO="${UBUNTU_REPO}"
  fi
fi

# Enable detailed task profiling
sed -i '/\[defaults\]/a callback_plugins = plugins/callbacks' $(dirname ${0})/../playbooks/ansible.cfg

# Bootstrap an AIO setup if required
if [ "${BOOTSTRAP_AIO}" == "yes" ]; then
  source $(dirname ${0})/bootstrap-aio.sh
fi

# Bootstrap ansible if required
if [ "${BOOTSTRAP_ANSIBLE}" == "yes" ]; then
  source $(dirname ${0})/bootstrap-ansible.sh
fi

# Enable debug logging for all services to make failure debugging easier
echo "debug: True" | tee -a /etc/openstack_deploy/user_variables.yml

# NOTE: hpcloud-b4's eth0 uses 10.0.3.0/24, which overlaps with the
#       lxc_net_address default
# TODO: We'll need to implement a mechanism to determine valid lxc_net_address
#       value which will not overlap with an IP already assigned to the host.
echo "lxc_net_address: 10.255.255.1" | tee -a /etc/openstack_deploy/user_variables.yml
echo "lxc_net_netmask: 255.255.255.0" | tee -a /etc/openstack_deploy/user_variables.yml
echo "lxc_net_dhcp_range: 10.255.255.2,10.255.255.253" | tee -a /etc/openstack_deploy/user_variables.yml

# Limit the number of processes used by Keystone
# The defaults cause tempest failures in OpenStack CI due to resource constraints
echo "keystone_wsgi_processes: 4" | tee -a /etc/openstack_deploy/user_variables.yml

# Disable the python output buffering so that jenkins gets the output properly
export PYTHONUNBUFFERED=1

# Run the ansible playbooks if required
if [ "${RUN_PLAYBOOKS}" == "yes" ]; then
  # Set-up our tiny awk script.
  strip_debug="
    !/(^[ 0-9|:.-]+<[0-9.]|localhost+>)|Extracting/ {
      gsub(/{.*/, \"\");
      gsub(/\\n.*/, \"\");
      gsub(/\=\>.*/, \"\");
      print
    }
  "
  set -o pipefail
  bash $(dirname ${0})/run-playbooks.sh | awk "${strip_debug}"
  set +o pipefail
fi

# Run the tempest tests if required
if [ "${RUN_TEMPEST}" == "yes" ]; then
  source $(dirname ${0})/run-tempest.sh
fi

exit_success
