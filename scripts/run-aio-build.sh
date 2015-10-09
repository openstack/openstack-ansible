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

export REPO_URL=${REPO_URL:-"https://github.com/openstack/openstack-ansible.git"}
export REPO_BRANCH=${REPO_BRANCH:-"master"}
export WORKING_FOLDER=${WORKING_FOLDER:-"/opt/openstack-ansible"}

## Main ----------------------------------------------------------------------

# set verbosity
set -x

# install git so that we can fetch the repo
# note: the redirect of stdin to /dev/null is necessary for when this script is
# run as part of a curl-pipe-shell. otherwise apt-get will consume the rest of
# this file as if it was its own stdin (despite using -y to skip interaction).
apt-get update && apt-get install -y git < /dev/null

# fetch the repo
git clone -b ${REPO_BRANCH} ${REPO_URL} ${WORKING_FOLDER}

# change into the expected root directory
cd ${WORKING_FOLDER}

# first, bootstrap the AIO host
source scripts/bootstrap-aio.sh

# next, bootstrap Ansible
source scripts/bootstrap-ansible.sh

# finally, run all the playbooks
bash scripts/run-playbooks.sh

# put a motd in place to help the user know what stuff is accessible once the build is complete
cat > /etc/update-motd.d/20-openstack<< EOF
#!/usr/bin/env bash
echo ""
echo "############ openstack-ansible all-in-one build #############"
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
echo "This requires you to identify the most advanced node. For details see http://galeracluster.com/documentation-webpages/quorumreset.html
echo ""
EOF
chmod +x /etc/update-motd.d/21-galera
