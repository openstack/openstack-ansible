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

from __future__ import print_function
from optparse import OptionParser
from os.path import exists

import json
import pickle
import sys

USAGE = "usage: %prog -f <swift_ring.contentsa> -r <managed_region>"

DEVICE_KEY = "%(ip)s:%(port)d/%(device)s"


class RingComparisonError(Exception):
    pass


def get_build_file_data(build_file):
    build_file_data = None
    if exists(build_file):
        try:
            with open(build_file) as bf_stream:
                build_file_data = pickle.load(bf_stream)
        except Exception as ex:
            print("Error: failed to load build file '%s': %s" % (build_file,
                                                                 ex))
            build_file_data = None
    return build_file_data


def check_ring_settings(build_file, part_power, repl, min_part_hours,
                        data=None):
    # Check if the build file is emptuy
    if data is None:
        raise RingComparisonError('Build file %s is empty or does '
                                  'not exist.' % build_file)
    # Check if replica count matches for contents and ring file
    if repl != data.get('replicas'):
        raise RingComparisonError('Replica count does not match')
    # Check min_part_hours matches for contents and ring file
    if min_part_hours != data.get('min_part_hours'):
        raise RingComparisonError('min_part_hours does not match')
    # Check part_power matches for contents and ring file
    if part_power != data.get('part_power'):
        raise RingComparisonError('part_power does not match')


def check_host_settings(content_host, ring_host):
    devstr = DEVICE_KEY % content_host
    if content_host.get('zone', 0) != ring_host['zone']:
        raise RingComparisonError('Zone on device %s differs to the ring.'
                                  % devstr)
    if content_host.get('region', 1) != ring_host['region']:
        raise RingComparisonError('Region on device %s differs to the ring.'
                                  % devstr)

    content_repl_ip = content_host.get('repl_ip', content_host['ip'])
    content_repl_port = content_host.get('repl_port', content_host['port'])
    content_weight = content_host.get('weight')
    ring_repl_ip = ring_host['replication_ip']
    ring_repl_port = ring_host['replication_port']
    ring_weight = ring_host['weight']
    if content_repl_ip != ring_repl_ip:
        raise RingComparisonError('Replication IP for device %s differs '
                                  'to the ring.' % devstr)
    if content_repl_port != ring_repl_port:
        raise RingComparisonError('Replication Port for device %s differs '
                                  'to the ring.' % devstr)
    if content_weight != ring_weight:
        raise RingComparisonError('Device weight for device %s differs to the '
                                  'ring.' % devstr)


def check_ring(build_name, repl, min_part_hours, part_power, content_hosts,
               region=None):
    build_file = "%s.builder" % build_name
    build_file_data = get_build_file_data(build_file)
    check_ring_settings(
        build_file,
        part_power,
        repl,
        min_part_hours,
        data=build_file_data
    )

    ring_hosts = {}
    for i, dev in enumerate(build_file_data['devs']):
        if dev is not None:
            if region is None or int(region) == int(dev['region']):
                ring_hosts[DEVICE_KEY % dev] = i
    for content_host in content_hosts:
        host_key = DEVICE_KEY % content_host
        if region is None or int(region) == int(content_host['region']):
            if host_key in ring_hosts:
                ring_host = build_file_data['devs'][ring_hosts[host_key]]
                check_host_settings(content_host, ring_host)
                ring_hosts.pop(host_key)
            else:
                raise RingComparisonError('Device %s is not in the ring.'
                                          % host_key)

    if ring_hosts:
        for ring_host in ring_hosts:
            if build_file_data['devs'][ring_hosts[ring_host]]['weight'] != 0:
                raise RingComparisonError('There are devices in the ring that'
                                          'are not in the inventory/contents'
                                          'file.')


def main(setup, region):
    # load the json file
    try:
        with open(setup) as json_stream:
            _contents_file = json.load(json_stream)
    except Exception as ex:
        print("Failed to load json string %s" % ex)
        return 1

    content_hosts = _contents_file['drives']
    kargs = {'content_hosts': content_hosts, 'region': region}
    ring_call = [
        _contents_file['builder_file'],
        _contents_file['repl_number'],
        _contents_file['min_part_hours'],
        _contents_file['part_power']
    ]

    try:
        check_ring(*ring_call, **kargs)
        print('SUCCESS: Ring is consistent with contents file')
    except RingComparisonError as ex:
        print(ex)
        return 2

if __name__ == "__main__":
    parser = OptionParser(USAGE)
    parser.add_option(
        "-f",
        "--file",
        dest="setup",
        help="Specify the swift ring contents file.",
        metavar="FILE"
    )
    parser.add_option(
        "-r",
        "--region",
        help="Specify the region to manage for the ring file.",
        dest="region",
        type='int',
        metavar="REGION"
    )

    options, _args = parser.parse_args(sys.argv[1:])
    if options.setup and not exists(options.setup):
        print("Swift ring contents file not found or doesn't exist")
        parser.print_help()
        sys.exit(1)

    sys.exit(main(options.setup, options.region))
