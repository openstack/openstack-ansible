#!/usr/bin/env python
# Copyright 2016, Rackspace US, Inc.
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

# These values happen to be both the keys and the values removed from the
# environment file
BLACK_LIST = [
    'ceilometer_alarm_notifier',
    'ceilometer_alarm_evaluator'
]


def clean_vars():
    with open('/etc/openstack_deploy/env.d/ceilometer.yml', 'r') as f:
        environment = yaml.safe_load(f.read())

    for var in BLACK_LIST:
        # If the values aren't present, using 'pop' and the try/except
        # allow the script to continue without changes
        environment['component_skel'].pop(var, None)
        container_skel = environment['container_skel']
        try:
            container_skel['ceilometer_api_container']['contains'].remove(var)
        except ValueError:
            pass

    with open('/etc/openstack_deploy/env.d/ceilometer.yml', 'w') as f:
        f.write(yaml.safe_dump(environment, default_flow_style=False,
                               width=1000))

if __name__ == '__main__':
    clean_vars()
    with open('/etc/openstack_deploy.KILO/CEILOMETER_MIGRATED', 'w') as f:
        f.write('Deprecated ceilometer environment info has been removed.')
