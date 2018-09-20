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
export ANSIBLE_PACKAGE=${ANSIBLE_PACKAGE:-"ansible==2.4.4.0"}
export ANSIBLE_ROLE_FILE=${ANSIBLE_ROLE_FILE:-"ansible-role-requirements.yml"}
export SSH_DIR=${SSH_DIR:-"/root/.ssh"}
export DEBIAN_FRONTEND=${DEBIAN_FRONTEND:-"noninteractive"}

# Set the role fetch mode to any option [galaxy, git-clone]
export ANSIBLE_ROLE_FETCH_MODE=${ANSIBLE_ROLE_FETCH_MODE:-git-clone}

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

# Create the ssh dir if needed
ssh_key_create

# Determine the distribution which the host is running on
determine_distro

# Prefer dnf over yum for CentOS.
which dnf &>/dev/null && RHT_PKG_MGR='dnf' || RHT_PKG_MGR='yum'

# Install the base packages
case ${DISTRO_ID} in
    centos|rhel)
        $RHT_PKG_MGR -y install \
          git curl autoconf gcc gcc-c++ nc \
          python2 python2-devel \
          openssl-devel libffi-devel \
          libselinux-python
          # CentOS base does not include a recent
          # enough version of virtualenv or pip,
          # so we do not bother trying to install
          # them.
        ;;
    ubuntu)
        apt-get update
        DEBIAN_FRONTEND=noninteractive apt-get -y install \
          git-core curl gcc netcat \
          python-minimal python-dev \
          libssl-dev libffi-dev \
          python-apt \
          python-virtualenv
        ;;
    opensuse)
        zypper -n install -l git-core curl autoconf gcc gcc-c++ \
            netcat-openbsd python python-xml python-devel gcc \
            libffi-devel libopenssl-devel \
            python-virtualenv
        # Leap ships with python3.4 which is not supported by ansible and as
        # such we are using python2
        # See https://github.com/ansible/ansible/issues/24180
        PYTHON_EXEC_PATH="/usr/bin/python2"
        alternatives --set pip /usr/bin/pip2.7 || true
        ;;
esac

# Ensure we use the HTTPS/HTTP proxy with pip if it is specified
PIP_OPTS=""
if [ -n "$HTTPS_PROXY" ]; then
  PIP_OPTS="--proxy $HTTPS_PROXY"

elif [ -n "$HTTP_PROXY" ]; then
  PIP_OPTS="--proxy $HTTP_PROXY"
fi


# Figure out the version of python is being used
PYTHON_EXEC_PATH="${PYTHON_EXEC_PATH:-$(which python2)}"
PYTHON_VERSION="$($PYTHON_EXEC_PATH -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"

# Use https when Python with native SNI support is available
UPPER_CONSTRAINTS_PROTO=$([ "$PYTHON_VERSION" == $(echo -e "$PYTHON_VERSION\n2.7.9" | sort -V | tail -1) ] && echo "https" || echo "http")

# Set the location of the constraints to use for all pip installations
export UPPER_CONSTRAINTS_FILE=${UPPER_CONSTRAINTS_FILE:-"$UPPER_CONSTRAINTS_PROTO://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?id=$(awk '/requirements_git_install_branch:/ {print $2}' playbooks/defaults/repo_packages/openstack_services.yml)"}

# Install virtualenv if it is not already installed,
# but also make sure it is at least version 13.x or above
# so that it supports using the no-pip, no-setuptools
# and no-wheels options (the last one was added in v13.0.0).
VIRTUALENV_VERSION=$(virtualenv --version 2>/dev/null | cut -d. -f1)
if [[ "${VIRTUALENV_VERSION}" -lt "13" ]]; then

  # Install pip on the host if it is not already installed,
  # but also make sure that it is at least version 7.x or above
  # so that it supports the use of the constraint option which
  # was added in pip 7.1.
  PIP_VERSION=$(pip --version 2>/dev/null | awk '{print $2}' | cut -d. -f1)
  if [[ "${PIP_VERSION}" -lt "7" ]]; then
    get_pip ${PYTHON_EXEC_PATH}
    # Ensure that our shell knows about the new pip
    hash -r pip
  fi

  pip install ${PIP_OPTS} \
    --constraint ${UPPER_CONSTRAINTS_FILE} \
    virtualenv \
    || pip install ${PIP_OPTS} \
         --constraint ${UPPER_CONSTRAINTS_FILE} \
         --isolated \
         virtualenv
  # Ensure that our shell knows about the new pip
  hash -r virtualenv
fi

# Create a Virtualenv for the Ansible runtime
if [ -f "/opt/ansible-runtime/bin/python" ]; then
  VENV_PYTHON_VERSION="$(/opt/ansible-runtime/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
  if [ "$PYTHON_VERSION" != "$VENV_PYTHON_VERSION" ]; then
    rm -rf /opt/ansible-runtime
  fi
fi
virtualenv --python=${PYTHON_EXEC_PATH} \
           --clear \
           --no-pip --no-setuptools --no-wheel \
           /opt/ansible-runtime

# Install pip, setuptools and wheel into the venv
get_pip /opt/ansible-runtime/bin/python2

# The vars used to prepare the Ansible runtime venv
PIP_OPTS+=" --constraint global-requirement-pins.txt"
PIP_OPTS+=" --constraint ${UPPER_CONSTRAINTS_FILE}"

# When upgrading there will already be a pip.conf file locking pip down to the
# repo server, in such cases it may be necessary to use --isolated because the
# repo server does not meet the specified requirements.

# Install ansible and the other required packages
${PIP_COMMAND} install ${PIP_OPTS} -r requirements.txt ${ANSIBLE_PACKAGE} \
  || ${PIP_COMMAND} install --isolated ${PIP_OPTS} -r requirements.txt ${ANSIBLE_PACKAGE}

# Install our osa_toolkit code from the current checkout
$PIP_COMMAND install -e .

# Add SELinux support to the venv
if [ -d "/usr/lib64/python2.7/site-packages/selinux/" ]; then
  rsync -avX /usr/lib64/python2.7/site-packages/selinux/ /opt/ansible-runtime/lib64/python2.7/selinux/
fi

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


# Create openstack ansible wrapper tool
cat > /usr/local/bin/openstack-ansible <<EOF
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

# OpenStack wrapper tool to ease the use of ansible with multiple variable files.

export PATH="/opt/ansible-runtime/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}"

function info() {
    if [ "\${ANSIBLE_NOCOLOR:-0}" -eq "1" ]; then
      echo -e "\${@}"
    else
      echo -e "\e[0;35m\${@}\e[0m"
    fi
}

# Figure out which Ansible binary was executed
RUN_CMD=\$(basename \${0})

# Apply the OpenStack-Ansible configuration selectively.
if [[ "\${PWD}" == *"${OSA_CLONE_DIR}"* ]] || [ "\${RUN_CMD}" == "openstack-ansible" ]; then

  # Source the Ansible configuration.
  . /usr/local/bin/openstack-ansible.rc

  # Load userspace group vars
  if [[ -d /etc/openstack_deploy/group_vars || -d /etc/openstack_deploy/host_vars ]]; then
     if [[ ! -f /etc/openstack_deploy/inventory.ini ]]; then
        echo '[all]' > /etc/openstack_deploy/inventory.ini
     fi
  fi

  # Check whether there are any user configuration files
  if ls -1 /etc/openstack_deploy/user_*.yml &> /dev/null; then

    # Discover the variable files.
    VAR1="\$(for i in \$(ls /etc/openstack_deploy/user_*.yml); do echo -ne "-e @\$i "; done)"

    # Provide information on the discovered variables.
    info "Variable files: \"\${VAR1}\""

  fi

else

  # If you're not executing 'openstack-ansible' and are
  # not in the OSA git clone root, then do not source
  # the configuration and do not add extra vars.
  VAR1=""

fi

# Execute the Ansible command.
if [ "\${RUN_CMD}" == "openstack-ansible" ] || [ "\${RUN_CMD}" == "ansible-playbook" ]; then
  ansible-playbook "\${@}" \${VAR1}
  PLAYBOOK_RC="\$?"
  if [[ "\${PLAYBOOK_RC}" -ne "0" ]]; then
    echo -e "\nEXIT NOTICE [Playbook execution failure] **************************************"
  else
    echo -e "\nEXIT NOTICE [Playbook execution success] **************************************"
  fi
  echo "==============================================================================="
  exit "\${PLAYBOOK_RC}"
else
  \${RUN_CMD} "\${@}"
fi
EOF

# Ensure wrapper tool is executable
chmod +x /usr/local/bin/openstack-ansible

echo "openstack-ansible wrapper created."

# If the Ansible plugins are in the old location remove them.
[[ -d "/etc/ansible/plugins" ]] && rm -rf "/etc/ansible/plugins"

# Update dependent roles
if [ -f "${ANSIBLE_ROLE_FILE}" ]; then
  if [[ "${ANSIBLE_ROLE_FETCH_MODE}" == 'galaxy' ]];then
    # Pull all required roles.
    ansible-galaxy install --role-file="${ANSIBLE_ROLE_FILE}" \
                           --force
  elif [[ "${ANSIBLE_ROLE_FETCH_MODE}" == 'git-clone' ]];then
    # NOTE(cloudnull): When bootstrapping we don't want ansible to interact
    #                  with our plugins by default. This change will force
    #                  ansible to ignore our plugins during this process.
    export ANSIBLE_LIBRARY="/dev/null"
    export ANSIBLE_LOOKUP_PLUGINS="/dev/null"
    export ANSIBLE_FILTER_PLUGINS="/dev/null"
    export ANSIBLE_ACTION_PLUGINS="/dev/null"
    export ANSIBLE_CALLBACK_PLUGINS="/dev/null"
    export ANSIBLE_CALLBACK_WHITELIST="/dev/null"
    export ANSIBLE_TEST_PLUGINS="/dev/null"
    export ANSIBLE_VARS_PLUGINS="/dev/null"
    export ANSIBLE_STRATEGY_PLUGINS="/dev/null"
    export ANSIBLE_CONFIG="none-ansible.cfg"

    pushd tests
      /opt/ansible-runtime/bin/ansible-playbook get-ansible-role-requirements.yml \
                       -i ${OSA_CLONE_DIR}/tests/test-inventory.ini \
                       -e role_file="${ANSIBLE_ROLE_FILE}"
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
  else
    echo "Please set the ANSIBLE_ROLE_FETCH_MODE to either of the following options ['galaxy', 'git-clone']"
    exit 99
  fi
fi

echo "System is bootstrapped and ready for use."
