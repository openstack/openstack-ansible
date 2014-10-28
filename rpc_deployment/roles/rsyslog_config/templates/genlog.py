#!/usr/bin/env python
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

import os
import fnmatch

print "$ModLoad imfile\t\t# Load the imfile input module\n"
print "$ActionQueueType LinkedList\t\t# Use asynchronous processing"
print "$ActionQueueFileName srvrfwd\t\t# Set file name, also enables disk mode"
print "$ActionResumeRetryCount -1\t\t# Infinite retries on insert failure"
print "$ActionQueueSaveOnShutdown on\t\t# Save in-memory data if rsyslog shuts down\n"

matches = []
for root, dirnames, filenames in os.walk('/openstack/log'):
        for filename in fnmatch.filter(filenames, '*.log'):
                matches.append(os.path.join(root, filename))

for log in matches:
        container = log.split('/')[3]
        service = log.split('/')[4].split('.')[0]
        if 'horizon' in container:
            service = container + '_' + service

        if 'logstash' in container:
            continue

        print "$InputFileName {}".format(log)
        print "$InputFileTag {}.{}:".format(container, service)
        print "$InputFileStateFile state-{}-{}".format(container, service)
        print "$InputFileFacility local7"
        print "$InputRunFileMonitor\n"

{% raw %}
print r'''$template ls_json,"{%timestamp:::date-rfc3339,jsonf:@timestamp%,%source:::jsonf:@source_host%,\"@source\":\"syslog://%app-name:::json%\",\"@message\":\"%msg:::json%\",\"@fields\":{%syslogfacility-text:::jsonf:facility%,%syslogseverity-text:::jsonf:severity%,%app-name:::jsonf:program%,%procid:::jsonf:processid%}}"'''
{% endraw %}

print "*.* @@{{ hostvars[groups['logstash'][0]]['container_address'] }}:{{ logstash_port }};ls_json"
