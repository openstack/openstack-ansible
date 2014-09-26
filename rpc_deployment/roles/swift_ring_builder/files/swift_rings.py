#!/usr/bin/env python
from __future__ import print_function
from optparse import OptionParser
from os.path import exists
from swift.cli.ringbuilder import main as rb_main

import sys
import threading
import yaml

USAGE = "usage: %prog -s <swift setup yaml>"

DEFAULT_PART_POWER = 10
DEFAULT_REPL = 3
DEFAULT_MIN_PART_HOURS = 1
DEFAULT_HOST_DRIVES = '/srv/drive/'
DEFAULT_HOST_DRIVE = '/sdb'
DEFAULT_HOST_ZONE = 0
DEFAULT_HOST_WEIGHT = 1
DEFAULT_ACCOUNT_PORT = 6002
DEFAULT_CONTAINER_PORT = 6001
DEFAULT_OBJECT_PORT = 6000
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
    host_str += "-%(host)s:%(port)d" % host
    if host.get('repl_port'):
        r_ip = host.get('repl_ip', host['host'])
        host_str += "R%s:%d" % (r_ip, host['repl_port'])
    host_str += "/%(drive)s" % host

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

    # Add the hosts
    if not has_section(conf, 'hosts') or len(conf.get('hosts')) == 0:
        print("No hosts/drives assigned to the %s ring" % section)
        sys.exit(3)

    section_key = section.split('-')[0]
    service_port = conf.get('port', DEFAULT_SECTION_PORT[section_key])
    for host in conf['hosts']:
        if 'name' in host:
            if host['name'] not in hosts:
                print("Host %(name) reference not found." % host)
                sys.exit(3)
            host = hosts[host['name']]
        else:
            if 'drive' not in host:
                host['drive'] = DEFAULT_HOST_DRIVE
        host['port'] = service_port
        add_host_to_ring(build_file, host)

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

    if _swift.get("hosts"):
        for host in _swift['hosts']:
            if not host.get('drive'):
                host['drive'] = DEFAULT_HOST_DRIVE
            key = "%(host)s/%(drive)s" % host
            if key in _hosts:
                print("%(host)s already definined" % host)
                return 1
            _hosts[key] = host

    check_section(_swift, 'swift')
    part_power = _swift['swift'].get('part_power', DEFAULT_PART_POWER)

    # Create account ring
    check_section(_swift, 'account')
    build_ring('account', _swift['account'], part_power, _hosts)

    # Create container ring
    check_section(_swift, 'container')
    build_ring('container', _swift['container'], part_power, _hosts)

    # Create object rings (storage policies)
    check_section(_swift, 'storage_policies')
    check_section(_swift['storage_policies'], 'policies')
    indexes = set()
    for sp in _swift['storage_policies']['policies']:
        if sp['index'] in indexes:
            print("Storage Policy index %d already in use" % (sp['index']))
            return 4
        buildfilename = 'object-%d' % (sp['index'])
        indexes.add(sp['index'])
        if 'port' not in sp:
            sp['port'] = _swift['storage_policies'].get('port',
                                                        DEFAULT_OBJECT_PORT)
        build_ring(buildfilename, sp, part_power, _hosts)

if __name__ == "__main__":
    parser = OptionParser(USAGE)
    parser.add_option("-s", "--setup", dest="setup",
                      help="Specify the swift setup file.", metavar="FILE",
                      default="/etc/swift/swift_inventory.yml")

    options, args = parser.parse_args(sys.argv[1:])
    if options.setup and not exists(options.setup):
        print("Swift setup file not found or doesn't exist")
        parser.print_help()
        sys.exit(1)

    sys.exit(main(options.setup))
