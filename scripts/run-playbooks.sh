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

set -e -u -v +x

## Variables -----------------------------------------------------------------

DEPLOY_HOST=${DEPLOY_HOST:-"yes"}
DEPLOY_LB=${DEPLOY_LB:-"yes"}
DEPLOY_INFRASTRUCTURE=${DEPLOY_INFRASTRUCTURE:-"yes"}
DEPLOY_LOGGING=${DEPLOY_LOGGING:-"yes"}
DEPLOY_OPENSTACK=${DEPLOY_OPENSTACK:-"yes"}
DEPLOY_SWIFT=${DEPLOY_SWIFT:-"yes"}
DEPLOY_RPC_SUPPORT=${DEPLOY_RPC_SUPPORT:-"yes"}
DEPLOY_TEMPEST=${DEPLOY_TEMPEST:-"no"}
ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-"--forks 10"}
PLAYBOOK_DIRECTORY=${PLAYBOOK_DIRECTORY:-"rpc_deployment"}

## Functions -----------------------------------------------------------------

info_block "Checking for required libraries." || source $(dirname ${0})/scripts-library.sh

function install_bits() {
  successerator openstack-ansible ${ANSIBLE_PARAMETERS} playbooks/$@
}

## Main ----------------------------------------------------------------------

# Initiate the deployment
pushd ${PLAYBOOK_DIRECTORY}
  if [ "${DEPLOY_HOST}" == "yes" ]; then
    # Install all host bits
    install_bits setup/host-setup.yml
  fi

  if [ "${DEPLOY_LB}" == "yes" ]; then
    # Install haproxy for dev purposes only
    install_bits infrastructure/haproxy-install.yml
  fi
  if [ "${DEPLOY_INFRASTRUCTURE}" == "yes" ]; then
    # Install all of the infra bits
    install_bits infrastructure/memcached-install.yml
    install_bits infrastructure/galera-install.yml
    install_bits infrastructure/rabbit-install.yml
    if [ "${DEPLOY_LOGGING}" == "yes" ]; then
      install_bits infrastructure/rsyslog-install.yml
      install_bits infrastructure/elasticsearch-install.yml
      install_bits infrastructure/logstash-install.yml
      install_bits infrastructure/kibana-install.yml
      install_bits infrastructure/es2unix-install.yml
    fi
  fi

  if [ "${DEPLOY_OPENSTACK}" == "yes" ]; then
    # install all of the OpenStack Bits
    if [ -f playbooks/openstack/openstack-common.yml ]; then
      # cater for 9.x.x release (icehouse)
      install_bits openstack/openstack-common.yml
    fi
    if [ -f playbooks/openstack/keystone-all.yml ]; then
      # cater for 10.x.x release (juno) onwards
      install_bits openstack/keystone-all.yml
    else
      # cater for 9.x.x release (icehouse)
      install_bits openstack/keystone.yml
      install_bits openstack/keystone-add-all-services.yml
    fi
    if [ "${DEPLOY_SWIFT}" == "yes" ]; then
      install_bits openstack/swift-all.yml
    fi
    install_bits openstack/glance-all.yml
    install_bits openstack/heat-all.yml
    install_bits openstack/nova-all.yml
    install_bits openstack/neutron-all.yml
    install_bits openstack/cinder-all.yml
    install_bits openstack/horizon-all.yml
    if [ -f playbooks/openstack/utility-all.yml ]; then
      # cater for 10.x.x release (juno) onwards
      install_bits openstack/utility-all.yml
    elif [ -f playbooks/openstack/utility.yml ]; then
      # cater for 9.x.x release (icehouse)
      install_bits openstack/utility.yml
    fi
    if [ "${DEPLOY_TEMPEST}" == "yes" ]; then
      # Deploy tempest
      install_bits openstack/tempest.yml
    fi
  fi
  if [ "${DEPLOY_RPC_SUPPORT}" == "yes" ]; then
    if [ -f playbooks/openstack/rpc-support-all.yml ]; then
      # cater for 10.x.x release (juno) onwards
      install_bits openstack/rpc-support-all.yml
    elif [ -f playbooks/openstack/rpc-support.yml ]; then
      # cater for 9.x.x release (icehouse)
      install_bits openstack/rpc-support.yml
    fi
  fi
  if [ "${DEPLOY_INFRASTRUCTURE}" == "yes" ] && [ "${DEPLOY_LOGGING}" == "yes" ]; then
    # Configure Rsyslog
    install_bits infrastructure/rsyslog-config.yml
  fi
popd
