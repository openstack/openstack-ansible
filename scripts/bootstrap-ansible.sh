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

set -e -u -v +x

## Variables -----------------------------------------------------------------

ANSIBLE_DEPLOY_METHOD="pip"
ANSIBLE_GIT_REPO="https://github.com/ansible/ansible"
ANSIBLE_GIT_RELEASE="${ANSIBLE_GIT_RELEASE:-1.6.10}"
ANSIBLE_WORKING_DIR="/opt/ansible_v${ANSIBLE_GIT_RELEASE}"
GET_PIP_URL="${GET_PIP_URL:-https://mirror.rackspace.com/rackspaceprivatecloud/downloads/get-pip.py}"

## Functions -----------------------------------------------------------------

info_block "Checking for required libraries." || source $(dirname ${0})/scripts-library.sh

## Main ----------------------------------------------------------------------

# Enable logging of all commands executed
set -x

# Install the base packages
apt-get update && apt-get -y install git python-all python-dev curl

# Install pip
if [ ! "$(which pip)" ];then
    curl ${GET_PIP_URL} > /opt/get-pip.py
    python2 /opt/get-pip.py || python /opt/get-pip.py
fi

if [ "${ANSIBLE_DEPLOY_METHOD}" == "git" ]; then
  # If the working directory exists remove it
  if [ -d "${ANSIBLE_WORKING_DIR}" ];then
    rm -rf "${ANSIBLE_WORKING_DIR}"
  fi
  # Clone down the base ansible source
  git clone "${ANSIBLE_GIT_REPO}" "${ANSIBLE_WORKING_DIR}"
  pushd "${ANSIBLE_WORKING_DIR}"
    git checkout "v${ANSIBLE_GIT_RELEASE}"
    git submodule update --init --recursive
  popd
  # Install requirements if there are any
  if [ -f "${ANSIBLE_WORKING_DIR}/requirements.txt" ];then
    pip2 install -r "${ANSIBLE_WORKING_DIR}/requirements.txt" || pip install -r "${ANSIBLE_WORKING_DIR}/requirements.txt"
  fi
  # Install ansible
  pip2 install "${ANSIBLE_WORKING_DIR}" || pip install "${ANSIBLE_WORKING_DIR}"
else
  # Use pip to install ansible
  pip install ansible==${ANSIBLE_GIT_RELEASE}
fi

set +x
info_block "Ansible is now bootstrapped and ready for use."

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

# Openstack wrapper tool to ease the use of ansible with multiple variable files.

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Discover the variable files.
VAR1="\$(for i in \$(ls /etc/*_deploy/*user_*.yml); do echo -ne "-e @\$i "; done)"

# Provide information on the discovered variables.
echo -e "\n--- [ Variable files ] ---\n \"\${VAR1}\""

# Run the ansible playbook command.
\$(which ansible-playbook) \${VAR1} \$@
EOF

set -x
# Ensure wrapper tool is executable
chmod +x /usr/local/bin/openstack-ansible

# Enable logging of all commands executed
set +x

info_block "The openstack-ansible convenience script has been created."
