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

with open('/etc/openstack_deploy/openstack_user_config.yml', 'r') as f:
    user_config = yaml.safe_load(f.read())

# Create the new repo servers entries
repo_servers = dict()
o = repo_servers['repo-infra_hosts'] = user_config['infra_hosts']

with open('/etc/openstack_deploy/conf.d/repo-servers.yml', 'w') as fsw:
    fsw.write(
        yaml.safe_dump(
            repo_servers,
            default_flow_style=False,
            width=1000
        )
    )
