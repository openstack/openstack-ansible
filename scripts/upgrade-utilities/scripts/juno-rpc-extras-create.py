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

# Grab a map of the old rpc maas entries
extra_types = ['maas_', 'rackspace_', 'elasticsearch_', 'kibana_', 'logstash_']
rpc_extras = dict()
for k, v in user_vars.items():
    for i in extra_types:
        if k.startswith(i):
            rpc_extras[k] = v

# Clean up rpc extra variables from user variables
for i in rpc_extras.keys():
    del(user_vars[i])

with open('/etc/openstack_deploy/user_variables.yml', 'w') as fsw:
    fsw.write(
        yaml.safe_dump(
            user_vars,
            default_flow_style=False,
            width=1000
        )
    )

with open('/etc/openstack_deploy/user_extras_variables.yml', 'w') as fsw:
    fsw.write(
        yaml.safe_dump(
            rpc_extras,
            default_flow_style=False,
            width=1000
        )
    )
