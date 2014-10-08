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

import pickle
import sys
import threading
import yaml

USAGE = "usage: %prog -s <rpc_user_config.yml>"

DEV_KEY = "%(ip)s:%(port)d/%(device)s"

DEFAULT_REPL = {{ swift_default_replication_number }}
DEFAULT_MIN_PART_HOURS = {{ swift_default_min_part_hours }}
DEFAULT_HOST_ZONE = {{ swift_default_host_zone }}
DEFAULT_HOST_WEIGHT = {{ swift_default_drive_weight }}
DEFAULT_ACCOUNT_PORT = {{ swift_account_port }}
DEFAULT_CONTAINER_PORT = {{ swift_container_port }}
DEFAULT_OBJECT_PORT = {{ swift_object_port }}
DEFAULT_SECTION_PORT = {
    'account': DEFAULT_ACCOUNT_PORT,
    'container': DEFAULT_CONTAINER_PORT,
    'object': DEFAULT_OBJECT_PORT,
}
DEFAULT_GROUP_MAP = {
    'account': 'account',
{% for policy in swift.storage_policies %}
{%   if policy.policy.index == 0 %}
    'object': '{{ policy.policy.name }}',
{%   else %}
    'object-{{ policy.policy.index}}': '{{ policy.policy.name }}',
{%   endif %}
{% endfor %}
    'container': 'container'
}
DEFAULT_GROUPS= [
    'account',
{% for policy in swift.storage_policies %}
    '{{ policy.policy.name }}',
{% endfor %}
    'container'
]

def create_buildfile(build_file, part_power, repl, min_part_hours,
                     update=False, data=None):
    if update:
        # build file exists, so lets just update the existing build file
        if not data:
            data = get_build_file_data(build_file)
            if data is None:
                data = {}

        if repl != data.get('replicas'):
            run_and_wait(rb_main, ["swift-ring-builder", build_file,
                                   "set_replicas", repl])
        if min_part_hours != data.get('min_part_hours'):
            run_and_wait(rb_main, ["swift-ring-builder", build_file,
                                   "set_min_part_hours", min_part_hours])
        if part_power != data.get('part_power'):
            print('Part power cannot be changed.. you must rebuild the ring "
                  "if you need to change it.')

    else:
        run_and_wait(rb_main, ["swift-ring-builder", build_file, "create",
                     part_power, repl, min_part_hours])

def change_host_weight(build_file, host_search_str, weight):
    run_and_wait(rb_main, ["swift-ring-builder", build_file, "set_weight",
                 host_search_str, weight])

def remove_host_from_ring(build_file, host):
    run_and_wait(rb_main, ["swift-ring-builder", build_file, "remove",
                 DEV_KEY % host])

def update_host_in_ring(build_file, new_host, old_host):
    r_ip = new_host.get('repl_ip', new_host['ip'])
    r_port = new_host.get('repl_port', new_host['port'])
    weight = new_host.get('weight', DEFAULT_HOST_WEIGHT)
    if r_ip != old_host['replication_ip'] or \
        r_port != old_host['replication_port']:
        host_d = {'r_ip': r_ip, 'r_port': r_port}
        host_d.update(host)
        host_str = "%(ip)s:%(port)dR%(r_ip)s:%(d_port)d/%(name)s" % host_d
        run_and_wait(rb_main, ["swift-ring-builder", build_file, "set_info",
                               DEV_KEY % new_host, host_str])

    if weight != old_host['weight']:
        change_host_weight(build_file, DEV_KEY % new_host, weight)


def add_host_to_ring(build_file, host):
    host_str = ""
    if host.get('region') is not None:
        host_str += 'r%(region)d' % host
    host_str += "z%d" % (host.get('zone', DEFAULT_HOST_ZONE))
    host_str += "-%(ip)s:%(port)d" % host
    if host.get('repl_port'):
        r_ip = host.get('repl_ip', host['ip'])
        host_str += "R%s:%d" % (r_ip, host['repl_port'])
    host_str += "/%(name)s" % host

    weight = host.get('weight', DEFAULT_HOST_WEIGHT)
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
        print("Section %s doesn't exist" % (section))
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


def build_ring(section, conf, part_power, hosts):
    # Create the build file
    build_file = "%s.builder" % (section)
    build_file_data = get_build_file_data(build_file)

    repl = conf.get('repl_number', DEFAULT_REPL)
    min_part_hours = conf.get('min_part_hours',
                              DEFAULT_MIN_PART_HOURS)
    update = build_file_data not None
    create_buildfile(build_file, part_power, repl, min_part_hours, update,
                     data=build_file_data)

    old_hosts = {}
    if update:
        old_hosts = dict([(DEV_KEY % dev, i)
                          for i, dev in enumerate(build_file_data['devs'])])
    section_key = section.split('-')[0]
    service_port = conf.get('port', DEFAULT_SECTION_PORT[section_key])
    for host in hosts:
        host_vars = hosts[host]
        host_vars['device'] = host_vars['name']
        host_vars['port'] = service_port
        host_vars['groups'] = host_vars.get('groups', DEFAULT_GROUPS)
        if DEFAULT_GROUP_MAP[section] in host_vars['groups']:
            host_key = DEV_KEY % host_vars
            if host_key in old_hosts:
                old_host = build_file_data['devs'][old_hosts[host_key]]
                update_host_in_ring(build_file, host_vars, old_host)
                old_hosts.pop(host_key)
            else:
                add_host_to_ring(build_file, host_vars)

    if old_hosts:
        # There are still old hosts, these hosts must've been removed
        for host in old_hosts:
            remove_host_from_ring(build_file, host)

    # Rebalance ring
    run_and_wait(rb_main, ["swift-ring-builder", build_file, "rebalance"])

def main(setup):
    # load the yaml file
    try:
        with open(setup) as yaml_stream:
            _swift = yaml.load(yaml_stream)
    except Exception as ex:
        print("Failed to load yaml string %s" % (ex))
        return 1

    _hosts = {}
    if _swift.get("swift_hosts"):
        for host in _swift['swift_hosts']:
            host_vars = \
                _swift['swift_hosts'][host]['container_vars']['swift_vars']
            host_ip = host_vars.get('ip', _swift['swift_hosts'][host]['ip'])
            if not host_vars.get('drives'):
                continue
            host_drives = host_vars.get('drives')
            for host_drive in host_drives:
                host_drive['ip'] = host_drive.get('ip', host_ip)
                if host_vars.get('groups'):
                   host_drive['groups'] = host_drive.get('groups',
                                                         host_vars['groups'])
                if host_vars.get('repl_ip'):
                   host_drive['repl_ip'] = host_drive.get('repl_ip',
                                                          host_vars['repl_ip'])
                if host_vars.get('repl_port'):
                   host_drive['repl_port'] = \
                       host_drive.get('repl_port', host_vars['repl_port'])
                if host_vars.get('weight'):
                   host_drive['weight'] = host_drive.get('weight',
                                                         host_vars['weight'])
                key = "%s/%s" % (host_drive['ip'], host_drive['name'])
                if key in _hosts:
                    print("%s already definined - duplicate device" % key)
                    return 1
                _hosts[key] = host_drive

    global_vars  = _swift['global_overrides']
    check_section(global_vars, 'swift')
    swift_vars = global_vars['swift']
    if not swift_vars.get('part_power'):
        print('No part_power specified - please set a part_power value')
        return 1
    part_power = swift_vars.get('part_power')

    # Create account ring - if the section is empty create an empty dict
    # so defaults are used
    if not has_section(swift_vars, 'account'):
        swift_vars['account'] = {}
    build_ring('account', swift_vars['account'], part_power, _hosts)

    # Create container ring - if the section is empty create an empty dict
    # so defaults are used
    if not has_section(swift_vars, 'container'):
        swift_vars['container'] = {}
    build_ring('container', swift_vars['container'], part_power, _hosts)

    # Create object rings (storage policies)
    check_section(swift_vars, 'storage_policies')
    indexes = set()
    for policy in swift_vars['storage_policies']:
        policy = policy['policy']
        if policy['index'] in indexes:
            print("Storage Policy index %d already in use" % (policy['index']))
            return 4
        if policy['index'] == 0:
            buildfilename = 'object'
        else:
            buildfilename = 'object-%d' % (policy['index'])
        indexes.add(policy['index'])
        if 'port' not in policy:
            policy['port'] = policy.get('port', DEFAULT_OBJECT_PORT)
        build_ring(buildfilename, policy, part_power, _hosts)

if __name__ == "__main__":
    parser = OptionParser(USAGE)
    parser.add_option("-s", "--setup", dest="setup",
                      help="Specify the swift setup file.", metavar="FILE",
                      default="/etc/rpc_deploy/rpc_user_config.yml")

    options, args = parser.parse_args(sys.argv[1:])
    if options.setup and not exists(options.setup):
        print("Swift setup file not found or doesn't exist")
        parser.print_help()
        sys.exit(1)

    sys.exit(main(options.setup))
