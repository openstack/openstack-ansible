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

ADMIN_PASSWORD=${ADMIN_PASSWORD:-"secrete"}
BOOTSTRAP_ANSIBLE=${BOOTSTRAP_ANSIBLE:-"yes"}
BOOTSTRAP_AIO=${BOOTSTRAP_AIO:-"yes"}
DEPLOY_SWIFT=${DEPLOY_SWIFT:-"yes"}
DEPLOY_TEMPEST=${DEPLOY_TEMPEST:-"no"}
RUN_PLAYBOOKS=${RUN_PLAYBOOKS:-"yes"}
RUN_TEMPEST=${RUN_TEMPEST:-"no"}
CONFIG_PREFIX=${CONFIG_PREFIX:-"rpc"}
PLAYBOOK_DIRECTORY=${PLAYBOOK_DIRECTORY:-"${CONFIG_PREFIX}_deployment"}
ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-"--forks 10 -vvvv"}

## Functions -----------------------------------------------------------------

info_block "Checking for required libraries." || source $(dirname ${0})/scripts-library.sh

## Main ----------------------------------------------------------------------

# ensure that the current kernel can support vxlan
if ! modprobe vxlan; then
  MINIMUM_KERNEL_VERSION=$(awk '/required_kernel/ {print $2}' ${PLAYBOOK_DIRECTORY}/inventory/group_vars/all.yml)
  info_block "A minimum kernel version of ${MINIMUM_KERNEL_VERSION} is required for vxlan support."
  exit 1
fi

# Get initial host information and reset verbosity
set +x && get_instance_info && set -x

# Bootstrap ansible if required
if [ "${BOOTSTRAP_ANSIBLE}" == "yes" ]; then
  source $(dirname ${0})/bootstrap-ansible.sh
fi

# Bootstrap an AIO setup if required
if [ "${BOOTSTRAP_AIO}" == "yes" ]; then
  source $(dirname ${0})/bootstrap-aio.sh
fi

# Get initial host information and reset verbosity
set +x && get_instance_info && set -x

# Install requirements
pip2 install -r requirements.txt || pip install -r requirements.txt

# Copy the base etc files
if [ ! -d "/etc/${CONFIG_PREFIX}_deploy" ];then
  cp -R etc/${CONFIG_PREFIX}_deploy /etc/

  # Generate the passwords
  USER_VARS_PATH="/etc/${CONFIG_PREFIX}_deploy/user_variables.yml"

  # Adjust any defaults to suit the AIO
  # commented lines are removed by pw-token gen, so this substitution must
  # happen prior.
  sed -i "s/# nova_virt_type:.*/nova_virt_type: qemu/" ${USER_VARS_PATH}

  ./scripts/pw-token-gen.py --file ${USER_VARS_PATH}


  # change the generated passwords for the OpenStack (admin) and Kibana (kibana) accounts
  sed -i "s/keystone_auth_admin_password:.*/keystone_auth_admin_password: ${ADMIN_PASSWORD}/" ${USER_VARS_PATH}
  sed -i "s/kibana_password:.*/kibana_password: ${ADMIN_PASSWORD}/" ${USER_VARS_PATH}

  if [ "${DEPLOY_SWIFT}" == "yes" ]; then
    # ensure that glance is configured to use swift
    sed -i "s/glance_default_store:.*/glance_default_store: swift/" ${USER_VARS_PATH}
    sed -i "s/glance_swift_store_auth_address:.*/glance_swift_store_auth_address: '{{ auth_identity_uri }}'/" ${USER_VARS_PATH}
    sed -i "s/glance_swift_store_container:.*/glance_swift_store_container: glance_images/" ${USER_VARS_PATH}
    sed -i "s/glance_swift_store_key:.*/glance_swift_store_key: '{{ glance_service_password }}'/" ${USER_VARS_PATH}
    sed -i "s/glance_swift_store_region:.*/glance_swift_store_region: RegionOne/" ${USER_VARS_PATH}
    sed -i "s/glance_swift_store_user:.*/glance_swift_store_user: 'service:glance'/" ${USER_VARS_PATH}
  fi

  if [ "${BOOTSTRAP_AIO}" == "yes" ]; then
    # adjust the default user configuration for the AIO
    USER_CONFIG_PATH="/etc/${CONFIG_PREFIX}_deploy/${CONFIG_PREFIX}_user_config.yml"
    ENV_CONFIG_PATH="/etc/${CONFIG_PREFIX}_deploy/${CONFIG_PREFIX}_environment.yml"
    sed -i "s/environment_version: .*/environment_version: $(md5sum ${ENV_CONFIG_PATH} | awk '{print $1}')/" ${USER_CONFIG_PATH}
    SERVER_IP_ADDRESS="$(ip -o -4 addr show dev eth0 | awk -F '[ /]+' '/global/ {print $4}')"
    sed -i "s/external_lb_vip_address: .*/external_lb_vip_address: ${SERVER_IP_ADDRESS}/" ${USER_CONFIG_PATH}
    if [ "${DEPLOY_SWIFT}" == "yes" ]; then
      # add the swift proxy host network provider map
      sed -i 's/# - swift_proxy/- swift_proxy/' ${USER_CONFIG_PATH}
    fi
  fi
fi

# Run the ansible playbooks if required
if [ "${RUN_PLAYBOOKS}" == "yes" ]; then
  source $(dirname ${0})/run-playbooks.sh
fi

# Run the tempest tests if required
if [ "${RUN_TEMPEST}" == "yes" ]; then
  source $(dirname ${0})/run-tempest.sh
fi
