#!/usr/bin/env python
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

import yaml

with open('/etc/openstack_deploy/user_variables.yml', 'r') as f:
    user_vars = yaml.safe_load(f.read())

# Grab a map of the old keystone ldap entries
new_ldap = dict()
for k, v in user_vars.items():
    if k.startswith('keystone_ldap'):
        new_ldap['%s' % k.split('keystone_ldap_')[-1]] = v

# Rename misnamed old keystone ldap entries
MISNAMED_ENTRIES = {'user_bind': 'user', 'user_bind_password': 'password'}

for entry in MISNAMED_ENTRIES:
    if entry in new_ldap:
        new_ldap[MISNAMED_ENTRIES[entry]] = new_ldap.pop(entry)

if 'server' in new_ldap:
    if 'scheme' in new_ldap:
        ldap_scheme = new_ldap['scheme']
        new_ldap.pop('scheme')
    else:
        ldap_scheme = 'ldap'
    new_ldap['url'] = "%s://%s" % (ldap_scheme, new_ldap['server'])
    new_ldap.pop('server')

# Open user secrets file.
with open('/etc/openstack_deploy/user_secrets.yml', 'r') as fsr:
    user_secrets = yaml.safe_load(fsr.read())

# LDAP variable to instruct keystone to use ldap
ldap = user_secrets['keystone_ldap'] = dict()

# "ldap" section within the keystone_ldap variable.
ldap['ldap'] = new_ldap
with open('/etc/openstack_deploy/user_secrets.yml', 'w') as fsw:
    fsw.write(
        yaml.safe_dump(
            user_secrets,
            default_flow_style=False,
            width=1000
        )
    )
