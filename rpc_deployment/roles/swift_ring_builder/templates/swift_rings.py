#!/usr/bin/env python
from __future__ import print_function
from optparse import OptionParser
from os.path import exists
from swift.cli.ringbuilder import main as rb_main

import sys
import threading
import yaml

USAGE = "usage: %prog -s <rpc_user_config.yml>"

DEFAULT_PART_POWER = 10
DEFAULT_REPL = 3
DEFAULT_MIN_PART_HOURS = 1
DEFAULT_HOST_DRIVE = 'sdb'
DEFAULT_HOST_ZONE = 0
DEFAULT_HOST_WEIGHT = 100
DEFAULT_ACCOUNT_PORT = {{ swift_account_port }}
DEFAULT_CONTAINER_PORT = {{ swift_container_port }}
DEFAULT_OBJECT_PORT = {{ swift_object_port }}
DEFAULT_SECTION_PORT = {
    'account': DEFAULT_ACCOUNT_PORT,
    'container': DEFAULT_CONTAINER_PORT,
    'object': DEFAULT_OBJECT_PORT,
}


def create_buildfile(build_file, part_power, repl, min_part_hours):
    run_and_wait(rb_main, ["swift-ring-builder", build_file, "create",
                 part_power, repl, min_part_hours])


def add_host_to_ring(build_file, host):
    host_str = ""
    if host.get('region') is not None:
        host_str += 'r%(region)d' % host
    host_str += "z%d" % (host.get('zone', DEFAULT_HOST_ZONE))
    host_str += "-%(ip)s:%(port)d" % host
    if host.get('repl_port'):
        r_ip = host.get('repl_ip', host['host'])
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


def build_ring(section, conf, part_power, hosts):
    # Create the build file
    build_file = "%s.builder" % (section)
    repl = conf.get('repl_number', DEFAULT_REPL)
    min_part_hours = conf.get('min_part_hours',
                              DEFAULT_MIN_PART_HOURS)
    create_buildfile(build_file, part_power, repl, min_part_hours)

    section_key = section.split('-')[0]
    service_port = conf.get('port', DEFAULT_SECTION_PORT[section_key])
    for host in hosts:
        host_vars = hosts[host]
        host_vars['port'] = service_port
        add_host_to_ring(build_file, host_vars)

    # Rebalance ring
    run_and_wait(rb_main, ["swift-ring-builder", build_file, "rebalance"])
    # rb_main(("swift-ring-builder", build_file, "rebalance"))


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
            host_vars = _swift['swift_hosts'][host]['container_vars']['swift_vars']
            if not host_vars.get('drive'):
                host_vars['drive'] = DEFAULT_HOST_DRIVE
            host_ip = _swift['swift_hosts'][host]['ip']
            host_drives = host_vars.get('drive')
            for host_drive in host_drives:
                host_drive['ip'] = host_drive.get('ip', host_ip)
                if host_vars.get('repl_ip'):
                   host_drive['repl_ip'] = host_drives[host_drive].get('repl_ip', host_vars['repl_ip'])
                if host_vars.get('repl_port'):
                   host_drive['repl_port'] = host_drives[host_drive].get('repl_port', host_vars['repl_port'])
                if host_vars.get('weight'):
                   host_drive['weight'] = host_drives[host_drive].get('weight', host_vars['weight'])
                key = "%s/%s" % (host_drive['ip'], host_drive['name'])
                if key in _hosts:
                    print("%(host)s already definined" % host)
                    return 1
                _hosts[key] = host_drive
    
    global_vars  = _swift['global_overrides']
    check_section(global_vars, 'swift')
    swift_vars = global_vars['swift']
    part_power = swift_vars.get('part_power', DEFAULT_PART_POWER)

    # Create account ring
    check_section(swift_vars, 'account')
    build_ring('account', swift_vars['account'], part_power, _hosts)

    # Create container ring
    check_section(swift_vars, 'container')
    build_ring('container', swift_vars['container'], part_power, _hosts)

    # Create object rings (storage policies)
    check_section(swift_vars, 'storage_policies')
    indexes = set()
    for policy in swift_vars['storage_policies']:
        policy = policy['policy']
        if policy['index'] in indexes:
            print("Storage Policy index %d already in use" % (policy['index']))
            return 4
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
