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

set -e -u +x

## Variables -----------------------------------------------------------------
export REPO_URL=${REPO_URL:-"https://github.com/stackforge/os-ansible-deployment.git"}
export REPO_BRANCH=${REPO_BRANCH:-"master"}
export WORKING_FOLDER=${WORKING_FOLDER:-"/opt/stackforge/os-ansible-deployment"}
# On normal AIO build the script should do everything possible to try for success
export MAX_RETRIES=${MAX_RETRIES:-"5"}


## Main ----------------------------------------------------------------------

# set verbosity
set -x

# install git so that we can fetch the repo
apt-get update && apt-get install -y git

# fetch the repo
git clone -b ${REPO_BRANCH} ${REPO_URL} ${WORKING_FOLDER}

# run the same aio build script that is used in the OpenStack CI pipeline
cd ${WORKING_FOLDER}

bash scripts/gate-check-commit.sh

# put a motd in place to help the user know what stuff is accessible once the build is complete
cat > /etc/update-motd.d/20-openstack<< EOF
#!/usr/bin/env bash
echo ""
echo "############ os-ansible-deployment all-in-one build #############"
echo ""
echo " OpenStack Services are now listening on $(ip -o -4 addr show dev eth0 | awk -F '[ /]+' '/global/ {print $4}')"
echo ""
EOF
chmod +x /etc/update-motd.d/20-openstack

# put an motd in place to help the user know how to restart galera after reboot
cat > /etc/update-motd.d/21-galera<< EOF
#!/usr/bin/env bash
echo ""
echo "If this server has been rebooted, you will need to re-bootstrap"
echo "Galera to get the cluster operational. To do this execute:"
echo ""
echo "cd $(pwd)/playbooks"
echo "openstack-ansible galera-install --tags galera-bootstrap"
echo ""
EOF
chmod +x /etc/update-motd.d/21-galera
