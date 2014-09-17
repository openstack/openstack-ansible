#!/usr/bin/env python
from __future__ import print_function

import datetime
import sys
import yaml

from optparse import OptionParser
from os.path import exists, isdir, join

VERSION = '0.1'
USAGE = "usage: %prog [options] -s <swift setup yaml>"

DEFAULT_PART_POWER = 8
DEFAULT_REPL_NUM = 3
DEFAULT_REGION = 0
DEFAULT_ZONE = 0
DEFAULT_WEIGHT = 100
DEFAULT_DRIVE = "/srv/disk"
DEFAULT_OUTPUT_DIR = "/etc/ansible"
DEFAULT_OUTPUT_FILENAME = "hosts"

RETURN_NOT_DEFINED = 3

# FILE formatted strings
HEADER = """# This file was generated using the %s version %s at %s
[local]
localhost ansible_connection=local

[proxy]"""

CATCH_ALL_GROUPS = """
[object:children]
storagepolocy

[swift:children]
proxy
account
container
object

[swift:vars]"""

DRIVE_FORMAT = "%(host)s drive=%(drive)s region=%(region)s zone=%(zone)s "
DRIVE_FORMAT += "weight=%(weight)s"

DEFAULT_AUTHTOKEN_SETTINGS = {
    'auth_version': 'v2.0',
    'auth_host': 'keystone',
    'auth_port': '35357',
    'auth_protocol': 'https',
    'admin_tenant_name': 'service',
    'admin_user': 'swift',
    'admin_password': 'ADMIN',
}


def main(setup, verbose=False, dry_run=False, overwrite=True):
    # Parse the setup file, which should be yaml
    _swift = {}
    _drives = {}
    try:
        with open(setup) as yaml_stream:
            _swift = yaml.load(yaml_stream)
    except Exception as err:
        print("ERROR: Failed to yaml failure: %s", err)
        return 2

    def _section_defined(section):
        if section not in _swift:
            print("ERROR: no swift section defined")
            return False
        return True

    def _get_output_fd(filename):
        if dry_run:
            return None
        elif not overwrite and exists(filename):
            i = 1
            while exists("%s_%d" % (filename, i)):
                i += 1
            return open("%s_%d" % (filename, i), 'w')
        else:
            return open(filename, 'w')

    def _write_to_file(fd, data):
        if not fd or verbose:
            print(data)

        if fd:
            if not data.endswith('\n'):
                data += "\n"
            fd.write(data)
            fd.flush()

    def _get_drive(drive):
        _drive = {
            'drive': DEFAULT_DRIVE,
            'region': DEFAULT_REGION,
            'zone': DEFAULT_ZONE,
            'weight': DEFAULT_WEIGHT}

        if "drive" not in drive:
            drive["drive"] = DEFAULT_DRIVE

        key = "%(host)s%(drive)s" % drive
        if key in _drives:
            return _drives[key]
        else:
            _drive.update(drive)
            data = DRIVE_FORMAT % _drive
            _drives[key] = data
            return data

    # First attempt to get swift settings
    if not _section_defined("swift"):
        return RETURN_NOT_DEFINED

    swift_options = [
        "part_power=%s" % (_swift['swift'].get('part_power',
                                               DEFAULT_PART_POWER)),
        "user=%s" % (_swift['swift'].get('user', 'swift')),
        "swift_hash_path_suffix=%s" % (_swift['swift'].get("hash_path_suffix")),
        "swift_hash_path_prefix=%s" % (_swift['swift'].get("hash_path_prefix")),
        "syslog_host=%s" % (_swift['swift'].get('syslog_host',
                                                'localhost:514')),
    ]
    output_path = _swift['swift'].get("output_directory", DEFAULT_OUTPUT_DIR)
    output_file = _swift['swift'].get("output_filename",
                                      DEFAULT_OUTPUT_FILENAME)
    if not isdir(output_path):
        print("Outdir path '%s' doesn't exist", output_path)
        return 4

    output_file = join(output_path, output_file)
    output_fd = _get_output_fd(output_file)

    n = datetime.datetime.now()
    _write_to_file(output_fd, HEADER % (__file__, VERSION, n.ctime()))

    if not _section_defined("proxy"):
        return RETURN_NOT_DEFINED

    # Parse proxies
    # TODO: Add read anfinity and pipeline here?
    for proxy in _swift["proxy"]["hosts"]:
        _write_to_file(output_fd, "%s" % (proxy["host"]))
    _write_to_file(output_fd, "\n[proxy:vars]")
    _mc_servers = _swift["proxy"].get('memcache_servers')
    memcache_servers = ",".join(_mc_servers) if _mc_servers else \
                       '127.0.0.1:11211'
    _write_to_file(output_fd, "memcache_servers=%s" % (memcache_servers))
    _at = _swift["proxy"].get('authtoken')
    if _at:
        authtoken = DEFAULT_AUTHTOKEN_SETTINGS
        authtoken.update(_at)
        at_active = authtoken.get("active", False)
        if at_active:
            _write_to_file(output_fd, "authtoken_active=true")
            _write_to_file(output_fd, "delay_auth_decision="
                                      "%(delay_auth_decision)s" % authtoken)
            _write_to_file(output_fd, "auth_version="
                                      "%(auth_version)s" % authtoken)
            _write_to_file(output_fd, "auth_host="
                                      "%(auth_host)s" % authtoken)
            _write_to_file(output_fd, "auth_port="
                                      "%(auth_port)s" % authtoken)
            _write_to_file(output_fd, "auth_protocol="
                                      "%(auth_protocol)s" % authtoken)
            _write_to_file(output_fd, "auth_uri="
                                      "%(auth_uri)s" % authtoken)
            _write_to_file(output_fd, "admin_tenant_name="
                                      "%(admin_tenant_name)s" % authtoken)
            _write_to_file(output_fd, "admin_user="
                                      "%(admin_user)s" % authtoken)
            _write_to_file(output_fd, "admin_password="
                                      "%(admin_password)s" % authtoken)
        else:
            _write_to_file(output_fd, "authtoken_active=false")

    _write_to_file(output_fd, "\n[account]")

    if not _section_defined("account"):
        return RETURN_NOT_DEFINED

    for account in _swift["account"]["hosts"]:
        data = _get_drive(account)
        _write_to_file(output_fd, data)

    _write_to_file(output_fd, "\n[account:vars]")
    repl_num = _swift["account"].get("repl_number", DEFAULT_REPL_NUM)
    _write_to_file(output_fd, "repl_number=%d" % (repl_num))

    # Container section
    _write_to_file(output_fd, "\n[container]")

    if not _section_defined("container"):
        return RETURN_NOT_DEFINED

    for container in _swift["container"]["hosts"]:
        data = _get_drive(container)
        _write_to_file(output_fd, data)

    _write_to_file(output_fd, "\n[container:vars]")
    repl_num = _swift["container"].get("repl_number", DEFAULT_REPL_NUM)
    _write_to_file(output_fd, "repl_number=%d" % (repl_num))

    # Objects / Storage polices
    _storage_policies = {}
    _storage_policies_idx = {}
    if not _section_defined("storage_policies"):
        return RETURN_NOT_DEFINED

    if "policies" not in _swift["storage_policies"]:
        print("ERROR: No storage policies defined")
        return 4

    for policy in _swift["storage_policies"]["policies"]:
        if policy["name"] in _storage_policies:
            print("ERROR: Storage policy '%s' already defined" % policy["name"])
            return 5

        if policy["index"] in _storage_policies_idx:
            print("ERROR: Storage policy index '%s' already defined" %
                  policy["index"])
            return 5

        _storage_policies[policy['name']] = "storagepolicy_%(name)s" % policy
        _storage_policies_idx[policy['index']] = policy["name"]

        _write_to_file(output_fd,
                       "\n[%s]" % (_storage_policies[policy['name']]))

        # print the storage policy hosts.
        for drive in policy.get("hosts", []):
            data = _get_drive(drive)
            _write_to_file(output_fd, data)

        _write_to_file(output_fd,
                       "\n[%s:vars]" % (_storage_policies[policy['name']]))
        _write_to_file(output_fd, "index=%d" % (policy['index']))
        _write_to_file(output_fd, "policy_name=%s" % (policy['name']))
        policy_type = policy.get("type", 'replication')
        _write_to_file(output_fd, "type=%s" % (policy_type))

        depricated = policy.get("depricated", False)
        if depricated:
            _write_to_file(output_fd, "depricated=True")

        default = policy.get("default", False)
        if default:
            _write_to_file(output_fd, "default=True")

        if policy_type == 'replication':
            repl_num = policy.get("repl_number", DEFAULT_REPL_NUM)
            _write_to_file(output_fd, "repl_num=%d" % (repl_num))

    # Write out the storage policy catch all group
    _write_to_file(output_fd, "\n[storagepolicy:children]")
    for name, longname in _storage_policies.items():
        _write_to_file(output_fd, "%s" % (longname))

    _write_to_file(output_fd, "\n[storagepolicy:vars]")
    if 'default' in _swift["storage_policies"]:
        default_sp = _swift["storage_policies"]["default"]
        if default_sp in _storage_policies:
            _write_to_file(output_fd, "default=%s" % (default_sp))
        elif default_sp in _storage_policies_idx:
            _write_to_file(output_fd,
                           "default=%s" % (_storage_policies_idx[default_sp]))
        else:
            print("ERROR: Default storage policy '%s' doesn't exist",
                  default_sp)

    # Write out the object and swift catchall groups
    _write_to_file(output_fd, CATCH_ALL_GROUPS)

    # Now write out the global swift options that is gathered in the file
    for option in swift_options:
        _write_to_file(output_fd, option)

    # Done
    if output_fd:
        output_fd.flush()
        output_fd.close()
    return 0

if __name__ == "__main__":
    parser = OptionParser(USAGE)
    parser.add_option("-s", "--setup", dest="setup",
                      help="Specify the swift setup file.", metavar="FILE")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="Be more verbose")
    parser.add_option("-d", "--dryrun", action="store_true", dest="dry_run",
                      default=False, help="Print result out to stdout.")
    parser.add_option("-C", "--copy", action="store_false", dest="overwrite",
                      default=True, help="Make a copy if inventory file exists")
    parser.add_option("-i", "--import", dest="ring_folder", metavar="FILE",
                      help="Attempt to build a swift setup file"
                           " from the Swift builder files. Pass directory here")

    options, args = parser.parse_args(sys.argv[1:])
    if not options.setup or not exists(options.setup):
        print("Swift setup file not found or doesn't exist")
        parser.print_help()
        sys.exit(1)

    sys.exit(main(options.setup, options.verbose, options.dry_run,
                  options.overwrite))
