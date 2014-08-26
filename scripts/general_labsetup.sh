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
#
# (c) 2014, Kevin Carter <kevin.carter@rackspace.com>

set -e -u -v -x
LAB=${1}
# Go to rpc_deployment directory
pushd ../rpc_deployment

# Build all of the containers
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 setup/build-containers.yml

# Install Lab bits
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 setup/general_labsetup.yml

# Build out HAProxy
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 setup/haproxy.yml

# install all of Keystone
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 openstack/keystone.yml

# install all of Glance
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 openstack/glance-all.yml

# install all of Cinder
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 openstack/cinder-all.yml

# install all of Heat
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 openstack/heat-all.yml

# install all of Neutron
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 openstack/neutron-all.yml

# Install All of Nova
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 openstack/nova-all.yml

# Install All of Horizon
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 openstack/horizon.yml

# Restart Everything
ansible-playbook -i inventory/${LAB}.yml \
                 -e dinv=inventory/host_vars/${LAB}.yml \
                 -e @inventory/overrides/${LAB}.yml \
                 setup/restart-containers.yml

popd
