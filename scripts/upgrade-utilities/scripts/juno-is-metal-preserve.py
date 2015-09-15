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

import os
import yaml

with open('/etc/rpc_deploy.OLD/rpc_environment.yml', 'r') as f:
    rpc_environment = yaml.safe_load(f.read())

for root, _, files in os.walk('/etc/openstack_deploy/env.d'):
    for item in files:
        env_file = os.path.join(root, item)
        with open(env_file, 'r') as f:
            os_environment = yaml.safe_load(f.read())

        if 'container_skel' not in os_environment:
            continue

        changed = False

        for i in os_environment['container_skel']:
            os_item = os_environment['container_skel'][i]

            if i not in rpc_environment['container_skel']:
                continue

            rpc_item = rpc_environment['container_skel'][i]

            if 'is_metal' in rpc_item:
                rpc_metal = rpc_item['is_metal']
            else:
                rpc_metal = False

            if 'is_metal' in os_item['properties']:
                os_metal = os_item['properties']['is_metal']
            else:
                os_metal = False

            if rpc_metal != os_metal:
                changed = True
                os_item['properties']['is_metal'] = rpc_metal

        if changed:
            with open(env_file, 'w') as fsw:
                fsw.write(
                    yaml.safe_dump(
                        os_environment,
                        default_flow_style=False,
                        width=1000
                    )
                )
