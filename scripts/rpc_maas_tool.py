#!/usr/bin/env python

from rackspace_monitoring.drivers.rackspace import RackspaceMonitoringValidationError
from rackspace_monitoring.providers import get_driver
from rackspace_monitoring.types import Provider

import ConfigParser
import argparse
import sys


def main(args):
    config = ConfigParser.RawConfigParser()
    config.read('/root/.raxrc')

    driver = get_driver(Provider.RACKSPACE)
    conn = _get_conn(config, driver)

    if conn is None:
        print("Unable to get a client to MaaS, exiting")
        sys.exit(1)

    if args.command == 'alarms':
        alarms(args, conn)
    elif args.command == 'check':
        check(args, conn)
    elif args.command == 'delete':
        delete(args, conn)


def alarms(args, conn):
    for entity in _get_entities(args, conn):
        alarms = conn.list_alarms(entity)
        if alarms:
            print('Entity %s (%s):' % (entity.id, entity.label))
            for alarm in alarms:
                print ' - %s' % alarm.label


def check(args, conn):
    for entity in _get_entities(args, conn):
        error = 0
        for check in conn.list_checks(entity):
            try:
                result = conn.test_existing_check(check)
            except RackspaceMonitoringValidationError as e:
                print('Entity %s (%s):' % (entity.id, entity.label))
                print(' - %s' % e)
                break

            available = result[0]['available']
            status = result[0]['status']

            if available is False or status != 'okay':
                if error == 0:
                    print('Entity %s (%s):' % (entity.id, entity.label))
                    error = 1
                if available is False:
                    print(' - Check %s (%s) did not run correctly' %
                          (check.id, check.label))
                elif status != 'okay':
                    print(" - Check %s (%s) ran correctly but returned a "
                          "'%s' status" % (check.id, check.label, status))


def delete(args, conn):
    count = 0

    if args.force is False:
        print "*** Proceeding WILL delete ALL your checks (and data) ****"
        if raw_input("Type 'from orbit' to continue: ") != 'from orbit':
            return

    for entity in _get_entities(args, conn):
        error = 0
        for check in conn.list_checks(entity):
            conn.delete_check(check)
            count += 1

    print "Number of checks deleted: %s" % count


def _get_conn(config, driver):
    conn = None

    if config.has_section('credentials'):
        try:
            user = config.get('credentials', 'username')
            api_key = config.get('credentials', 'api_key')
        except Exception as e:
            print e
        else:
            conn = driver(user, api_key)
    if not conn and config.has_section('api'):
        try:
            url = config.get('api', 'url')
            token = config.get('api', 'token')
        except Exception as e:
            print e
        else:
            conn = driver(None, None, ex_force_base_url=url,
                          ex_force_auth_token=token)

    return conn


def _get_entities(args, conn):
    entities = []

    for entity in conn.list_entities():
        if args.prefix is None or args.prefix in entity.label:
            entities.append(entity)

    return entities


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test MaaS checks')
    parser.add_argument('command',
                        type=str,
                        choices=['alarms', 'check', 'delete'],
                        help='Command to execute')
    parser.add_argument('--force',
                        action="store_true",
                        help='Do stuff irrespective of consequence'),
    parser.add_argument('--prefix',
                        type=str,
                        help='Limit testing to checks on entities labelled w/ '
                             'this prefix',
                        default=None)
    args = parser.parse_args()

    main(args)
