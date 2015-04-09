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
from swift.cli.ringbuilder import main as rb_main

import json
import pickle
import sys
import threading


USAGE = "usage: %prog -f <swift_ring.contents>"

DEVICE_KEY = "%(ip)s:%(port)d/%(device)s"


class RingValidationError(Exception):
    pass


def create_buildfile(build_file, part_power, repl, min_part_hours,
                     update=False, data=None, validate=False):
    if update:
        # build file exists, so lets just update the existing build file
        if not data:
            data = get_build_file_data(build_file)
            if data is None:
                data = {}

        if repl != data.get('replicas') and not validate:
            run_and_wait(rb_main, ["swift-ring-builder", build_file,
                                   "set_replicas", repl])
        if min_part_hours != data.get('min_part_hours') and not validate:
            run_and_wait(rb_main, ["swift-ring-builder", build_file,
                                   "set_min_part_hours", min_part_hours])
        if part_power != data.get('part_power'):
            raise RingValidationError('Part power cannot be changed! '
                                      'you must rebuild the ring if you need '
                                      'to change it.\nRing part power: %s '
                                      'Inventory part power: %s'
                                      % (data.get('part_power'), part_power))

    elif not validate:
        run_and_wait(rb_main, ["swift-ring-builder", build_file, "create",
                     part_power, repl, min_part_hours])


def change_host_weight(build_file, host_search_str, weight):
    run_and_wait(rb_main, ["swift-ring-builder", build_file, "set_weight",
                 host_search_str, weight])


def remove_host_from_ring(build_file, host):
    run_and_wait(rb_main, ["swift-ring-builder", build_file, "remove",
                 host])


def update_host_in_ring(build_file, new_host, old_host, validate=False):
    if new_host.get('zone', 0) != old_host['zone']:
        devstr = DEVICE_KEY % new_host
        raise RingValidationError('Cannot update zone on %s, this can only be '
                                  'done when the drive is added' % devstr)
    if new_host.get('region', 1) != old_host['region']:
        devstr = DEVICE_KEY % new_host
        raise RingValidationError('Cannot update region on %s, this can only '
                                  'be done when the drive is added' % devstr)

    try:
        r_ip = new_host.get('repl_ip', new_host['ip'])
        r_port = new_host.get('repl_port', new_host['port'])
        weight = new_host.get('weight')

        old_r_ip = old_host['replication_ip']
        old_r_port = old_host['replication_port']

        if r_ip != old_r_ip or r_port != old_r_port:
            host_d = {'r_ip': r_ip, 'r_port': r_port}
            host_d.update(new_host)
            host_str = (
                "%(ip)s:%(port)dR%(r_ip)s:%(r_port)d/%(device)s" % host_d
            )
            if not validate:
                run_and_wait(rb_main, ["swift-ring-builder", build_file,
                                       "set_info", DEVICE_KEY % new_host,
                                       host_str])
    except Exception as ex:
        raise RingValidationError(ex)

    if weight != old_host['weight'] and not validate:
        change_host_weight(build_file, DEVICE_KEY % new_host, weight)


def add_host_to_ring(build_file, host, validate=False):
    host_str = ""
    try:
        if host.get('region') is not None:
            host_str += 'r%(region)d' % host
        host_str += "z%d" % (host.get('zone'))
        host_str += "-%(ip)s:%(port)d" % host
        if host.get('repl_ip'):
            r_ip = host['repl_ip']
            r_port = host.get('repl_port', host['port'])
            host_str += "R%s:%d" % (r_ip, r_port)
        elif host.get('repl_port'):
            r_ip = host.get('repl_ip', host['ip'])
            r_port = host['repl_port']
            host_str += "R%s:%d" % (r_ip, r_port)
        host_str += "/%(device)s" % host
        weight = host.get('weight')
    except Exception as ex:
        raise RingValidationError(ex)
    if not validate:
        run_and_wait(rb_main, ["swift-ring-builder", build_file, 'add',
                               host_str, str(weight)])


def run_and_wait(func, *args):
    t = threading.Thread(target=func, args=args)
    t.start()
    return t.join()


def has_section(conf, section):
    return True if conf.get(section) else False


def check_section(conf, section):
    if not has_section(conf, section):
        print("Section %s doesn't exist" % section)
        sys.exit(2)


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


def build_ring(build_name, repl, min_part_hours, part_power, hosts,
               validate=False):
    # Create the build file
    build_file = "%s.builder" % build_name
    build_file_data = get_build_file_data(build_file)

    update = build_file_data is not None
    create_buildfile(
        build_file,
        part_power,
        repl,
        min_part_hours,
        update,
        data=build_file_data,
        validate=validate
    )

    old_hosts = {}
    if update:
        for i, dev in enumerate(build_file_data['devs']):
            if dev is not None:
                old_hosts[DEVICE_KEY % dev] = i
    for host in hosts:
        host_key = DEVICE_KEY % host
        if host_key in old_hosts:
            old_host = build_file_data['devs'][old_hosts[host_key]]
            update_host_in_ring(build_file, host, old_host,
                                validate=validate)
            old_hosts.pop(host_key)
        else:
            add_host_to_ring(build_file, host, validate=validate)

    if old_hosts and not validate:
        # There are still old hosts, these hosts must've been removed
        for host in old_hosts:
            remove_host_from_ring(build_file, host)

    # Rebalance ring
    if not validate:
        if not hosts:
            run_and_wait(
                rb_main, ["swift-ring-builder", build_file, "write_ring"]
            )
        else:
            run_and_wait(
                rb_main, ["swift-ring-builder", build_file, "rebalance"]
            )


def main(setup):
    # load the json file
    try:
        with open(setup) as json_stream:
            _contents_file = json.load(json_stream)
    except Exception as ex:
        print("Failed to load json string %s" % ex)
        return 1

    hosts = _contents_file['drives']
    kargs = {'validate': True, 'hosts': hosts}
    ring_call = [
        _contents_file['builder_file'],
        _contents_file['repl_number'],
        _contents_file['min_part_hours'],
        _contents_file['part_power']
    ]

    try:
        build_ring(*ring_call, **kargs)
    except RingValidationError as ex:
        print(ex)
        return 2

    # If the validation passes lets go ahead and build the rings.
    kargs.pop('validate')
    build_ring(*ring_call, **kargs)


if __name__ == "__main__":
    parser = OptionParser(USAGE)
    parser.add_option(
        "-f",
        "--file",
        dest="setup",
        help="Specify the swift ring contents file.",
        metavar="FILE"
    )

    options, _args = parser.parse_args(sys.argv[1:])
    if options.setup and not exists(options.setup):
        print("Swift ring contents file not found or doesn't exist")
        parser.print_help()
        sys.exit(1)

    sys.exit(main(options.setup))
