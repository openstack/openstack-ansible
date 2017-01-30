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
export ANSIBLE_PACKAGE=${ANSIBLE_PACKAGE:-"git+https://github.com/ansible/ansible@e85f3f44610fa454c80da6b0f5ae84e3887a6955"} # stable-2.2 post 2.2.1.0 with yaml fix
export ANSIBLE_ROLE_FILE=${ANSIBLE_ROLE_FILE:-"ansible-role-requirements.yml"}
export SSH_DIR=${SSH_DIR:-"/root/.ssh"}
export DEBIAN_FRONTEND=${DEBIAN_FRONTEND:-"noninteractive"}
PYTHON_EXEC_PATH="$(which python2 || which python)"
PYTHON_VERSION="$($PYTHON_EXEC_PATH -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
# Use https when Python with native SNI support is available
UPPER_CONSTRAINTS_PROTO=$([ "$PYTHON_VERSION" == $(echo -e "$PYTHON_VERSION\n2.7.9" | sort -V | tail -1) ] && echo "https" || echo "http")
# Set the location of the constraints to use for all pip installations
export UPPER_CONSTRAINTS_FILE=${UPPER_CONSTRAINTS_FILE:-"$UPPER_CONSTRAINTS_PROTO://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?id=$(awk '/requirements_git_install_branch:/ {print $2}' playbooks/defaults/repo_packages/openstack_services.yml)"}
# Set the role fetch mode to any option [galaxy, git-clone]
export ANSIBLE_ROLE_FETCH_MODE=${ANSIBLE_ROLE_FETCH_MODE:-galaxy}
# virtualenv vars
VIRTUALENV_OPTIONS="--always-copy"

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
OSA_INVENTORY_PATH="$(readlink -f playbooks/inventory)"

# Create the ssh dir if needed
ssh_key_create

# Determine the distribution which the host is running on
determine_distro

# Install the base packages
case ${DISTRO_ID} in
    centos|rhel)
        yum -y install git python2 curl autoconf gcc-c++ \
          python2-devel gcc libffi-devel nc openssl-devel \
          python-pyasn1 pyOpenSSL python-ndg_httpsclient \
          python-netaddr python-prettytable python-crypto PyYAML \
          python-virtualenv
          VIRTUALENV_OPTIONS=""
        ;;
    ubuntu)
        apt-get update
        DEBIAN_FRONTEND=noninteractive apt-get -y install \
          git python-all python-dev curl python2.7-dev build-essential \
          libssl-dev libffi-dev netcat python-requests python-openssl python-pyasn1 \
          python-netaddr python-prettytable python-crypto python-yaml \
          python-virtualenv
        ;;
esac

# NOTE(mhayden): Ubuntu 16.04 needs python-ndg-httpsclient for SSL SNI support.
#                This package is not needed in Ubuntu 14.04 and isn't available
#                there as a package.
if [[ "${DISTRO_ID}" == 'ubuntu' ]] && [[ "${DISTRO_VERSION_ID}" == '16.04' ]]; then
  DEBIAN_FRONTEND=noninteractive apt-get -y install python-ndg-httpsclient
fi

# Install pip
get_pip

# Ensure we use the HTTPS/HTTP proxy with pip if it is specified
PIP_OPTS=""
if [ -n "$HTTPS_PROXY" ]; then
  PIP_OPTS="--proxy $HTTPS_PROXY"
elif [ -n "$HTTP_PROXY" ]; then
  PIP_OPTS="--proxy $HTTP_PROXY"
fi

# Create a Virtualenv for the Ansible runtime
virtualenv --clear ${VIRTUALENV_OPTIONS} --system-site-packages --python="${PYTHON_EXEC_PATH}" /opt/ansible-runtime

# The vars used to prepare the Ansible runtime venv
PIP_OPTS+=" --upgrade"
PIP_COMMAND="/opt/ansible-runtime/bin/pip"

# When upgrading there will already be a pip.conf file locking pip down to the
# repo server, in such cases it may be necessary to use --isolated because the
# repo server does not meet the specified requirements.

# Ensure we are running the required versions of pip, wheel and setuptools
${PIP_COMMAND} install ${PIP_OPTS} ${PIP_INSTALL_OPTIONS} || ${PIP_COMMAND} install ${PIP_OPTS} --isolated ${PIP_INSTALL_OPTIONS}

# Set the constraints now that we know we're using the right version of pip
PIP_OPTS+=" --constraint global-requirement-pins.txt --constraint ${UPPER_CONSTRAINTS_FILE}"

# Install the required packages for ansible
$PIP_COMMAND install $PIP_OPTS -r requirements.txt ${ANSIBLE_PACKAGE} || $PIP_COMMAND install --isolated $PIP_OPTS -r requirements.txt ${ANSIBLE_PACKAGE}

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

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}"

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
  /opt/ansible-runtime/bin/ansible-playbook "\${@}" \${VAR1}
else
  /opt/ansible-runtime/bin/\${RUN_CMD} "\${@}"
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
    pushd tests
      ansible-playbook get-ansible-role-requirements.yml \
                       -i ${OSA_CLONE_DIR}/tests/test-inventory.ini \
                       -e role_file="${ANSIBLE_ROLE_FILE}"
    popd
  else
    echo "Please set the ANSIBLE_ROLE_FETCH_MODE to either of the following options ['galaxy', 'git-clone']"
    exit 99
  fi
fi

echo "System is bootstrapped and ready for use."
