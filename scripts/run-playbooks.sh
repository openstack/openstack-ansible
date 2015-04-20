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
DEPLOY_HOST=${DEPLOY_HOST:-"yes"}
DEPLOY_LB=${DEPLOY_LB:-"yes"}
DEPLOY_INFRASTRUCTURE=${DEPLOY_INFRASTRUCTURE:-"yes"}
DEPLOY_LOGGING=${DEPLOY_LOGGING:-"yes"}
DEPLOY_OPENSTACK=${DEPLOY_OPENSTACK:-"yes"}
DEPLOY_SWIFT=${DEPLOY_SWIFT:-"yes"}
DEPLOY_TEMPEST=${DEPLOY_TEMPEST:-"no"}


## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null || source $(dirname ${0})/scripts-library.sh


## Main ----------------------------------------------------------------------
# Initiate the deployment
pushd "playbooks"
  if [ "${DEPLOY_HOST}" == "yes" ]; then
    # Install all host bits
    install_bits openstack-hosts-setup.yml
    install_bits lxc-hosts-setup.yml

    # Bring the lxc bridge down and back up to ensures the iptables rules are in-place
    # This also will ensure that the lxc dnsmasq rules are active.
    ansible hosts -m shell -a '(ifdown lxcbr0 || true); ifup lxcbr0'

    # Restart any containers that may already exist
    ansible hosts -m shell -a 'for i in $(lxc-ls); do lxc-stop -n $i; lxc-start -d -n $i; done'

    # Create the containers.
    install_bits lxc-containers-create.yml

    # Make sure there are no dead veth(s)
    # This is good when using a host with multiple times, IE: Rebuilding.
    ansible hosts -m shell -a 'lxc-system-manage veth-cleanup'

    # Flush the net cache
    # This is good when using a host with multiple times, IE: Rebuilding.
    ansible hosts -m shell -a 'lxc-system-manage flush-net-cache'

    # Log some data about the instance and the rest of the system
    log_instance_info
  fi

  if [ "${DEPLOY_LB}" == "yes" ]; then
    # Install haproxy for dev purposes only
    install_bits haproxy-install.yml
  fi

  if [ "${DEPLOY_INFRASTRUCTURE}" == "yes" ]; then
    # Install all of the infra bits
    install_bits memcached-install.yml

    # For the purposes of gating the repository of python wheels are built within
    # the environment. Normal installation would simply clone the upstream mirror.
    install_bits repo-server.yml
    install_bits repo-build.yml

    install_bits galera-install.yml
    install_bits rabbitmq-install.yml
    install_bits utility-install.yml

    if [ "${DEPLOY_LOGGING}" == "yes" ]; then
      install_bits rsyslog-install.yml
    fi
  fi

  if [ "${DEPLOY_OPENSTACK}" == "yes" ]; then
    # install all of the compute Bits
    install_bits os-keystone-install.yml
    install_bits os-glance-install.yml
    install_bits os-cinder-install.yml
    install_bits os-nova-install.yml
    install_bits os-neutron-install.yml
    install_bits os-heat-install.yml
    install_bits os-horizon-install.yml
  fi

  if [ "${DEPLOY_SWIFT}" == "yes" ]; then
    if [ "${DEPLOY_OPENSTACK}" == "no" ]; then
      # When os install is no, make sure we still have keystone for use in swift.
      install_bits os-keystone-install.yml
    fi
    # install all of the swift Bits
    install_bits os-swift-install.yml
  fi

  if [ "${DEPLOY_TEMPEST}" == "yes" ]; then
    # Deploy tempest
    install_bits os-tempest-install.yml
  fi

popd

# print the report data
set +x && print_report
