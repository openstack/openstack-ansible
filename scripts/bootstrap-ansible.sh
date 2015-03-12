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

export GET_PIP_URL="${GET_PIP_URL:-https://mirror.rackspace.com/rackspaceprivatecloud/downloads/get-pip.py}"

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

# Use pip to install ansible
pip install ansible==1.6.10

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
