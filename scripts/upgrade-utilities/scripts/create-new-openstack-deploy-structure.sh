#!/usr/bin/env bash
# Copyright 2015, Rackspace US, Inc.
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
set -e -u -v

# Create new openstack_deploy directory.
if [ -d "/etc/rpc_deploy" ];then
  # Create an archive of the old deployment directory
  tar -czf ~/pre-upgrade-backup.tgz /etc/rpc_deploy
  # Move the new deployment directory bits into place
  mkdir -p /etc/openstack_deploy/
  cp -R /etc/rpc_deploy/* /etc/openstack_deploy/
  mv /etc/rpc_deploy /etc/rpc_deploy.OLD
else
  echo "No /etc/rpc_deploy directory found, thus nothing to upgrade."
  exit 1
fi

if [ ! -d "/etc/openstack_deploy/upgrade-juno" ];then
  mkdir -p "/etc/openstack_deploy/upgrade-juno"
fi

# Drop deprecation file.
cat > /etc/rpc_deploy.OLD/DEPRECATED.txt <<EOF
This directory have been deprecated please navigate to "/etc/openstack_deploy"
EOF

# Move the old RPC files to OpenStack files.
pushd /etc/openstack_deploy
  rename 's/rpc_/openstack_/g' rpc_*
popd

# Make the extra configuration directories within the "/etc/openstack_deploy" directory
mkdir -p /etc/openstack_deploy/conf.d
mkdir -p /etc/openstack_deploy/env.d
