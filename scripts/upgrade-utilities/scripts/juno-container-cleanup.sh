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

## Shell Opts ----------------------------------------------------------------
set -e -u -v

export PLAYBOOK_PATH="${PLAYBOOK_PATH:-$(dirname $(dirname $(dirname $(dirname $(readlink -f $0)))))}"
export SCRIPTS_PATH="${SCRIPTS_PATH:-$(dirname $(dirname $(dirname $(readlink -f $0))))}"

function remove_inv_items {
  ${SCRIPTS_PATH}/inventory-manage.py -f /etc/openstack_deploy/openstack_inventory.json -r "$1"
}

function get_inv_items {
  ${SCRIPTS_PATH}/inventory-manage.py -f /etc/openstack_deploy/openstack_inventory.json -l | grep -w ".*$1"
}

function remove_inv_groups {
  ${SCRIPTS_PATH}/inventory-manage.py -f /etc/openstack_deploy/openstack_inventory.json --remove-group "$1"
}

# Remove containers that we no longer need
pushd ${PLAYBOOK_PATH}/playbooks
  # Before interacting with any containers make sure that the libs are updated
  openstack-ansible lxc-hosts-setup.yml

  # Clean up post destroy
  openstack-ansible lxc-containers-destroy.yml -e container_group="rsyslog_all"
  openstack-ansible lxc-containers-destroy.yml -e container_group="nova_api_ec2"
  openstack-ansible lxc-containers-destroy.yml -e container_group="nova_spice_console"

  # Remove the dead container types from inventory
  REMOVED_CONTAINERS=""
  REMOVED_CONTAINERS+="$(get_inv_items 'rsyslog_container' | awk '{print $2}') "
  REMOVED_CONTAINERS+="$(get_inv_items 'nova_api_ec2' | awk '{print $2}') "
  REMOVED_CONTAINERS+="$(get_inv_items 'nova_spice_console' | awk '{print $2}') "

  # Remove unused groups from inventory
  REMOVED_GROUPS="nova_api_ec2 nova_api_ec2_container nova_spice_console nova_spice_console_container rabbit rabbit_all"
  for i in ${REMOVED_GROUPS}; do
    remove_inv_groups $i
  done

  for i in ${REMOVED_CONTAINERS};do
    remove_inv_items $i
  done

  # Ensure the destruction of the containers we don't need.
  ansible hosts \
          -m shell \
          -a 'for i in $(lxc-ls | grep -e "rsyslog" -e "nova_api_ec2" -e "nova_spice_console"); do lxc-destroy -fn $i; done'

  # Ensure that apt-transport-https is installed everywhere before doing anything else,
  #  forces True as containers may not exist at this point.
  ansible "hosts:all_containers" \
          -m "apt" \
          -a "update_cache=yes name=apt-transport-https" || true

  # Hunt for and remove any rpc_release link files from pip, forces True as
  #  containers may not exist at this point.
  ansible "hosts:all_containers" \
          -m "file" \
          -a "path=/root/.pip/links.d/rpc_release.link state=absent" || true

  # Remove MariaDB repositories left over from Juno, forces True as
  #  containers may not exist at this point.
  ansible "hosts:all_containers" \
          -m "shell" \
          -a "sed -i '/http:.*maria.*/d' /etc/apt/sources.list.d/*" || true

  ansible haproxy_hosts \
          -m "file" \
          -a "path=/etc/haproxy/conf.d/nova_api_ec2 state=absent" || true

  ansible haproxy_hosts \
          -m "file" \
          -a "path=/etc/haproxy/conf.d/nova_spice_console state=absent" || true
popd
