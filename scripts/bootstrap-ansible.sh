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

## Shell Opts ----------------------------------------------------------------
set -e -u -x

## Vars ----------------------------------------------------------------------
export HTTP_PROXY=${HTTP_PROXY:-""}
export HTTPS_PROXY=${HTTPS_PROXY:-""}
# The Ansible version used for testing
export ANSIBLE_PACKAGE=${ANSIBLE_PACKAGE:-"ansible-base==2.10.10"}
export ANSIBLE_ROLE_FILE=${ANSIBLE_ROLE_FILE:-"ansible-role-requirements.yml"}
export ANSIBLE_COLLECTION_FILE=${ANSIBLE_COLLECTION_FILE:-"ansible-collection-requirements.yml"}
export USER_ROLE_FILE=${USER_ROLE_FILE:-"user-role-requirements.yml"}
export USER_COLLECTION_FILE=${USER_COLLECTION_FILE:-"user-collection-requirements.yml"}
export SSH_DIR=${SSH_DIR:-"/root/.ssh"}
export DEBIAN_FRONTEND=${DEBIAN_FRONTEND:-"noninteractive"}
# check whether to install the ARA callback plugin
export SETUP_ARA=${SETUP_ARA:-"false"}

# Use pip opts to add options to the pip install command.
# This can be used to tell it which index to use, etc.
export PIP_OPTS=${PIP_OPTS:-""}

export OSA_WRAPPER_BIN="${OSA_WRAPPER_BIN:-scripts/openstack-ansible.sh}"

# This script should be executed from the root directory of the cloned repo
cd "$(dirname "${0}")/.."

## Functions -----------------------------------------------------------------
info_block "Checking for required libraries." 2> /dev/null ||
    source scripts/scripts-library.sh


## Main ----------------------------------------------------------------------
info_block "Bootstrapping System with Ansible"

# Store the clone repo root location
export OSA_CLONE_DIR="$(pwd)"

# Set the variable to the role file to be the absolute path
ANSIBLE_ROLE_FILE="$(readlink -f "${ANSIBLE_ROLE_FILE}")"
OSA_INVENTORY_PATH="$(readlink -f inventory)"
OSA_PLAYBOOK_PATH="$(readlink -f playbooks)"
OSA_ANSIBLE_PYTHON_INTERPRETER="auto"

# Create the ssh dir if needed
ssh_key_create

# Determine the distribution which the host is running on
determine_distro

# Install the base packages
case ${DISTRO_ID} in
    centos|rhel)
        dnf -y install \
          git curl autoconf gcc gcc-c++ nc \
          python3 python3-devel libselinux-python3 \
          systemd-devel pkgconf \
          openssl-devel libffi-devel \
          python3-virtualenv rsync wget
        ;;
    ubuntu|debian)
        apt-get update
        DEBIAN_FRONTEND=noninteractive apt-get -y install \
          git-core curl gcc netcat \
          python3 python3-dev \
          libssl-dev libffi-dev \
          libsystemd-dev pkg-config \
          python3-apt virtualenv \
          python3-minimal wget
        ;;
    opensuse*)
        zypper -n install -l git-core curl autoconf gcc gcc-c++ \
            netcat-openbsd python python-xml python-devel gcc \
            libffi-devel libopenssl-devel python-setuptools python-virtualenv \
            patterns-devel-python-devel_python3
        ;;
esac

# Ensure that our shell knows about the new virtualenv
hash -r virtualenv

# Load nodepool PIP mirror settings
load_nodepool_pip_opts

# Ensure we use the HTTPS/HTTP proxy with pip if it is specified
if [ -n "$HTTPS_PROXY" ]; then
  PIP_OPTS+="--proxy $HTTPS_PROXY"

elif [ -n "$HTTP_PROXY" ]; then
  PIP_OPTS+="--proxy $HTTP_PROXY"
fi

PYTHON_EXEC_PATH="${PYTHON_EXEC_PATH:-$(which python3)}"

# Obtain the SHA of the upper-constraints to use for the ansible runtime venv
UPPER_CONSTRAINTS_SHA=$(awk '/requirements_git_install_branch:/ {print $2}' playbooks/defaults/repo_packages/openstack_services.yml)

# if we are in CI, grab the u-c file from the locally cached repo, otherwise download
UPPER_CONSTRAINTS_PATH="/opt/ansible-runtime-constraints-${UPPER_CONSTRAINTS_SHA}.txt"
if [[ -z "${ZUUL_SRC_PATH+defined}" ]]; then
  wget ${UPPER_CONSTRAINTS_FILE:-"https://opendev.org/openstack/requirements/raw/${UPPER_CONSTRAINTS_SHA}/upper-constraints.txt"} -O ${UPPER_CONSTRAINTS_PATH}
else
  git --git-dir=${ZUUL_SRC_PATH}/opendev.org/openstack/requirements/.git show ${UPPER_CONSTRAINTS_SHA}:upper-constraints.txt > ${UPPER_CONSTRAINTS_PATH}
fi

export UPPER_CONSTRAINTS_FILE="file://${UPPER_CONSTRAINTS_PATH}"

if [[ -z "${SKIP_OSA_RUNTIME_VENV_BUILD+defined}" ]]; then
    build_ansible_runtime_venv
fi

# Install and export the ARA callback plugin
if [ "${SETUP_ARA}" == "true" ]; then
  setup_ara
fi

# Get current code version (this runs at the root of OSA clone)
export CURRENT_OSA_VERSION=$(cd ${OSA_CLONE_DIR}; /opt/ansible-runtime/bin/python setup.py --version)

# Ensure that Ansible binaries run from the venv
pushd /opt/ansible-runtime/bin
  for ansible_bin in $(ls -1 ansible*); do
    if [ "${ansible_bin}" == "ansible" ] || [ "${ansible_bin}" == "ansible-playbook" ]; then

      # For the 'ansible' and 'ansible-playbook' commands we want to use our wrapper
      ln -sf /usr/local/bin/openstack-ansible /usr/local/bin/${ansible_bin}

    else

      # For any other commands, we want to link directly to the binary
      ln -sf /opt/ansible-runtime/bin/${ansible_bin} /usr/local/bin/${ansible_bin}

    fi
  done
popd

# Write the OSA Ansible rc file
sed "s|OSA_INVENTORY_PATH|${OSA_INVENTORY_PATH}|g" scripts/openstack-ansible.rc > /usr/local/bin/openstack-ansible.rc
sed -i "s|OSA_PLAYBOOK_PATH|${OSA_PLAYBOOK_PATH}|g" /usr/local/bin/openstack-ansible.rc
sed -i "s|OSA_ANSIBLE_PYTHON_INTERPRETER|${OSA_ANSIBLE_PYTHON_INTERPRETER}|g" /usr/local/bin/openstack-ansible.rc
sed -i "s|OSA_ANSIBLE_FORKS|${ANSIBLE_FORKS}|g" /usr/local/bin/openstack-ansible.rc

# Create openstack ansible wrapper tool
cp -v ${OSA_WRAPPER_BIN} /usr/local/bin/openstack-ansible
# Mark the current OSA git repo clone directory, so we don't need to compute it every time.
sed -i "s|OSA_CLONE_DIR|${OSA_CLONE_DIR}|g" /usr/local/bin/openstack-ansible
# Mark the current OSA version in the wrapper, so we don't need to compute it every time.
sed -i "s|CURRENT_OSA_VERSION|${CURRENT_OSA_VERSION}|g" /usr/local/bin/openstack-ansible

# Ensure wrapper tool is executable
chmod +x /usr/local/bin/openstack-ansible

echo "openstack-ansible wrapper created."

# If the Ansible plugins are in the old location remove them.
[[ -d "/etc/ansible/plugins" ]] && rm -rf "/etc/ansible/plugins"

# Update dependent roles
if [ -f "${ANSIBLE_ROLE_FILE}" ] && [[ -z "${SKIP_OSA_ROLE_CLONE+defined}" ]]; then
    # NOTE(cloudnull): When bootstrapping we don't want ansible to interact
    #                  with our plugins by default. This change will force
    #                  ansible to ignore our plugins during this process.
    export ANSIBLE_LIBRARY="${OSA_CLONE_DIR}/playbooks/library"
    export ANSIBLE_LOOKUP_PLUGINS="/dev/null"
    export ANSIBLE_FILTER_PLUGINS="/dev/null"
    export ANSIBLE_ACTION_PLUGINS="/dev/null"
    export ANSIBLE_CALLBACK_PLUGINS="/dev/null"
    export ANSIBLE_CALLBACK_WHITELIST="/dev/null"
    export ANSIBLE_TEST_PLUGINS="/dev/null"
    export ANSIBLE_VARS_PLUGINS="/dev/null"
    export ANSIBLE_STRATEGY_PLUGINS="/dev/null"
    export ANSIBLE_CONFIG="none-ansible.cfg"
    export ANSIBLE_COLLECTIONS_PATH="/etc/ansible"

    pushd scripts
      /opt/ansible-runtime/bin/ansible-playbook get-ansible-collection-requirements.yml \
                       -e collection_file="${ANSIBLE_COLLECTION_FILE}" -e user_collection_file="${USER_COLLECTION_FILE}"

      /opt/ansible-runtime/bin/ansible-playbook get-ansible-role-requirements.yml \
                       -e role_file="${ANSIBLE_ROLE_FILE}" -e user_role_file="${USER_ROLE_FILE}"
    popd

    unset ANSIBLE_LIBRARY
    unset ANSIBLE_LOOKUP_PLUGINS
    unset ANSIBLE_FILTER_PLUGINS
    unset ANSIBLE_ACTION_PLUGINS
    unset ANSIBLE_CALLBACK_PLUGINS
    unset ANSIBLE_CALLBACK_WHITELIST
    unset ANSIBLE_TEST_PLUGINS
    unset ANSIBLE_VARS_PLUGINS
    unset ANSIBLE_STRATEGY_PLUGINS
    unset ANSIBLE_CONFIG
    unset ANSIBLE_COLLECTIONS_PATH
fi

echo "System is bootstrapped and ready for use."
