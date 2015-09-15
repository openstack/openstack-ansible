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

# Remove old ldap variables from "user_variables.yml".
sed -i '/keystone_ldap.*/d' /etc/openstack_deploy/user_variables.yml

# Remove secrets from the user_variables file that are now in the secrets file.
sed -i -e '/key\:/d' -e '/token\:/d' -e '/password\:/d' -e '/secret\:/d' /etc/openstack_deploy/user_extras_variables.yml

# Remove secrets from the user_variables file that are now in the secrets file.
sed -i -e '/key\:/d' -e '/token\:/d' -e '/swift_hash_path/d' -e '/password\:/d' -e '/secret\:/d' /etc/openstack_deploy/user_variables.yml

# Remove the environment version entry from user config.
sed -i '/^environment_version.*/d' /etc/openstack_deploy/openstack_user_config.yml
