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
# ----------------------------------------------------------------------------
#
# This script configures an all-in-one (AIO) deployment. For more details, see
# the quick start documentation for openstack-ansible:
#
#   http://docs.openstack.org/developer/openstack-ansible/developer-docs/quickstart-aio.html#running-an-aio-build-in-one-step

## Shell Opts ----------------------------------------------------------------

set -e -u +x

## Variables -----------------------------------------------------------------

export REPO_URL=${REPO_URL:-"https://github.com/openstack/openstack-ansible.git"}
export REPO_BRANCH=${REPO_BRANCH:-"master"}
export WORKING_FOLDER=${WORKING_FOLDER:-"/opt/openstack-ansible"}

## Main ----------------------------------------------------------------------

# Set verbosity
set -x

# Install git so that we can fetch various git repositories.
# Note: the redirect of stdin to /dev/null is necessary for when this script is
# run as part of a curl-pipe-shell. otherwise apt-get will consume the rest of
# this file as if it was its own stdin (despite using -y to skip interaction).
apt-get update && apt-get install -y git < /dev/null

# Fetch the openstack-ansible repository.
git clone -b ${REPO_BRANCH} ${REPO_URL} ${WORKING_FOLDER}

# Change into the expected root directory.
cd ${WORKING_FOLDER}

# Start by bootstrapping Ansible from source.
source scripts/bootstrap-ansible.sh

# Next, bootstrap the AIO host.
source scripts/bootstrap-aio.sh

# Finally, run all of the playbooks.
bash scripts/run-playbooks.sh

# Add a MOTD to explain to the deployer what is accessible once the build
# is complete.
cat > /etc/update-motd.d/20-openstack<< EOF
#!/usr/bin/env bash
echo ""
echo "############ openstack-ansible all-in-one build #############"
echo ""
echo " OpenStack Services are now listening on $(ip -o -4 addr show dev eth0 | awk -F '[ /]+' '/global/ {print $4}')"
echo ""
EOF
chmod +x /etc/update-motd.d/20-openstack

# Add a MOTD to explain to the deployer how to restart galera properly after a
# reboot.
cat > /etc/update-motd.d/21-galera<< EOF
#!/usr/bin/env bash
echo ""
echo "If this server has been rebooted, you will need to re-bootstrap"
echo "Galera to get the cluster operational. To do this execute:"
echo ""
echo "This requires you to identify the most advanced node. For details see http://galeracluster.com/documentation-webpages/quorumreset.html
echo ""
EOF
chmod +x /etc/update-motd.d/21-galera
